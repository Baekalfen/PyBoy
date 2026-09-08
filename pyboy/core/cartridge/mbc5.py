#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pyboy

from .base_mbc import BaseMBC

logger = pyboy.logging.get_logger(__name__)


class MBC5(BaseMBC):
    # Rumble cartridge types from Pan Docs
    RUMBLE_CARTRIDGE_TYPES = {0x1C, 0x1D, 0x1E}

    def __init__(self, rombanks, ram_file, rtc_file, external_ram_count, carttype, sram, battery, rtc_enabled):
        super().__init__(rombanks, ram_file, rtc_file, external_ram_count, carttype, sram, battery, rtc_enabled)

        # Rumble pack support detection
        self.rumble_supported = carttype in self.RUMBLE_CARTRIDGE_TYPES
        self.rumble_enabled = False

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
            # RAM bank select + rumble control (bit 3)
            self.rambank_selected = (value & 0xF) % self.external_ram_count
            # Bit 3 controls rumble motor (if rumble is supported)
            if self.rumble_supported:
                self.rumble_enabled = value & 0x08
        elif 0xA000 <= address < 0xC000:
            if self.rambank_enabled:
                self.rambanks[self.rambank_selected, address - 0xA000] = value
        else:
            logger.debug("Unexpected write to 0x%0.4x, value: 0x%0.2x", address, value)

    def save_state(self, f):
        """Save MBC5 state including rumble support"""
        BaseMBC.save_state(self, f)
        # Save rumble state only if rumble is supported
        f.write(self.rumble_supported)
        if self.rumble_supported:
            f.write(self.rumble_enabled)

    def load_state(self, f, state_version):
        """Load MBC5 state including rumble support"""
        BaseMBC.load_state(self, f, state_version)
        # Load rumble state
        self.rumble_supported = f.read()
        if self.rumble_supported:
            self.rumble_enabled = f.read()
        else:
            # For cartridges that don't support rumble, ensure it's disabled
            self.rumble_enabled = False
