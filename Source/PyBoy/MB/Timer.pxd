# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cdef class Timer:
    cdef public unsigned int DIV, TIMA, TMA, TAC
    cdef public unsigned int DIVcounter, TIMAcounter
    cdef public unsigned int[4] dividers

    cdef bint tick(self, unsigned int)
    cdef unsigned int cyclesToInterrupt(self)
