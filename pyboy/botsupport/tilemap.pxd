#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.core.mb cimport Motherboard



cdef class TileMap:
    cdef Motherboard mb
    cdef bint signed_tile_data
    cdef bint _use_tile_objects
    cdef int map_offset
    cdef str _select
    cdef public tuple shape
