'''
    LCD/VFD for XBMC
    Copyright (C) 2011 Team XBMC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

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
 
# global functions
def log(loglevel, msg):
  xbmc.log("### [%s] - %s" % (__scriptname__,msg,),level=loglevel ) 

'''
# TEMPLATE: TRANSLATION-TABLE FOR FUTURE LCD-TYPE-CHARSETS
{
0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f,
0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f,
0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e, 0x4f,
0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x5b, 0x5c, 0x5d, 0x5e, 0x5f,
0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x6b, 0x6c, 0x6d, 0x6e, 0x6f,
0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x7b, 0x7c, 0x7d, 0x7e, 0x7f,
0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x8b, 0x8c, 0x8d, 0x8e, 0x8f,
0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0x9b, 0x9c, 0x9d, 0x9e, 0x9f,
0xa0, 0xa1, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xab, 0xac, 0xad, 0xae, 0xaf,
0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xbb, 0xbc, 0xbd, 0xbe, 0xbf,
0xc0, 0xc1, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xcb, 0xcc, 0xcd, 0xce, 0xcf,
0xd0, 0xd1, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda, 0xdb, 0xdc, 0xdd, 0xde, 0xdf,
0xe0, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xeb, 0xec, 0xed, 0xee, 0xef,
0xf0, 0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8, 0xf9, 0xfa, 0xfb, 0xfc, 0xfd, 0xfe, 0xff
}

'''
'''
# UNUSED by now
def GetLCDCharsetCharacter(_nCharacter, _nCharset):

  arrCharsets = [[ # Xbmc default, currently implemented elsewhere
  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
  ],
  [ # Small Char
  [0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01], #    |    _
  [0x1f, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x1f], #   _     _|
  [0x1f, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11], #  | |
  [0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x1f], #         _|
  [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1f], #  |_|    _
  [0x1f, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1f], #   _    |_
  [0x1f, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01], #    |    _
  [0x1f, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1f]  #        |_|
  ],
  [ # Medium Char
  [0x1f, 0x1f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], #
  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1f, 0x1f], #         _
  [0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x1f, 0x1f], #  |_     _
  [0x1f, 0x1f, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18], #   _      |
  [0x1f, 0x1f, 0x18, 0x18, 0x18, 0x18, 0x1f, 0x1f], #  |_     _
  [0x1f, 0x1f, 0x03, 0x03, 0x03, 0x03, 0x1f, 0x1f], #  _      _|
  [0x1f, 0x1f, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03], #   |
  [0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x1f, 0x1f]  #         _|
  ],
  [ # Big Char
  [0x01, 0x03, 0x03, 0x07, 0x07, 0x0f, 0x0f, 0x1f], # topleft corner
  [0x10, 0x18, 0x18, 0x1c, 0x1c, 0x1e, 0x1e, 0x1f], # topright corner
  [0x1f, 0x1e, 0x1e, 0x1c, 0x1c, 0x18, 0x18, 0x10], # bottomright corner
  [0x1f, 0x0f, 0x0f, 0x07, 0x07, 0x03, 0x03, 0x01], # bottomleft corner
  [0x1f, 0x1f, 0x1f, 0x1f, 0x00, 0x00, 0x00, 0x00], # upper half block
  # Free to use
  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
  ]]
  
  if _nCharset == -1:
    _nCharset = m_eCurrentCharset

  if ( ( _nCharacter >= 64 ) or ( _nCharset >= CUSTOM_CHARSET.CUSTOM_CHARSET_MAX ) ):
    return 0

  return arrCharsets[_nCharset][_nCharacter/8][_nCharacter%8]
'''

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
  LCD_MODE_MAX         = 6

class CUSTOM_CHARSET:
  CUSTOM_CHARSET_DEFAULT      = 0
  CUSTOM_CHARSET_SMALLCHAR    = 1
  CUSTOM_CHARSET_MEDIUMCHAR   = 2
  CUSTOM_CHARSET_BIGCHAR      = 3
  CUSTOM_CHARSET_MAX          = 4

class LcdBase():
  def __init__(self):
    self.m_disableOnPlay = DISABLE_ON_PLAY.DISABLE_ON_PLAY_NONE
    self.m_eCurrentCharset = CUSTOM_CHARSET.CUSTOM_CHARSET_DEFAULT
    self.m_lcdMode = [None] * LCD_MODE.LCD_MODE_MAX
    self.m_bDimmedOnPlayback = False

#  @abstractmethod
  def _concrete_method(self):
      pass
#  @abstractmethod
  def Stop(self):
    pass

#  @abstractmethod
  def Suspend(self):
    pass

#  @abstractmethod   
  def Resume(self):
    pass

#  @abstractmethod   
  def SetBackLight(self, iLight):
    pass

#  @abstractmethod  
  def SetContrast(self, iContrast):
    pass

#  @abstractmethod     
  def SetLine(self, iLine, strLine):
    pass
    
#  @abstractmethod	
  def GetColumns(self):
    pass

#  @abstractmethod
  def GetRows(self):
    pass

#  @abstractmethod
  def SetProgressBar(self, percent, lineIdx):
    pass

  def GetProgressBarPercent(self, tCurrent, tTotal):
    return float(tCurrent)/float(tTotal)

  def SetCharset(self,_nCharset):
    if _nCharset < CUSTOM_CHARSET.CUSTOM_CHARSET_MAX:
      self.m_eCurrentCharset = _nCharset

  def GetBigDigit(self,_nCharset, _nDigit, _nLine, _nMinSize, _nMaxSize, _bSpacePadding):
    # Get the partial digit(s) for the given line
    # that is needed to build a big character
    nCurrentSize = 0
    nCurrentValue = 0
    nValue = 0
    strDigits = ""
    strCurrentDigit = ""

    # If the charset doesn't match our
    # custom chars, return with nothing
    # The XBMC 'icon' charset
    if ( _nCharset == CUSTOM_CHARSET.CUSTOM_CHARSET_DEFAULT ) or ( _nCharset >= CUSTOM_CHARSET.CUSTOM_CHARSET_MAX ):
      return ""

    arrSizes = [ 
    [ 1, 1 ],
    [ 1, 2 ],
    [ 2, 2 ],
    [ 3, 4 ]]

    # Return with nothing if the linenumber falls outside our char 'height'
    if _nLine > arrSizes[ _nCharset ][1]:
      return ""

    # Define the 2x1 line characters
    arrMedNumbers = [ 
    [[0x0a], [0x0c]], # 0
    [[0x08], [0x08]], # 1 # 0xaf
    [[0x0e], [0x0d]], # 2
    [[0x09], [0x0b]], # 3
    [[0x0c], [0x08]], # 4
    [[0x0d], [0x0b]], # 5
    [[0x0d], [0x0c]], # 6
    [[0x0e], [0x08]], # 7
    [[0x0f], [0x0c]], # 8
    [[0x0f], [0x0b]]] # 9

    # Define the 2x2 bold line characters
    arrMedBoldNumbers = [ 
    [[0x0b, 0x0e], [0x0a, 0x0f]], #0
    [[0x0e, 0x20], [0x0f, 0x09]], #1
    [[0x08, 0x0d], [0x0c, 0x09]], #2
    [[0x08, 0x0d], [0x09, 0x0f]], #3
    [[0x0a, 0x0f], [0x20, 0x0e]], #4
    [[0x0c, 0x08], [0x09, 0x0d]], #5
    [[0x0b, 0x08], [0x0c, 0x0d]], #6
    [[0x08, 0x0e], [0x20, 0x0e]], #7
    [[0x0c, 0x0d], [0x0a, 0x0f]], #8
    [[0x0c, 0x0d], [0x09, 0x0f]]] # 9
    
    # Define the 4 line characters (this could be more readable, but that may take up to 3 screens)
    arrBigNumbers = [
    [
    [0x08, 0xa0, 0x09],    # 0
    [0xa0, 0x20, 0xa0],    # 0
    [0xa0, 0x20, 0xa0],    # 0
    [0x0b, 0xa0, 0x0a],    # 0
    ],
    [ 
    [0x08, 0xa0, 0x20],    # 1
    [0x20, 0xa0, 0x20],    # 1
    [0x20, 0xa0, 0x20],    # 1
    [0xa0, 0xa0, 0xa0],   # 1
    ], 
    [ 
    [0x08, 0xa0, 0x09],    # 2
    [0x20, 0x08, 0x0a],    # 2
    [0x08, 0x0a, 0x20],    # 2
    [0xa0, 0xa0, 0xa0],    # 2
    ],
    [ 
    [0x08, 0xa0, 0x09],    # 3
    [0x20, 0x20, 0xa0],    # 3
    [0x20, 0x0c, 0xa0],    # 3
    [0x0b, 0xa0, 0x0a],    # 3
    ],
    [ 
    [0xa0, 0x20, 0xa0],    # 4
    [0xa0, 0xa0, 0xa0],    # 4
    [0x20, 0x20, 0xa0],    # 4
    [0x20, 0x20, 0xa0],    # 4
    ],
    [ 
    [0xa0, 0xa0, 0xa0],    # 5
    [0xa0, 0x20, 0x20],    # 5
    [0x20, 0x0c, 0xa0],    # 5
    [0xa0, 0xa0, 0x0a],    # 5
    ],
    [ 
    [0x08, 0xa0, 0x09],    # 6
    [0xa0, 0x20, 0x20],    # 6
    [0xa0, 0x0c, 0xa0],    # 6
    [0x0b, 0xa0, 0x0a],    # 6
    ],
    [ 
    [0xa0, 0xa0, 0xa0],    # 7
    [0x20, 0x20, 0xa0],    # 7
    [0x20, 0x20, 0xa0],    # 7
    [0x20, 0x20, 0xa0],    # 7
    ],
    [ 
    [0x08, 0xa0, 0x09],    # 8
    [0xa0, 0x20, 0xa0],    # 8
    [0xa0, 0x0c, 0xa0],    # 8
    [0x0b, 0xa0, 0x0a],    # 8
    ],
    [ 
    [0x08, 0xa0, 0x09],    # 9
    [0xa0, 0x20, 0xa0],    # 9
    [0x20, 0x0c, 0xa0],    # 9
    [0x0b, 0xa0, 0x0a],    # 9 
    ],
    ]


    if _nDigit < 0:
      # TODO: Add a '-' sign
      _nDigit = -_nDigit

    # Set the current size, and value (base numer)
    nCurrentSize = 1
    nCurrentValue = 10

    # Build the characters
    strDigits = ""

    while ( nCurrentSize <= _nMinSize ) or ( _nDigit >= nCurrentValue and (nCurrentSize <= _nMaxSize or _nMaxSize == 0) ):
      # Determine current value
      nValue = ( _nDigit % nCurrentValue ) / ( nCurrentValue / 10 )

      # Reset current digit
      strCurrentDigit = ""
      for nX in range(0, arrSizes[ _nCharset ][0]):
        #   Add a space if we have more than one digit, and the given
        #  digit is smaller than the current value (base numer) we are dealing with
        if _bSpacePadding and ((nCurrentValue / 10) > _nDigit ) and ( nCurrentSize > 1 ):
          strCurrentDigit += " "
        # TODO: make sure this is not hardcoded
        else:       
          if _nCharset == CUSTOM_CHARSET.CUSTOM_CHARSET_SMALLCHAR:
            strCurrentDigit += arrMedNumbers[ nValue ][ _nLine ][ nX ]
          elif _nCharset == CUSTOM_CHARSET.CUSTOM_CHARSET_SMALLCHAR:
            strCurrentDigit += arrMedBoldNumbers[ nValue ][ _nLine ][ nX ]
          elif _nCharset == CUSTOM_CHARSET.CUSTOM_CHARSET_BIGCHAR:
            strCurrentDigit += arrBigNumbers[ nValue ][ _nLine ][ nX ]

      # Add as partial string
      # Note that is it reversed, I.E. 'LSB' is added first
      strDigits = strCurrentDigit + strDigits

      # Increase the size and base number
      nCurrentSize += 1
      nCurrentValue *= 10

    # Update the character mode
    m_eCurrentCharset = _nCharset

    # Return the created digit part
    return strDigits

  def Initialize(self):
    self.m_eCurrentCharset = CUSTOM_CHARSET.CUSTOM_CHARSET_DEFAULT
    self.m_disableOnPlay = DISABLE_ON_PLAY.DISABLE_ON_PLAY_NONE
    self.LoadSkin(__lcdxml__)

    # Big number blocks, used for screensaver clock
    # Note, the big block isn't here, it's in the LCD's ROM

  def IsConnected(self):
    return True


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
        #load moads
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


  def LoadMode(self, node, mode):
    if node == None:
      return
    for line in node.findall("line"):
      self.m_lcdMode[mode].append(str(line.text))

  def Reset(self):
    self.m_disableOnPlay = DISABLE_ON_PLAY.DISABLE_ON_PLAY_NONE
    for i in range(0,LCD_MODE.LCD_MODE_MAX):
      self.m_lcdMode[i] = []			#clear list

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
    return self.timeToSecs(currentTimeAr)
 
  def getCurrentDurationSecs(self):
    currentDurationAr = xbmc.getInfoLabel("Player.Duration").split(":")
    return self.timeToSecs(currentDurationAr)

  def Render(self, mode, bForce):
    outLine = 0
    inLine = 0

    while (outLine < int(self.GetRows()) and inLine < len(self.m_lcdMode[mode])):
      #parse the progressbar infolabel by ourselfs!
      if self.m_lcdMode[mode][inLine] == "$INFO[LCD.ProgressBar]":
      	# get playtime and duration and convert into seconds
        currentSecs = self.getCurrentTimeSecs()
        durationSecs = self.getCurrentDurationSecs()
        percent = self.GetProgressBarPercent(currentSecs,durationSecs)
        pixelsWidth = self.SetProgressBar(percent, outLine)
        line = "p" + str(pixelsWidth)
      else:
        line = xbmc.getInfoLabel(self.m_lcdMode[mode][inLine])
        self.SetProgressBar(0, -1)

      inLine += 1
      if len(line) > 0:
#        log(xbmc.LOGDEBUG, "Request write of line" + str(outLine) + ": " + str(line))
        self.SetLine(outLine, line, bForce)
        outLine += 1

    # fill remainder with empty space
    while outLine < int(self.GetRows()):
#      log(xbmc.LOGDEBUG, "Request write of emptyline" + str(outLine))
      self.SetLine(outLine, "", bForce)
      outLine += 1

  def DisableOnPlayback(self, playingVideo, playingAudio):
    if (playingVideo and (self.m_disableOnPlay & DISABLE_ON_PLAY.DISABLE_ON_PLAY_VIDEO)) or (playingAudio and (self.m_disableOnPlay & DISABLE_ON_PLAY.DISABLE_ON_PLAY_MUSIC)):
      if not self.m_bDimmedOnPlayback:
        self.SetBackLight(0)
        self.m_bDimmedOnPlayback = True
    elif self.m_bDimmedOnPlayback:
      self.SetBackLight(1)
      self.m_bDimmedOnPlayback = False

