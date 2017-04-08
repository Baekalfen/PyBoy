# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import CoreDump
import os
import time
import struct


def Cartridge(logger, filename):
    ROMBanks = loadROMfile(filename)
    cartType = ROMBanks[0][0x0147]
    logger(hex(ROMBanks[0][0x0146]), hex(ROMBanks[0][0x0148]))
    logger("Cartridge type:", hex(cartType))
    # ROMSize = ROMBanks[0][0x0148]
    # WARN: The following table doesn't work for MBC2! See Pan Docs
    exRAMCount = ExRAMTable[ROMBanks[0][0x0149]]

    validateCartType(cartType)
    ROMBankController = cartridgeTable[cartType][0]

    return ROMBankController(logger, filename, ROMBanks, exRAMCount, cartType)


def loadROMfile(filename):
    with open(filename, 'rb') as ROMFile:
        ROMData = ROMFile.read()

        bankSize = (16 * 1024)
        ROMBanks = [[0] * bankSize for n in xrange(len(ROMData) / bankSize)]

        for i, byte in enumerate(ROMData):
            ROMBanks[i / bankSize][i % bankSize] = ord(byte)

    return ROMBanks


def validateCartType(cartType):
    try:
        cartridgeInfo = cartridgeTable[cartType]
    except KeyError:
        raise Exception("Catridge type invalid: %s" % cartType)

    if cartridgeInfo is None:
        raise Exception("Cartridge type not supported")


class GenericMBC:
    def __init__(self, logger, filename, ROMBanks, exRAMCount, cartType):
        self.logger = logger
        self.filename = filename  # For debugging and saving
        self.ROMBanks = ROMBanks
        self.cartType = cartType

        (self.ROMBankController,
         _, # True/False if cartridge RAM is present
         self.battery,
         self.rtcEnabled) = cartridgeTable[self.cartType]

        if self.rtcEnabled:
            self.rtc = RTC(logger)

        self.initRAMBanks(exRAMCount)
        self.gameName = self.getGameName(ROMBanks)

        self.memoryModel = 0
        # self.RAMRange = (0xA000, 0xC000)
        self.RAMBankEnabled = False
        self.RAMBankSelected = 0  # TODO: Check this, not documented
        self.ROMBankSelected = 1  # TODO: Check this, not documented #NOTE: TestROM 01-special.gb
                                  # assumes initial value of 1

    def saveRAM(self, filename = None):
        if self.RAMBanks is None:
            self.logger("Saving non-volatile memory is not supported on %s" % self.ROMBankController)
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
            self.logger("Loading non-volatile memory is not supported on %s" % self.ROMBankController)
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
            return None

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
        string += "Memory bank type: %s\n" % self.ROMBankController
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


class MBC1(GenericMBC):
    def __setitem__(self, address, value):
        if 0x0000 <= address < 0x2000:
            if (value & 0b00001111) == 0b1010:
                self.RAMBankEnabled = True
            else:
                self.RAMBankEnabled = False
        elif 0x2000 <= address < 0x4000:
            # But (when using the register below to specify the upper ROM Bank bits), the same
            # happens for Bank 20h, 40h, and 60h. Any attempt to address these ROM Banks will select
            # Bank 21h, 41h, and 61h instead
            if value == 0:
                value = 1

            # sets 5LSB of ROM bank address
            self.ROMBankSelected = (self.ROMBankSelected & 0b11100000) | (value & 0b00011111)
        elif 0x4000 <= address < 0x6000:
            # NOTE: 16mbit = 2MB. 2MB/(8KB banks) = 128 banks. 128 is
            # addressable with 7 bits
            if self.memoryModel == 0:  # 16/8 mode
                # sets 2MSB of ROM bank address
                self.ROMBankSelected = (self.ROMBankSelected & 0b00011111) | ((address & 0b11) << 5)

            # NOTE: 4mbit = 0.5MB. 0.5MB/(8KB banks) = 32 banks. 32 is
            # addressably with 5 bits
            elif self.memoryModel == 1:  # 4/32 mode
                self.RAMBankSelected = value & 0b00000011
            else:
                raise CoreDump.CoreDump("Invalid memoryModel: %s" % self.memoryModel)
        elif 0x6000 <= address < 0x8000:
            self.memoryModel = value & 0x1
        elif 0xA000 <= address < 0xC000:
            self.RAMBanks[self.RAMBankSelected][address - 0xA000] = value
        else:
            raise CoreDump.CoreDump("Invalid writing address: %s" % hex(address))


class MBC2(GenericMBC):
    def __setitem__(self, address, value):
        raise Exception("Not implemented")

class RTC():
    def __init__(self, logger):
        self.logger = logger
        self.latchEnabled = False

        self.timeZero = time.time()

        self.secLatch = 0
        self.minLatch = 0
        self.hourLatch = 0
        self.dayLatchLow = 0

        self.dayLatchHigh = 0
        self.dayCarry = 0
        self.halt = 0

    def save(self, filename):
        self.logger("Saving RTC...")
        romPath, ext = os.path.splitext(filename)
        with open(romPath + ".rtc", "wb") as f:
            f.write(struct.pack('f', self.timeZero))
            f.write(chr(self.halt))
            f.write(chr(self.dayCarry))
        self.logger("RTC saved.")

    def load(self, filename):
        self.logger("Loading RTC...")
        try:
            romPath, ext = os.path.splitext(filename)
            with open(romPath + ".rtc", "rb") as f:
                # import pdb; pdb.set_trace()
                self.timeZero = struct.unpack('f',f.read(4))[0]
                self.halt = ord(f.read(1))
                self.dayCarry = ord(f.read(1))
            self.logger("RTC loaded.")
        except Exception as ex:
            self.logger("Couldn't read RTC for cartridge:", ex)

    def latchRTC(self):
        t = time.time() - self.timeZero
        self.secLatch = int(t % 60)
        self.minLatch = int(t / 60 % 60)
        self.hourLatch = int(t / 3600 % 24)
        days = int(t / 3600 / 24)
        self.dayLatchLow = days & 0xFF
        self.dayLatchHigh = days >> 8

        if self.dayLatchHigh > 1:
            self.dayCarry = 1
            self.dayLatchHigh &= 0b1
            self.timeZero += 0x200 * 3600 * 24 # Add 0x200 (512) days to "reset" the day counter to zero

    def writeCommand(self, value):
        if value == 0x00:
            self.latchEnabled = False
        elif value == 0x01:
            if not self.latchEnabled:
                self.latchRTC()
            self.latchEnabled = True
        else:
            raise CoreDump.CoreDump("Invalid RTC command: %s" % hex(value))

    def getRegister(self, register):
        if not self.latchEnabled:
            self.logger("RTC: Get register, but nothing is latched!", register, value)

        if register == 0x08:
            return self.secLatch
        elif register == 0x09:
            return self.minLatch
        elif register == 0x0A:
            return self.hourLatch
        elif register == 0x0B:
            return self.dayLatchLow
        elif register == 0x0C:
            dayHigh = self.dayLatchHigh & 0b1
            halt = self.halt << 6
            dayCarry = self.dayCarry << 7
            return dayHigh + halt + dayCarry
        else:
            raise CoreDump.CoreDump("Invalid RTC register: %s" % hex(register))

    def setRegister(self, register, value):
        if not self.latchEnabled:
            self.logger("RTC: Set register, but nothing is latched!", register, value)

        t = time.time() - self.timeZero
        if register == 0x08:
            self.timeZero -= int(t % 60) - value # TODO: What happens, when these value are larger than allowed?
        elif register == 0x09:
            self.timeZero -= int(t / 60 % 60) - value
        elif register == 0x0A:
            self.timeZero -= int(t / 3600 % 24) - value
        elif register == 0x0B:
            self.timeZero -= int(t / 3600 / 24) - value
        elif register == 0x0C:
            dayHigh = value & 0b1
            halt = (value & 0b1000000) >> 6
            dayCarry = (value & 0b10000000) >> 7

            self.halt = halt
            if self.halt == 0:
                pass # TODO: Start the timer
            else:
                raise CoreDump.CoreDump("Stopping RTC is not implemented!")

            self.timeZero -= int(t / 3600 / 24) - (dayHigh<<8)
            self.dayCarry = dayCarry
        else:
            raise CoreDump.CoreDump("Invalid RTC register: %s" % hex(register))

class MBC3(GenericMBC):
    def __setitem__(self, address, value):
        if 0x0000 <= address < 0x2000:
            if (value & 0b00001111) == 0b1010:
                self.RAMBankEnabled = True
            elif value == 0:
                self.RAMBankEnabled = False
            else:
                raise CoreDump.CoreDump("Invalid command for MBC: Address: %s, Value: %s" % (hex(address), hex(value)))

        elif 0x2000 <= address < 0x4000:
            if value == 0:
                value = 1
            # Same as for MBC1, except that the whole 7 bits of the RAM Bank Number are written
            # directly to this address
            self.ROMBankSelected = value & 0b01111111  # sets 7LSB of ROM bank address
        elif 0x4000 <= address < 0x6000:
            # MBC3 is always 16/8 mode
            self.RAMBankSelected = value # TODO: Should this has a mask?
        elif 0x6000 <= address < 0x8000:
            if self.rtcEnabled:
                self.rtc.writeCommand(value)
            else:
                # NOTE: Pokemon Red/Blue will do this, but it can safely be ignored:
                # https://github.com/pret/pokered/issues/155
                self.logger("RTC not present. Game tried to issue RTC command:", hex(address), hex(value))
        elif 0xA000 <= address < 0xC000:
            if self.RAMBankSelected <= 0x03:
                self.RAMBanks[self.RAMBankSelected][address - 0xA000] = value
            elif 0x08 <= self.RAMBankSelected <= 0x0C:
                self.rtc.setRegister(self.RAMBankSelected, value)
            else:
                raise CoreDump.CoreDump("Invalid RAM bank selected: %s" % hex(self.RAMBankSelected))
        else:
            raise CoreDump.CoreDump("Invalid writing address: %s" % hex(address))


class MBC5(GenericMBC):
    def __setitem__(self, address, value):
        raise Exception("Not implemented")



cartridgeTable = {
#          cart     , SRAM  , Battery , RTC
    0x00: (ROM_only , False , False   , False) , # ROM
    0x01: (MBC1     , False , False   , False) , # MBC1
    0x02: (MBC1     , True  , False   , False) , # MBC1+RAM
    0x03: (MBC1     , True  , True    , False) , # MBC1+RAM+BATT
    0x05: (MBC2     , False , False   , False) , # MBC2
    0x06: (MBC2     , False , True    , False) , # MBC2+BATTERY
    0x08: (ROM_only , True  , False   , False) , # ROM+RAM
    0x09: (ROM_only , True  , True    , False) , # ROM+RAM+BATTERY
    0x0F: (MBC3     , False , True    , True)  , # MBC3+TIMER+BATT
    0x10: (MBC3     , True  , True    , True)  , # MBC3+TIMER+RAM+BATT
    0x11: (MBC3     , False , False   , False) , # MBC3
    0x12: (MBC3     , True  , False   , False) , # MBC3+RAM
    0x13: (MBC3     , True  , True    , False) , # MBC3+RAM+BATT
    0x19: (MBC5     , False , False   , False) , # MBC5
    0x1A: (MBC5     , True  , False   , False) , # MBC5+RAM
    0x1B: (MBC5     , True  , True    , False) , # MBC5+RAM+BATT
}

# ROMTable = {}
ExRAMTable = {
    0x00 : None,
    0x02 : 1, # Number of 8KB banks
    0x03 : 4, # Number of 8KB banks
    0x04 : 16, # Number of 8KB banks
}
