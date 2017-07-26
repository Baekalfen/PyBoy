# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


def lshift(x):
    return (x << 1) & 0xFF, x & 0x80 # 7th bit

def rshift(x):
    return x >> 1, x & 1

def lrotate_inC(x):
    a = x >> 7
    x = (x << 1) + a
    return (x & 0xFF, a == 1)

def lrotate_thruC(x, c):
    x = (x << 1) + c
    return (x & 0xFF, (x >> 8) == 1)

def rrotate_inC(x):
    a = x & 0x1
    x = (x >> 1) + (a << 7)
    return (x, a == 1)  # x, carry

def rrotate_thruC(x, c):
    return ((x >> 1) + (c << 7), (x & 1) == 1)  # x, carry

def getSignedInt8(x):
    if x & 0b10000000:  # Test MSB for negative
        return -(~x & 0xFF)-1
    else:
        return x & 0xFF
