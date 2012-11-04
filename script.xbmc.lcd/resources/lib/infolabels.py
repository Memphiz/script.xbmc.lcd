'''
    XBMC LCDproc addon
    Copyright (C) 2012 Team XBMC
    
    InfoLabel handling
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
import xbmcgui

# enum snippet from http://stackoverflow.com/a/1695250 - thanks!
def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

# interesting XBMC GUI Window IDs (no defines seem to exist for this)
class WINDOW_IDS:
  WINDOW_DIALOG_VOLUME_BAR = 10104
  WINDOW_DIALOG_KAI_TOAST  = 10107

def InfoLabel_WindowIsActive(WindowID):
  return xbmc.getCondVisibility("Window.IsActive(" + str(WindowID) + ")")

def InfoLabel_PlayingVideo():
  return xbmc.getCondVisibility("Player.HasVideo")

def InfoLabel_PlayingAudio():
  return xbmc.getCondVisibility("Player.HasAudio")

def InfoLabel_GetPlayerTime():
  return xbmc.getInfoLabel("Player.Time")

def InfoLabel_IsPlayerPlaying():
  return xbmc.getCondVisibility("Player.Playing")

def InfoLabel_IsPlayerPaused():
  return xbmc.getCondVisibility("Player.Paused")

def InfoLabel_IsPlayerForwarding():
  return xbmc.getCondVisibility("Player.Forwarding")

def InfoLabel_IsPlayerRewinding():
  return xbmc.getCondVisibility("Player.Rewinding")

def InfoLabel_IsPlayingAny():
  return (InfoLabel_IsPlayerPlaying() |
          InfoLabel_IsPlayerPaused() |
          InfoLabel_IsPlayerForwarding() |
          InfoLabel_IsPlayerRewinding())
