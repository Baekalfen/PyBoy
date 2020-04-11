#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t
import cython


cdef class Timer:
    cdef uint64_t DIV, TIMA, TMA, TAC
    cdef uint64_t DIV_counter, TIMA_counter
    cdef uint64_t[4] dividers

    @cython.locals(divider=cython.int)
    cdef bint tick(self, uint64_t)
    @cython.locals(divider=cython.int, cyclesleft=cython.uint)
    cdef uint64_t cyclestointerrupt(self)
