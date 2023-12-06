#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython

cimport pyboy.utils
from pyboy.core.mb cimport Motherboard


cdef class Sprite:
    cdef Motherboard mb
    cdef readonly int _offset

    cdef readonly int sprite_index
    cdef readonly int y
    cdef readonly int x
    cdef readonly int tile_identifier
    cdef readonly bint attr_obj_bg_priority
    cdef readonly bint attr_y_flip
    cdef readonly bint attr_x_flip
    cdef readonly int attr_palette_number
    cdef readonly bint attr_cgb_bank_number
    cdef readonly tuple shape
    cdef readonly list tiles
    cdef readonly bint on_screen
    cdef int _sprite_index
