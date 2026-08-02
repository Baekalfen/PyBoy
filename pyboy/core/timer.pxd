#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from cython cimport final

from libc.stdint cimport int64_t, uint8_t, uint16_t, uint32_t, uint64_t

from pyboy.utils cimport IntIOInterface

import cython

from pyboy.logging.logging cimport Logger

cdef uint64_t MAX_CYCLES

cdef Logger logger

@final
cdef class Timer:
    cdef uint64_t DIV, TIMA, TMA, TAC
    cdef uint64_t DIV_counter, TIMA_counter
    cdef uint64_t[4] dividers
    cdef uint8_t tima_reload_state
    cdef int64_t _cycles_to_interrupt
    cdef uint64_t last_cycles

    @cython.locals(timer_bit=uint16_t)
    cdef void reset(self) noexcept nogil
    cdef void _increase_tima(self) noexcept nogil
    cdef void write_tima(self, uint8_t) noexcept nogil
    cdef void write_tma(self, uint8_t) noexcept nogil
    @cython.locals(old_timer_bit=uint16_t, new_timer_bit=uint16_t)
    cdef void write_tac(self, uint8_t) noexcept nogil
    cdef uint8_t read_tima(self) noexcept nogil
    @cython.locals(cycles=uint64_t, counter=uint16_t, new_counter=uint16_t, timer_bit=uint16_t)
    cdef bint tick(self, uint64_t) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1
