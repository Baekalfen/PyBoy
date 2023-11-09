#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t, uint16_t

from pyboy.logging.logging cimport Logger

from .base_mbc cimport BaseMBC


cdef Logger logger

cdef class MBC2(BaseMBC):
    cdef void setitem(self, uint16_t, uint8_t) noexcept nogil
