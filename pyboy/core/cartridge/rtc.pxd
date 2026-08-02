#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import cython

from cpython cimport time
from libc.stdint cimport uint8_t, uint16_t, uint64_t

from pyboy cimport utils
from pyboy.logging.logging cimport Logger
from pyboy.utils cimport IntIOInterface


cdef Logger logger
cdef uint64_t RTC_CYCLES_PER_SECOND

cdef class RTC:
    cdef bint latch_enabled
    cdef cython.double timezero
    cdef bint timelock
    cdef uint8_t seconds
    cdef uint8_t minutes
    cdef uint8_t hours
    cdef uint8_t day_low
    cdef uint8_t day_high
    cdef uint8_t day_carry
    cdef uint8_t halt
    cdef uint8_t sec_latch
    cdef uint8_t min_latch
    cdef uint8_t hour_latch
    cdef uint8_t day_latch_low
    cdef uint8_t day_latch_high
    cdef uint64_t rtc_cycles
    cdef uint64_t last_cycles

    cdef void stop(self, object) noexcept
    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1
    cdef void latch_rtc(self) noexcept nogil
    @cython.locals(
        elapsed=uint64_t,
        elapsed_seconds=uint64_t,
        now=cython.double,
        host_elapsed=cython.double,
    )
    cdef void tick(self, uint64_t) noexcept nogil
    @cython.locals(
        seconds=uint64_t,
        old_seconds=uint8_t,
        old_minutes=uint8_t,
        old_hours=uint8_t,
        day=uint16_t,
        total=uint64_t,
        days_elapsed=uint64_t,
    )
    cdef void _advance_seconds(self, uint64_t) noexcept nogil
    cdef void writecommand(self, uint8_t) noexcept nogil
    cdef uint8_t getregister(self, uint8_t) noexcept nogil
    cdef void setregister(self, uint8_t, uint8_t) noexcept nogil
