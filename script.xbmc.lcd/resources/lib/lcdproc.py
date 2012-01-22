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

from socket import *

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__settings__ = sys.modules[ "__main__" ].__settings__
__cwd__ = sys.modules[ "__main__" ].__cwd__
__icon__ = sys.modules[ "__main__" ].__icon__

from settings import *
from lcdbase import *


'''
def fhem_parseXML(xmlstr):
  global g_fht_list
  global g_fhttk_list
  global g_fs20_list

  ret = True
  fhemcontents = xmltree.fromstring(xmlstr)
  for element in fhemcontents.getiterator():
    #PARSE FHT infos heating control
    if element.tag == "FHT_LIST":
      for child in element:
        if child.tag == "FHT":
          fhtobj = FHTObj()
          fhtobj.name = child.attrib.get('name')
          for subchild in child:
            if subchild.tag == "ATTR" and subchild.attrib.get('key') == "room":
			  fhtobj.room = subchild.attrib.get('value')
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "measured-temp":
              fhtobj.temperature = subchild.attrib.get('value')
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "actuator":
			  fhtobj.actuator = subchild.attrib.get('value')
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "battery":
			  fhtobj.battery = subchild.attrib.get('value')		
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "mode":
			  fhtobj.mode = subchild.attrib.get('value')	
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "desired-temp":
			  fhtobj.setTemp = subchild.attrib.get('value')
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "windowsensor":
			  fhtobj.windowSensor = subchild.attrib.get('value')			    
        g_fht_list.append(fhtobj)

    #PARSE FHTTK infos window sensors
    if element.tag == "CUL_FHTTK_LIST":
      for child in element:
        if child.tag == "CUL_FHTTK":
          fhttkobj = FHTTKObj()
          fhttkobj.name = child.attrib.get('name')
          for subchild in child:
            if subchild.tag == "ATTR" and subchild.attrib.get('key') == "room":
	          fhttkobj.room = subchild.attrib.get('value')
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "Battery":
              fhttkobj.battery = subchild.attrib.get('value')
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "Window":
              fhttkobj.window = subchild.attrib.get('value')
        g_fhttk_list.append(fhttkobj)

    #PARSE FS20 infos switches
    if element.tag == "FS20_LIST":
      for child in element:
        if child.tag == "FS20":
          fs20obj = FS20Obj()
          fs20obj.name = child.attrib.get('name')
          for subchild in child:
            if subchild.tag == "ATTR" and subchild.attrib.get('key') == "room":
	          fs20obj.room = subchild.attrib.get('value')
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "state":
              fs20obj.state = subchild.attrib.get('value')

        g_fs20_list.append(fs20obj)        

  return ret
'''  
  
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
    self.m_strLine = [None]*MAX_ROWS
    LcdBase.__init__(self)

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
      
      if len(reply) < 5:
        return False

      i = 0
      while (i < (len(reply)-5)) and reply[i:i+3] != "lcd" and (i+3) < len(reply):
        i = i + 1
      
      if i < len(reply):
        tmparray = re.findall(r'\d+',reply[i:])
        if len(tmparray) >= 2:
          self.m_iColumns = tmparray[0]
          self.m_iRows  = tmparray[1]
          log(xbmc.LOGDEBUG, "LCDproc data: Columns %s - Rows %s." % (str(self.m_iColumns), str(self.m_iRows)))
    except:
      log(xbmc.LOGERROR,"Connect: Telnet exception.")
      return False

    # Build command to setup screen
    cmd = "screen_add xbmc\n"
    if not settings_getHeartBeat():
      cmd += "screen_set xbmc -heartbeat off\n"
 
    if settings_getScrollDelay():
      for i in range(1,int(self.m_iRows)+1):
        cmd += "widget_add xbmc line" + str(i) + " scroller\n"
    else:
      for i in range(1,int(self.m_iRows)+1):
        cmd += "widget_add xbmc line" + str(i) + " string\n"

    try:
      #Send to server
      self.tn.write(cmd)
      self.tn.read_until("\n",3)            
    except:
      log(xbmc.LOGERROR, "Connect: Telnet exception - send")
      return False

    return True


  def CloseSocket(self):
    self.tn.close()

  def IsConnected(self):
    if self.tn.get_socket() == None:
      return False
      
    try:
      self.tn.write("noop\n")
      self.tn.read_until("\n",3)      
    except:
      log(xbmc.LOGERROR, "Unable to write to socket - IsConnected")
      self.CloseSocket()
      return False
    return True

  def SetBackLight(self, iLight):
    if self.tn.get_socket() == None:
      return
    log(xbmc.LOGDEBUG, "Switch Backlight to: " + str(iLight))

    # Build command
    cmd = ""
    if iLight == 0:
      self.m_bStop = True
      cmd += "screen_set xbmc -backlight off\n"
      for i in range(1,int(self.m_iRows)+1):
        cmd += "widget_del xbmc line" + str(i) + "\n"      
    elif iLight > 0:
      self.m_bStop = False
      cmd += "screen_set xbmc -backlight on\n"
      if settings_getScrollDelay() != 0:
        for i in range(1,int(self.m_iRows)+1):
          cmd += "widget_add xbmc line" + str(i) + " scroller\n"      
      else:
        for i in range(1,int(self.m_iRows)+1):
          cmd += "widget_add xbmc line" + str(i) + " string\n"      

    # Send to server
    try:
      self.tn.write(cmd)
      self.tn.read_until("\n",3)      
    except:
      log(xbmc.LOGERROR, "Unable to write to socket - SetBackLight")
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
    try:
      self.tn.write(cmd)
      self.tn.read_until("\n",3)            
    except:
      log(xbmc.LOGERROR, "Unable to write to socket - Suspend")
      self.CloseSocket()

  def Resume(self):
    if self.m_bStop or self.tn.get_socket() == None:
      return

    # Build command to resume screen
    cmd = "screen_set xbmc -priority info\n"

    # Send to server
    try:
      self.tn.write(cmd)
      self.tn.read_until("\n",3)           
    except:
      log(xbmc.LOGERROR, "Unable to write to socket - Resume")
      self.CloseSocket()

  def GetColumns(self):
    return self.m_iColumns

  def GetRows(self):
    return self.m_iRows

  def SetLine(self, iLine, strLine, bForce):
    if self.m_bStop or self.tn.get_socket() == None:
      return

    if iLine < 0 or iLine >= self.m_iRows:
      return

    strLineLong = strLine
    strLineLong.strip()
    strLineLong = StringToLCDCharSet(strLineLong)

    # make string fit the display if it's smaller than the width
    if len(strLineLong) < int(self.m_iColumns):
      numSpaces = int(self.m_iColumns) - len(strLineLong)
      strLineLong.ljust(numSpaces) #pad with spaces
    elif len(strLineLong) > int(self.m_iColumns): #else if the string doesn't fit the display, lcdproc will scroll it, so we need a space
      strLineLong += " "

    if strLineLong != self.m_strLine[iLine] or bForce:
      ln = iLine + 1
      cmd = ""
      if settings_getScrollDelay() != 0:
        cmd = "widget_set xbmc line%i 1 %i %i %i m %i \"%s\"\n" % (ln, ln, int(self.m_iColumns), ln, settings_getScrollDelay(), strLineLong)
      else:
        cmd = "widget_set xbmc line%i 1 %i \"%s\"\n" % (ln, ln, strLineLong)

      # Send to server
      try:
        self.tn.get_socket().send(cmd)	#use the socket here for getting the special chars over the wire
        self.tn.read_until("\n",3)           
      except:
        log(xbmc.LOGERROR, "Unable to write to socket - SetLine")
        self.CloseSocket()

    self.m_strLine[iLine] = strLineLong

