#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from pyboy.core.mb cimport Motherboard


cdef class Rumble:
    cdef Motherboard mb