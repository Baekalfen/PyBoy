#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.core.mb cimport Motherboard

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2


cdef class TileMap:
    cdef Motherboard mb
    cdef bint signed_tile_data
    cdef bint _use_tile_objects
    cdef int map_offset
