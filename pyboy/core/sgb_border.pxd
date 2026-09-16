#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t, uint16_t, uint32_t
from pyboy.utils cimport IntIOInterface

cdef class SGBBorderRenderer:
    cdef object sgb
    cdef object border_buffer
    cdef object border_tile_cache
    cdef object _composited
    cdef object _frozen_frame
    cdef bint border_dirty
    cdef bint tiles_dirty
    cdef bint palettes_dirty
    cdef bint _border_copied
    cdef int _prev_mask_mode
    cdef object palettes_rgba
    
    cdef void reset(self) except *
    cpdef void update(self) except *
    cpdef void update_palettes(self, object) except *
    cpdef void update_tiles(self, object) except *
    cpdef void render_border(self, object) except *
    
    cpdef object get_composited_frame(self, object)
    