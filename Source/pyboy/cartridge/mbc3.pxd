#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from .genericmbc cimport GenericMBC


cdef class MBC3(GenericMBC):
    cdef void setitem(self, unsigned short, unsigned char)
