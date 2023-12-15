#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
from libc.stdint cimport uint8_t

from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper


cdef Logger logger

cdef int ROWS, COLS
cdef int NEXT_TETROMINO_ADDR

cdef class GameWrapperTetris(PyBoyGameWrapper):
    cdef public int score
    cdef public int level
    cdef public int lines
    cdef public int fitness

    cpdef void set_tetromino(self, str) noexcept
    cpdef str next_tetromino(self) noexcept

    cpdef void start_game(self, timer_div=*) noexcept
    cpdef void reset_game(self, timer_div=*) noexcept
