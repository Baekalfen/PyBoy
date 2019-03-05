# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


cdef tuple lshift(int x)
cdef tuple rshift(int x)
cdef tuple lrotate_inC(int x)
cdef tuple lrotate_thruC(int x, int c)
cdef tuple rrotate_inC(int x)
cdef tuple rrotate_thruC(int x, int c)
cpdef short getSignedInt8(int x)

