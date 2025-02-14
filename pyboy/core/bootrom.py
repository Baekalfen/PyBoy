#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import array
import os
import struct


class BootROM:
    def __init__(self, bootrom_file, cartridge_cgb):
        if bootrom_file is None:
            # Default to PyBoy boot ROM
            rom = "/bootrom_cgb.bin" if cartridge_cgb else "/bootrom_dmg.bin"
            bootrom_file = os.path.dirname(os.path.realpath(__file__)) + rom

        with open(bootrom_file, "rb") as f:
            rom = f.read()

        self.bootrom = array.array("B", struct.unpack("%iB" % len(rom), rom))
        self.cgb = len(rom) > 0x100

    def getitem(self, addr):
        return self.bootrom[addr]
