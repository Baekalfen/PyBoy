# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from .. import CoreDump
from ..Logger import logger
from GenericMBC import GenericMBC
import cython

class MBC1(GenericMBC):
    @cython.locals(address=cython.ushort, value=cython.uchar)
    def __setitem__(self, address, value):
        if 0x0000 <= address < 0x2000:
            if (value & 0b00001111) == 0x0A:
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
            if self.RAMBanks == None:
                from . import ExRAMTable
                logger.warn("Game tries to set value 0x%0.2x at RAM address 0x%0.4x, but RAM banks are not initialized. Initializing %d RAM banks as precaution" % (value, address, ExRAMTable[0x02]))
                self.initRAMBanks(ExRAMTable[0x02])
            self.RAMBanks[self.RAMBankSelected][address - 0xA000] = value
        else:
            raise CoreDump.CoreDump("Invalid writing address: %s" % hex(address))

