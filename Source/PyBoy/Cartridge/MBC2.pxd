# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from GenericMBC cimport GenericMBC

cdef class MBC2(GenericMBC):
    cdef void setitem(self, unsigned short, unsigned char)
