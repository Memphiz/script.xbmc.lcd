'''
    XBMC LCDproc addon
    Copyright (C) 2012 Team XBMC

    Support for extra symbols on SoundGraph iMON LCD displays
    Copyright (C) 2012 Daniel Scheller
    Original C implementation (C) 2010 theonlychrizz

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

import xbmc
import sys

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__settings__ = sys.modules[ "__main__" ].__settings__
__cwd__ = sys.modules[ "__main__" ].__cwd__
__icon__ = sys.modules[ "__main__" ].__icon__

from lcdproc import *
from lcdbase import LCD_EXTRAICONS
from extraicons import *

def log(loglevel, msg):
  xbmc.log("### [%s] - %s" % (__scriptname__,msg,), level=loglevel) 
  
# extra icon bitmasks
class IMON_ICONS:
  ICON_SPINDISC        = 0x01 << 0
  ICON_TOP_MUSIC       = 0x01 << 1
  ICON_TOP_MOVIE       = 0x01 << 2
  ICON_TOP_PHOTO       = (0x01 << 1) | (0x01 << 2)
  ICON_TOP_CDDVD       = 0x01 << 3
  ICON_TOP_TV          = (0x01 << 1) | (0x01 << 3)
  ICON_TOP_WEBCASTING  = (0x01 << 2) | (0x01 << 3)
  ICON_TOP_NEWSWEATHER = (0x01 << 1) | (0x01 << 2) | (0x01 << 3)
  ICON_CH_2_0          = 0x01 << 4
  ICON_CH_5_1          = 0x01 << 5
  ICON_CH_7_1          = (0x01 << 4) | (0x01 << 5)
  ICON_SPDIF           = 0x01 << 6
  ICON_OUT_SRC         = 0x01 << 7
  ICON_OUT_FIT         = 0x01 << 8
  ICON_OUT_SD          = 0x01 << 9
  ICON_OUT_HDTV        = 0x01 << 10
  ICON_SCR1            = 0x01 << 11
  ICON_SCR2            = 0x01 << 12
  ICON_ACODEC_MP3      = 0x01 << 13
  ICON_ACODEC_OGG      = 0x01 << 14
  ICON_ACODEC_AWMA     = (0x01 << 13) | (0x01 << 14)
  ICON_ACODEC_WAV      = 0x01 << 15
  ICON_ACODEC_MPEG     = 0x01 << 16
  ICON_ACODEC_AC3      = 0x01 << 17
  ICON_ACODEC_DTS      = (0x01 << 16) | (0x01 << 17)
  ICON_ACODEC_VWMA     = 0x01 << 18
  ICON_VCODEC_MPEG     = 0x01 << 19
  ICON_VCODEC_DIVX     = 0x01 << 20
  ICON_VCODEC_XVID     = (0x01 << 19) | (0x01 << 20)
  ICON_VCODEC_WMV      = 0x01 << 21
  ICON_VOLUME          = 0x01 << 22
  ICON_TIME            = 0x01 << 23
  ICON_ALARM           = 0x01 << 24
  ICON_REC             = 0x01 << 25
  ICON_REPEAT          = 0x01 << 26
  ICON_SHUFFLE         = 0x01 << 27
  BARS                 = 0x01 << 28 # additionally needs bar values in other bits
  ICON_DISC_IN         = 0x01 << 29

  # clear masks
  ICON_CLEAR_TOPROW    = 0xffffffff &~ ((0x01 << 1) | (0x01 << 2) | (0x01 << 3))
  ICON_CLEAR_CHANNELS  = 0xffffffff &~ ((0x01 << 4) | (0x01 << 5))
  ICON_CLEAR_BR        = 0xffffffff &~ ((0x01 << 13) | (0x01 << 14) | (0x01 << 15))
  ICON_CLEAR_BM        = 0xffffffff &~ ((0x01 << 16) | (0x01 << 17) | (0x01 << 18))
  ICON_CLEAR_BL        = 0xffffffff &~ ((0x01 << 19) | (0x01 << 20) | (0x01 << 21))

class LCDproc_extra_imon():
  def __init__(self):
    self.m_iOutputValueOldIcons = 1
    self.m_iOutputValueOldBars = 1
    self.m_iOutputValueIcons = 0
    self.m_iOutputValueBars = 0

  def __SetBar(self, barnum, value):
    if barnum == 1:
      bitmask = 0x00000FC0
      bitshift = 6
    elif barnum == 2:
      bitmask = 0x00FC0000
      bitshift = 18
    elif barnum == 3:
      bitmask = 0x0000003F
      bitshift = 0
    elif barnum == 4:
      bitmask = 0x0003F000
      bitshift = 12
    else:
      return self.m_iOutputValueProgress

    self.m_iOutputValueBars = (self.m_iOutputValueBars &~ bitmask)
    self.m_iOutputValueBars |= (int(32 * (value / 100)) << bitshift) & bitmask
    self.m_iOutputValueBars |= 1 << IMON_ICONS.BARS

  def SetOutputIcons(self):
    ret = ""

    if self.m_iOutputValueIcons != self.m_iOutputValueOldIcons:
      self.m_iOutputValueOldIcons = self.m_iOutputValueIcons
      ret += "output %d\n" % (self.m_iOutputValueIcons)

    return ret

  def SetOutputBars(self):
    ret = ""

    if self.m_iOutputValueBars != self.m_iOutputValueOldBars:
      self.m_iOutputValueOldBars = self.m_iOutputValueBars
      ret += "output %d\n" % (self.m_iOutputValueBars)

    return ret
