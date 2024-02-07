#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport int64_t, uint8_t, uint16_t, uint32_t, uint64_t

from pyboy.utils cimport IntIOInterface

import cython

from pyboy.logging.logging cimport Logger


cdef Logger logger

cdef class Timer:
    cdef uint64_t DIV, TIMA, TMA, TAC
    cdef uint16_t DIV_counter, TIMA_counter
    cdef uint64_t[4] dividers

    cdef void reset(self) noexcept nogil
    @cython.locals(divider=cython.int)
    cdef bint tick(self, uint64_t) noexcept nogil
    @cython.locals(divider=cython.int, cyclesleft=cython.uint)
    cdef int64_t cycles_to_interrupt(self) noexcept nogil

    cdef void save_state(self, IntIOInterface) noexcept
    cdef void load_state(self, IntIOInterface, int) noexcept
