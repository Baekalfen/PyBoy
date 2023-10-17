#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t, uint16_t

cdef class BootROM:
    cdef uint8_t[:] bootrom
    cdef uint8_t getitem(self, uint16_t) noexcept
