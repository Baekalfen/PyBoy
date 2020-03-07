#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
from pyboy.core.mb cimport Motherboard

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2


cdef class Sprite:
    cdef Motherboard mb
    cdef int _offset
