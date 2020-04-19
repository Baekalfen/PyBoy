#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from libc.stdint cimport uint8_t
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper
cimport cython

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2
cdef int ROWS, COLS


cdef class GameWrapperSuperMarioLand(PyBoyGameWrapper):
    cdef public tuple world
    cdef public int coins
    cdef public int lives_left
    cdef public int score
    cdef public int time_left
    cdef public int level_progress
    cdef public int _level_progress_max
    cdef public int fitness
