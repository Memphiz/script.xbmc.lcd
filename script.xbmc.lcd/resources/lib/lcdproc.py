'''
    XBMC LCDproc addon
    Copyright (C) 2012 Team XBMC

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

from socket import *

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__settings__ = sys.modules[ "__main__" ].__settings__
__cwd__ = sys.modules[ "__main__" ].__cwd__
__icon__ = sys.modules[ "__main__" ].__icon__

from settings import *
from lcdbase import *

def log(loglevel, msg):
  xbmc.log("### [%s] - %s" % (__scriptname__,msg,), level=loglevel) 
  
MAX_ROWS = 20
MAX_BIGDIGITS = 20
INIT_RETRY_INTERVAL = 2
INIT_RETRY_INTERVAL_MAX = 60000

class LCDProc(LcdBase):
  def __init__(self):
    self.m_bStop        = True
    self.m_lastInitAttempt = 0
    self.m_initRetryInterval = INIT_RETRY_INTERVAL
    self.m_used = True
    self.tn = telnetlib.Telnet()
    self.m_timeLastSockAction = time.time()
    self.m_timeSocketIdleTimeout = 2
    self.m_strLineText = [None]*MAX_ROWS
    self.m_strLineType = [None]*MAX_ROWS
    self.m_strLineIcon = [None]*MAX_ROWS
    self.m_strDigits = [None]*MAX_BIGDIGITS
    self.m_iProgressBarWidth = 0
    self.m_iProgressBarLine = -1
    self.m_strIconName = "BLOCK_FILLED"
    self.m_iBigDigits = int(8) # 12:45:78 / colons count as digit
    self.m_strSetLineCmds = ""
    self.m_vPythonVersion = sys.version_info

    if self.m_vPythonVersion < (2, 7):
      log(xbmc.LOGWARNING, "Python < 2.7 detected. Upgrade your Python for optimal results.")

    LcdBase.__init__(self)

  def SendCommand(self, strCmd, bCheckRet):
    countcmds = string.count(strCmd, '\n')
    sendcmd = strCmd
    ret = True

    # Single command without lf
    if countcmds < 1:
      #countcmds = 1
      sendcmd += "\n"

    try:
      # Send to server
      self.tn.write(sendcmd)
    except:
      # Something bad happened, abort
      log(xbmc.LOGERROR, "SendCommand: Telnet exception - send")
      return False

    # Update last socketaction timestamp
    self.m_timeLastSockAction = time.time()
    
    # Repeat for number of found commands
    for i in range(1, (countcmds + 1)):
      # Read in (multiple) responses
      while True:
        try:
          # Read server reply
          reply = self.tn.read_until("\n",3)            
        except:
          # (Re)read failed, abort
          log(xbmc.LOGERROR, "SendCommand: Telnet exception - reread")
          return False

        # Skip these messages
        if reply[:6] == 'listen':
          continue
        elif reply[:6] == 'ignore':
          continue
        elif reply[:3] == 'key':
          continue
        elif reply[:9] == 'menuevent':
          continue

        # Response seems interesting, so stop here      
        break
      
      if not bCheckRet:
        continue # no return checking desired, so be fine

      if strCmd == 'noop' and reply == 'noop complete\n':
        continue # noop has special reply

      if reply == 'success\n':
        continue
      
      ret = False

    # Leave information something undesired happened
    if ret is False:
      log(xbmc.LOGWARNING, "Reply to '" + strCmd +"' was '" + reply)

    return ret

  def SetupScreen(self):
    # Add screen first
    if not self.SendCommand("screen_add xbmc", True):
      return False

    # Set screen priority
    if not self.SendCommand("screen_set xbmc -priority info", True):
      return False

    # Turn off heartbeat if desired
    if not settings_getHeartBeat():
      if not self.SendCommand("screen_set xbmc -heartbeat off", True):
        return False

    # Setup widgets
    for i in range(1,int(self.m_iRows)+1):
      # Text widgets
      if not self.SendCommand("widget_add xbmc lineScroller" + str(i) + " scroller", True):
        return False

      # Progress bars
      if not self.SendCommand("widget_add xbmc lineProgress" + str(i) + " hbar", True):
        return False

      # Reset bars to zero
      if not self.SendCommand("widget_set xbmc lineProgress" + str(i) + " 0 0 0", True):
        return False

      # Icons
      if not self.SendCommand("widget_add xbmc lineIcon" + str(i) + " icon", True):
        return False

      # Default icon
      if not self.SendCommand("widget_set xbmc lineIcon" + str(i) + " 0 0 BLOCK_FILLED", True):
        return False

      self.m_strLineText[i-1] = ""
      self.m_strLineType[i-1] = ""
      self.m_strLineIcon[i-1] = ""

    for i in range(1,int(self.m_iBigDigits + 1)):
      # Big Digit
      if not self.SendCommand("widget_add xbmc lineBigDigit" + str(i) + " num", True):
        return False

      # Set Digit
      if not self.SendCommand("widget_set xbmc lineBigDigit" + str(i) + " 0 0", True):
        return False

      self.m_strDigits[i] = ""

    return True

  def Initialize(self):
    connected = False
    if not self.m_used:
      return False#nothing to do

    #don't try to initialize too often
    now = time.time()
    if (now - self.m_lastInitAttempt) < self.m_initRetryInterval:
      return False
    self.m_lastInitAttempt = now

    if self.Connect():
      # reset the retry interval after a successful connect
      self.m_initRetryInterval = INIT_RETRY_INTERVAL
      self.m_bStop = False
      connected = True
    else:
      self.CloseSocket()

    if not connected:
      # give up after 60 seconds
      if self.m_initRetryInterval > INIT_RETRY_INTERVAL_MAX:
        self.m_used = False
        log(xbmc.LOGERROR,"Connect failed. Giving up.")
      else:
        self.m_initRetryInterval = self.m_initRetryInterval * 2
        log(xbmc.LOGERROR,"Connect failed. Retry in %d seconds." % self.m_initRetryInterval)
    else:
      LcdBase.Initialize(self)

    return connected

  def Connect(self):
    self.CloseSocket()

    try:
      ip = settings_getHostIp()
      port = settings_getHostPort()
      log(xbmc.LOGDEBUG,"Open " + str(ip) + ":" + str(port))
      
      self.tn.open(ip, port)
      # Start a new session
      self.tn.write("hello\n")

      # Receive LCDproc data to determine row and column information
      reply = self.tn.read_until("\n",3)
      log(xbmc.LOGDEBUG,"Reply: " + reply)
      
      # parse reply by regex
      lcdinfo = re.match("^connect .+ protocol ([0-9\.]+) lcd wid (\d+) hgt (\d+) cellwid (\d+) cellhgt (\d+)$", reply)

      # if regex didn't match, LCDproc is incompatible or something's odd
      if lcdinfo is None:
        return False

      # protocol version must currently be 0.3
      if float(lcdinfo.group(1)) != 0.3:
        log(xbmc.LOGERROR, "Only LCDproc protocol 0.3 supported (got " + lcdinfo.group(1) +")")
        return False

      # set up class vars
      self.m_iColumns = int(lcdinfo.group(2))
      self.m_iRows  = int(lcdinfo.group(3))
      self.m_iCellWidth = int(lcdinfo.group(4))
      self.m_iCellHeight = int(lcdinfo.group(5))

      # tell users what's going on
      log(xbmc.LOGNOTICE, "Connected to LCDd at %s:%s, Protocol version %s - Geometry %sx%s characters (%sx%s pixels, %sx%s pixels per character)" % (str(ip), str(port), float(lcdinfo.group(1)), str(self.m_iColumns), str(self.m_iRows), str(self.m_iColumns * self.m_iCellWidth), str(self.m_iRows * self.m_iCellHeight), str(self.m_iCellWidth), str(self.m_iCellHeight)))

      # Retrieve driver name for additional functionality
      self.tn.write("info\n")
      reply = self.tn.read_until("\n",3)
      log(xbmc.LOGDEBUG,"info Reply: " + reply)

      # Set up BigNum values based on display geometry
      if self.m_iColumns < 16:
        self.m_iBigDigits = 5
      elif self.m_iColumns < 20:
        self.m_iBigDigits = 7

    except:
      log(xbmc.LOGERROR,"Connect: Telnet exception.")
      return False

    if not self.SetupScreen():
      log(xbmc.LOGERROR, "Screen setup failed!")
      return False      

    return True

  def CloseSocket(self):
    self.tn.close()
    del self.tn
    self.tn = telnetlib.Telnet()

  def IsConnected(self):
    if self.tn.get_socket() == None:
      return False

    # Ping only every SocketIdleTimeout seconds
    if (self.m_timeLastSockAction + self.m_timeSocketIdleTimeout) > time.time():
      return True

    if not self.SendCommand("noop", True):
      log(xbmc.LOGERROR, "noop failed in IsConnected(), aborting!")
      return False

    return True

  def SetBackLight(self, iLight):
    if self.tn.get_socket() == None:
      return
    log(xbmc.LOGDEBUG, "Switch Backlight to: " + str(iLight))

    # Build command
    if iLight == 0:
      #self.m_bStop = True
      cmd = "screen_set xbmc -backlight off\n"
    elif iLight > 0:
      #self.m_bStop = False
      cmd = "screen_set xbmc -backlight on\n"

    # Send to server
    if not self.SendCommand(cmd, True):
      log(xbmc.LOGERROR, "SetBackLight(): Cannot change backlight state")
      self.CloseSocket()

  def SetContrast(self, iContrast):
    #TODO: Not sure if you can control contrast from client
    return

  def Stop(self):
    self.CloseSocket()
    self.m_bStop = True

  def Suspend(self):
    if self.m_bStop or self.tn.get_socket() == None:
      return

    # Build command to suspend screen
    cmd = "screen_set xbmc -priority hidden\n"

    # Send to server
    if not self.SendCommand(cmd, True):
      log(xbmc.LOGERROR, "Suspend(): Cannot suspend")
      self.CloseSocket()

  def Resume(self):
    if self.m_bStop or self.tn.get_socket() == None:
      return

    # Build command to resume screen
    cmd = "screen_set xbmc -priority info\n"

    # Send to server
    if not self.SendCommand(cmd, True):
      log(xbmc.LOGERROR, "Resume(): Cannot resume")
      self.CloseSocket()

  def GetColumns(self):
    return int(self.m_iColumns)

  def GetBigDigitTime(self):
      ret = xbmc.getInfoLabel("Player.Time")

      if ret == "": # no usable timestring, e.g. not playing anything
        if self.m_iBigDigits < 8: # return only h:m when display too small
          ret = time.strftime("%X")[:5] # %X = locale-based currenttime
        else:
          ret = time.strftime("%X")[:8]

      return ret

  def SetBigDigits(self, strTimeString, bForceUpdate):
    iOffset = 1
    iDigitCount = 1
    iStringOffset = 0
    strRealTimeString = ""

    if strTimeString == "" or strTimeString == None:
      return

    iStringLength = int(len(strTimeString))

    if iStringLength > self.m_iBigDigits:
      iStringOffset = len(strTimeString) - self.m_iBigDigits

    for i in range(int(iStringOffset), int(iStringLength)):
      if self.m_strDigits[iDigitCount] != strTimeString[i] or bForceUpdate:
        self.m_strDigits[iDigitCount] = strTimeString[i]
        
        if strTimeString[i] == ":":
          self.m_strSetLineCmds += "widget_set xbmc lineBigDigit%i %i 10\n" % (iDigitCount, iOffset)
        else:
          self.m_strSetLineCmds += "widget_set xbmc lineBigDigit%i %i %s\n" % (iDigitCount, iOffset, strTimeString[i])

      if strTimeString[i] == ":":
        iOffset += 1
      else:
        iOffset += 3

      iDigitCount += 1

    for j in range(i + 2, int(self.m_iBigDigits + 1)):
      if self.m_strDigits[iDigitCount] != "" or bForceUpdate:
        self.m_strDigits[iDigitCount] = ""
        self.m_strSetLineCmds += "widget_set xbmc lineBigDigit" + str(j) + " 0 0\n"
      
      iDigitCount += 1

  def SetProgressBar(self, percent, pxWidth):
    self.m_iProgressBarWidth = int(float(percent) * pxWidth)
    return self.m_iProgressBarWidth

  def SetPlayingStateIcon(self):
    bPlaying = xbmc.getCondVisibility("Player.Playing")
    bPaused = xbmc.getCondVisibility("Player.Paused")
    bForwarding = xbmc.getCondVisibility("Player.Forwarding")
    bRewinding = xbmc.getCondVisibility("Player.Rewinding")

    self.m_strIconName = "STOP"

    if bForwarding:
      self.m_strIconName = "FF"
    elif bRewinding:
      self.m_strIconName = "FR"
    elif bPaused:
      self.m_strIconName = "PAUSE"
    elif bPlaying:
      self.m_strIconName = "PLAY"

  def GetRows(self):
    return int(self.m_iRows)

  def ClearBigDigits(self):
    for i in range(1,int(self.m_iBigDigits + 1)):
      # Clear Digit
      self.m_strSetLineCmds += "widget_set xbmc lineBigDigit" + str(i) + " 0 0\n"
      self.m_strDigits[i] = ""

    # make sure all widget get redrawn by resetting their type
    for i in range(0, int(self.GetRows())):
      self.m_strLineType[i] = ""
      self.m_strLineText[i] = ""
      self.m_strLineIcon[i] = ""

  def ClearLine(self, iLine):
    self.m_strSetLineCmds += "widget_set xbmc lineIcon%i 0 0 BLOCK_FILLED\n" % (iLine)
    self.m_strSetLineCmds += "widget_set xbmc lineProgress%i 0 0 0\n" % (iLine)
    self.m_strSetLineCmds += "widget_set xbmc lineScroller%i 1 %i %i %i m 1 \"\"\n" % (iLine, iLine, self.m_iColumns, iLine)
    
  def SetLine(self, iLine, strLine, dictDescriptor, bForce):
    if self.m_bStop or self.tn.get_socket() == None:
      return

    if iLine < 0 or iLine >= int(self.m_iRows):
      return

    ln = iLine + 1
    bExtraForce = False

    if self.m_strLineType[iLine] != dictDescriptor['type']:
      if dictDescriptor['type'] == LCD_LINETYPE.LCD_LINETYPE_BIGSCREEN:
        self.ClearDisplay()
      else:
        if self.m_strLineType[iLine] == LCD_LINETYPE.LCD_LINETYPE_BIGSCREEN:
          self.ClearBigDigits()
        else:
          self.ClearLine(int(iLine + 1))

      self.m_strLineType[iLine] = dictDescriptor['type']
      bExtraForce = True

      if dictDescriptor['type'] == LCD_LINETYPE.LCD_LINETYPE_PROGRESS and dictDescriptor['text'] != "":
        self.m_strSetLineCmds += "widget_set xbmc lineScroller%i 1 %i %i %i m 1 \"%s\"\n" % (ln, ln, self.m_iColumns, ln, dictDescriptor['text'])

    if dictDescriptor['type'] == LCD_LINETYPE.LCD_LINETYPE_BIGSCREEN:
      strLineLong = self.GetBigDigitTime()
    else:
      strLineLong = strLine

    strLineLong.strip()
  
    iMaxLineLen = dictDescriptor['endx'] - (int(dictDescriptor['startx']) - 1)
    iScrollSpeed = settings_getScrollDelay()
    strScrollMode = settings_getLCDprocScrollMode()

    # make string fit the display if it's smaller than the width
    if len(strLineLong) < int(self.m_iColumns):
      numSpaces = int(iMaxLineLen) - len(strLineLong)
      strLineLong.ljust(numSpaces) #pad with spaces
    elif len(strLineLong) > int(self.m_iColumns): #else if the string doesn't fit the display...
      if iScrollSpeed != 0:          # add separator when scrolling enabled
        if strScrollMode == "m":     # and scrollmode is marquee
          strLineLong += self.m_strScrollSeparator      
      else:                                       # or cut off
        strLineLong = strLineLong[:iMaxLineLen]
        iScrollSpeed = 1

    # check if update is required
    if strLineLong != self.m_strLineText[iLine] or bForce:
      # bigscreen
      if dictDescriptor['type'] == LCD_LINETYPE.LCD_LINETYPE_BIGSCREEN:
        self.SetBigDigits(strLineLong, bExtraForce)
      # progressbar line
      elif dictDescriptor['type'] == LCD_LINETYPE.LCD_LINETYPE_PROGRESS:
        self.m_strSetLineCmds += "widget_set xbmc lineProgress%i %i %i %i\n" % (ln, dictDescriptor['startx'], ln, self.m_iProgressBarWidth)
      # everything else (text, icontext)
      else:
        self.m_strSetLineCmds += "widget_set xbmc lineScroller%i %i %i %i %i %s %i \"%s\"\n" % (ln, dictDescriptor['startx'], ln, self.m_iColumns, ln, strScrollMode, iScrollSpeed, re.escape(strLineLong))

      # cache contents
      self.m_strLineText[iLine] = strLineLong

    if dictDescriptor['type'] == LCD_LINETYPE.LCD_LINETYPE_ICONTEXT:
      if self.m_strLineIcon[iLine] != self.m_strIconName or bExtraForce:
        self.m_strLineIcon[iLine] = self.m_strIconName
        
        self.m_strSetLineCmds += "widget_set xbmc lineIcon%i 1 %i %s\n" % (ln, ln, self.m_strIconName)

  def ClearDisplay(self):
    log(xbmc.LOGDEBUG, "Clearing display contents")

    # clear line buffer first
    self.FlushLines()

    # set all widgets to empty stuff and/or offscreen
    for i in range(1,int(self.m_iRows)+1):
      self.ClearLine(i)

    # add commands to clear big digits
    self.ClearBigDigits()

    # send to display
    self.FlushLines()

  def FlushLines(self):
      if len(self.m_strSetLineCmds) > 0:
        # Send complete command package
        self.SendCommand(self.m_strSetLineCmds, False)

        self.m_strSetLineCmds = ""
