#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


cdef class RTC:
    cdef unicode filename
    cdef bint latchenabled
    cdef double timezero
    cdef unsigned int seclatch
    cdef unsigned int minlatch
    cdef unsigned int hourlatch
    cdef unsigned int daylatchlow
    cdef unsigned int daylatchhigh
    cdef unsigned int daycarry
    cdef unsigned int halt

    cdef void stop(self)
    cdef void save_state(self, file)
    cdef void load_state(self, file)
    cdef void latch_rtc(self)
    cdef void writecommand(self, unsigned char)
    cdef unsigned char getregister(self, unsigned char)
    cdef void setregister(self, unsigned char, unsigned char)
