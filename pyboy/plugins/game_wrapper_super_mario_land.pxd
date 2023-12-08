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


cdef class GameWrapperSuperMarioLand(PyBoyGameWrapper):
    cdef public tuple world
    cdef public int coins
    cdef public int lives_left
    cdef public int score
    cdef public int time_left
    cdef public int level_progress
    cdef public int _level_progress_max
    cdef public int fitness

    cpdef void start_game(self, timer_div=*, world_level=*, unlock_level_select=*) noexcept
    cpdef void reset_game(self, timer_div=*) noexcept
    cpdef set_lives_left(self, int) noexcept