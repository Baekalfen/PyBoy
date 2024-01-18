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


cdef class GameWrapperKirbyDreamLand(PyBoyGameWrapper):
    cdef readonly int score
    cdef readonly int health
    cdef readonly int lives_left
    cdef readonly int _game_over