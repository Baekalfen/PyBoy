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
    # return (self.ram[0xFF0F] & (1 << flag)) != 0
    return self.testRAMRegisterFlag(0xFF0F,flag)


def setInterruptFlag(self, flag, value=True):
    # self.ram[0xFF0F] = (self.ram[0xFF0F] & (0xFF - (1 << flag)))
    # if value:
    #     self.ram[0xFF0F] = (self.ram[0xFF0F] + (1 << flag))
    return self.setRAMRegisterFlag(0xFF0F,flag,value)


def clearInterruptFlag(self, flag):
    # self.ram[0xFF0F] = (self.ram[0xFF0F] & (0xFF - (1 << flag)))
    self.clearRAMRegisterFlag(0xFF0F,flag)


def testInterruptFlagEnabled(self, flag):
    # return (self.ram[0xFFFF] & (1 << flag)) != 0
    return self.testRAMRegisterFlagEnabled(0xFFFF,flag)
    



# Bit 6 - LYC=LY Coincidence Interrupt (1=Enable) (Read/Write)
# Bit 5 - Mode 2 OAM Interrupt         (1=Enable) (Read/Write)
# Bit 4 - Mode 1 V-Blank Interrupt     (1=Enable) (Read/Write)
# Bit 3 - Mode 0 H-Blank Interrupt     (1=Enable) (Read/Write)
# Bit 2 - Coincidence Flag  (0:LYC<>LY, 1:LYC=LY) (Read Only)
# Bit 1-0 - Mode Flag       (Mode 0-3, see below) (Read Only)
#         0: During H-Blank
#         1: During V-Blank
#         2: During Searching OAM-RAM
#         3: During Transfering Data to LCD Driver

LYCFlag, _, _, _, LYCFlagEnable = range(2,7)

def testSTATFlag(self, flag):
    return self.testRAMRegisterFlag(0xFF41,flag)

def setSTATFlag(self, flag, value=True):
    return self.setRAMRegisterFlag(0xFF41,flag,value)

def clearSTATFlag(self, flag):
    self.clearRAMRegisterFlag(0xFF41,flag)

def testSTATFlagEnabled(self, flag):
    return self.testRAMRegisterFlagEnabled(0xFF41,flag)



def testRAMRegisterFlag(self, address, flag):
    return (self.ram[address] & (1 << flag)) != 0

def setRAMRegisterFlag(self, address, flag, value=True):
    self.clearRAMRegisterFlag(address, flag)
    # self.ram[address] = (self.ram[address] & (0xFF - (1 << flag)))
    # if value:
    self.ram[address] = (self.ram[address] + (value << flag))

def clearRAMRegisterFlag(self, address, flag):
    self.ram[address] = (self.ram[address] & (0xFF - (1 << flag)))

def testRAMRegisterFlagEnabled(self, address, flag):
    return (self.ram[address] & (1 << flag)) != 0
