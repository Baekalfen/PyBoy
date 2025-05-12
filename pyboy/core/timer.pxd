#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport int64_t, uint8_t, uint16_t, uint32_t, uint64_t

from pyboy.utils cimport IntIOInterface

import cython

from pyboy.logging.logging cimport Logger

cdef uint64_t MAX_CYCLES

cdef Logger logger

cdef class Timer:
    cdef uint64_t DIV, TIMA, TMA, TAC
    cdef uint64_t DIV_counter, TIMA_counter
    cdef uint64_t[4] dividers
    cdef int64_t _cycles_to_interrupt
    cdef uint64_t last_cycles

    cdef void reset(self) noexcept nogil
    @cython.locals(divider=uint8_t)
    cdef bint tick(self, uint64_t) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1
