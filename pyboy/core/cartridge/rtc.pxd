#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t, uint16_t, uint64_t
from pyboy.utils cimport IntIOInterface

cdef class RTC:
    cdef str filename
    cdef bint latch_enabled
    cdef double timezero
    cdef uint64_t sec_latch
    cdef uint64_t min_latch
    cdef uint64_t hour_latch
    cdef uint64_t day_latch_low
    cdef uint64_t day_latch_high
    cdef uint64_t day_carry
    cdef uint64_t halt

    cdef void stop(self)
    cdef void save_state(self, IntIOInterface)
    cdef void load_state(self, IntIOInterface, int)
    cdef void latch_rtc(self)
    cdef void writecommand(self, uint8_t)
    cdef uint8_t getregister(self, uint8_t)
    cdef void setregister(self, uint8_t, uint8_t)
