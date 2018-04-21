# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cdef class Timer:
    cdef public unsigned char DIV, TIMA, TMA, TAC
    cdef public unsigned int DIVcounter, TIMAcounter
    cdef public unsigned int[4] dividers

    cpdef bint tick(self, unsigned int)
    cpdef unsigned int cyclesToInterrupt(self)
