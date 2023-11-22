#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
from libc.stdint cimport uint8_t

from pyboy.plugins.base_plugin cimport PyBoyGameWrapper


cdef int ROWS, COLS


cdef class GameWrapperKirbyDreamLand(PyBoyGameWrapper):
    cdef readonly int score
    cdef readonly int health
    cdef readonly int lives_left
    cdef readonly int fitness
    cdef readonly int _game_over