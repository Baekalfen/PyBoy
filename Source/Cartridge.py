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

#                cart,  ROM,        RAM,   RAMbanks,  batt,   RTC
cartridgeTable = {0x00: ("ROM-only",  None,        1, False, False),  # ROM

                  0x01: ("MBC1",      None,        1, False, False),  # ROM+MBC1
                  0x02: ("MBC1",     "RAM",        4, False, False),  # ROM+MBC1+RAM
                  0x03: ("MBC1",     "RAM",        4,  True, False),  # ROM+MBC1+RAM+BATT

                  0x05: ("MBC2",      None,     None, False, False),  # ROM+MBC2
                  0x06: ("MBC2",      None,     None,  True, False),  # ROM+MBC2+BATTERY

                  0x08: ("RAM",      "RAM",     None, False, False),  # ROM+RAM
                  0x09: ("RAM",      "RAM",     None,  True, False),  # ROM+RAM+BATTERY

                  0x0B: None,                                         # ROM+MMM01
                  0x0C: None,                                         # ROM+MMM01+SRAM
                  0x0D: None,                                         # ROM+MMM01+SRAM+BATT

                  # Pan docs seems to be wrong. All MBC3's should have RTC according to the official programmers guide
                  0x0F: ("MBC3",      None,        4,  True,  True),  # ROM+MBC3+TIMER+BATT
                  0x10: ("MBC3",     "RAM",        4,  True,  True),  # ROM+MBC3+TIMER+RAM+BATT
                  0x11: ("MBC3",      None,        4, False,  True),  # ROM+MBC3
                  0x12: ("MBC3",     "RAM",        4, False,  True),  # ROM+MBC3+RAM
                  0x13: ("MBC3",     "RAM",        4, False,  True),  # ROM+MBC3+RAM+BATT

                  0x19: ("MBC5",      None,     None, False, False),  # ROM+MBC5
                  0x1A: ("MBC5",     "RAM",     None, False, False),  # ROM+MBC5+RAM
                  0x1B: ("MBC5",     "RAM",     None,  True, False),  # ROM+MBC5+RAM+BATT
                  0x1C: ("MBC5",      None,     None, False, False),  # ROM+MBC5+RUMBLE
                  0x1D: ("MBC5",     "SRAM",    None, False, False),  # ROM+MBC5+RUMBLE+SRAM
                  0x1E: ("MBC5",     "SRAM",    None,  True, False),  # ROM+MBC5+RUMBLE+SRAM+BATT
                  0x1F: None,                                         # Pocket Camera
                  0xFD: None,                                         # Bandai TAMA5/FE Hudson HuC-3
                  0xFF: None}                                         # Hudson HuC-1


def Cartridge(logger, filename):
    ROMBanks = loadROMfile(filename)
    cartType = ROMBanks[0][0x0147]

    validateCartType(cartType)
    ROMBankController = cartridgeTable[cartType][0]

    if ROMBankController == "ROM-only":
        return ROM_only(logger, filename, ROMBanks, cartType)
    elif ROMBankController == "MBC1":
        return MBC1(logger, filename, ROMBanks, cartType)
    elif ROMBankController == "MBC2":
        return MBC2(logger, filename, ROMBanks, cartType)
    elif ROMBankController == "MBC3":
        return MBC3(logger, filename, ROMBanks, cartType)
    elif ROMBankController == "MBC5":
        return MBC5(logger, filename, ROMBanks, cartType)
    else:
        raise CoreDump.CoreDump("Memory bank invalid: %s" % str(ROMBankController))


def loadROMfile(filename):
    with open(filename, 'rb') as ROMFile:
        ROMData = ROMFile.read()

        ROMBanks = [[0] * (16 * 1024) for n in xrange(len(ROMData) / (16 * 1024))]

        for i, byte in enumerate(ROMData):
            ROMBanks[i / (16 * 1024)][i % (16 * 1024)] = ord(byte)

    return ROMBanks


def validateCartType(cartType):
    try:
        cartridgeInfo = cartridgeTable[cartType]
    except KeyError:
        raise Exception("Catridge type invalid: %s" % cartType)

    if cartridgeInfo is None:
        raise Exception("Cartridge type not supported")


class GenericMBC:
    def __init__(self, logger, filename, ROMBanks, cartType):
        self.logger = logger
        self.filename = filename  # For debugging and saving
        self.ROMBanks = ROMBanks
        self.cartType = cartType

        (self.ROMBankController,
         self.RAMBankController,
         self.RAMBanks,
         self.battery,
         self.rtcEnabled) = cartridgeTable[self.cartType]

        if self.rtcEnabled:
            self.rtc = RTC(logger)

        self.RAMBanks = self.initRAMBanks(self.RAMBanks)

        self.gameName = self.getGameName(ROMBanks)

        self.memoryModel = 0  # Should not be hardcoded, but no other model is implemented
        self.RAMRange = (0xA000, 0xBFFF)
        self.RAMBankEnabled = False
        self.RAMBankSelected = 0  # TODO: Check this, not documented
        self.ROMBankSelected = 1  # TODO: Check this, not documented #NOTE: TestROM 01-special.gb
                                  # assumes initial value of 1

    def saveRAMSparse(self):
        minIdx, maxIdx = self.RAMRange

        if minIdx is None or maxIdx is None:
            self.logger("Saving non-volatile memory is not supported on %s" % self.ROMBankController)
            return

        self.logger("Saving non-volatile memory")
        romPath, ext = os.path.splitext(self.filename)

        writeBuffer = ""
        for bank in range(len(self.RAMBanks)):
            self.RAMBankSelected = bank

            for i in range(minIdx, maxIdx+1):
                if self[i] != 0:
                    writeBuffer += "%i,%s,%s\n" % (bank, hex(i)[2:], hex(self[i])[2:])

        with open(romPath+".ram", "wb") as saveRAM:
            saveRAM.write(writeBuffer)

    def loadRAMSparse(self):
        minIdx, maxIdx = self.RAMRange

        if minIdx is None or maxIdx is None:
            self.logger("Loading non-volatile memory is not supported on %s" % self.ROMBankController)
            return

        romPath, ext = os.path.splitext(self.filename)
        if not os.path.exists(romPath+".ram"):
            self.logger("No RAM file found. Skipping load of non-volatile memory")
            return

        self.logger("Loading non-volatile memory")

        with open(romPath+".ram", "rb") as loadRAM:
            data = map(lambda x: x.split(","), loadRAM.read().split("\n"))

            for line in data:
                if 1 < len(line):  # Ignore empty lines (typically the last line)
                    bank, idx, value = map(lambda v: int(v, 16), line)

                    self.RAMBankSelected = bank
                    self[idx] = value

    def initRAMBanks(self, n):
        if n is None:
            return None

        banks = []
        for n in range(n):
            # In real life the RAM is scrambled on initialization
            banks.append([0 for x in xrange(8 * 1024)])
        return banks

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
        string += "RAM bank: %s\n" % self.RAMBankController
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
            self.rtc.writeCommand(value)
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
