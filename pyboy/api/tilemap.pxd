#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython
from libc.stdint cimport uint64_t

from pyboy.core.lcd cimport LCDCRegister
from pyboy.core.mb cimport Motherboard


cdef int HIGH_TILEMAP, LCDC_OFFSET, LOW_TILEDATA_NTILES, LOW_TILEMAP

cdef class TileMap:
    cdef object pyboy
    cdef Motherboard mb
    cdef bint signed_tile_data
    cdef bint _use_tile_objects
    cdef uint64_t frame_count_update
    cpdef int _refresh_lcdc(self) except -1
    @cython.locals(LCDC=LCDCRegister)
    cdef int __refresh_lcdc(self) except -1
    cdef readonly int map_offset
    cdef str _select
    cdef readonly tuple shape
