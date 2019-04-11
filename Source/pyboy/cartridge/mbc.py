#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import array
import os

from .rtc import RTC
from ..logger import logger


class MBC:
    def __init__(self, filename, rombanks, exramcount, carttype, sram, battery, rtcenabled):
        self.filename = filename + ".ram"
        banks = len(rombanks)
        self.rombanks = [[0] * (16 * 1024) for _ in range(256)]
        for n in range(banks):
            self.rombanks[n][:] = rombanks[n]
        self.carttype = carttype

        self.battery = battery
        self.rtcenabled = rtcenabled

        if self.rtcenabled:
            self.rtc = RTC(filename)

        self.rambanksinitialized = False
        self.exramcount = exramcount
        self.initrambanks(exramcount)
        self.gamename = self.getgamename(rombanks)

        self.memorymodel = 0
        self.rambankenabled = False
        self.rambankselected = 0  # TODO: Check this, not documented
        self.rombankselected = 1  # TODO: Check this, not documented
        # Note: TestROM 01-special.gb assumes initial value of 1

        if not os.path.exists(self.filename):
            logger.info("No RAM file found. Skipping.")
        else:
            with open(self.filename, "rb") as f:
                self.load_ram(f)

    def stop(self):
        with open(self.filename, "wb") as f:
            self.save_ram(f)

        if self.rtcenabled:
            self.rtc.stop()

    def save_state(self, f):
        f.write(self.rombankselected.to_bytes(1, 'little'))
        f.write(self.rambankselected.to_bytes(1, 'little'))
        f.write(self.rambankenabled.to_bytes(1, 'little'))
        f.write(self.memorymodel.to_bytes(1, 'little'))
        self.save_ram(f)
        if self.rtcEnabled:
            self.rtc.saveState(f)

    def load_state(self, f):
        self.rombankselected = ord(f.read(1))
        self.rambankselected = ord(f.read(1))
        self.rambankenabled = ord(f.read(1))
        self.memorymodel = ord(f.read(1))
        self.load_ram(f)
        if self.rtcenabled:
            self.rtc.load_state(f)

    def save_ram(self, f):
        if not self.rambanksinitialized:
            logger.info("Saving RAM is not supported on {}".format(self.carttype))
            return

        for bank in range(self.exramcount):
            for byte in range(8*1024):
                f.write(self.rambanks[bank][byte].to_bytes(1, "little"))

        logger.info("RAM saved.")

    def load_ram(self, f):
        if not self.rambanksinitialized:
            logger.info("Loading RAM is not supported on {}".format(self.carttype))
            return

        for bank in range(self.exramcount):
            for byte in range(8*1024):
                self.rambanks[bank][byte] = ord(f.read(1))

        logger.info("RAM loaded.")

    def initrambanks(self, n):
        if n is None:
            return

        self.rambanksinitialized = True

        # In real life the values in RAM are scrambled on
        # initialization.
        # Allocating the maximum, as it is easier with
        # static array sizes. And it's just 128KB...
        self.rambanks = [array.array('B', [0] * (8 * 1024)) for _ in range(16)]
        # Trying to do CPython a favor with static arrays, although not 2D

    def getgamename(self, rombanks):
        return "".join([chr(x) for x in rombanks[0][0x0134:0x0142]]).rstrip("\0")

    def setitem(self, address, value):
        raise Exception("Cannot set item in MBC")

    def getitem(self, address):
        if 0x0000 <= address < 0x4000:
            return self.rombanks[0][address]
        elif 0x4000 <= address < 0x8000:
            return self.rombanks[self.rombankselected][address-0x4000]
        elif 0xA000 <= address < 0xC000:
            if not self.rambanksinitialized:
                raise logger.error("RAM banks not initialized: %s" % hex(address))

            if self.rtcenabled and 0x08 <= self.rambankselected <= 0x0C:
                return self.rtc.getregister(self.rambankselected)
            else:
                return self.rambanks[self.rambankselected][address - 0xA000]
        else:
            raise logger.error("Reading address invalid: %s" % address)

    def __str__(self):
        return "\n".join([
            "Cartridge:",
            "Filename: %s" % self.filename,
            "Game name: %s" % self.gameName,
            "GB Color: %s" % str(self.ROMBanks[0][0x143] == 0x80),
            "Cartridge type: %s" % hex(self.cartType),
            "Number of ROM banks: %s" % len(self.ROMBanks),
            "Active ROM bank: %s" % self.ROMBankSelected,
            # "Memory bank type: %s" % self.ROMBankController,
            "Number of RAM banks: %s" % len(self.RAMBanks),
            "Active RAM bank: %s" % self.RAMBankSelected,
            "Battery: %s" % self.battery,
            "RTC: %s" % self.RTC])


class ROM(MBC):
    def setitem(self, address, value):
        if 0x2000 <= address < 0x4000:
            if value == 0:
                value = 1
            self.rombankselected = (value & 0b1)
            logger.info("Switching bank 0x%0.4x, 0x%0.2x" % (address, value))
        elif 0xA000 <= address < 0xC000:
            if self.RAMBanks is None:
                from . import EXRAMTABLE
                logger.warning("Game tries to set value 0x%0.2x at RAM address 0x%0.4x, but "
                               "RAM banks are not initialized. Initializing %d RAM banks as "
                               "precaution" % (value, address, EXRAMTABLE[0x02]))
                self.initrambanks(EXRAMTABLE[0x02])
            self.rambanks[self.rambankselected][address-0xA000] = value
        else:
            logger.warning("Unexpected write to 0x%0.4x, value: 0x%0.2x" % (address, value))
