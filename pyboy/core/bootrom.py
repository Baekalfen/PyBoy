#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import array
import os
import struct


class BootROM:
    def __init__(self, bootrom_file):
        # TODO: Remove this, when no unittests depend on it.
        if bootrom_file == "pyboy_fast":
            self.bootrom = array.array("B", [0] * 256)
            # Set stack pointer
            self.bootrom[0x00] = 0x31
            self.bootrom[0x01] = 0xFE
            self.bootrom[0x02] = 0xFF

            # Inject jump to 0xFC
            self.bootrom[0x03] = 0xC3
            self.bootrom[0x04] = 0xFC
            self.bootrom[0x05] = 0x00

            # Inject code to disable boot-ROM
            self.bootrom[0xFC] = 0x3E
            self.bootrom[0xFD] = 0x01
            self.bootrom[0xFE] = 0xE0
            self.bootrom[0xFF] = 0x50
            return

        if bootrom_file is None:
            # Default to PyBoy boot ROM
            bootrom_file = os.path.dirname(os.path.realpath(__file__)) + "/bootrom.bin"

        with open(bootrom_file, "rb") as f:
            rom = f.read()

        self.bootrom = array.array("B", struct.unpack("%iB" % len(rom), rom))

    def getitem(self, addr):
        return self.bootrom[addr]
