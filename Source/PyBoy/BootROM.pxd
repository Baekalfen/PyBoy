# -*- encoding: utf-8 -*-
#
# Authors: Mads Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cdef class BootROM:
    cdef unsigned char[256] bootROM
    cdef unsigned char getitem(self, unsigned short)

