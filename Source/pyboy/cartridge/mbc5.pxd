#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .base_mbc cimport BaseMBC


cdef class MBC5(BaseMBC):
    cdef void setitem(self, unsigned short, unsigned char)
