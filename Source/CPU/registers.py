# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

#      A  F  B  C  D  E  HL  SP PC
reg = [0, 0, 0, 0, 0, 0, 0,  0, 0]

_A, _F, _B, _C, _D, _E, _HL, _SP, _PC = range(9)

def setA(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self.reg[_A] = x

def setF(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self.reg[_F] = x & 0xF0 # This register cannot store values in bit 0-3
    # See undocumented behavior in 01-special.gb at 0xC31A

def setB(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self.reg[_B] = x

def setC(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self.reg[_C] = x

def setD(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self.reg[_D] = x

def setE(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self.reg[_E] = x

def setH(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self.reg[_HL] &= 0x00FF
    self.reg[_HL] |= x << 8

def setL(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self.reg[_HL] &= 0xFF00
    self.reg[_HL] |= x

def setHL(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self.reg[_HL] = x

def setSP(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self.reg[_SP] = x

def setPC(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self.reg[_PC] = x


def setAF(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self.reg[_A] = x >> 8
    self.reg[_F] = x & 0x00F0 # Lower nibble of F is always zero!

def setBC(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self.reg[_B] = x >> 8
    self.reg[_C] = x & 0x00FF

def setDE(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self.reg[_D] = x >> 8
    self.reg[_E] = x & 0x00FF

