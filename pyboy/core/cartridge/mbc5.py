#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import logging

from pyboy.logger import logger

from .base_mbc import BaseMBC


class MBC5(BaseMBC):
    def setitem(self, address, value):
        if 0x0000 <= address < 0x2000:
            # 8-bit register. All bits matter, so only 0b00001010 enables RAM.
            self.rambank_enabled = (value == 0b00001010)
        elif 0x2000 <= address < 0x3000:
            # 8-bit register used for the lower 8 bits of the ROM bank number.
            self.rombank_selected = (self.rombank_selected & 0b100000000) | value
        elif 0x3000 <= address < 0x4000:
            # 1-bit register used for the most significant bit of the ROM bank number.
            self.rombank_selected = ((value & 0x1) << 8) | (self.rombank_selected & 0xFF)
        elif 0x4000 <= address < 0x6000:
            self.rambank_selected = value & 0xF
        elif 0xA000 <= address < 0xC000:
            if self.rambanks is None:
                logger.warning(
                    "Game tries to set value 0x%0.2x at RAM address 0x%0.4x, but RAM "
                    "banks are not initialized. Initializing %d RAM banks as "
                    "precaution" % (value, address, self.external_ram_count)
                )
                self.init_rambanks(self.external_ram_count)
            if self.rambank_enabled:
                self.rambanks[self.rambank_selected % self.external_ram_count][address - 0xA000] = value
        else:
            logger.error("Unexpected write to 0x%0.4x, value: 0x%0.2x" % (address, value))
