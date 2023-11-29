#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.logging.logging cimport Logger

from libc.stdint cimport uint8_t, uint16_t, uint64_t
from .base_mbc cimport BaseMBC


cdef Logger logger

cdef class MBC3(BaseMBC):
    cdef void setitem(self, uint64_t, uint8_t) noexcept nogil
