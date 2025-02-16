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


cdef class GameWrapperMetroidII(PyBoyGameWrapper):
    cdef int _game_over
    cdef readonly int x_pos_pixels
    cdef readonly int y_pos_pixels
    cdef readonly int x_pos_area
    cdef readonly int y_pos_area
    cdef readonly int pose

    cdef readonly int samus_facing
    cdef readonly int major_upgrades
    cdef readonly int beam
    cdef readonly int e_tanks
    cdef readonly int hp
    cdef readonly int full_e_tanks
    cdef readonly int missiles
    cdef readonly int missile_capacity
    cdef readonly int displayed_hp
    cdef readonly int displayed_missiles
    cdef readonly int global_metroid_count
    cdef readonly int local_metroid_count


    
