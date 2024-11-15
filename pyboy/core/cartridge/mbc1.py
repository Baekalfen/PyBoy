#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pyboy

from .base_mbc import BaseMBC

logger = pyboy.logging.get_logger(__name__)


class MBC1(BaseMBC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bank_select_register1 = 1
        self.bank_select_register2 = 0

    def setitem(self, address, value):
        if 0x0000 <= address < 0x2000:
            self.rambank_enabled = (value & 0b00001111) == 0b1010
        elif 0x2000 <= address < 0x4000:
            value &= 0b00011111
            # The register cannot contain zero (0b00000) and will be initialized as 0b00001
            # Attempting to write 0b00000 will write 0b00001 instead.
            if value == 0:
                value = 1
            self.bank_select_register1 = value
        elif 0x4000 <= address < 0x6000:
            self.bank_select_register2 = value & 0b11
        elif 0x6000 <= address < 0x8000:
            self.memorymodel = value & 0b1
        elif 0xA000 <= address < 0xC000:
            if self.rambank_enabled:
                self.rambank_selected = self.bank_select_register2 if self.memorymodel == 1 else 0
                self.rambanks[self.rambank_selected % self.external_ram_count, address - 0xA000] = value
        # else:
        #     logger.error("Invalid writing address: %0.4x", address)
        if self.memorymodel == 1:
            self.rombank_selected_low = (self.bank_select_register2 << 5) % self.external_rom_count
        else:
            self.rombank_selected_low = 0
        self.rombank_selected = (
            (self.bank_select_register2 << 5) | self.bank_select_register1
        ) % self.external_rom_count

    def getitem(self, address):
        if 0xA000 <= address < 0xC000:
            if not self.rambank_initialized:
                logger.error("RAM banks not initialized: %0.4x", address)

            if not self.rambank_enabled:
                return 0xFF

            if self.memorymodel == 1:
                self.rambank_selected = self.bank_select_register2 % self.external_ram_count
            else:
                self.rambank_selected = 0
            return self.rambanks[self.rambank_selected, address - 0xA000]
        # else:
        #     logger.error("Reading address invalid: %0.4x", address)

    def save_state(self, f):
        # Cython doesn't like super()
        BaseMBC.save_state(self, f)
        f.write(self.bank_select_register1)
        f.write(self.bank_select_register2)

    def load_state(self, f, state_version):
        # Cython doesn't like super()
        BaseMBC.load_state(self, f, state_version)
        if state_version >= 3:
            self.bank_select_register1 = f.read()
            self.bank_select_register2 = f.read()
        else:
            self.bank_select_register1 = self.rombank_selected & 0b00011111
            self.bank_select_register2 = (self.rombank_selected & 0b01100000) >> 5
            self.rambank_selected = self.bank_select_register2
