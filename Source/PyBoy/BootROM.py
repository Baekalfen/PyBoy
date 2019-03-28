# -*- encoding: utf-8 -*-
#
# Authors: Mads Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import Global
import struct
import array

class BootROM():
    def __init__(self, bootROMFile):
        if bootROMFile is not None:
            with open(bootROMFile, "rb") as bootROMFileHandle:
                rom = bootROMFileHandle.read()
            self.bootROM = array.array('B', struct.unpack('%iB' % len(rom), rom))
        else:
            self.bootROM = array.array('B', [0] * 256)
            # Set stack pointer
            self.bootROM[0x00] = 0x31
            self.bootROM[0x01] = 0xFE
            self.bootROM[0x02] = 0xFF

            # Inject jump to 0xFC
            self.bootROM[0x03] = 0xC3
            self.bootROM[0x04] = 0xFC
            self.bootROM[0x05] = 0x00

            # Inject code to disable boot-ROM
            self.bootROM[0xFC] = 0x3E
            self.bootROM[0xFD] = 0x01
            self.bootROM[0xFE] = 0xE0
            self.bootROM[0xFF] = 0x50

    def getitem(self, addr):
        return self.bootROM[addr]
