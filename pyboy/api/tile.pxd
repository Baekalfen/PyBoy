#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import cython

from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t

from pyboy cimport utils
from pyboy.core.mb cimport Motherboard


cdef uint16_t VRAM_OFFSET, LOW_TILEDATA

cdef class Tile:
    cdef Motherboard mb

    cdef readonly int vram_bank
    cdef readonly str raw_buffer_format
    cdef readonly int tile_identifier
    cdef readonly int data_address
    cdef readonly tuple shape
    cpdef object image(self)
    cpdef object ndarray(self)

    cdef uint32_t[:,:] data # TODO: Add to locals instead
    @cython.locals(byte1=uint8_t, byte2=uint8_t, colorcode=uint64_t)
    cdef uint32_t[:,:] _image_data(self) noexcept
