#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from libc.stdint cimport uint8_t
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper
cimport cython

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

    cpdef void start_game(self, timer_div=*, world_level=*, unlock_level_select=*)
    cpdef void reset_game(self, timer_div=*)
