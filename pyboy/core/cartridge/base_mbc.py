#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import array
import os

import pyboy
from pyboy.utils import IntIOWrapper, PyBoyException, PyBoyInvalidInputException

from .rtc import RTC

logger = pyboy.logging.get_logger(__name__)


class BaseMBC:
    def __init__(self, filename, rombanks, external_ram_count, carttype, sram, battery, rtc_enabled):
        self.filename = filename + ".ram"
        self.rombanks = rombanks
        self.carttype = carttype

        self.battery = battery
        self.rtc_enabled = rtc_enabled

        if self.rtc_enabled:
            self.rtc = RTC(filename)
        else:
            self.rtc = None

        self.rambank_initialized = False
        self.external_rom_count = len(rombanks)
        self.external_ram_count = external_ram_count
        self.init_rambanks(external_ram_count)

        # CGB flag overlaps with earlier game titles
        self.cgb = bool(self.rombanks[0, 0x0143] >> 7)
        self.gamename = self.getgamename(rombanks)

        self.memorymodel = 0
        self.rambank_enabled = False
        self.rambank_selected = 0
        self.rombank_selected = 1
        self.rombank_selected_low = 0

        if not os.path.exists(self.filename):
            logger.debug("No RAM file found. Skipping.")
        else:
            with open(self.filename, "rb") as f:
                self.load_ram(IntIOWrapper(f))

    def stop(self):
        with open(self.filename, "wb") as f:
            self.save_ram(IntIOWrapper(f))

        if self.rtc_enabled:
            self.rtc.stop()

    def save_state(self, f):
        f.write(self.rombank_selected)
        f.write(self.rambank_selected)
        f.write(self.rambank_enabled)
        f.write(self.memorymodel)
        self.save_ram(f)
        if self.rtc_enabled:
            self.rtc.save_state(f)

    def load_state(self, f, state_version):
        self.rombank_selected = f.read()
        self.rambank_selected = f.read()
        self.rambank_enabled = f.read()
        self.memorymodel = f.read()
        self.load_ram(f)
        if self.rtc_enabled:
            self.rtc.load_state(f, state_version)

    def save_ram(self, f):
        if not self.rambank_initialized:
            logger.warning("Saving RAM is not supported on %0.2x", self.carttype)
            return 0

        for bank in range(self.external_ram_count):
            for byte in range(8 * 1024):
                f.write(self.rambanks[bank, byte])

        logger.debug("RAM saved.")

    def load_ram(self, f):
        if not self.rambank_initialized:
            logger.warning("Loading RAM is not supported on %0.2x", self.carttype)
            return 0

        for bank in range(self.external_ram_count):
            for byte in range(8 * 1024):
                self.rambanks[bank, byte] = f.read()

        logger.debug("RAM loaded.")

    def init_rambanks(self, n):
        self.rambank_initialized = True
        # In real life the values in RAM are scrambled on initialization.
        # Allocating the maximum, as it is easier in Cython. And it's just 128KB...
        self.rambanks = memoryview(array.array("B", [0] * (8 * 1024 * 16))).cast("B", shape=(16, 8 * 1024))

    def getgamename(self, rombanks):
        # Title was originally 0x134-0x143.
        # Later 0x13F-0x142 became manufacturer code and 0x143 became a CGB flag
        if self.cgb:
            end = 0x0142  # Including manufacturer code
            # end = 0x013F # Excluding potential(?) manufacturer code
        else:
            end = 0x0143
        return "".join([chr(rombanks[0, x]) for x in range(0x0134, end)]).split("\0")[0]

    def setitem(self, address, value):
        raise PyBoyException("Cannot set item in MBC")

    def overrideitem(self, rom_bank, address, value):
        if 0x0000 <= address < 0x4000:
            logger.debug(
                "Performing overwrite on address: 0x%04x:0x%04x. New value: 0x%04x Old value: 0x%04x",
                rom_bank,
                address,
                value,
                self.rombanks[rom_bank, address],
            )
            self.rombanks[rom_bank, address] = value
        else:
            raise PyBoyInvalidInputException("Invalid override address: %0.4x", address)

    def getitem(self, address):
        if 0xA000 <= address < 0xC000:
            # if not self.rambank_initialized:
            #     logger.error("RAM banks not initialized: 0.4x", address)

            if not self.rambank_enabled:
                return 0xFF

            if self.rtc_enabled and 0x08 <= self.rambank_selected <= 0x0C:
                return self.rtc.getregister(self.rambank_selected)
            else:
                return self.rambanks[self.rambank_selected, address - 0xA000]
        # else:
        #     logger.error("Reading address invalid: %0.4x", address)

    def __repr__(self):
        return "\n".join(
            [
                "MBC class: %s" % self.__class__.__name__,
                "Filename: %s" % self.filename,
                "Game name: %s" % self.gamename,
                "GB Color: %s" % str(self.rombanks[0, 0x143] == 0x80),
                "Cartridge type: %s" % hex(self.carttype),
                "Number of ROM banks: %s" % self.external_rom_count,
                "Active ROM bank: %s" % self.rombank_selected,
                # "Memory bank type: %s" % self.ROMBankController,
                "Number of RAM banks: %s" % len(self.rambanks),
                "Active RAM bank: %s" % self.rambank_selected,
                "Battery: %s" % self.battery,
                "RTC: %s" % self.rtc_enabled,
            ]
        )


class ROMOnly(BaseMBC):
    def setitem(self, address, value):
        if 0x2000 <= address < 0x4000:
            if value == 0:
                value = 1
            self.rombank_selected = value & 0b1
            logger.debug("Switching bank 0x%0.4x, 0x%0.2x", address, value)
        elif 0xA000 <= address < 0xC000:
            self.rambanks[self.rambank_selected, address - 0xA000] = value
        # else:
        #     logger.debug("Unexpected write to 0x%0.4x, value: 0x%0.2x", address, value)
