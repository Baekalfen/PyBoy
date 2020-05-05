#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from libc.stdint cimport uint8_t
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper
cimport cython

cdef int ROWS, COLS


cdef class GameWrapperKirbyDreamLand(PyBoyGameWrapper):
    cdef public int score
    cdef public int health
    cdef public int lives_left
    cdef public int fitness
