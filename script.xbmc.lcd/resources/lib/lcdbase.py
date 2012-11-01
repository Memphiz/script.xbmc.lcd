'''
    XBMC LCDproc addon
    Copyright (C) 2012 Team XBMC
    Copyright (C) 2012 Daniel Scheller
    
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import platform
import xbmc
import xbmcgui
import sys
import os
import re
import telnetlib
import time

from xml.etree import ElementTree as xmltree
from array import array

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__settings__ = sys.modules[ "__main__" ].__settings__
__cwd__ = sys.modules[ "__main__" ].__cwd__
__icon__ = sys.modules[ "__main__" ].__icon__
__lcdxml__ = xbmc.translatePath( os.path.join("special://masterprofile","LCD.xml"))

from settings import *
from extraicons import *

g_dictEmptyLineDescriptor = {} 
g_dictEmptyLineDescriptor['type'] = str("text")
g_dictEmptyLineDescriptor['startx'] = int(0)
g_dictEmptyLineDescriptor['text'] = str("")
g_dictEmptyLineDescriptor['endx'] = int(0)

# global functions
def log(loglevel, msg):
  xbmc.log("### [%s] - %s" % (__scriptname__,msg,),level=loglevel ) 

# enumerations
class DISABLE_ON_PLAY:
  DISABLE_ON_PLAY_NONE = 0
  DISABLE_ON_PLAY_VIDEO = 1
  DISABLE_ON_PLAY_MUSIC = 2
  
class LCD_MODE:
  LCD_MODE_GENERAL     = 0
  LCD_MODE_MUSIC       = 1
  LCD_MODE_VIDEO       = 2
  LCD_MODE_NAVIGATION  = 3
  LCD_MODE_SCREENSAVER = 4
  LCD_MODE_XBE_LAUNCH  = 5
  LCD_MODE_PVRTV       = 6
  LCD_MODE_PVRRADIO    = 7
  LCD_MODE_MAX         = 8

class LCD_LINETYPE:
  LCD_LINETYPE_TEXT      = "text"
  LCD_LINETYPE_PROGRESS  = "progressbar"
  LCD_LINETYPE_ICONTEXT  = "icontext"
  LCD_LINETYPE_BIGSCREEN = "bigscreen"

class LcdBase():
  def __init__(self):
    self.m_disableOnPlay = DISABLE_ON_PLAY.DISABLE_ON_PLAY_NONE
    self.m_lcdMode = [None] * LCD_MODE.LCD_MODE_MAX
    self.m_extraBars = [None] * (LCD_EXTRABARS_MAX + 1)
    self.m_bDimmedOnPlayback = False
    self.m_strInfoLabelEncoding = "utf-8" # http://forum.xbmc.org/showthread.php?tid=125492&pid=1045926#pid1045926
    self.m_strLCDEncoding = "iso-8859-1" # LCDproc wants iso-8859-1!
    self.m_strScrollSeparator = " "
    self.m_bProgressbarSurroundings = False
    self.m_iIconTextOffset = 2
    self.m_bAllowEmptyLines = False

# @abstractmethod
  def _concrete_method(self):
    pass

# @abstractmethod
  def IsConnected(self):
    pass

# @abstractmethod
  def Stop(self):
    pass

# @abstractmethod
  def Suspend(self):
    pass

# @abstractmethod   
  def Resume(self):
    pass

# @abstractmethod   
  def SetBackLight(self, iLight):
    pass

# @abstractmethod
  def SetContrast(self, iContrast):
    pass

# @abstractmethod  
  def SetBigDigits(self, strTimeString, bForceUpdate):
    pass

# @abstractmethod   
  def ClearLine(self, iLine):
    pass

# @abstractmethod     
  def SetLine(self, iLine, strLine, dictDescriptor, bForce):
    pass

# @abstractmethod     
  def ClearDisplay(self):
    pass

# @abstractmethod     
  def FlushLines(self):
    pass
    
# @abstractmethod	
  def GetColumns(self):
    pass

# @abstractmethod
  def GetRows(self):
    pass

# @abstractmethod
  def SetPlayingStateIcon(self):
    pass

# @abstractmethod
  def SetProgressBar(self, percent, lineIdx):
    pass

  def GetProgressBarPercent(self, tCurrent, tTotal):
    if float(tTotal) == 0.0:
      return 0

    return float(tCurrent)/float(tTotal)

  def Initialize(self):
    self.m_disableOnPlay = DISABLE_ON_PLAY.DISABLE_ON_PLAY_NONE
    self.LoadSkin(__lcdxml__)

  def LoadSkin(self, xmlFile):
    self.Reset()
    doc = xmltree.parse(xmlFile)
    for element in doc.getiterator():
      #PARSE LCD infos
      if element.tag == "lcd":
        # load our settings  
        disableOnPlay = element.find("disableonplay")
        if disableOnPlay != None:
          self.m_disableOnPlay = DISABLE_ON_PLAY.DISABLE_ON_PLAY_NONE
          if str(disableOnPlay.text).find("video") >= 0:
            self.m_disableOnPlay += DISABLE_ON_PLAY.DISABLE_ON_PLAY_VIDEO
          if str(disableOnPlay.text).find("music") >= 0:
            self.m_disableOnPlay += DISABLE_ON_PLAY.DISABLE_ON_PLAY_MUSIC

        # apply scrollseparator
        scrollSeparator = element.find("scrollseparator")
        if scrollSeparator != None:

          if str(scrollSeparator.text).strip() != "":
            self.m_strScrollSeparator = " " + scrollSeparator.text + " "

        # check for progressbarsurroundings setting
        self.m_bProgressbarSurroundings = False

        progressbarSurroundings = element.find("progressbarsurroundings")
        if progressbarSurroundings != None:
          if str(progressbarSurroundings.text) == "on":
            self.m_bProgressbarSurroundings = True

        # icontext offset setting
        self.m_iIconTextOffset = 2

        icontextoffset = element.find("icontextoffset")
        if icontextoffset != None and icontextoffset.text != None:
          try:
            intoffset = int(icontextoffset.text)
          except ValueError, TypeError:
            log(xbmc.LOGERROR, "Value for icontextoffset must be integer (got: %s)" % (icontextoffset.text))
          else:
            if intoffset <= 0 or intoffset >= self.GetColumns():
              log(xbmc.LOGERROR, "Value %d for icontextoffset out of range, ignoring" % (intoffset))
            else:
              if intoffset < 2:
                log(xbmc.LOGWARNING, "Value %d for icontextoffset smaller than LCDproc's icon width" % (intoffset))
              self.m_iIconTextOffset = intoffset

        # check for allowemptylines setting
        self.m_bAllowEmptyLines = False

        allowemptylines = element.find("allowemptylines")
        if allowemptylines != None:
          if str(allowemptylines.text) == "on":
            self.m_bAllowEmptyLines = True

        # extra progress bars
        for i in range(1, LCD_EXTRABARS_MAX + 1):
          extrabar = None
          extrabar = element.find("extrabar%i" % (i))
          if extrabar != None:
            if str(extrabar.text).strip() in ["progress", "volume", "menu"]:
              self.m_extraBars[i] = str(extrabar.text).strip()
            else:
              self.m_extraBars[i] = ""

        #load modes
        tmpMode = element.find("music")
        self.LoadMode(tmpMode, LCD_MODE.LCD_MODE_MUSIC)

        tmpMode = element.find("video")
        self.LoadMode(tmpMode, LCD_MODE.LCD_MODE_VIDEO)

        tmpMode = element.find("general")
        self.LoadMode(tmpMode, LCD_MODE.LCD_MODE_GENERAL)

        tmpMode = element.find("navigation")
        self.LoadMode(tmpMode, LCD_MODE.LCD_MODE_NAVIGATION)
    
        tmpMode = element.find("screensaver")
        self.LoadMode(tmpMode, LCD_MODE.LCD_MODE_SCREENSAVER)

        tmpMode = element.find("xbelaunch")
        self.LoadMode(tmpMode, LCD_MODE.LCD_MODE_XBE_LAUNCH)

        tmpMode = element.find("pvrtv")
        self.LoadMode(tmpMode, LCD_MODE.LCD_MODE_PVRTV)

        tmpMode = element.find("pvrradio")
        self.LoadMode(tmpMode, LCD_MODE.LCD_MODE_PVRRADIO)

  def LoadMode(self, node, mode):
    if node == None:
      log(xbmc.LOGWARNING, "Empty Mode %d, check LCD.xml" % (mode))
      self.m_lcdMode[mode].append(g_dictEmptyLineDescriptor)
      return

    if len(node.findall("line")) <= 0:
      log(xbmc.LOGWARNING, "Mode %d defined without lines, check LCD.xml" % (mode))
      self.m_lcdMode[mode].append(g_dictEmptyLineDescriptor)
      return

    # regex to determine any of $INFO[LCD.Time(Wide)21-44]
    timeregex = r'' + re.escape('$INFO[LCD.') + 'Time((Wide)?\d?\d?)' + re.escape(']')

    for line in node.findall("line"):
      linedescriptor = {}
      if line.text == None:
        linetext = ""
      else:
        linetext = str(line.text).strip()
      
      # make sure linetext has something so re.match won't fail
      if linetext != "":
        timematch = re.match(timeregex, linetext, flags=re.IGNORECASE)

        # if line matches, throw away mode, add BigDigit descriptor and end processing for this mode
        if timematch != None:
          linedescriptor['type'] = LCD_LINETYPE.LCD_LINETYPE_BIGSCREEN
          linedescriptor['startx'] = int(1)
          linedescriptor['text'] = "Time"
          linedescriptor['endx'] = int(self.GetColumns())

          self.m_lcdMode[mode] = []
          self.m_lcdMode[mode].append(linedescriptor)
          return

      # progressbar line if InfoLabel exists
      if str(linetext).lower().find("$info[lcd.progressbar]") >= 0:
        linedescriptor['type'] = LCD_LINETYPE.LCD_LINETYPE_PROGRESS
        linedescriptor['startx'] = int(1)
        linedescriptor['text'] = ""
        linedescriptor['endx'] = int(self.m_iCellWidth) * int(self.m_iColumns)

        if self.m_bProgressbarSurroundings == True:
          linedescriptor['startx'] = int(2)
          linedescriptor['text'] = "[" + " " * (self.m_iColumns - 2) + "]"
          linedescriptor['endx'] = int(self.m_iCellWidth) * (int(self.GetColumns()) - 2)

      # textline with icon in front
      elif str(linetext).lower().find("$info[lcd.playicon]") >= 0:
        linedescriptor['type'] = LCD_LINETYPE.LCD_LINETYPE_ICONTEXT
        linedescriptor['startx'] = int(1 + self.m_iIconTextOffset) # icon widgets take 2 chars, so shift text offset (default: 2)
        # support Python < 2.7 (e.g. Debian Squeeze)
        if self.m_vPythonVersion < (2, 7):
          linedescriptor['text'] = str(re.sub(r'\s?' + re.escape("$INFO[LCD.PlayIcon]") + '\s?', ' ', str(linetext))).strip()
        else:
          linedescriptor['text'] = str(re.sub(r'\s?' + re.escape("$INFO[LCD.PlayIcon]") + '\s?', ' ', str(linetext), flags=re.IGNORECASE)).strip()
        linedescriptor['endx'] = int(self.GetColumns())
      # standard (scrolling) text line
      else:
        linedescriptor['type'] = LCD_LINETYPE.LCD_LINETYPE_TEXT
        linedescriptor['startx'] = int(1)
        linedescriptor['text'] = str(linetext)
        linedescriptor['endx'] = int(self.GetColumns())

      self.m_lcdMode[mode].append(linedescriptor)

  def Reset(self):
    self.m_disableOnPlay = DISABLE_ON_PLAY.DISABLE_ON_PLAY_NONE
    for i in range(0,LCD_MODE.LCD_MODE_MAX):
      self.m_lcdMode[i] = []			#clear list

  def Shutdown(self):
    from settings import settings_getDimOnShutdown

    log(xbmc.LOGNOTICE, "Shutting down")

    if settings_getDimOnShutdown():
      self.SetBackLight(0)

    if self.m_cExtraIcons is not None:
      if not self.SendCommand(self.m_cExtraIcons.GetClearAllCmd(), True):
        log(xbmc.LOGERROR, "Shutdown(): Cannot clear extra icons")

    self.CloseSocket()

  def timeToSecs(self, timeAr):
    arLen = len(timeAr)
    if arLen == 1:
      currentSecs = int(timeAr[0])
    elif arLen == 2:
      currentSecs = int(timeAr[0]) * 60 + int(timeAr[1])
    elif arLen == 3:
      currentSecs = int(timeAr[0]) * 60 * 60 + int(timeAr[1]) * 60 + int(timeAr[2])
    return currentSecs

  def getCurrentTimeSecs(self):
    currentTimeAr = xbmc.getInfoLabel("Player.Time").split(":")
    if currentTimeAr[0] == "":
      return 0

    return self.timeToSecs(currentTimeAr)
 
  def getCurrentDurationSecs(self):
    currentDurationAr = xbmc.getInfoLabel("Player.Duration").split(":")
    if currentDurationAr[0] == "":
      return 0

    return self.timeToSecs(currentDurationAr)

  def GetProgress(self):
    currentSecs = self.getCurrentTimeSecs()
    durationSecs = self.getCurrentDurationSecs()
    return self.GetProgressBarPercent(currentSecs,durationSecs)

  def GetVolumePercent(self):
    volumedb = float(string.replace(string.replace(xbmc.getInfoLabel("Player.Volume"), ",", "."), " dB", ""))
    return (100 * (60.0 + volumedb) / 60)

  def Render(self, mode, bForce):
    outLine = 0
    inLine = 0

    while (outLine < int(self.GetRows()) and inLine < len(self.m_lcdMode[mode])):
      #parse the progressbar infolabel by ourselfs!
      if self.m_lcdMode[mode][inLine]['type'] == LCD_LINETYPE.LCD_LINETYPE_PROGRESS:
        # get playtime and duration and convert into seconds
        percent = self.GetProgress()
        pixelsWidth = self.SetProgressBar(percent, self.m_lcdMode[mode][inLine]['endx'])
        line = "p" + str(pixelsWidth)
      else:
        if self.m_lcdMode[mode][inLine]['type'] == LCD_LINETYPE.LCD_LINETYPE_ICONTEXT:
          self.SetPlayingStateIcon()

        line = xbmc.getInfoLabel(self.m_lcdMode[mode][inLine]['text'])
        if self.m_strInfoLabelEncoding != self.m_strLCDEncoding:
          line = line.decode(self.m_strInfoLabelEncoding).encode(self.m_strLCDEncoding, "replace")
        self.SetProgressBar(0, -1)

      if self.m_bAllowEmptyLines or len(line) > 0:
        self.SetLine(outLine, line, self.m_lcdMode[mode][inLine], bForce)
        outLine += 1

      inLine += 1

    # fill remainder with empty space if not bigscreen
    if self.m_lcdMode[mode][0]['type'] != LCD_LINETYPE.LCD_LINETYPE_BIGSCREEN:
      while outLine < int(self.GetRows()):
        self.SetLine(outLine, "", g_dictEmptyLineDescriptor, bForce)
        outLine += 1

    if self.m_cExtraIcons is not None:
      self.SetExtraInformation()
      self.m_strSetLineCmds += self.m_cExtraIcons.GetOutputCommands()

    self.FlushLines()

  def DisableOnPlayback(self, playingVideo, playingAudio):
    if (playingVideo and (self.m_disableOnPlay & DISABLE_ON_PLAY.DISABLE_ON_PLAY_VIDEO)) or (playingAudio and (self.m_disableOnPlay & DISABLE_ON_PLAY.DISABLE_ON_PLAY_MUSIC)):
      if not self.m_bDimmedOnPlayback:
        self.SetBackLight(0)
        self.m_bDimmedOnPlayback = True
        self.ClearDisplay()
    elif self.m_bDimmedOnPlayback:
      self.SetBackLight(1)
      self.m_bDimmedOnPlayback = False

  def SetExtraInfoPlaying(self, isplaying, isvideo, isaudio):
    if isplaying:
      if isvideo:
        try:
          iVideoRes = int(xbmc.getInfoLabel("VideoPlayer.VideoResolution"))
        except:
          iVideoRes = int(0)

        try:
          iScreenRes = int(xbmc.getInfoLabel("System.ScreenHeight"))
        except:
          iScreenRes = int(0)

        if xbmc.getCondVisibility("PVR.IsPlayingTV"):
          self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_TV, True)
        else:
          self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_MOVIE, True)

        if iVideoRes < 720:
          self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_RESOLUTION_SD, True)
        else:
          self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_RESOLUTION_HD, True)

        if iScreenRes <= (iVideoRes + (float(iVideoRes) * 0.1)) and iScreenRes >= (iVideoRes - (float(iVideoRes) * 0.1)):
          self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_OUTSOURCE, True)
        else:
          self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_OUTFIT, True)

      elif isaudio:
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_MUSIC, True)

    else:
      self.m_cExtraIcons.ClearIconStates(LCD_EXTRAICONCATEGORIES.LCD_ICONCAT_MODES)
      ###FIXME###TODO### ID = g_windowManager.GetActiveWindow() translation for navigation

  def SetExtraInfoCodecs(self, isplaying, isvideo, isaudio):
    # initialise stuff to avoid uninitialised var stuff
    strVideoCodec = ""
    strAudioCodec = ""
    iAudioChannels = 0

    if isplaying:
      if xbmc.getCondVisibility("Player.Passthrough"):
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_SPDIF, True)
      else:
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_SPDIF, False)
      
      if isvideo:
        strVideoCodec = str(xbmc.getInfoLabel("VideoPlayer.VideoCodec")).lower()
        strAudioCodec = str(xbmc.getInfoLabel("VideoPlayer.AudioCodec")).lower()
        iAudioChannels = xbmc.getInfoLabel("VideoPlayer.AudioChannels")
      elif isaudio:
        strVideoCodec = ""
        strAudioCodec = str(xbmc.getInfoLabel("MusicPlayer.Codec")).lower()
        iAudioChannels = xbmc.getInfoLabel("MusicPlayer.Channels")

      # check video codec
      # any mpeg video
      if strVideoCodec in ["mpg", "mpeg", "mpeg2video", "h264", "x264", "mpeg4"]:
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_VCODEC_MPEG, True)

      # any divx
      elif strVideoCodec in ["divx", "dx50", "div3"]:
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_VCODEC_DIVX, True)

      # xvid
      elif strVideoCodec == "xvid":
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_VCODEC_XVID, True)

      # wmv
      elif strVideoCodec == "wmv":
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_VCODEC_WMV, True)

      # anything else
      else:
        self.m_cExtraIcons.ClearIconStates(LCD_EXTRAICONCATEGORIES.LCD_ICONCAT_VIDEOCODECS)

      # check audio codec
      # any mpeg audio
      if strAudioCodec in ["mpga", "mp2"]:
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_ACODEC_MPEG, True)

      # any ac3/dolby digital
      elif strAudioCodec in ["ac3", "truehd"]:
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_ACODEC_AC3, True)

      # any dts
      elif strAudioCodec in ["dts", "dca", "dtshd_ma"]:
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_ACODEC_DTS, True)

      # mp3
      elif strAudioCodec == "mp3":
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_ACODEC_MP3, True)

      # any ogg vorbis
      elif strAudioCodec in ["ogg", "vorbis"]:
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_ACODEC_OGG, True)

      # any wma        
      elif strAudioCodec in ["wma", "wmav2"]:
        if isvideo:
          self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_ACODEC_VWMA, True)
        else:
          self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_ACODEC_AWMA, True)

      # any pcm, wav or flac
      elif strAudioCodec in ["wav", "pcm", "flac"]:
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_ACODEC_WAV, True)

      # anything else
      else:
        self.m_cExtraIcons.ClearIconStates(LCD_EXTRAICONCATEGORIES.LCD_ICONCAT_AUDIOCODECS)

      # make sure iAudioChannels contains something useful
      if iAudioChannels == "" and strAudioCodec != "":
        iAudioChannels = 2
      elif iAudioChannels == "":
        iAudioChannels = 0
      else:
        iAudioChannels = int(iAudioChannels)

      # decide which icon (set) to activate
      if iAudioChannels > 0 and iAudioChannels <= 3:
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_OUT_2_0, True)
      elif iAudioChannels <= 6:
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_OUT_5_1, True)
      elif iAudioChannels <= 8:
        self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_OUT_7_1, True)
      else:
        self.m_cExtraIcons.ClearIconStates(LCD_EXTRAICONCATEGORIES.LCD_ICONCAT_AUDIOCHANNELS)

    else:
      self.m_cExtraIcons.ClearIconStates(LCD_EXTRAICONCATEGORIES.LCD_ICONCAT_CODECS)

  def SetExtraInfoGeneric(self, ispaused):
    if self.GetVolumePercent() == 0.0:
      self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_MUTE, True)
    else:
      self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_MUTE, False)

    if xbmc.getCondVisibility("Player.Paused"):
      self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_PAUSE, True)
    else:
      self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_PAUSE, False)

    if xbmc.getCondVisibility("PVR.IsRecording"):
      self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_RECORD, True)
    else:
      self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_RECORD, False)

    if xbmc.getCondVisibility("Playlist.IsRandom"):
      self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_SHUFFLE, True)
    else:
      self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_SHUFFLE, False)

    if xbmc.getCondVisibility("Playlist.IsRepeat") or xbmc.getCondVisibility("Playlist.IsRepeatOne"):
      self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_REPEAT, True)
    else:
      self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_REPEAT, False)

    if xbmc.getCondVisibility("System.HasMediaDVD"):
      self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_DISC_IN, True)
    else:
      self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_DISC_IN, False)

    if xbmc.getCondVisibility("System.ScreenSaverActive"):
      self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_TIME, True)
    else:
      self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_TIME, False)
      
    ###FIXME###TODO### g_windowManager.IsWindowActive(WINDOW_DIALOG_VOLUME_BAR) : ICON_VOLUME
    ###FIXME###TODO### g_windowManager.IsWindowActive(WINDOW_DIALOG_KAI_TOAST)  : ICON_ALARM

  def SetExtraInfoBars(self, isplaying):
    for i in range(1, LCD_EXTRABARS_MAX):
      if self.m_extraBars[i] == "progress":
        if isplaying:
          self.m_cExtraIcons.SetBar(i, (self.GetProgress() * 100))
        else:
          self.m_cExtraIcons.SetBar(i, 0)
      elif self.m_extraBars[i] == "volume":
        self.m_cExtraIcons.SetBar(i, self.GetVolumePercent())
      elif self.m_extraBars[i] == "menu":
        if isplaying:
          self.m_cExtraIcons.SetBar(i, 0)
        else:
          self.m_cExtraIcons.SetBar(i, 100)
      else:
        self.m_cExtraIcons.SetBar(i, 0)

  def SetExtraInformation(self):
    # These four states count for "isplayinganything"
    bPaused = xbmc.getCondVisibility("Player.Paused")
    bPlaying = (xbmc.getCondVisibility("Player.Playing") |
                bPaused |
                xbmc.getCondVisibility("Player.Forwarding") |
                xbmc.getCondVisibility("Player.Rewinding"))

    bIsVideo = xbmc.getCondVisibility("Player.HasVideo")
    bIsAudio = xbmc.getCondVisibility("Player.HasAudio")
    
    self.m_cExtraIcons.SetIconState(LCD_EXTRAICONS.LCD_EXTRAICON_PLAYING, bPlaying)

    self.SetExtraInfoPlaying(bPlaying, bIsVideo, bIsAudio)
    self.SetExtraInfoCodecs(bPlaying, bIsVideo, bIsAudio)
    self.SetExtraInfoGeneric(bPaused)
    self.SetExtraInfoBars(bPlaying)









