#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
cimport numpy as np
from libc.stdint cimport uint8_t, uint32_t

from pyboy.core.mb cimport Motherboard


cdef class Screen:
    cdef Motherboard mb
    cpdef ((int, int), (int, int)) tilemap_position(self)
    cpdef list tilemap_position_list(self)
    # cpdef int[:,:] tilemap_position_list(self)
    cpdef uint32_t[:,:] raw_screen_buffer(self)
    cpdef (int, int) raw_screen_buffer_dims(self)
    cpdef str raw_screen_buffer_format(self)
    cpdef np.ndarray[np.uint8_t, ndim=3] screen_ndarray(self)
    cpdef object screen_image(self)
