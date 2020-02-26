#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import cython


cdef class Timer:
    cdef unsigned int DIV, TIMA, TMA, TAC
    cdef unsigned int DIV_counter, TIMA_counter
    cdef unsigned int[4] dividers

    @cython.locals(divider=cython.int)
    cdef bint tick(self, unsigned int)
    @cython.locals(divider=cython.int, cyclesleft=cython.uint)
    cdef unsigned int cyclestointerrupt(self)
