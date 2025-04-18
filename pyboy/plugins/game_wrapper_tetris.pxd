#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
from libc.stdint cimport uint8_t

from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper


cdef Logger logger

cdef int TILES
cdef int NEXT_TETROMINO_ADDR

cdef class GameWrapperTetris(PyBoyGameWrapper):
    cdef readonly int score
    cdef readonly int level
    cdef readonly int lines

    cpdef void set_tetromino(self, str) noexcept
    cpdef str next_tetromino(self)
