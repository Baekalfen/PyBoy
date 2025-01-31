#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
from libc.stdint cimport uint8_t

from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyGameWrapper


cdef Logger logger

cdef class GameWrapperCastlevaniaTheAdventure(PyBoyGameWrapper):
    cdef readonly int level_score
    cdef readonly int time_left
    cdef readonly int lives_left
    cdef readonly int health
    cdef readonly int whipe_level
    cdef readonly int invincible_timer
