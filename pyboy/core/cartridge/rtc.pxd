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

cdef class RTC:
    cdef str filename
    cdef bint latch_enabled
    cdef cython.double timezero
    cdef bint timelock
    cdef uint64_t sec_latch
    cdef uint64_t min_latch
    cdef uint64_t hour_latch
    cdef uint64_t day_latch_low
    cdef uint64_t day_latch_high
    cdef uint64_t day_carry
    cdef uint64_t halt

    cdef void stop(self) noexcept
    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1
    @cython.locals(days=uint64_t)
    cdef void latch_rtc(self) noexcept nogil
    cdef void writecommand(self, uint8_t) noexcept nogil
    cdef uint8_t getregister(self, uint8_t) noexcept nogil
    @cython.locals(t=cython.double, days=uint64_t)
    cdef void setregister(self, uint8_t, uint8_t) noexcept nogil
