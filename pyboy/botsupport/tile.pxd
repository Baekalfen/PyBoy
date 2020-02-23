#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint32_t

cimport pyboy.window.window
cimport pyboy.window.base_window
cimport pyboy.window.window_sdl2
from pyboy.core.mb cimport Motherboard

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2


cdef class Tile:
    cdef Motherboard mb
    cdef bint _signed_tile_data
    cdef int _index
    cdef int _data_address

    cpdef int get_identifier(self)
    cpdef int get_data_address(self)
    cpdef (bint, int) get_index(self)
    cpdef uint32_t[:,:] image_data(self)
    cpdef object image(self)
    cpdef object image_ndarray(self)
    # cpdef void highlight(self)
