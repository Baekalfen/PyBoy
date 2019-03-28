# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from .. import CoreDump
import array
import os
from RTC import RTC
from ..Logger import logger
from .. import Global
import cython

class GenericMBC:
    def __init__(self, filename, ROMBanks, exRAMCount, cartType, SRAM, battery, rtcEnabled):
        self.filename = filename + ".ram"
        banks = ROMBanks.shape[0]
        self.ROMBanks = [[0] * (16 * 1024) for _ in range(256)]
        for n in range(banks):
            self.ROMBanks[n][:] = ROMBanks[n]
        # self.ROMBanks = ROMBanks
        self.cartType = cartType

        # self.SRAM = SRAM
        self.battery = battery
        self.rtcEnabled = rtcEnabled

        if self.rtcEnabled:
            self.rtc = RTC(filename)


        # self.RAMBanks = None
        self.RAMBanksInitialized = False
        self.exRAMCount = exRAMCount
        self.initRAMBanks(exRAMCount)
        self.gameName = self.getGameName(ROMBanks)

        self.memoryModel = 0
        self.RAMBankEnabled = False
        self.RAMBankSelected = 0  # TODO: Check this, not documented
        self.ROMBankSelected = 1  # TODO: Check this, not documented #NOTE: TestROM 01-special.gb
                                  # assumes initial value of 1

        if not os.path.exists(self.filename):
            logger.info("No RAM file found. Skipping.")
        else:
            with open(self.filename, "rb") as f:
                self.loadRAM(f)

    def stop(self):
        with open(self.filename, "wb") as f:
            self.saveRAM(f)

        if self.rtcEnabled:
            self.rtc.stop()

    def saveState(self, f):
        f.write(chr(self.ROMBankSelected))
        f.write(chr(self.RAMBankSelected))
        f.write(chr(self.RAMBankEnabled))
        f.write(chr(self.memoryModel))
        self.saveRAM(f)
        if self.rtcEnabled:
            self.rtc.saveState(f)

    def loadState(self, f):
        self.ROMBankSelected = ord(f.read(1))
        self.RAMBankSelected = ord(f.read(1))
        self.RAMBankEnabled = ord(f.read(1))
        self.memoryModel = ord(f.read(1))
        self.loadRAM(f)
        if self.rtcEnabled:
            self.rtc.loadState(f)

    def saveRAM(self, f):
        if not self.RAMBanksInitialized:
            logger.info("Saving RAM is not supported on {}".format(self.cartType))
            return

        for bank in xrange(self.exRAMCount):
            for byte in xrange(8*1024):
                f.write(chr(self.RAMBanks[bank][byte]))

        logger.info("RAM saved.")

    def loadRAM(self, f):
        if not self.RAMBanksInitialized:
            logger.info("Loading RAM is not supported on {}".format(self.cartType))
            return

        for bank in xrange(self.exRAMCount):
            for byte in xrange(8*1024):
                self.RAMBanks[bank][byte] = ord(f.read(1))

        logger.info("RAM loaded.")

    def initRAMBanks(self, n):
        if n is None:
            return

        self.RAMBanksInitialized = True

        # In real life the values in RAM are scrambled on initialization
        # Allocating the maximum, as it is easier with static array sizes. And it's just 128KB...
        self.RAMBanks = [array.array('B', [0] * (8 * 1024)) for _ in range(16)] # Trying to do CPython a favor with static arrays, although not 2D

    def getGameName(self, ROMBanks):
        return unicode("".join([chr(x) for x in ROMBanks[0][0x0134:0x0142]]).rstrip("\0"))


    def setitem(self, address, value):
        raise Exception("Cannot set item in GenericMBC")

    # @cython.locals(address=cython.ushort)
    # def __getitem__(self, address):
    def getitem(self, address):
        if 0x0000 <= address < 0x4000:
            return self.ROMBanks[0][address]
        elif 0x4000 <= address < 0x8000:
            return self.ROMBanks[self.ROMBankSelected][address - 0x4000]
        elif 0xA000 <= address < 0xC000:
            if not self.RAMBanksInitialized:
                raise CoreDump.CoreDump("RAM banks not initialized: %s" % hex(address))

            if self.rtcEnabled and 0x08 <= self.RAMBankSelected <= 0x0C:
                return self.rtc.getRegister(self.RAMBankSelected)
            else:
                return self.RAMBanks[self.RAMBankSelected][address - 0xA000]
        else:
            raise CoreDump.CoreDump("Reading address invalid: %s" % address)

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
    def setitem(self, address, value):
        if 0x2000 <= address < 0x4000:
            if value == 0:
                value = 1
            self.ROMBankSelected = (value & 0b1)
            logger.info("Switching bank 0x%0.4x, 0x%0.2x" % (address, value))
        elif 0xA000 <= address < 0xC000:
            if self.RAMBanks == None:
                from . import ExRAMTable
                logger.warn("Game tries to set value 0x%0.2x at RAM address 0x%0.4x, but RAM banks are not initialized. Initializing %d RAM banks as precaution" % (value, address, ExRAMTable[0x02]))
                self.initRAMBanks(ExRAMTable[0x02])
            self.RAMBanks[self.RAMBankSelected][address - 0xA000] = value
        else:
            logger.warn("Unexpected write to 0x%0.4x, value: 0x%0.2x" % (address, value))
        #     raise CoreDump.CoreDump("Invalid writing address: 0x%0.4x, value: 0x%0.2x" % (address, value))


