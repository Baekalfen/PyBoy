#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
from pyboy.core.mb cimport Motherboard



cdef class Screen:
    cdef Motherboard mb
