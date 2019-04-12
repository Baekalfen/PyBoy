#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import cython


cdef class Timer:
    cdef public unsigned int DIV, TIMA, TMA, TAC
    cdef public unsigned int DIV_counter, TIMA_counter
    cdef public unsigned int[4] dividers

    @cython.locals(divider=cython.int)
    cdef bint tick(self, unsigned int)
    @cython.locals(divider=cython.int, cyclesLeft=cython.uint)
    cdef unsigned int cyclestointerrupt(self)
