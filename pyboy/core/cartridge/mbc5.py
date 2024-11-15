#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pyboy

from .base_mbc import BaseMBC

logger = pyboy.logging.get_logger(__name__)


class MBC5(BaseMBC):
    def setitem(self, address, value):
        if 0x0000 <= address < 0x2000:
            # 8-bit register. All bits matter, so only 0b00001010 enables RAM.
            self.rambank_enabled = value == 0b00001010
        elif 0x2000 <= address < 0x3000:
            # 8-bit register used for the lower 8 bits of the ROM bank number.
            self.rombank_selected = ((self.rombank_selected & 0b100000000) | value) % self.external_rom_count
        elif 0x3000 <= address < 0x4000:
            # 1-bit register used for the most significant bit of the ROM bank number.
            self.rombank_selected = (((value & 0x1) << 8) | (self.rombank_selected & 0xFF)) % self.external_rom_count
        elif 0x4000 <= address < 0x6000:
            self.rambank_selected = (value & 0xF) % self.external_ram_count
        elif 0xA000 <= address < 0xC000:
            if self.rambank_enabled:
                self.rambanks[self.rambank_selected, address - 0xA000] = value
        else:
            logger.debug("Unexpected write to 0x%0.4x, value: 0x%0.2x", address, value)
