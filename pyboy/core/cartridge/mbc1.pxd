#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .base_mbc cimport BaseMBC
from libc.stdint cimport uint8_t, uint16_t


cdef class MBC1(BaseMBC):
    cdef void setitem(self, unsigned short, unsigned char)
    cdef uint8_t bank_select_register1
    cdef uint8_t bank_select_register2
