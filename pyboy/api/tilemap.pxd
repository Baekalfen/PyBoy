#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint64_t

from pyboy.core.mb cimport Motherboard


cdef class TileMap:
    cdef object pyboy
    cdef Motherboard mb
    cdef bint signed_tile_data
    cdef bint _use_tile_objects
    cdef uint64_t frame_count_update
    cpdef _refresh_lcdc(self)
    cdef __refresh_lcdc(self)
    cdef readonly int map_offset
    cdef str _select
    cdef readonly tuple shape
