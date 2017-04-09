# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import CoreDump
import os
from RTC import RTC

class GenericMBC:
    def __init__(self, logger, filename, ROMBanks, exRAMCount, cartType, SRAM  , battery , rtcEnabled):
        self.logger = logger
        self.filename = filename  # For debugging and saving
        self.ROMBanks = ROMBanks
        self.cartType = cartType

        # self.SRAM = SRAM
        self.battery = battery
        self.rtcEnabled = rtcEnabled

        if self.rtcEnabled:
            self.rtc = RTC(logger)


        self.RAMBanks = None
        self.initRAMBanks(exRAMCount)
        self.gameName = self.getGameName(ROMBanks)

        self.memoryModel = 0
        self.RAMBankEnabled = False
        self.RAMBankSelected = 0  # TODO: Check this, not documented
        self.ROMBankSelected = 1  # TODO: Check this, not documented #NOTE: TestROM 01-special.gb
                                  # assumes initial value of 1

    def saveRAM(self, filename = None):
        if self.RAMBanks is None:
            self.logger("Saving non-volatile memory is not supported on 0x%x" % self.cartType)
            return

        self.logger("Saving non-volatile memory")
        if filename is None:
            romPath, ext = os.path.splitext(self.filename)
        else:
            romPath = filename

        with open(romPath+".ram", "wb") as saveRAM:
            for bank in self.RAMBanks:
                for byte in bank:
                    saveRAM.write(chr(byte))

    def loadRAM(self, filename = None):
        if self.RAMBanks is None:
            self.logger("Loading non-volatile memory is not supported on 0x%x" % self.cartType)
            return

        if filename is None:
            romPath, ext = os.path.splitext(self.filename)
        else:
            romPath = filename

        if not os.path.exists(romPath+".ram"):
            self.logger("No RAM file found. Skipping load of non-volatile memory")
            return

        self.logger("Loading non-volatile memory")

        with open(romPath+".ram", "rb") as loadRAM:
            for bank in xrange(len(self.RAMBanks)):
                for byte in xrange(8*1024):
                    self.RAMBanks[bank][byte] = ord(loadRAM.read(1))

    def initRAMBanks(self, n):
        if n is None:
            return

        self.RAMBanks = []
        for n in range(n):
            # In real life the values in RAM are scrambled on initialization
            self.RAMBanks.append([0 for x in xrange(8 * 1024)])

    def getGameName(self, ROMBanks):
        return "".join([chr(x) for x in ROMBanks[0][0x0134:0x0142]]).rstrip("\0")

    def __getitem__(self, address):
        if 0x0000 <= address < 0x4000:
            return self.ROMBanks[0][address]
        elif 0x4000 <= address < 0x8000:
            return self.ROMBanks[self.ROMBankSelected][address - 0x4000]
        elif 0xA000 <= address < 0xC000:
            if not self.RAMBanks:
                raise CoreDump.CoreDump("RAMBanks not initialized: %s" % hex(address))

            if self.rtcEnabled and 0x08 <= self.RAMBankSelected <= 0x0C:
                return self.rtc.getRegister(self.RAMBankSelected)
            else:
                return self.RAMBanks[self.RAMBankSelected][address - 0xA000]
        else:
            raise CoreDump.CoreDump("Reading address invalid: %s" % address)

    def __getslice__(self, a, b):
        #TODO: Optimize this
        if b-a < 0:
            raise CoreDump.CoreDump("Negative slice not allowed")
        chunk = []
        for n in xrange(b-a):
            chunk.append(self.__getitem__(a+n))
        return chunk

    def __str__(self):
        string = "Cartridge:\n"
        string += "Filename: %s\n" % self.filename
        # Defined constant
        string += "Game name: %s\n" % self.gameName
        string += "GB Color: %s\n" % str(self.ROMBanks[0][0x143] == 0x80)
        string += "Cartridge type: %s\n" % hex(self.cartType)
        string += "Number of ROM banks: %s\n" % len(self.ROMBanks)
        string += "Active ROM bank: %s\n" % self.ROMBankSelected
        # string += "Memory bank type: %s\n" % self.ROMBankController
        string += "Number of RAM banks: %s\n" % len(self.RAMBanks)
        string += "Active RAM bank: %s\n" % self.RAMBankSelected
        string += "Battery: %s\n" % self.battery
        string += "RTC: %s\n" % self.RTC
        return string


class ROM_only(GenericMBC):
    def __setitem__(self, address, value):
        if 0x2000 <= address < 0x4000:
            if value == 0:
                value = 1
            self.ROMBankSelected = (value & 0b1)
            self.logger("Switching bank", hex(address), hex(value))
        else:
            raise CoreDump.CoreDump("Invalid writing address: %s" % hex(address))
