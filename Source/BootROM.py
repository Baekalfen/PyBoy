# -*- encoding: utf-8 -*-
#
# Authors: Mads Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import struct


class BootROM():
    def __init__(self, bootROMFile):
        if bootROMFile is not None:
            with open(bootROMFile, "rb") as bootROMFileHandle:
                rom = bootROMFileHandle.read()
                self.bootROM = struct.unpack('%iB' % len(rom), rom)
        else:
            self.bootROM = [0 for x in range(256)]
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

    def __getitem__(self, i):
        return self.bootROM[i]
