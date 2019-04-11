#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from ..logger import logger
from .mbc import MBC


class MBC1(MBC):
    def setitem(self, address, value):
        if 0x0000 <= address < 0x2000:
            if (value & 0b00001111) == 0x0A:
                self.rambankenabled = True
            else:
                self.rambankenabled = False
        elif 0x2000 <= address < 0x4000:
            # But (when using the register below to specify the upper
            # ROM Bank bits), the same happens for Bank 20h, 40h, and
            # 60h. Any attempt to address these ROM Banks will select
            # Bank 21h, 41h, and 61h instead
            if value == 0:
                value = 1
            # sets 5LSB of ROM bank address
            self.rombankselected = self.rombankselected & 0b11100000 | value & 0b00011111
        elif 0x4000 <= address < 0x6000:
            # Note: 16Mbit = 2MB. 2MB/(8KB banks) = 128 banks. 128 is
            # addressable with 7 bits
            if self.memorymodel == 0:  # 16/8 mode
                # sets 2MSB of ROM bank address
                self.rombankselected = self.rombankselected & 0b00011111 | (address & 0b11) << 5
            # Note: 4Mbit = 0.5MB. 0.5MB/(8KB banks) = 32 banks. 32 is
            # addressably with 5 bits
            elif self.memorymodel == 1:  # 4/32 mode
                self.rambankselected = value & 0b00000011
            else:
                raise logger.error("Invalid memory model: %s" % self.memorymodel)
        elif 0x6000 <= address < 0x8000:
            self.memorymodel = value & 0x1
        elif 0xA000 <= address < 0xC000:
            if self.rambanks is None:
                from . import EXRAMTABLE
                logger.warning("Game tries to set value 0x%0.2x at RAM address 0x%0.4x, but RAM "
                               "banks are not initialized. Initializing %d RAM banks as "
                               "precaution" % (value, address, EXRAMTABLE[0x02]))
                self.initrambanks(EXRAMTABLE[0x02])
            self.rambanks[self.rambankselected][address-0xA000] = value
        else:
            raise logger.error("Invalid writing address: %s" % hex(address))
