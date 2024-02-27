#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from libc.stdint cimport uint8_t
from pyboy.pyboy cimport PyBoy
cimport cython

cdef class MemoryManager:
    cdef PyBoy pyboy