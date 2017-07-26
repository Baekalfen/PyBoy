# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

### CPU Flags
flagC, flagH, flagN, flagZ = range(4, 8)
from registers import F


def testFlag(self, flag):
    return (self.reg[F] & (1 << flag)) != 0


def setFlag(self, flag, value=True):
    self.reg[F] = (self.reg[F] & (0xFF - (1 << flag)))
    if value:
        self.reg[F] = (self.reg[F] + (1 << flag))


def clearFlag(self, flag):
    self.reg[F] = (self.reg[F] & (0xFF - (1 << flag)))

### Interrupt flags
VBlank, LCDC, TIMER, Serial, HightoLow = range(5)


def testInterruptFlag(self, flag):
    # return (self.mb[0xFF0F] & (1 << flag)) != 0
    return self.testRAMRegisterFlag(0xFF0F,flag)


def setInterruptFlag(self, flag, value=True):
    # self.mb[0xFF0F] = (self.mb[0xFF0F] & (0xFF - (1 << flag)))
    # if value:
    #     self.mb[0xFF0F] = (self.mb[0xFF0F] + (1 << flag))
    return self.setRAMRegisterFlag(0xFF0F,flag,value)


def clearInterruptFlag(self, flag):
    # self.mb[0xFF0F] = (self.mb[0xFF0F] & (0xFF - (1 << flag)))
    self.clearRAMRegisterFlag(0xFF0F,flag)


def testInterruptFlagEnabled(self, flag):
    # return (self.mb[0xFFFF] & (1 << flag)) != 0
    return self.testRAMRegisterFlagEnabled(0xFFFF,flag)



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
