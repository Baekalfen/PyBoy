#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import array

# MEMORY SIZES
INTERNAL_RAM_0 = 8 * 1024  # 8KB
NON_IO_INTERNAL_RAM0 = 0x60
IO_PORTS = 0x4C
NON_IO_INTERNAL_RAM1 = 0x34
INTERNAL_RAM_1 = 0x7F
INTERRUPT_ENABLE_REGISTER = 1
###########

class RAM():

    def __init__(self, random=False):
        if random: #NOTE: In real life, the RAM is scrambled with random data on boot.
            raise Exception("Random RAM not implemented")

        self.internalRAM0 = array.array('B', [0]*(INTERNAL_RAM_0))
        self.nonIOInternalRAM0 = array.array('B', [0]*(NON_IO_INTERNAL_RAM0))
        self.IOPorts = array.array('B', [0]*(IO_PORTS))
        self.internalRAM1 = array.array('B', [0]*(INTERNAL_RAM_1))
        self.nonIOInternalRAM1 = array.array('B', [0]*(NON_IO_INTERNAL_RAM1))
        self.interruptRegister = array.array('B', [0]*(INTERRUPT_ENABLE_REGISTER))

    def saveState(self, f):
        for n in range(INTERNAL_RAM_0):
            f.write(self.internalRAM0[n].to_bytes(1, 'little'))
        for n in range(NON_IO_INTERNAL_RAM0):
            f.write(self.nonIOInternalRAM0[n].to_bytes(1, 'little'))
        for n in range(IO_PORTS):
            f.write(self.IOPorts[n].to_bytes(1, 'little'))
        for n in range(INTERNAL_RAM_1):
            f.write(self.internalRAM1[n].to_bytes(1, 'little'))
        for n in range(NON_IO_INTERNAL_RAM1):
            f.write(self.nonIOInternalRAM1[n].to_bytes(1, 'little'))
        for n in range(INTERRUPT_ENABLE_REGISTER):
            f.write(self.interruptRegister[n].to_bytes(1, 'little'))

    def loadState(self, f):
        for n in range(INTERNAL_RAM_0):
            self.internalRAM0[n] = ord(f.read(1))
        for n in range(NON_IO_INTERNAL_RAM0):
            self.nonIOInternalRAM0[n] = ord(f.read(1))
        for n in range(IO_PORTS):
            self.IOPorts[n] = ord(f.read(1))
        for n in range(INTERNAL_RAM_1):
            self.internalRAM1[n] = ord(f.read(1))
        for n in range(NON_IO_INTERNAL_RAM1):
            self.nonIOInternalRAM1[n] = ord(f.read(1))
        for n in range(INTERRUPT_ENABLE_REGISTER):
            self.interruptRegister[n] = ord(f.read(1))

