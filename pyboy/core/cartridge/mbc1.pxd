#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t, uint16_t
from .base_mbc cimport BaseMBC


cdef class MBC1(BaseMBC):
    cdef void setitem(self, uint16_t, uint8_t)
    cdef uint8_t bank_select_register1
    cdef uint8_t bank_select_register2
