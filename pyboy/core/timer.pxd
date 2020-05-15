#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t
from pyboy.utils cimport IntIOInterface
import cython


cdef class Timer:
    cdef uint64_t DIV, TIMA, TMA, TAC
    cdef uint16_t DIV_counter, TIMA_counter
    cdef uint64_t[4] dividers

    @cython.locals(divider=cython.int)
    cdef bint tick(self, uint64_t)
    @cython.locals(divider=cython.int, cyclesleft=cython.uint)
    cdef uint64_t cyclestointerrupt(self)

    cdef void save_state(self, IntIOInterface)
    cdef void load_state(self, IntIOInterface, int)
