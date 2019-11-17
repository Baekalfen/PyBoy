#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.rewind cimport IntIOWrapper

cdef class RTC:
    cdef unicode filename
    cdef bint latch_enabled
    cdef double timezero
    cdef unsigned int sec_latch
    cdef unsigned int min_latch
    cdef unsigned int hour_latch
    cdef unsigned int day_latch_low
    cdef unsigned int day_latch_high
    cdef unsigned int day_carry
    cdef unsigned int halt

    cdef void stop(self)
    cdef void save_state(self, IntIOWrapper)
    cdef void load_state(self, IntIOWrapper)
    cdef void latch_rtc(self)
    cdef void writecommand(self, unsigned char)
    cdef unsigned char getregister(self, unsigned char)
    cdef void setregister(self, unsigned char, unsigned char)
