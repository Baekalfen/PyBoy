#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t

from pyboy.utils cimport IntIOInterface

import cython

from pyboy.logging.logging cimport Logger


cdef Logger logger

cdef class Timer:
    cdef cython.long TAC
    cdef uint8_t TMA
    cdef uint16_t DIV, DIV_counter, TIMA_counter, TIMA
    cdef uint16_t[4] dividers

    cdef void reset(self) noexcept nogil
    @cython.locals(divider=uint16_t)
    cdef bint tick(self, int) noexcept nogil
    @cython.locals(divider=cython.int, cyclesleft=cython.uint)
    cdef uint64_t cycles_to_interrupt(self) noexcept nogil

    cdef void save_state(self, IntIOInterface) noexcept
    cdef void load_state(self, IntIOInterface, int) noexcept
