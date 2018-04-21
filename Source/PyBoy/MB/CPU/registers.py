# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

def setH(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self.HL &= 0x00FF
    self.HL |= x << 8

def setL(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self.HL &= 0xFF00
    self.HL |= x

def setAF(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self.A = x >> 8
    self.F = x & 0x00F0 # Lower nibble of F is always zero!

def setBC(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self.B = x >> 8
    self.C = x & 0x00FF

def setDE(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self.D = x >> 8
    self.E = x & 0x00FF

