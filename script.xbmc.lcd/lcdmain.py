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

import xbmc
import xbmcaddon
import xbmcgui
import time
import os

__settings__   = xbmcaddon.Addon(id='script.xbmc.lcd')
__cwd__        = __settings__.getAddonInfo('path')
__icon__       = os.path.join(__cwd__,"icon.png")
__scriptname__ = "XBMC LCD/VFD"

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
sys.path.append (BASE_RESOURCE_PATH)

from settings import *
from lcdproc import *

global g_failedConnectionNotified
global g_initialConnectAttempt
global g_lcdproc

global g_oldMenu
global g_oldSubMenu
global g_timer

def initGlobals():
  global g_failedConnectionNotified
  global g_initialConnectAttempt
  global g_lcdproc 
  global g_oldMenu
  global g_oldSubMenu
  global g_timer

  g_failedConnectionNotified = False   
  g_initialConnectAttempt = True
  settings_initGlobals()
  g_lcdproc = LCDProc()
  g_oldMenu = ""
  g_oldSubMenu = ""
  g_timer = time.time()

def isNavigationActive():
  global g_oldMenu
  global g_oldSubMenu
  global g_timer

  ret = False

  navtimeout = settings_getNavTimeout()
  menu = xbmc.getInfoLabel("$INFO[System.CurrentWindow]")
  subMenu = xbmc.getInfoLabel("$INFO[System.CurrentControl]")

  if menu != g_oldMenu or subMenu != g_oldSubMenu or (g_timer + navtimeout) > time.time():
    ret = True
    if menu != g_oldMenu or subMenu != g_oldSubMenu:
      g_timer = time.time()      
    g_oldMenu = menu
    g_oldSubMenu = subMenu

  return ret

# returns mode identifier based on currently playing media/active navigation
def getLcdMode():                 
  ret = LCD_MODE.LCD_MODE_GENERAL

  navActive = isNavigationActive()
  screenSaver = xbmc.getCondVisibility("System.ScreenSaverActive")
  playingVideo = xbmc.getCondVisibility("Player.HasVideo")
  playingMusic = xbmc.getCondVisibility("Player.HasAudio")
  playingPVRTV = xbmc.getCondVisibility("PVR.IsPlayingTV")
  playingPVRRadio = xbmc.getCondVisibility("PVR.IsPlayingRadio")

  if navActive:
    ret = LCD_MODE.LCD_MODE_NAVIGATION
  elif screenSaver:
    ret = LCD_MODE.LCD_MODE_SCREENSAVER
  elif playingPVRTV:
    ret = LCD_MODE.LCD_MODE_PVRTV
  elif playingPVRRadio:
    ret = LCD_MODE.LCD_MODE_PVRRADIO
  elif playingVideo:
    ret = LCD_MODE.LCD_MODE_VIDEO
  elif playingMusic:
    ret = LCD_MODE.LCD_MODE_MUSIC
   
  return ret

def process_lcd():
  bBacklightDimmed = False

  while not xbmc.abortRequested:
    if handleConnectLCD():
      settingsChanged = settings_didSettingsChange()
      mode = getLcdMode()

      if mode == LCD_MODE.LCD_MODE_SCREENSAVER and settings_getDimOnScreensaver() and not bBacklightDimmed:
        g_lcdproc.SetBackLight(0)
        bBacklightDimmed = True

      g_lcdproc.Render(mode, settingsChanged)

      # turn the backlight on when leaving screensaver and it was dimmed
      if mode != LCD_MODE.LCD_MODE_SCREENSAVER and bBacklightDimmed:
        g_lcdproc.SetBackLight(1)
        bBacklightDimmed = False
    
      if mode == LCD_MODE.LCD_MODE_MUSIC:
        g_lcdproc.DisableOnPlayback(False, True)
      elif mode == LCD_MODE.LCD_MODE_VIDEO:
        g_lcdproc.DisableOnPlayback(True, False)
      else:
        g_lcdproc.DisableOnPlayback(False, False)

      time.sleep(1.0 / float(settings_getRefreshRate())) # refresh after configured rate

  g_lcdproc.Shutdown()

def handleConnectLCD():
  global g_failedConnectionNotified
  global g_initialConnectAttempt
  ret = True
   
  while not xbmc.abortRequested:
    #check for new settings
    if settings_checkForNewSettings() or not g_lcdproc.IsConnected():    #networksettings changed?
      g_failedConnectionNotified = False  #reset notification flag
    else:
      return True

    ret = g_lcdproc.Initialize()

    if not ret:
      count = 10
      if not g_failedConnectionNotified:
        g_failedConnectionNotified = True
	g_initialConnectAttempt = False
        text = __settings__.getLocalizedString(500)
        xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,text,10,__icon__))
      while (not xbmc.abortRequested) and (count > 0):
        time.sleep(1)
        count -= 1
	ret = False
    else:
      text = __settings__.getLocalizedString(501)
      if not g_failedConnectionNotified and not g_initialConnectAttempt:
        xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,text,10,__icon__))
        g_failedConnectionNotified = True
      break

  # initial connection attempt done, update flag
  g_initialConnectAttempt = False
  return ret

#MAIN - entry point
initGlobals()

#main loop
while not xbmc.abortRequested:
  settings_setup()
  process_lcd()    #lcd loop
