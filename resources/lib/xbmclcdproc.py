'''
    XBMC LCDproc addon

    Main addon handler/control

    Copyright (C) 2012-2018 Team Kodi
    Copyright (C) 2012-2018 Daniel 'herrnst' Scheller

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

# base imports
import time

# Kodi imports
import xbmc
import xbmcgui

from .common import *
from .settings import *
from .lcdproc import *
from .infolabels import *

class XBMCLCDproc():

    ########
    # ctor
    def __init__(self):
        self._failedConnectionNotified = False
        self._initialConnectAttempt = True

        # instantiate xbmc.Monitor object
        self._xbmcMonitor = xbmc.Monitor()

        # instantiate Settings object
        self._Settings = Settings()

        # instantiate LCDProc object
        self._LCDproc = LCDProc(self._Settings)

        # initialize components
        self._Settings.setup()
        InfoLabel_Initialize()

    ########
    # HandleConnectionNotification():
    # evaluate and handle dispay of connection notification popups
    def HandleConnectionNotification(self, bConnectSuccess):
        if not bConnectSuccess:
            if not self._failedConnectionNotified:
                self._failedConnectionNotified = True
                self._initialConnectAttempt = False
                text = KODI_ADDON_SETTINGS.getLocalizedString(32500)
                xbmcgui.Dialog().notification(KODI_ADDON_NAME, text, KODI_ADDON_ICON)
        else:
            text = KODI_ADDON_SETTINGS.getLocalizedString(32501)
            if not self._initialConnectAttempt:
                xbmcgui.Dialog().notification(KODI_ADDON_NAME, text, KODI_ADDON_ICON)
                self._failedConnectionNotified = True

    ########
    # GetLCDMode():
    # returns mode identifier based on currently playing media/active navigation
    def GetLCDMode(self):
        ret = LCD_MODE.LCD_MODE_GENERAL

        navActive = InfoLabel_IsNavigationActive(self._Settings)
        screenSaver = InfoLabel_IsScreenSaverActive()
        playingVideo = InfoLabel_PlayingVideo()
        playingTVShow = InfoLabel_PlayingTVShow()
        playingMusic = InfoLabel_PlayingAudio()
        playingPVRTV = InfoLabel_PlayingLiveTV()
        playingPVRRadio = InfoLabel_PlayingLiveRadio()

        if navActive:
            ret = LCD_MODE.LCD_MODE_NAVIGATION
        elif screenSaver:
            ret = LCD_MODE.LCD_MODE_SCREENSAVER
        elif playingPVRTV:
            ret = LCD_MODE.LCD_MODE_PVRTV
        elif playingPVRRadio:
            ret = LCD_MODE.LCD_MODE_PVRRADIO
        elif playingTVShow:
            ret = LCD_MODE.LCD_MODE_TVSHOW
        elif playingVideo:
            ret = LCD_MODE.LCD_MODE_VIDEO
        elif playingMusic:
            ret = LCD_MODE.LCD_MODE_MUSIC

        return ret

    def HandleConnectLCD(self):
        ret = True

        reconnect = self._Settings.checkForNewSettings()

        # check for new settings - networksettings changed?
        if reconnect or not self._LCDproc.IsConnected():

            # reset notification flag if settingchanges require reconnect
            if reconnect:
                self._failedConnectionNotified = False

            ret = self._LCDproc.Initialize()
            if not self._Settings.getHideConnPopups():
                self.HandleConnectionNotification(ret)

        return ret

    ########
    # RunLCD():
    # Main loop, triggers data inquiry and rendering, handles setting changes and connection issues
    def RunLCD(self):
        while not self._xbmcMonitor.abortRequested():
            if self.HandleConnectLCD():
                settingsChanged = self._Settings.didSettingsChange()

                if settingsChanged:
                    self._LCDproc.UpdateGUISettings()

                self._LCDproc.Render(self.GetLCDMode(), settingsChanged)

            # refresh after configured rate
            time.sleep(1.0 / float(self._Settings.getRefreshRate()))

        self._LCDproc.Shutdown()
