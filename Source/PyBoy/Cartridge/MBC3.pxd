# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from PyBoy.Cartridge.GenericMBC cimport GenericMBC

cdef class MBC3(GenericMBC):
    cdef void setitem(self, unsigned short, unsigned char)

