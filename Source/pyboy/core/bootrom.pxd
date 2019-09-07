#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cdef class BootROM:
    cdef unsigned char[256] bootrom
    cdef unsigned char getitem(self, unsigned short)
