#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import logging

from .base_mbc import BaseMBC

logger = logging.getLogger(__name__)


class MBC2(BaseMBC):
    def setitem(self, address, value):
        if 0x0000 <= address < 0x4000:
            value &= 0b00001111
            if ((address & 0x100) == 0):
                self.rambank_enabled = (value == 0b00001010)
            else:
                if value == 0:
                    value = 1
                self.rombank_selected = value
        elif 0xA000 <= address < 0xC000:
            if self.rambanks is None:
                logger.warning(
                    f"Game tries to set value 0x{value:02x} at RAM address 0x{address:04x}, but RAM "
                    f"banks are not initialized. Initializing {self.external_ram_count} RAM banks as precaution"
                )
                self.init_rambanks(self.external_ram_count)
            if self.rambank_enabled:
                # MBC2 includes built-in RAM of 512 x 4 bits (Only the 4 LSBs are used)
                self.rambanks[0][address % 512] = value | 0b11110000
        else:
            logger.error(f"Unexpected write to 0x{address:04x}, value: 0x{value:02x}")

    def getitem(self, address):
        if 0x0000 <= address < 0x4000:
            return self.rombanks[0][address]
        elif 0x4000 <= address < 0x8000:
            return self.rombanks[self.rombank_selected % len(self.rombanks)][address - 0x4000]
        elif 0xA000 <= address < 0xC000:
            if not self.rambank_initialized:
                logger.error(f"RAM banks not initialized: {address:04x}")

            if not self.rambank_enabled:
                return 0xFF

            else:
                return self.rambanks[0][address % 512] | 0b11110000
        else:
            logger.error(f"Reading address invalid: {address:04x}")
