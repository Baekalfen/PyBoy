#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import array
import os

from ..logger import logger
from .rtc import RTC


class BaseMBC:
    def __init__(self, filename, rombanks, external_ram_count, carttype, sram, battery, rtc_enabled):
        self.filename = filename + ".ram"
        banks = len(rombanks)
        self.rombanks = [[0] * (16*1024) for _ in range(256)]
        for n in range(banks):
            self.rombanks[n][:] = rombanks[n]
        self.carttype = carttype

        self.battery = battery
        self.rtc_enabled = rtc_enabled

        if self.rtc_enabled:
            self.rtc = RTC(filename)

        self.rambank_initialized = False
        self.external_ram_count = external_ram_count
        self.init_rambanks(external_ram_count)
        self.gamename = self.getgamename(rombanks)

        self.memorymodel = 0
        self.rambank_enabled = False
        self.rambank_selected = 0 # TODO: Check this, not documented
        self.rombank_selected = 1 # TODO: Check this, not documented
        # Note: TestROM 01-special.gb assumes initial value of 1

        if not os.path.exists(self.filename):
            logger.info("No RAM file found. Skipping.")
        else:
            with open(self.filename, "rb") as f:
                self.load_ram(f)

    def stop(self):
        with open(self.filename, "wb") as f:
            self.save_ram(f)

        if self.rtc_enabled:
            self.rtc.stop()

    def save_state(self, f):
        f.write(self.rombank_selected.to_bytes(1, 'little'))
        f.write(self.rambank_selected.to_bytes(1, 'little'))
        f.write(self.rambank_enabled.to_bytes(1, 'little'))
        f.write(self.memorymodel.to_bytes(1, 'little'))
        self.save_ram(f)
        if self.rtc_enabled:
            self.rtc.save_state(f)

    def load_state(self, f):
        self.rombank_selected = ord(f.read(1))
        self.rambank_selected = ord(f.read(1))
        self.rambank_enabled = ord(f.read(1))
        self.memorymodel = ord(f.read(1))
        self.load_ram(f)
        if self.rtc_enabled:
            self.rtc.load_state(f)

    def save_ram(self, f):
        if not self.rambank_initialized:
            logger.info("Saving RAM is not supported on {}".format(self.carttype))
            return

        for bank in range(self.external_ram_count):
            for byte in range(8*1024):
                f.write(self.rambanks[bank][byte].to_bytes(1, "little"))

        logger.info("RAM saved.")

    def load_ram(self, f):
        if not self.rambank_initialized:
            logger.info("Loading RAM is not supported on {}".format(self.carttype))
            return

        for bank in range(self.external_ram_count):
            for byte in range(8*1024):
                self.rambanks[bank][byte] = ord(f.read(1))

        logger.info("RAM loaded.")

    def init_rambanks(self, n):
        if n is None:
            return

        self.rambank_initialized = True

        # In real life the values in RAM are scrambled on initialization.
        # Allocating the maximum, as it is easier with static array sizes. And it's just 128KB...
        self.rambanks = [array.array('B', [0] * (8*1024)) for _ in range(16)]

    def getgamename(self, rombanks):
        return "".join([chr(x) for x in rombanks[0][0x0134:0x0142]]).rstrip("\0")

    def setitem(self, address, value):
        raise Exception("Cannot set item in MBC")

    def getitem(self, address):
        if 0x0000 <= address < 0x4000:
            return self.rombanks[0][address]
        elif 0x4000 <= address < 0x8000:
            return self.rombanks[self.rombank_selected][address-0x4000]
        elif 0xA000 <= address < 0xC000:
            if not self.rambank_initialized:
                raise logger.error("RAM banks not initialized: %s" % hex(address))

            if self.rtc_enabled and 0x08 <= self.rambank_selected <= 0x0C:
                return self.rtc.getregister(self.rambank_selected)
            else:
                return self.rambanks[self.rambank_selected][address-0xA000]
        else:
            raise logger.error("Reading address invalid: %s" % address)

    def __str__(self):
        return "\n".join([
            "Cartridge:",
            "Filename: %s" % self.filename,
            "Game name: %s" % self.gamename,
            "GB Color: %s" % str(self.ROMBanks[0][0x143] == 0x80),
            "Cartridge type: %s" % hex(self.cartType),
            "Number of ROM banks: %s" % len(self.rombanks),
            "Active ROM bank: %s" % self.rombank_selected,
            # "Memory bank type: %s" % self.ROMBankController,
            "Number of RAM banks: %s" % len(self.rambanks),
            "Active RAM bank: %s" % self.rambank_selected,
            "Battery: %s" % self.battery,
            "RTC: %s" % self.rtc])


class ROMOnly(BaseMBC):
    def setitem(self, address, value):
        if 0x2000 <= address < 0x4000:
            if value == 0:
                value = 1
            self.rombank_selected = (value & 0b1)
            logger.info("Switching bank 0x%0.4x, 0x%0.2x" % (address, value))
        elif 0xA000 <= address < 0xC000:
            if self.rambanks is None:
                from . import EXTERNAL_RAM_TABLE
                logger.warning("Game tries to set value 0x%0.2x at RAM address 0x%0.4x, but "
                               "RAM banks are not initialized. Initializing %d RAM banks as "
                               "precaution" % (value, address, EXTERNAL_RAM_TABLE[0x02]))
                self.init_rambanks(EXTERNAL_RAM_TABLE[0x02])
            self.rambanks[self.rambank_selected][address-0xA000] = value
        else:
            logger.warning("Unexpected write to 0x%0.4x, value: 0x%0.2x" % (address, value))
