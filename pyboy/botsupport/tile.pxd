#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint32_t

from pyboy.core.mb cimport Motherboard



cdef class Tile:
    cdef Motherboard mb

    cdef public int tile_identifier
    cdef public int data_address
    cdef public tuple shape
    cpdef object image(self)
    cpdef object image_ndarray(self)
    cpdef uint32_t[:,:] image_data(self)
