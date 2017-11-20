# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

### CPU Flags
flagC, flagH, flagN, flagZ = range(4, 8)

def testFlag(self, flag):
    return (self.F & (1 << flag)) != 0

def setFlag(self, flag, value=True):
    self.F = (self.F & (0xFF - (1 << flag)))
    if value:
        self.F = (self.F + (1 << flag))

def clearFlag(self, flag):
    self.F = (self.F & (0xFF - (1 << flag)))

### Interrupt flags
VBlank, LCDC, TIMER, Serial, HightoLow = range(5)


def testInterruptFlag(self, flag):
    return (self.mb[0xFF0F] & (1 << flag)) != 0


def setInterruptFlag(self, flag):
    self.mb[0xFF0F] |= (1 << flag)


def clearInterruptFlag(self, flag):
    self.mb[0xFF0F] &= (0xFF - (1 << flag))


def testInterruptFlagEnabled(self, flag):
    return (self.mb[0xFFFF] & (1 << flag)) != 0



def testRAMRegisterFlag(self, address, flag):
    return (self.mb[address] & (1 << flag)) != 0

def setRAMRegisterFlag(self, address, flag, value=True):
    self.clearRAMRegisterFlag(address, flag)
    # self.mb[address] = (self.mb[address] & (0xFF - (1 << flag)))
    # if value:
    self.mb[address] = (self.mb[address] + (value << flag))

def clearRAMRegisterFlag(self, address, flag):
    self.mb[address] = (self.mb[address] & (0xFF - (1 << flag)))

def testRAMRegisterFlagEnabled(self, address, flag):
    return (self.mb[address] & (1 << flag)) != 0
