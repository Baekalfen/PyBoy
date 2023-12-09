#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython

cimport pyboy.utils
from pyboy.core.mb cimport Motherboard


cdef class Sprite:
    cdef Motherboard mb
    cdef public int _offset

    cdef public int sprite_index
    cdef public int y
    cdef public int x
    cdef public int tile_identifier
    cdef public bint attr_obj_bg_priority
    cdef public bint attr_y_flip
    cdef public bint attr_x_flip
    cdef public bint attr_palette_number
    cdef public tuple shape
    cdef public list tiles
    cdef public bint on_screen
    cdef int _sprite_index
