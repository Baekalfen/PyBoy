# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import Global
import cython
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
            f.write(chr(self.internalRAM0[n]))
        for n in range(NON_IO_INTERNAL_RAM0):
            f.write(chr(self.nonIOInternalRAM0[n]))
        for n in range(IO_PORTS):
            f.write(chr(self.IOPorts[n]))
        for n in range(INTERNAL_RAM_1):
            f.write(chr(self.internalRAM1[n]))
        for n in range(NON_IO_INTERNAL_RAM1):
            f.write(chr(self.nonIOInternalRAM1[n]))
        for n in range(INTERRUPT_ENABLE_REGISTER):
            f.write(chr(self.interruptRegister[n]))

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

