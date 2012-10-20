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
  
class IMON_ICONS:
  ICON_SPINDISC = 0
  BARS = 29

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
