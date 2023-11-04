#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from libc.stdint cimport uint8_t
from pyboy.pyboy cimport PyBoy
cimport cython

cdef class Gen1MemoryManager:
    cdef PyBoy pyboy
    cdef str byte_order