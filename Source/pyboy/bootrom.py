#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import array
import struct


class BootROM:
    def __init__(self, bootromfile):
        if bootromfile is not None:
            with open(bootromfile, "rb") as bootromfilehandle:
                rom = bootromfilehandle.read()
            self.bootrom = array.array('B', struct.unpack('%iB' % len(rom), rom))
        else:
            self.bootrom = array.array('B', [0] * 256)

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

    def getitem(self, addr):
        return self.bootrom[addr]
