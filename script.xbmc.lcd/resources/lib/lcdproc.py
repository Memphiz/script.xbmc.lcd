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
  xbmc.log("### [%s] - %s" % (__scriptname__,msg,),level=loglevel ) 
  
SCROLL_SPEED_IN_MSEC = 250
MAX_ROWS = 20
INIT_RETRY_INTERVAL = 2
INIT_RETRY_INTERVAL_MAX = 60000

class LCDProc(LcdBase):
  def __init__(self):
    self.m_iActualpos   = 0
    self.m_iBackLight   = 32
    self.m_iLCDContrast = 50
    self.m_bStop        = True
    self.m_sockfd       = -1
    self.m_lastInitAttempt = 0
    self.m_initRetryInterval = INIT_RETRY_INTERVAL
    self.m_used = True
    self.tn = telnetlib.Telnet()
    self.m_timeLastSockAction = time.time()
    self.m_timeSocketIdleTimeout = 2
    self.m_strLine = [None]*MAX_ROWS
    self.m_iProgressBarWidth = 0
    self.m_iProgressBarLine = -1
    LcdBase.__init__(self)

  def SendCommand(self, strCmd, bCheckRet):
    try:
      # Send to server
      self.tn.write(strCmd + "\n")
    except:
      # Something bad happened, abort
      log(xbmc.LOGERROR, "SendCommand: Telnet exception - send")
      return False

    # Update last socketaction timestamp
    self.m_timeLastSockAction = time.time()
    
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
      return True # no return checking desired, so be fine

    if strCmd == 'noop' and reply == 'noop complete\n':
      return True # noop has special reply

    if reply == 'success\n':
      return True

    # Leave information something undesired happened
    log(xbmc.LOGWARNING, "Reply to '" + strCmd +"' was '" + reply)
    return False

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

      # Icons
      if not self.SendCommand("widget_add xbmc lineIcon" + str(i) + " icon", True):
        return False

      # Default icon
      if not self.SendCommand("widget_set xbmc lineIcon" + str(i) + " 0 0 BLOCK_FILLED", True):
        return False

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

    LcdBase.Initialize(self)

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
      # time.sleep(1)
      # Receive LCDproc data to determine row and column information
      reply = self.tn.read_until("\n",3)
      log(xbmc.LOGDEBUG,"Reply: " + reply)
      
      lcdinfo = re.match("^connect .+ protocol ([0-9\.]+) lcd wid (\d+) hgt (\d+) cellwid (\d+) cellhgt (\d+)$", reply)

      if lcdinfo is None:
        return False

      # protocol version must currently be 0.3
      if float(lcdinfo.group(1)) != 0.3:
        log(xbmc.LOGERROR, "Only LCDproc protocol 0.3 supported (got " + lcdinfo.group(1) +")")
        return False

      self.m_iColumns = int(lcdinfo.group(2))
      self.m_iRows  = int(lcdinfo.group(3))
      self.m_iCellWidth = int(lcdinfo.group(4))
      self.m_iCellHeight = int(lcdinfo.group(5))
      log(xbmc.LOGDEBUG, "LCDproc data: Columns %s - Rows %s - CellWidth %s - CellHeight %s" % (str(self.m_iColumns), str(self.m_iRows), str(self.m_iCellWidth), str(self.m_iCellHeight)))

      # Retrieve driver name for additional functionality
      self.tn.write("info\n")
      reply = self.tn.read_until("\n",3)
      log(xbmc.LOGDEBUG,"info Reply: " + reply)

    except:
      log(xbmc.LOGERROR,"Connect: Telnet exception.")
      return False

    if not self.SetupScreen():
      log(xbmc.LOGERROR, "Screen setup failed!")
      return False      

    return True

  def CloseSocket(self):
    self.tn.close()

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
      self.m_bStop = True
      cmd = "screen_set xbmc -backlight off\n"
    elif iLight > 0:
      self.m_bStop = False
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

  def SetProgressBar(self, percent, lineIdx):
    iColumns = int(self.m_iColumns) - 2 # -2 because of [surroundings]
    iNumHorPixels = int(self.m_iCellWidth) * int(iColumns)
    self.m_iProgressBarWidth = int(float(percent) * iNumHorPixels)   
    self.m_iProgressBarLine = lineIdx
    return self.m_iProgressBarWidth

  def GetRows(self):
    return int(self.m_iRows)

  def SetLine(self, iLine, strLine, bForce):
    if self.m_bStop or self.tn.get_socket() == None:
      return

    if iLine < 0 or iLine >= int(self.m_iRows):
      return

    strLineLong = strLine
    strLineLong.strip()

    # make string fit the display if it's smaller than the width
    if len(strLineLong) < int(self.m_iColumns):
      numSpaces = int(self.m_iColumns) - len(strLineLong)
      strLineLong.ljust(numSpaces) #pad with spaces
    elif len(strLineLong) > int(self.m_iColumns): #else if the string doesn't fit the display, lcdproc will scroll it, so we need a space
      strLineLong += " "

    if strLineLong != self.m_strLine[iLine] or bForce:
      ln = iLine + 1

      if int(self.m_iProgressBarLine) >= 0 and self.m_iProgressBarLine == iLine:
        barborder = "[" + " " * (self.m_iColumns - 2) + "]"
        self.SendCommand("widget_set xbmc lineScroller%i 1 %i %i %i m 1 \"%s\"" % (ln, ln, self.m_iColumns, ln, barborder), False)
        self.SendCommand("widget_set xbmc lineProgress%i 2 %i %i" % (ln, ln, self.m_iProgressBarWidth), False)
      else:
        self.SendCommand("widget_set xbmc lineIcon%i 0 0 BLOCK_FILLED" % (ln), False)
        self.SendCommand("widget_set xbmc lineProgress%i 0 0 0" % (ln), False)
        self.SendCommand("widget_set xbmc lineScroller%i 1 %i %i %i m %i \"%s\"" % (ln, ln, self.m_iColumns, ln, settings_getScrollDelay(), re.escape(strLineLong)), False)

      self.m_strLine[iLine] = strLineLong
