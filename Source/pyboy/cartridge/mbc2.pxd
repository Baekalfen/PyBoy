#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from .mbc cimport MBC


cdef class MBC2(MBC):
    cdef void setitem(self, unsigned short, unsigned char)
