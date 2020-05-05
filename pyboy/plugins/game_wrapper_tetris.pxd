#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from libc.stdint cimport uint8_t
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper
cimport cython

cdef int ROWS, COLS


cdef class GameWrapperTetris(PyBoyGameWrapper):
    cdef public int score
    cdef public int level
    cdef public int lines
    cdef public int fitness

    cpdef void set_tetromino(self, str)
    cpdef str next_tetromino(self)
