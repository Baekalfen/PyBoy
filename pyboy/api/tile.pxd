#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import cython

from libc.stdint cimport uint8_t, uint16_t, uint32_t

from pyboy cimport utils
from pyboy.core.mb cimport Motherboard


cdef uint16_t VRAM_OFFSET, LOW_TILEDATA

cdef class Tile:
    cdef Motherboard mb

    cdef public str raw_buffer_format
    cdef public int tile_identifier
    cdef public int data_address
    cdef public tuple shape
    cpdef object image(self) noexcept
    cpdef object image_ndarray(self) noexcept

    cdef uint32_t[:,:] data # TODO: Add to locals instead
    @cython.locals(byte1=uint8_t, byte2=uint8_t, colorcode=uint32_t)
    cdef uint32_t[:,:] _image_data(self) noexcept
