#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
from libc.stdint cimport uint8_t

from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper


cdef Logger logger


cdef class GameWrapper2048(PyBoyGameWrapper):
    cdef readonly int score
    cdef readonly bint winner
    cdef readonly bint _game_over
    cdef readonly list board
