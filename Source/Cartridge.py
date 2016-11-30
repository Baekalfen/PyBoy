# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# from PrimitiveTypes import uint8
from time import time
import CoreDump


# TODO: Refactor all of this

class Cartridge:

    def __init__(self, logger, filename):
        self.ROMBanks = None
        start = time()
        with open(filename, 'rb') as ROMFile:
            ROMData = ROMFile.read()

            self.ROMBanks = [[0] * (16 * 1024)
                             for n in xrange(len(ROMData) / (16 * 1024))]

            for i, byte in enumerate(ROMData):
                self.ROMBanks[i / (16 * 1024)][i %
                                               (16 * 1024)] = ord(byte)

        # logger("Loaded ROM in %s seconds" % (time() - start))
        # logger("Amount of ROM banks is: %s" % len(self.ROMBanks))

        self.gameName = "".join([chr(x) for x in self.ROMBanks[0][0x0134:0x0142]]).rstrip("\0")
        self.battery = False
        self.cartType = self[0x0147]
        self.filename = filename
        self.memoryModel = None
        self.RAMBankController = None
        self.RAMBankEnabled = False
        self.RAMBanks = None
        self.RAMBankSelected = 0 # TODO: Check this, not documented
        self.ROMBankController = None
        self.ROMBankSelected = 1 # TODO: Check this, not documented #NOTE: TestROM 01-special.gb assumes initial value of 1
        self.RTC = False

        #
        #
        #
        #
        #
        #
        #
        # IMPORTANT!!!!
        # http://gbdev.gg8.se/wiki/articles/Memory_Bank_Controllers
        #
        #
        #
        #
        #
        #


        # TODO: Make MBCs into classes
        if self.cartType == 0x00:  # ROM only:
            self.ROMBankController = "ROM-only"
            # Optionally up to 8KByte of RAM could be connected at A000-BFFF, even though
            # that could require a tiny MBC-like circuit, but no real MBC chip
            self.RAMBanks = initRAMBanks(1)
        elif self.cartType == 0x01:  # -ROM+MBC1
            self.ROMBankController = "MBC1"
            self.memoryModel = 0
            self.RAMBanks = initRAMBanks(1)
        elif self.cartType == 0x02:  # -ROM+MBC1+RAM
            self.ROMBankController = "MBC1"
            self.memoryModel = 0
            self.RAMBankController = "RAM"
            self.RAMBanks = initRAMBanks(1)
        elif self.cartType == 0x03:  # -ROM+MBC1+RAM+BATT
            self.ROMBankController = "MBC1"
            self.memoryModel = 0
            self.RAMBankController = "RAM"
            self.battery = True
            self.RAMBanks = initRAMBanks(1)
        elif self.cartType == 0x05:  # -ROM+MBC2
            self.ROMBankController = "MBC2"
        elif self.cartType == 0x06:  # -ROM+MBC2+BATTERY
            self.ROMBankController = "MBC2"
            self.battery = True
        elif self.cartType == 0x08:  # -ROM+RAM
            self.RAMBankController = "RAM"
        elif self.cartType == 0x09:  # -ROM+RAM+BATTERY
            self.RAMBankController = "RAM"
            self.battery = True
        elif self.cartType == 0x0B:  # -ROM+MMM01
            raise Exception("Cartridge type not supported")
        elif self.cartType == 0x0C:  # -ROM+MMM01+SRAM
            self.RAMBankController = "SRAM"
            raise Exception("Cartridge type not supported")
        elif self.cartType == 0x0D:  # -ROM+MMM01+SRAM+BATT
            self.RAMBankController = "SRAM"
            self.battery = True
            raise Exception("Cartridge type not supported")
        elif self.cartType == 0x0F:  # -ROM+MBC3+TIMER+BATT
            self.ROMBankController = "MBC3"
            self.RAMBanks = initRAMBanks(1)
            self.battery = True
            self.RTC = True
        elif self.cartType == 0x10:  # -ROM+MBC3+TIMER+RAM+BATT
            self.ROMBankController = "MBC3"
            self.RAMBanks = initRAMBanks(1)
            self.RAMBankController = "RAM"
            self.battery = True
            self.RTC = True
        elif self.cartType == 0x11:  # -ROM+MBC3
            self.ROMBankController = "MBC3"
            self.RAMBanks = initRAMBanks(1)
        elif self.cartType == 0x12:  # -ROM+MBC3+RAM
            self.ROMBankController = "MBC3"
            self.RAMBanks = initRAMBanks(1)
            self.RAMBankController = "RAM"
        elif self.cartType == 0x13:  # -ROM+MBC3+RAM+BATT
            self.ROMBankController = "MBC3"
            self.RAMBanks = initRAMBanks(1)
            self.RAMBankController = "RAM"
            self.battery = True
        elif self.cartType == 0x19:  # -ROM+MBC5
            self.ROMBankController = "MBC5"
        elif self.cartType == 0x1A:  # -ROM+MBC5+RAM
            self.ROMBankController = "MBC5"
            self.RAMBankController = "RAM"
        elif self.cartType == 0x1B:  # -ROM+MBC5+RAM+BATT
            self.ROMBankController = "MBC5"
            self.RAMBankController = "RAM"
            self.battery = True
        elif self.cartType == 0x1C:  # -ROM+MBC5+RUMBLE
            self.ROMBankController = "MBC5"
        elif self.cartType == 0x1D:  # -ROM+MBC5+RUMBLE+SRAM
            self.ROMBankController = "MBC5"
            self.RAMBankController = "SRAM"
        elif self.cartType == 0x1E:  # -ROM+MBC5+RUMBLE+SRAM+BATT
            self.ROMBankController = "MBC5"
            self.RAMBankController = "SRAM"
            self.battery = True
        elif self.cartType == 0x1F:  # -Pocket Camera
            raise Exception("Cartridge type not supported")
        elif self.cartType == 0xFD:  # -Bandai TAMA5 FE - Hudson HuC-3
            raise Exception("Cartridge type not supported")
        elif self.cartType == 0xFF:  # -Hudson HuC-1
            raise Exception("Cartridge type not supported")
        else:
            raise Exception("Catridge type invalid: %s" % self.cartType)

    def __setitem__(self, address, value):
        if self.ROMBankController == 'MBC1':
            if 0x0000 <= address < 0x2000:
                # if self.memoryModel == 1:
                if (value & 0b00001111) == 0b1010:
                    self.RAMBankEnabled = True
                    self.RAMBanks = initRAMBanks(4)
                else:
                    self.RAMBanks = None
                    self.RAMBankEnabled = False
                # else:
                #     raise CoreDump.CoreDump("Memory model not defined. Address: %s, Value: %s" % (hex(address),hex(value)))

            elif 0x2000 <= address < 0x4000:
                # But (when using the register below to specify the upper ROM Bank bits), the same happens for Bank 20h, 40h, and 60h. Any attempt to address these ROM Banks will select Bank 21h, 41h, and 61h instead
                if value == 0:
                    value = 1
                self.ROMBankSelected = (self.ROMBankSelected & 0b11100000) | (
                    value & 0b00011111)  # sets 5LSB of ROM bank address
            elif 0x4000 <= address < 0x6000:
                # NOTE: 16mbit = 2MB. 2MB/(8KB banks) = 128 banks. 128 is
                # addressable with 7 bits
                if self.memoryModel == 0:  # 16/8 mode
                    self.ROMBankSelected = (self.ROMBankSelected & 0b00011111) | (
                        (address & 0b11) << 5)  # sets 2MSB of ROM bank address
                # NOTE: 4mbit = 0.5MB. 0.5MB/(8KB banks) = 32 banks. 32 is
                # addressably with 5 bits
                elif self.memoryModel == 1:  # 4/32 mode
                    self.RAMBankSelected = value & 0b00000011
                else:
                    raise CoreDump.CoreDump("Invalid memoryModel: %s" %
                                    self.memoryModel)
            elif 0x6000 <= address < 0x8000:
                self.memoryModel = value & 0x1
            elif 0xA000 <= address < 0xC000:
                self.RAMBanks[self.RAMBankSelected][address - 0xA000] = value
            else:
                raise CoreDump.CoreDump("Invalid writing address: %s" % hex(address))
        elif self.ROMBankController == 'MBC3':
            if 0x0000 <= address < 0x2000:
                # if self.memoryModel == 1:
                if (value & 0b00001111) == 0b1010:
                    self.RAMBankEnabled = True
                    self.RAMBanks = initRAMBanks(4)
                elif value == 0:
                    # self.RAMBanks = None
                    self.RAMBankEnabled = False
                    logger("Disabling RAMBanks/RTC (not fully implemented)")
                else:
                    raise CoreDump.CoreDump("Invalid command for MBC: Address: %s, Value: %s" % (address, value))
                # else:
                #     raise CoreDump.CoreDump("Memory model not defined. Model: %s, Address: %s, Value: %s" % (self.memoryModel, address,value))

            elif 0x2000 <= address < 0x4000:
                if value == 0:
                    value = 1
                # Same as for MBC1, except that the whole 7 bits of the RAM Bank Number are written directly to this address
                self.ROMBankSelected = value & 0b01111111  # sets 7LSB of ROM bank address
            elif 0x4000 <= address < 0x6000:
                # MBC3 is always 16/8 mode
                self.ROMBankSelected = self.ROMBankSelected & 0b01111111
            elif 0x6000 <= address < 0x8000:
                logger("Latch RTC")
            elif 0xA000 <= address < 0xC000:
                # logger(self.RAMBankSelected, value, len(self.RAMBanks))
                self.RAMBanks[self.RAMBankSelected][address - 0xA000] = value
            else:
                raise CoreDump.CoreDump("Invalid writing address: %s" % hex(address))
        elif self.ROMBankController == 'ROM-only':
            if 0x2000 <= address < 0x4000:
                if value == 0:
                    value = 1
                self.ROMBankSelected = (value & 0b1)
                logger("Switching bank", hex(address), hex(value))
            else:
                raise CoreDump.CoreDump("Invalid writing address: %s" % hex(address))
        else:
            raise CoreDump.CoreDump("Memory bank invalid: %s" % self.ROMBankController)


    def __getitem__(self, address):
        if 0x0000 <= address < 0x4000:
            return self.ROMBanks[0][address]
        elif 0x4000 <= address < 0x8000:
            # logger("ROM Bank ACCESS!",hex(address),self.ROMBankSelected,self.ROMBankController)
            return self.ROMBanks[self.ROMBankSelected][address - 0x4000]
        elif 0xA000 <= address < 0xC000:
            if not self.RAMBanks:
                # return 0
                raise CoreDump.CoreDump("RAMBanks not initialized: %s" % hex(address))
            self.logger("Cartridge RAM implementation not verified!")
            return self.RAMBanks[self.RAMBankSelected][address - 0xA000]
            # raise Exception("Not implemented")
        else:
            raise CoreDump.CoreDump("Reading address invalid: %s" % address)

    def __getslice__(self,a,b):
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


def initRAMBanks(n):
    banks = []
    for n in range(n):
        # In real life the RAM is scrambled on initialization
        banks.append([0 for x in xrange(8 * 1024)])
    return banks

if __name__ == "__main__":
    cartridge = Cartridge("ROMs/SuperMarioLand.gb")
    logger(cartridge)
    cartridge = Cartridge("TestROMs/cpu_instrs/individual/01-special.gb")
    logger(cartridge)
    cartridge = Cartridge("ROMs/pokemon_blue.gb")
    logger(cartridge)
    cartridge = Cartridge("ROMs/pokemon_gold.gbc")
    logger(cartridge)
    cartridge = Cartridge("ROMs/Tetris.gb")
    logger(cartridge)
    cartridge = Cartridge("TestROMs/oam_bug/rom_singles/1-lcd_sync.gb")
    logger(cartridge)
