'''
    XBMC LCDproc addon
    Copyright (C) 2012 Team XBMC
    
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

import codecs

imon_decoding_table = (
    u'\x00'     #  0x00 -> NULL
    u'\x01'     #  0x01 -> START OF HEADING
    u'\x02'     #  0x02 -> START OF TEXT
    u'\x03'     #  0x03 -> END OF TEXT
    u'\x04'     #  0x04 -> END OF TRANSMISSION
    u'\x05'     #  0x05 -> ENQUIRY
    u'\x06'     #  0x06 -> ACKNOWLEDGE
    u'\x07'     #  0x07 -> BELL
    u'\x08'     #  0x08 -> BACKSPACE
    u'\t'       #  0x09 -> HORIZONTAL TABULATION
    u'\n'       #  0x0A -> LINE FEED
    u'\x0b'     #  0x0B -> VERTICAL TABULATION
    u'\x0c'     #  0x0C -> FORM FEED
    u'\r'       #  0x0D -> CARRIAGE RETURN
    u'\x0e'     #  0x0E -> SHIFT OUT
    u'\x0f'     #  0x0F -> SHIFT IN
    u'\u25b6'   #  0x10 -> BLACK RIGHT-POINTING TRIANGLE
    u'\u25c0'   #  0x11 -> BLACK LEFT-POINTING TRIANGLE
    u'\u201C'   #  0x12 -> LEFT DOUBLE QUOTATION MARK
    u'\u201D'   #  0x13 -> RIGHT DOUBLE QUOTATION MARK
    u'\u23eb'   #  0x14 -> BLACK UP-POINTING DOUBLE TRIANGLE
    u'\u23ec'   #  0x15 -> BLACK DOWN-POINTING DOUBLE TRIANGLE
    u'\u2b24'   #  0x16 -> BLACK LARGE CIRCLE
    u'\u21b2'   #  0x17 -> DOWNWARDS ARROW WITH TIP LEFTWARDS
    u'\u2191'   #  0x18 -> UPWARDS ARROW
    u'\u2193'   #  0x19 -> DOWNWARDS ARROW
    u'\u2192'   #  0x1A -> RIGHTWARDS ARROW
    u'\u2190'   #  0x1B -> LEFTWARDS ARROW
    u'\u2264'   #  0x1C -> LESS-THAN OR EQUAL TO
    u'\u2265'   #  0x1D -> GREATER-THAN OR EQUAL TO
    u'\u25b2'   #  0x1E -> BLACK UP-POINTING TRIANGLE
    u'\u25bc'   #  0x1F -> BLACK DOWN-POINTING TRIANGLE
    u' '        #  0x20 -> SPACE
    u'!'        #  0x21 -> EXCLAMATION MARK
    u'"'        #  0x22 -> QUOTATION MARK
    u'#'        #  0x23 -> NUMBER SIGN
    u'$'        #  0x24 -> DOLLAR SIGN
    u'%'        #  0x25 -> PERCENT SIGN
    u'&'        #  0x26 -> AMPERSAND
    u"'"        #  0x27 -> APOSTROPHE
    u'('        #  0x28 -> LEFT PARENTHESIS
    u')'        #  0x29 -> RIGHT PARENTHESIS
    u'*'        #  0x2A -> ASTERISK
    u'+'        #  0x2B -> PLUS SIGN
    u','        #  0x2C -> COMMA
    u'-'        #  0x2D -> HYPHEN-MINUS
    u'.'        #  0x2E -> FULL STOP
    u'/'        #  0x2F -> SOLIDUS
    u'0'        #  0x30 -> DIGIT ZERO
    u'1'        #  0x31 -> DIGIT ONE
    u'2'        #  0x32 -> DIGIT TWO
    u'3'        #  0x33 -> DIGIT THREE
    u'4'        #  0x34 -> DIGIT FOUR
    u'5'        #  0x35 -> DIGIT FIVE
    u'6'        #  0x36 -> DIGIT SIX
    u'7'        #  0x37 -> DIGIT SEVEN
    u'8'        #  0x38 -> DIGIT EIGHT
    u'9'        #  0x39 -> DIGIT NINE
    u':'        #  0x3A -> COLON
    u';'        #  0x3B -> SEMICOLON
    u'<'        #  0x3C -> LESS-THAN SIGN
    u'='        #  0x3D -> EQUALS SIGN
    u'>'        #  0x3E -> GREATER-THAN SIGN
    u'?'        #  0x3F -> QUESTION MARK
    u'@'        #  0x40 -> COMMERCIAL AT
    u'A'        #  0x41 -> LATIN CAPITAL LETTER A
    u'B'        #  0x42 -> LATIN CAPITAL LETTER B
    u'C'        #  0x43 -> LATIN CAPITAL LETTER C
    u'D'        #  0x44 -> LATIN CAPITAL LETTER D
    u'E'        #  0x45 -> LATIN CAPITAL LETTER E
    u'F'        #  0x46 -> LATIN CAPITAL LETTER F
    u'G'        #  0x47 -> LATIN CAPITAL LETTER G
    u'H'        #  0x48 -> LATIN CAPITAL LETTER H
    u'I'        #  0x49 -> LATIN CAPITAL LETTER I
    u'J'        #  0x4A -> LATIN CAPITAL LETTER J
    u'K'        #  0x4B -> LATIN CAPITAL LETTER K
    u'L'        #  0x4C -> LATIN CAPITAL LETTER L
    u'M'        #  0x4D -> LATIN CAPITAL LETTER M
    u'N'        #  0x4E -> LATIN CAPITAL LETTER N
    u'O'        #  0x4F -> LATIN CAPITAL LETTER O
    u'P'        #  0x50 -> LATIN CAPITAL LETTER P
    u'Q'        #  0x51 -> LATIN CAPITAL LETTER Q
    u'R'        #  0x52 -> LATIN CAPITAL LETTER R
    u'S'        #  0x53 -> LATIN CAPITAL LETTER S
    u'T'        #  0x54 -> LATIN CAPITAL LETTER T
    u'U'        #  0x55 -> LATIN CAPITAL LETTER U
    u'V'        #  0x56 -> LATIN CAPITAL LETTER V
    u'W'        #  0x57 -> LATIN CAPITAL LETTER W
    u'X'        #  0x58 -> LATIN CAPITAL LETTER X
    u'Y'        #  0x59 -> LATIN CAPITAL LETTER Y
    u'Z'        #  0x5A -> LATIN CAPITAL LETTER Z
    u'['        #  0x5B -> LEFT SQUARE BRACKET
    u'\\'       #  0x5C -> REVERSE SOLIDUS
    u']'        #  0x5D -> RIGHT SQUARE BRACKET
    u'^'        #  0x5E -> CIRCUMFLEX ACCENT
    u'_'        #  0x5F -> LOW LINE
    u'`'        #  0x60 -> GRAVE ACCENT
    u'a'        #  0x61 -> LATIN SMALL LETTER A
    u'b'        #  0x62 -> LATIN SMALL LETTER B
    u'c'        #  0x63 -> LATIN SMALL LETTER C
    u'd'        #  0x64 -> LATIN SMALL LETTER D
    u'e'        #  0x65 -> LATIN SMALL LETTER E
    u'f'        #  0x66 -> LATIN SMALL LETTER F
    u'g'        #  0x67 -> LATIN SMALL LETTER G
    u'h'        #  0x68 -> LATIN SMALL LETTER H
    u'i'        #  0x69 -> LATIN SMALL LETTER I
    u'j'        #  0x6A -> LATIN SMALL LETTER J
    u'k'        #  0x6B -> LATIN SMALL LETTER K
    u'l'        #  0x6C -> LATIN SMALL LETTER L
    u'm'        #  0x6D -> LATIN SMALL LETTER M
    u'n'        #  0x6E -> LATIN SMALL LETTER N
    u'o'        #  0x6F -> LATIN SMALL LETTER O
    u'p'        #  0x70 -> LATIN SMALL LETTER P
    u'q'        #  0x71 -> LATIN SMALL LETTER Q
    u'r'        #  0x72 -> LATIN SMALL LETTER R
    u's'        #  0x73 -> LATIN SMALL LETTER S
    u't'        #  0x74 -> LATIN SMALL LETTER T
    u'u'        #  0x75 -> LATIN SMALL LETTER U
    u'v'        #  0x76 -> LATIN SMALL LETTER V
    u'w'        #  0x77 -> LATIN SMALL LETTER W
    u'x'        #  0x78 -> LATIN SMALL LETTER X
    u'y'        #  0x79 -> LATIN SMALL LETTER Y
    u'z'        #  0x7A -> LATIN SMALL LETTER Z
    u'{'        #  0x7B -> LEFT CURLY BRACKET
    u'|'        #  0x7C -> VERTICAL LINE
    u'}'        #  0x7D -> RIGHT CURLY BRACKET
    u'~'        #  0x7E -> TILDE
    u'\x7f'     #  0x7F -> DELETE
    u'\u0411'   #  0x80 -> CYRILLIC CAPITAL LETTER BE
    u'\u0414'   #  0x81 -> CYRILLIC CAPITAL LETTER DE
    u'\u0417'   #  0x82 -> CYRILLIC CAPITAL LETTER GJE
    u'\u0453'   #  0x83 -> CYRILLIC CAPITAL LETTER ZE
    u'\u0418'   #  0x84 -> CYRILLIC CAPITAL LETTER I
    u'\u0419'   #  0x85 -> CYRILLIC CAPITAL LETTER SHORT I
    u'\u041b'   #  0x86 -> CYRILLIC CAPITAL LETTER EL
    u'\u041f'   #  0x87 -> CYRILLIC CAPITAL LETTER PE
    u'\u0423'   #  0x88 -> CYRILLIC CAPITAL LETTER U
    u'\u0426'   #  0x89 -> CYRILLIC CAPITAL LETTER TSE
    u'\u0427'   #  0x8A -> CYRILLIC CAPITAL LETTER CHE
    u'\u0428'   #  0x8B -> CYRILLIC CAPITAL LETTER SHA
    u'\u0429'   #  0x8C -> CYRILLIC CAPITAL LETTER SHCHA
    u'\u042A'   #  0x8D -> CYRILLIC CAPITAL LETTER HARD SIGN
    u'\u042B'   #  0x8E -> CYRILLIC CAPITAL LETTER YERU
    u'\u042d'   #  0x8F -> CYRILLIC CAPITAL LETTER E
    u'\u03b1'   #  0x90 -> GREEK SMALL LETTER ALPHA
    u'\u266a'   #  0x91 -> EIGHTH NOTE
    u'\u0413'   #  0x92 -> CYRILLIC CAPITAL LETTER GHE
    u'\u03c0'   #  0x93 -> GREEK SMALL LETTER PI
    u'\u03a3'   #  0x94 -> GREEK CAPITAL LETTER SIGMA
    u'\u03c3'   #  0x95 -> GREEK SMALL LETTER SIGMA
    u'\u266c'   #  0x96 -> BEAMED SIXTEENTH NOTES
    u'\u03c4'   #  0x97 -> GREEK SMALL LETTER TAU
    u'\uf0f3'   #  0x98 -> BELL ICON (not sure)
    u'\u0398'   #  0x99 -> GREEK CAPITAL LETTER THETA
    u'\u03a9'   #  0x9A -> GREEK CAPITAL LETTER OMEGA
    u'\u03b4'   #  0x9B -> GREEK SMALL LETTER DELTA
    u'\u221e'   #  0x9C -> INFINITY
    u'\u2664'   #  0x9D -> HEAVY BLACK HEART
    u'\u03b5'   #  0x9E -> GREEK SMALL LETTER EPSILON
    u'\u2229'   #  0x9F -> INTERSECTION
    u'\u2016'   #  0xA0 -> DOUBLE VERTICAL LINE
    u'\xa1'     #  0xA1 -> INVERTED EXCLAMATION MARK
    u'\xa2'     #  0xA2 -> CENT SIGN
    u'\xa3'     #  0xA3 -> POUND SIGN
    u'\xa4'     #  0xA4 -> CURRENCY SIGN
    u'\xa5'     #  0xA5 -> YEN SIGN
    u'\xa6'     #  0xA6 -> BROKEN BAR
    u'\xa7'     #  0xA7 -> SECTION SIGN
    u'\u0192'   #  0xA8 -> LATIN SMALL LETTER F WITH HOOK
    u'\xa9'     #  0xA9 -> COPYRIGHT SIGN
    u'\xaa'     #  0xAA -> FEMININE ORDINAL INDICATOR
    u'\xab'     #  0xAB -> LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    u'\u042e'   #  0xAC -> CYRILLIC CAPITAL LETTER YU
    u'\u042f'   #  0xAD -> CYRILLIC CAPITAL LETTER YA
    u'\xae'     #  0xAE -> REGISTERED SIGN
    u'\u2018'   #  0xAF -> LEFT SINGLE QUOTATION MARK
    u'\xb0'     #  0xB0 -> DEGREE SIGN
    u'\xb1'     #  0xB1 -> PLUS-MINUS SIGN
    u'\xb2'     #  0xB2 -> SUPERSCRIPT TWO
    u'\xb3'     #  0xB3 -> SUPERSCRIPT THREE
    u'\u2109'   #  0xB4 -> DEGREE FAHRENHEIT
    u'\xb5'     #  0xB5 -> MICRO SIGN
    u'\xb6'     #  0xB6 -> PILCROW SIGN
    u'\xb7'     #  0xB7 -> MIDDLE DOT
    u'\u03c9'   #  0xB8 -> GREEK SMALL LETTER OMEGA
    u'\xb9'     #  0xB9 -> SUPERSCRIPT ONE
    u'\xba'     #  0xBA -> MASCULINE ORDINAL INDICATOR
    u'\xbb'     #  0xBB -> RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    u'\xbc'     #  0xBC -> VULGAR FRACTION ONE QUARTER
    u'\xbd'     #  0xBD -> VULGAR FRACTION ONE HALF
    u'\xbe'     #  0xBE -> VULGAR FRACTION THREE QUARTERS
    u'\xbf'     #  0xBF -> INVERTED QUESTION MARK
    u'\xc0'     #  0xC0 -> LATIN CAPITAL LETTER A WITH GRAVE
    u'\xc1'     #  0xC1 -> LATIN CAPITAL LETTER A WITH ACUTE
    u'\xc2'     #  0xC2 -> LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    u'\xc3'     #  0xC3 -> LATIN CAPITAL LETTER A WITH TILDE
    u'\xc4'     #  0xC4 -> LATIN CAPITAL LETTER A WITH DIAERESIS
    u'\xc5'     #  0xC5 -> LATIN CAPITAL LETTER A WITH RING ABOVE
    u'\xc6'     #  0xC6 -> LATIN CAPITAL LETTER AE
    u'\xc7'     #  0xC7 -> LATIN CAPITAL LETTER C WITH CEDILLA
    u'\xc8'     #  0xC8 -> LATIN CAPITAL LETTER E WITH GRAVE
    u'\xc9'     #  0xC9 -> LATIN CAPITAL LETTER E WITH ACUTE
    u'\xca'     #  0xCA -> LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    u'\xcb'     #  0xCB -> LATIN CAPITAL LETTER E WITH DIAERESIS
    u'\xcc'     #  0xCC -> LATIN CAPITAL LETTER I WITH GRAVE
    u'\xcd'     #  0xCD -> LATIN CAPITAL LETTER I WITH ACUTE
    u'\xce'     #  0xCE -> LATIN CAPITAL LETTER I WITH CIRCUMFLEX
    u'\xcf'     #  0xCF -> LATIN CAPITAL LETTER I WITH DIAERESIS
    u'\xd0'     #  0xD0 -> LATIN CAPITAL LETTER ETH
    u'\xd1'     #  0xD1 -> LATIN CAPITAL LETTER N WITH TILDE
    u'\xd2'     #  0xD2 -> LATIN CAPITAL LETTER O WITH GRAVE
    u'\xd3'     #  0xD3 -> LATIN CAPITAL LETTER O WITH ACUTE
    u'\xd4'     #  0xD4 -> LATIN CAPITAL LETTER O WITH CIRCUMFLEX
    u'\xd5'     #  0xD5 -> LATIN CAPITAL LETTER O WITH TILDE
    u'\xd6'     #  0xD6 -> LATIN CAPITAL LETTER O WITH DIAERESIS
    u'\xd7'     #  0xD7 -> MULTIPLICATION SIGN
    u'\u0424'   #  0xD8 -> CYRILLIC CAPITAL LETTER EF
    u'\xd9'     #  0xD9 -> LATIN CAPITAL LETTER U WITH GRAVE
    u'\xda'     #  0xDA -> LATIN CAPITAL LETTER U WITH ACUTE
    u'\xdb'     #  0xDB -> LATIN CAPITAL LETTER U WITH CIRCUMFLEX
    u'\xdc'     #  0xDC -> LATIN CAPITAL LETTER U WITH DIAERESIS
    u'\xdd'     #  0xDD -> LATIN CAPITAL LETTER Y WITH ACUTE
    u'\xde'     #  0xDE -> LATIN CAPITAL LETTER THORN
    u'\xdf'     #  0xDF -> LATIN SMALL LETTER SHARP
    u'\xe0'     #  0xE0 -> LATIN SMALL LETTER A WITH GRAVE
    u'\xe1'     #  0xE1 -> LATIN SMALL LETTER A WITH ACUTE
    u'\xe2'     #  0xE2 -> LATIN SMALL LETTER A WITH CIRCUMFLEX
    u'\xe3'     #  0xE3 -> LATIN SMALL LETTER A WITH TILDE
    u'\xe4'     #  0xE4 -> LATIN SMALL LETTER A WITH DIAERESIS
    u'\xe5'     #  0xE5 -> LATIN SMALL LETTER A WITH RING ABOVE
    u'\xe6'     #  0xE6 -> LATIN SMALL LETTER AE
    u'\xe7'     #  0xE7 -> LATIN SMALL LETTER C WITH CEDILLA
    u'\xe8'     #  0xE8 -> LATIN SMALL LETTER E WITH GRAVE
    u'\xe9'     #  0xE9 -> LATIN SMALL LETTER E WITH ACUTE
    u'\xea'     #  0xEA -> LATIN SMALL LETTER E WITH CIRCUMFLEX
    u'\xeb'     #  0xEB -> LATIN SMALL LETTER E WITH DIAERESIS
    u'\xec'     #  0xEC -> LATIN SMALL LETTER I WITH GRAVE
    u'\xed'     #  0xED -> LATIN SMALL LETTER I WITH ACUTE
    u'\xee'     #  0xEE -> LATIN SMALL LETTER I WITH CIRCUMFLEX
    u'\xef'     #  0xEF -> LATIN SMALL LETTER I WITH DIAERESIS
    u'\xf0'     #  0xF0 -> LATIN SMALL LETTER ETH
    u'\xf1'     #  0xF1 -> LATIN SMALL LETTER N WITH TILDE
    u'\xf2'     #  0xF2 -> LATIN SMALL LETTER O WITH GRAVE
    u'\xf3'     #  0xF3 -> LATIN SMALL LETTER O WITH ACUTE
    u'\xf4'     #  0xF4 -> LATIN SMALL LETTER O WITH CIRCUMFLEX
    u'\xf5'     #  0xF5 -> LATIN SMALL LETTER O WITH TILDE
    u'\xf6'     #  0xF6 -> LATIN SMALL LETTER O WITH DIAERESIS
    u'\xf7'     #  0xF7 -> DIVISION SIGN
    u'\xf8'     #  0xF8 -> LATIN SMALL LETTER O WITH STROKE
    u'\xf9'     #  0xF9 -> LATIN SMALL LETTER U WITH GRAVE
    u'\xfa'     #  0xFA -> LATIN SMALL LETTER U WITH ACUTE
    u'\xfb'     #  0xFB -> LATIN SMALL LETTER U WITH CIRCUMFLEX
    u'\xfc'     #  0xFC -> LATIN SMALL LETTER U WITH DIAERESIS
    u'\xfd'     #  0xFD -> LATIN SMALL LETTER Y WITH ACUTE
    u'\xfe'     #  0xFE -> LATIN SMALL LETTER THORN
    u'\xff'     #  0xFF -> LATIN SMALL LETTER Y WITH DIAERESIS
)

imon_encoding_map = {
    0x0000: 0x0000,     #  NULL
    0x0001: 0x0001,     #  START OF HEADING
    0x0002: 0x0002,     #  START OF TEXT
    0x0003: 0x0003,     #  END OF TEXT
    0x0004: 0x0004,     #  END OF TRANSMISSION
    0x0005: 0x0005,     #  ENQUIRY
    0x0006: 0x0006,     #  ACKNOWLEDGE
    0x0007: 0x0007,     #  BELL
    0x0008: 0x0008,     #  BACKSPACE
    0x0009: 0x0009,     #  HORIZONTAL TABULATION
    0x000a: 0x000a,     #  LINE FEED
    0x000b: 0x000b,     #  VERTICAL TABULATION
    0x000c: 0x000c,     #  FORM FEED
    0x000d: 0x000d,     #  CARRIAGE RETURN
    0x000e: 0x000e,     #  SHIFT OUT
    0x000f: 0x000f,     #  SHIFT IN
    0x25b6: 0x0010,     #  BLACK RIGHT-POINTING TRIANGLE
    0x25c0: 0x0011,     #  BLACK LEFT-POINTING TRIANGLE
    0x201c: 0x0012,     #  LEFT DOUBLE QUOTATION MARK
    0x201d: 0x0013,     #  RIGHT DOUBLE QUOTATION MARK
    0x23eb: 0x0014,     #  BLACK UP-POINTING DOUBLE TRIANGLE
    0x23ec: 0x0015,     #  BLACK DOWN-POINTING DOUBLE TRIANGLE
    0x2b24: 0x0016,     #  BLACK LARGE CIRCLE
    0x21b2: 0x0017,     #  DOWNWARDS ARROW WITH TIP LEFTWARDS
    0x2191: 0x0018,     #  UPWARDS ARROW
    0x2193: 0x0019,     #  DOWNWARDS ARROW
    0x2192: 0x001a,     #  RIGHTWARDS ARROW
    0x2190: 0x001b,     #  LEFTWARDS ARROW
    0x2264: 0x001c,     #  LESS-THAN OR EQUAL TO
    0x2265: 0x001d,     #  GREATER-THAN OR EQUAL TO
    0x25b2: 0x001e,     #  BLACK UP-POINTING TRIANGLE
    0x25bc: 0x001f,     #  BLACK DOWN-POINTING TRIANGLE
    0x0020: 0x0020,     #  SPACE
    0x0021: 0x0021,     #  EXCLAMATION MARK
    0x0022: 0x0022,     #  QUOTATION MARK
    0x0023: 0x0023,     #  NUMBER SIGN
    0x0024: 0x0024,     #  DOLLAR SIGN
    0x0025: 0x0025,     #  PERCENT SIGN
    0x0026: 0x0026,     #  AMPERSAND
    0x0027: 0x0027,     #  APOSTROPHE
    0x0028: 0x0028,     #  LEFT PARENTHESIS
    0x0029: 0x0029,     #  RIGHT PARENTHESIS
    0x002a: 0x002a,     #  ASTERISK
    0x002b: 0x002b,     #  PLUS SIGN
    0x002c: 0x002c,     #  COMMA
    0x002d: 0x002d,     #  HYPHEN-MINUS
    0x002e: 0x002e,     #  FULL STOP
    0x002f: 0x002f,     #  SOLIDUS
    0x0030: 0x0030,     #  DIGIT ZERO
    0x0031: 0x0031,     #  DIGIT ONE
    0x0032: 0x0032,     #  DIGIT TWO
    0x0033: 0x0033,     #  DIGIT THREE
    0x0034: 0x0034,     #  DIGIT FOUR
    0x0035: 0x0035,     #  DIGIT FIVE
    0x0036: 0x0036,     #  DIGIT SIX
    0x0037: 0x0037,     #  DIGIT SEVEN
    0x0038: 0x0038,     #  DIGIT EIGHT
    0x0039: 0x0039,     #  DIGIT NINE
    0x003a: 0x003a,     #  COLON
    0x003b: 0x003b,     #  SEMICOLON
    0x003c: 0x003c,     #  LESS-THAN SIGN
    0x003d: 0x003d,     #  EQUALS SIGN
    0x003e: 0x003e,     #  GREATER-THAN SIGN
    0x003f: 0x003f,     #  QUESTION MARK
    0x0040: 0x0040,     #  COMMERCIAL AT
    0x0041: 0x0041,     #  LATIN CAPITAL LETTER A
    0x0042: 0x0042,     #  LATIN CAPITAL LETTER B
    0x0043: 0x0043,     #  LATIN CAPITAL LETTER C
    0x0044: 0x0044,     #  LATIN CAPITAL LETTER D
    0x0045: 0x0045,     #  LATIN CAPITAL LETTER E
    0x0046: 0x0046,     #  LATIN CAPITAL LETTER F
    0x0047: 0x0047,     #  LATIN CAPITAL LETTER G
    0x0048: 0x0048,     #  LATIN CAPITAL LETTER H
    0x0049: 0x0049,     #  LATIN CAPITAL LETTER I
    0x004a: 0x004a,     #  LATIN CAPITAL LETTER J
    0x004b: 0x004b,     #  LATIN CAPITAL LETTER K
    0x004c: 0x004c,     #  LATIN CAPITAL LETTER L
    0x004d: 0x004d,     #  LATIN CAPITAL LETTER M
    0x004e: 0x004e,     #  LATIN CAPITAL LETTER N
    0x004f: 0x004f,     #  LATIN CAPITAL LETTER O
    0x0050: 0x0050,     #  LATIN CAPITAL LETTER P
    0x0051: 0x0051,     #  LATIN CAPITAL LETTER Q
    0x0052: 0x0052,     #  LATIN CAPITAL LETTER R
    0x0053: 0x0053,     #  LATIN CAPITAL LETTER S
    0x0054: 0x0054,     #  LATIN CAPITAL LETTER T
    0x0055: 0x0055,     #  LATIN CAPITAL LETTER U
    0x0056: 0x0056,     #  LATIN CAPITAL LETTER V
    0x0057: 0x0057,     #  LATIN CAPITAL LETTER W
    0x0058: 0x0058,     #  LATIN CAPITAL LETTER X
    0x0059: 0x0059,     #  LATIN CAPITAL LETTER Y
    0x005a: 0x005a,     #  LATIN CAPITAL LETTER Z
    0x005b: 0x005b,     #  LEFT SQUARE BRACKET
    0x005c: 0x005c,     #  REVERSE SOLIDUS
    0x005d: 0x005d,     #  RIGHT SQUARE BRACKET
    0x005e: 0x005e,     #  CIRCUMFLEX ACCENT
    0x005f: 0x005f,     #  LOW LINE
    0x0060: 0x0060,     #  GRAVE ACCENT
    0x0061: 0x0061,     #  LATIN SMALL LETTER A
    0x0062: 0x0062,     #  LATIN SMALL LETTER B
    0x0063: 0x0063,     #  LATIN SMALL LETTER C
    0x0064: 0x0064,     #  LATIN SMALL LETTER D
    0x0065: 0x0065,     #  LATIN SMALL LETTER E
    0x0066: 0x0066,     #  LATIN SMALL LETTER F
    0x0067: 0x0067,     #  LATIN SMALL LETTER G
    0x0068: 0x0068,     #  LATIN SMALL LETTER H
    0x0069: 0x0069,     #  LATIN SMALL LETTER I
    0x006a: 0x006a,     #  LATIN SMALL LETTER J
    0x006b: 0x006b,     #  LATIN SMALL LETTER K
    0x006c: 0x006c,     #  LATIN SMALL LETTER L
    0x006d: 0x006d,     #  LATIN SMALL LETTER M
    0x006e: 0x006e,     #  LATIN SMALL LETTER N
    0x006f: 0x006f,     #  LATIN SMALL LETTER O
    0x0070: 0x0070,     #  LATIN SMALL LETTER P
    0x0071: 0x0071,     #  LATIN SMALL LETTER Q
    0x0072: 0x0072,     #  LATIN SMALL LETTER R
    0x0073: 0x0073,     #  LATIN SMALL LETTER S
    0x0074: 0x0074,     #  LATIN SMALL LETTER T
    0x0075: 0x0075,     #  LATIN SMALL LETTER U
    0x0076: 0x0076,     #  LATIN SMALL LETTER V
    0x0077: 0x0077,     #  LATIN SMALL LETTER W
    0x0078: 0x0078,     #  LATIN SMALL LETTER X
    0x0079: 0x0079,     #  LATIN SMALL LETTER Y
    0x007a: 0x007a,     #  LATIN SMALL LETTER Z
    0x007b: 0x007b,     #  LEFT CURLY BRACKET
    0x007c: 0x007c,     #  VERTICAL LINE
    0x007d: 0x007d,     #  RIGHT CURLY BRACKET
    0x007e: 0x007e,     #  TILDE
    0x007f: 0x007f,     #  DELETE
    0x0411: 0x0080,     #  CYRILLIC CAPITAL LETTER BE
    0x0414: 0x0081,     #  CYRILLIC CAPITAL LETTER DE
    0x0416: 0x0082,     #  CYRILLIC CAPITAL LETTER GJE
    0x0417: 0x0083,     #  CYRILLIC CAPITAL LETTER ZE
    0x0418: 0x0084,     #  CYRILLIC CAPITAL LETTER I
    0x0419: 0x0085,     #  CYRILLIC CAPITAL LETTER SHORT I
    0x041b: 0x0086,     #  CYRILLIC CAPITAL LETTER EL
    0x041f: 0x0087,     #  CYRILLIC CAPITAL LETTER PE
    0x0423: 0x0088,     #  CYRILLIC CAPITAL LETTER U
    0x0426: 0x0089,     #  CYRILLIC CAPITAL LETTER TSE
    0x0427: 0x008a,     #  CYRILLIC CAPITAL LETTER CHE
    0x0428: 0x008b,     #  CYRILLIC CAPITAL LETTER SHA
    0x0429: 0x008c,     #  CYRILLIC CAPITAL LETTER SHCHA
    0x042a: 0x008d,     #  CYRILLIC CAPITAL LETTER HARD SIGN
    0x042b: 0x008e,     #  CYRILLIC CAPITAL LETTER YERU
    0x042d: 0x008f,     #  CYRILLIC CAPITAL LETTER E
    0x03b1: 0x0090,     #  GREEK SMALL LETTER ALPHA
    0x266a: 0x0091,     #  EIGHTH NOTE
    0x0413: 0x0092,     #  CYRILLIC CAPITAL LETTER GHE
    0x03c0: 0x0093,     #  GREEK SMALL LETTER PI
    0x03a3: 0x0094,     #  GREEK CAPITAL LETTER SIGMA
    0x03c3: 0x0095,     #  GREEK SMALL LETTER SIGMA
    0x266c: 0x0096,     #  BEAMED SIXTEENTH NOTES
    0x03c4: 0x0097,     #  GREEK SMALL LETTER TAU
    0xf0f3: 0x0098,     #  BELL ICON (not sure)
    0x0398: 0x0099,     #  GREEK CAPITAL LETTER THETA
    0x03a9: 0x009a,     #  GREEK CAPITAL LETTER OMEGA
    0x03b4: 0x009b,     #  GREEK SMALL LETTER DELTA
    0x221e: 0x009c,     #  INFINITY
    0x2664: 0x009d,     #  HEAVY BLACK HEART
    0x03b5: 0x009e,     #  GREEK SMALL LETTER EPSILON
    0x2229: 0x009f,     #  INTERSECTION
    0x2016: 0x00a0,     #  DOUBLE VERTICAL LINE
    0x00a1: 0x00a1,     #  INVERTED EXCLAMATION MARK
    0x00a2: 0x00a2,     #  CENT SIGN
    0x00a3: 0x00a3,     #  POUND SIGN
    0x00a4: 0x00a4,     #  CURRENCY SIGN
    0x00a5: 0x00a5,     #  YEN SIGN
    0x00a6: 0x00a6,     #  BROKEN BAR
    0x00a7: 0x00a7,     #  SECTION SIGN
    0x0192: 0x00a8,     #  LATIN SMALL LETTER F WITH HOOK
    0x00a9: 0x00a9,     #  COPYRIGHT SIGN
    0x00aa: 0x00aa,     #  FEMININE ORDINAL INDICATOR
    0x00ab: 0x00ab,     #  LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    0x042e: 0x00ac,     #  CYRILLIC CAPITAL LETTER YU
    0x042f: 0x00ad,     #  CYRILLIC CAPITAL LETTER YA
    0x00ae: 0x00ae,     #  REGISTERED SIGN
    0x2018: 0x00af,     #  LEFT SINGLE QUOTATION MARK
    0x00b0: 0x00b0,     #  DEGREE SIGN
    0x00b1: 0x00b1,     #  PLUS-MINUS SIGN
    0x00b2: 0x00b2,     #  SUPERSCRIPT TWO
    0x00b3: 0x00b3,     #  SUPERSCRIPT THREE
    0x2109: 0x00b4,     #  DEGREE FAHRENHEIT
    0x00b5: 0x00b5,     #  MICRO SIGN
    0x00b6: 0x00b6,     #  PILCROW SIGN
    0x00b7: 0x00b7,     #  MIDDLE DOT
    0x03c9: 0x00b8,     #  GREEK SMALL LETTER OMEGA
    0x00b9: 0x00b9,     #  SUPERSCRIPT ONE
    0x00ba: 0x00ba,     #  MASCULINE ORDINAL INDICATOR
    0x00bb: 0x00bb,     #  RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    0x00bc: 0x00bc,     #  VULGAR FRACTION ONE QUARTER
    0x00bd: 0x00bd,     #  VULGAR FRACTION ONE HALF
    0x00be: 0x00be,     #  VULGAR FRACTION THREE QUARTERS
    0x00bf: 0x00bf,     #  INVERTED QUESTION MARK
    0x00c0: 0x00c0,     #  LATIN CAPITAL LETTER A WITH GRAVE
    0x00c1: 0x00c1,     #  LATIN CAPITAL LETTER A WITH ACUTE
    0x00c2: 0x00c2,     #  LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    0x00c3: 0x00c3,     #  LATIN CAPITAL LETTER A WITH TILDE
    0x00c4: 0x00c4,     #  LATIN CAPITAL LETTER A WITH DIAERESIS
    0x00c5: 0x00c5,     #  LATIN CAPITAL LETTER A WITH RING ABOVE
    0x00c6: 0x00c6,     #  LATIN CAPITAL LETTER AE
    0x00c7: 0x00c7,     #  LATIN CAPITAL LETTER C WITH CEDILLA
    0x00c8: 0x00c8,     #  LATIN CAPITAL LETTER E WITH GRAVE
    0x00c9: 0x00c9,     #  LATIN CAPITAL LETTER E WITH ACUTE
    0x00ca: 0x00ca,     #  LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    0x00cb: 0x00cb,     #  LATIN CAPITAL LETTER E WITH DIAERESIS
    0x00cc: 0x00cc,     #  LATIN CAPITAL LETTER I WITH GRAVE
    0x00cd: 0x00cd,     #  LATIN CAPITAL LETTER I WITH ACUTE
    0x00ce: 0x00ce,     #  LATIN CAPITAL LETTER I WITH CIRCUMFLEX
    0x00cf: 0x00cf,     #  LATIN CAPITAL LETTER I WITH DIAERESIS
    0x00d0: 0x00d0,     #  LATIN CAPITAL LETTER ETH
    0x00d1: 0x00d1,     #  LATIN CAPITAL LETTER N WITH TILDE
    0x00d2: 0x00d2,     #  LATIN CAPITAL LETTER O WITH GRAVE
    0x00d3: 0x00d3,     #  LATIN CAPITAL LETTER O WITH ACUTE
    0x00d4: 0x00d4,     #  LATIN CAPITAL LETTER O WITH CIRCUMFLEX
    0x00d5: 0x00d5,     #  LATIN CAPITAL LETTER O WITH TILDE
    0x00d6: 0x00d6,     #  LATIN CAPITAL LETTER O WITH DIAERESIS
    0x00d7: 0x00d7,     #  MULTIPLICATION SIGN
    0x0424: 0x00d8,     #  CYRILLIC CAPITAL LETTER EF
    0x00d9: 0x00d9,     #  LATIN CAPITAL LETTER U WITH GRAVE
    0x00da: 0x00da,     #  LATIN CAPITAL LETTER U WITH ACUTE
    0x00db: 0x00db,     #  LATIN CAPITAL LETTER U WITH CIRCUMFLEX
    0x00dc: 0x00dc,     #  LATIN CAPITAL LETTER U WITH DIAERESIS
    0x00dd: 0x00dd,     #  LATIN CAPITAL LETTER Y WITH ACUTE
    0x00de: 0x00de,     #  LATIN CAPITAL LETTER THORN
    0x00df: 0x00df,     #  LATIN SMALL LETTER SHARP
    0x00e0: 0x00e0,     #  LATIN SMALL LETTER A WITH GRAVE
    0x00e1: 0x00e1,     #  LATIN SMALL LETTER A WITH ACUTE
    0x00e2: 0x00e2,     #  LATIN SMALL LETTER A WITH CIRCUMFLEX
    0x00e3: 0x00e3,     #  LATIN SMALL LETTER A WITH TILDE
    0x00e4: 0x00e4,     #  LATIN SMALL LETTER A WITH DIAERESIS
    0x00e5: 0x00e5,     #  LATIN SMALL LETTER A WITH RING ABOVE
    0x00e6: 0x00e6,     #  LATIN SMALL LETTER AE
    0x00e7: 0x00e7,     #  LATIN SMALL LETTER C WITH CEDILLA
    0x00e8: 0x00e8,     #  LATIN SMALL LETTER E WITH GRAVE
    0x00e9: 0x00e9,     #  LATIN SMALL LETTER E WITH ACUTE
    0x00ea: 0x00ea,     #  LATIN SMALL LETTER E WITH CIRCUMFLEX
    0x00eb: 0x00eb,     #  LATIN SMALL LETTER E WITH DIAERESIS
    0x00ec: 0x00ec,     #  LATIN SMALL LETTER I WITH GRAVE
    0x00ed: 0x00ed,     #  LATIN SMALL LETTER I WITH ACUTE
    0x00ee: 0x00ee,     #  LATIN SMALL LETTER I WITH CIRCUMFLEX
    0x00ef: 0x00ef,     #  LATIN SMALL LETTER I WITH DIAERESIS
    0x00f0: 0x00f0,     #  LATIN SMALL LETTER ETH
    0x00f1: 0x00f1,     #  LATIN SMALL LETTER N WITH TILDE
    0x00f2: 0x00f2,     #  LATIN SMALL LETTER O WITH GRAVE
    0x00f3: 0x00f3,     #  LATIN SMALL LETTER O WITH ACUTE
    0x00f4: 0x00f4,     #  LATIN SMALL LETTER O WITH CIRCUMFLEX
    0x00f5: 0x00f5,     #  LATIN SMALL LETTER O WITH TILDE
    0x00f6: 0x00f6,     #  LATIN SMALL LETTER O WITH DIAERESIS
    0x00f7: 0x00f7,     #  DIVISION SIGN
    0x00f8: 0x00f8,     #  LATIN SMALL LETTER O WITH STROKE
    0x00f9: 0x00f9,     #  LATIN SMALL LETTER U WITH GRAVE
    0x00fa: 0x00fa,     #  LATIN SMALL LETTER U WITH ACUTE
    0x00fb: 0x00fb,     #  LATIN SMALL LETTER U WITH CIRCUMFLEX
    0x00fc: 0x00fc,     #  LATIN SMALL LETTER U WITH DIAERESIS
    0x00fd: 0x00fd,     #  LATIN SMALL LETTER Y WITH ACUTE
    0x00fe: 0x00fe,     #  LATIN SMALL LETTER THORN
    0x00ff: 0x00ff,     #  LATIN SMALL LETTER Y WITH DIAERESIS
# Rest of capital cyrillic letters
    0x0410: 0x0041,
    0x0412: 0x0042,
    0x0415: 0x0045,
    0x0401: 0x00cb,
    0x041a: 0x004b,
    0x041c: 0x004d,
    0x041d: 0x0048,
    0x041e: 0x004f,
    0x0420: 0x0050,
    0x0421: 0x0043,
    0x0422: 0x0054,
    0x0425: 0x0058,
    0x042c: 0x0062,
# Small Cyrillc letters
    0x0430: 0x0041,
    0x0431: 0x0080,
    0x0432: 0x0042,
    0x0433: 0x0092,
    0x0434: 0x0081,
    0x0435: 0x0045,
    0x0451: 0x00cb,
    0x0436: 0x0082,
    0x0437: 0x0083,
    0x0438: 0x0084,
    0x0439: 0x0085,
    0x043a: 0x004b,
    0x043b: 0x0086,
    0x043c: 0x004d,
    0x043d: 0x0048,
    0x043e: 0x004f,
    0x043f: 0x0087,
    0x0440: 0x0050,
    0x0441: 0x0043,
    0x0442: 0x0054,
    0x0443: 0x0088,
    0x0444: 0x00d8,
    0x0445: 0x0058,
    0x0446: 0x0089,
    0x0447: 0x008a,
    0x0448: 0x008b,
    0x0449: 0x008c,
    0x044a: 0x008d,
    0x044b: 0x008e,
    0x044c: 0x0062,
    0x044d: 0x008f,
    0x044e: 0x00ac,
    0x044f: 0x00ad
}

class Codec(codecs.Codec):

    def encode(self,input,errors='strict'):
        return codecs.charmap_encode(input,errors,imon_encoding_map)

    def decode(self,input,errors='strict'):
        return codecs.charmap_decode(input,errors,imon_decoding_table)

class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        return codecs.charmap_encode(input,self.errors,imon_encoding_map)[0]

class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=False):
        return codecs.charmap_decode(input,self.errors,imon_decoding_table)[0]

class StreamWriter(Codec,codecs.StreamWriter):
    pass

class StreamReader(Codec,codecs.StreamReader):
    pass

def searchcp(name):
    if name == 'imon':
        return codecs.CodecInfo(
            name='imon',
            encode=Codec().encode,
            decode=Codec().decode,
            incrementalencoder=IncrementalEncoder,
            incrementaldecoder=IncrementalDecoder,
            streamreader=StreamReader,
            streamwriter=StreamWriter,
        )
    else: return None

