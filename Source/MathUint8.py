# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


def AND(x, y):
    raise Exception("Not used")


def OR(x, y):
    raise Exception("Not used")


def XOR(x, y):
    raise Exception("Not used")


def add(x, y):
    raise Exception("Not used")


def sub(x, y):
    raise Exception("Not used")


def setBit(x, bit, value):
    raise Exception("Not used")


def getBit(x, bit):
    return ((x >> bit) & 1)


def clear(x, bit):
    raise Exception("Not used")


def swap(x):
    a = (x & 0xF0) >> 4
    b = (x & 0x0F) << 4

    return a + b


def lshift(x):
    return (x << 1) & 0xFF, getBit(x, 7)


def rshift(x):
    return x >> 1, getBit(x, 0)


#OPTIMIZE: Make seperate lrotate for each case
# def lrotate(x,c, intoCarry=False, throughCarry=False):
#     if intoCarry:  # Copies into carry
#         a = (x>>7) & 0xFF
#         x = ((x << 1) & 0xFF) + a #OPTIMIZE: Mask is probably not necessary

#         return (x, a == 1) #x, carry
#     elif throughCarry:  # Uses carry as Most Significant Bit (8+1 bit)
#         x = ((x << 1) & 0xFF) + c

#         return (x, (x>>7) & 0xFF == 1) #x, carry
#     else:
#         raise Exception("You must specify a carry mode; otherwise this is just a shift ;)")


def lrotate_inC(x):
    a = x >> 7
    x = (x << 1) + a
    return (x & 0xFF, a == 1)  # x, carry


def lrotate_thruC(x, c):
    x = (x << 1) + c
    return (x & 0xFF, (x >> 8) == 1)  # x, carry


def rrotate_inC(x):
    a = x & 0x1
    x = (x >> 1) + (a << 7)
    return (x, a == 1)  # x, carry


def rrotate_thruC(x, c):
    return ((x >> 1) + (c << 7), (x & 1) == 1)  # x, carry


def eq(x, y):
    raise Exception("Not used")
    return (x & 0xFF) == (y & 0xFF)


def getSignedInt8(x):
    if x & 0b10000000 == 0b10000000:  # Test MSB for negative
        # print "getSignedInt8",bin(x),-(~x & 0xFF)-1
        return -(~x & 0xFF)-1#-((~x & 0xFF) - 1)
    else:
        return x & 0xFF
