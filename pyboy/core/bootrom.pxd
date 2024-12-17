#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t, uint16_t

from pyboy.logging.logging cimport Logger


cdef Logger logger

cdef class BootROM:
    cdef uint8_t[:] bootrom
    cdef bint cgb
    cdef uint8_t getitem(self, uint16_t) noexcept nogil
