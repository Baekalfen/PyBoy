# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

#      A  F  B  C  D  E  H  L  SP PC
reg = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

A, F, B, C, D, E, H, L, SP, PC = range(10)


def setReg(self, x, value):
    self.reg[x] = value


# Reducing code in opcodes.py

def setPC(self, x):
    self.reg[PC] = x


def incPC(self, x):
    self.reg[PC] += x


def setAF(self, x):
    self.reg[A] = (x & 0xFF00) >> 8
    self.reg[F] = (x & 0x00F0) # Lower nibble of F is always zero!
    # See undocumented behavior and 01-special.gb at 0xC31A


def setBC(self, x):
    self.reg[B] = (x & 0xFF00) >> 8
    self.reg[C] = (x & 0x00FF)


def setDE(self, x):
    self.reg[D] = (x & 0xFF00) >> 8
    self.reg[E] = (x & 0x00FF)


def setHL(self, x):
    self.reg[H] = (x & 0xFF00) >> 8
    self.reg[L] = (x & 0x00FF)


def getAF(self):
    return (self.reg[A] << 8) + self.reg[F]


def getBC(self):
    return (self.reg[B] << 8) + self.reg[C]


def getDE(self):
    return (self.reg[D] << 8) + self.reg[E]


def getHL(self):
    return (self.reg[H] << 8) + self.reg[L]


def clearBit(self):
    raise Exception("Not implemented")
