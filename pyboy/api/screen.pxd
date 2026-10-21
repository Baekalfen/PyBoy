#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
cimport numpy as np
from libc.stdint cimport uint8_t, uint32_t, uint64_t

from pyboy.core.mb cimport Motherboard


cdef class Screen:
    cdef Motherboard mb
    cpdef ((int, int), (int, int)) get_tilemap_position(self) noexcept
    # cdef readonly list tilemap_position_list
    # cdef readonly uint8_t[:,:] tilemap_position_list
    cdef readonly uint32_t[:,:] raw_buffer
    cdef readonly (int, int) raw_buffer_dims
    cdef readonly str raw_buffer_format

    cdef readonly object ndarray
    cdef readonly object image
    cdef object _torch_renderer
    cdef bint _gpu_async_enabled
    cdef uint64_t _gpu_render_generation
    cpdef void _present_gpu_frame_metal(self, object layer_address) except *
