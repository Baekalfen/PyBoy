#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.logger import logger

from .base_mbc import BaseMBC


class MBC1(BaseMBC):
    def setitem(self, address, value):
        if 0x0000 <= address < 0x2000:
            self.rambank_enabled = (value & 0b00001111) == 0b1010
        elif 0x2000 <= address < 0x4000:
            value &= 0x1F
            if value == 0:
                value = 1
            self.bank1 = value
        elif 0x4000 <= address < 0x6000:
           self.bank2 = value & 0x3
        elif 0x6000 <= address < 0x8000:
            self.memorymodel = value & 0x1
        elif 0xA000 <= address < 0xC000:
            if self.rambanks is None:
                from . import EXTERNAL_RAM_TABLE
                logger.warning("Game tries to set value 0x%0.2x at RAM address 0x%0.4x, but RAM "
                               "banks are not initialized. Initializing %d RAM banks as "
                               "precaution" % (value, address, EXTERNAL_RAM_TABLE[0x02]))
                self.init_rambanks(EXTERNAL_RAM_TABLE[0x02])

            if self.rambank_enabled:
                self.rambank_selected = self.bank2 if self.memorymodel else 0
                self.rambanks[self.rambank_selected % len(self.rambanks)][address-0xA000] = value
        else:
            raise logger.error("Invalid writing address: %s" % hex(address))

    def getitem(self, address):
        if 0x0000 <= address < 0x4000:
            self.rombank_selected = (self.bank2 << 5) if self.memorymodel else 0
            return self.rombanks[self.rombank_selected % len(self.rombanks)][address]
        elif 0x4000 <= address < 0x8000:
            self.rombank_selected = (self.bank2 << 5) | self.bank1
            return self.rombanks[self.rombank_selected % len(self.rombanks)][address-0x4000]
        elif 0xA000 <= address < 0xC000:
            if not self.rambank_initialized:
                raise logger.error("RAM banks not initialized: %s" % hex(address))

            if not self.rambank_enabled:
                return 0xFF

            self.rambank_selected = self.bank2 if self.memorymodel else 0
            return self.rambanks[self.rambank_selected % len(self.rambanks)][address-0xA000]
        else:
            raise logger.error("Reading address invalid: %s" % address)
