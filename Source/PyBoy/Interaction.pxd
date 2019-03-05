# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cdef unsigned char P10, P11, P12, P13, P14, P15
cdef unsigned char resetBit(unsigned char, unsigned char)
cdef unsigned char setBit(unsigned char, unsigned char)

cdef class Interaction:
    cdef unsigned char directional, standard
    cdef void keyEvent(self, unsigned char)
    cdef unsigned char pull(self, unsigned char)

