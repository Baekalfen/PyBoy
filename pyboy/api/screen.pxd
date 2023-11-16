#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
cimport numpy as np

from pyboy.core.mb cimport Motherboard


cdef class Screen:
    cdef Motherboard mb
    cpdef ((int, int), (int, int)) get_tilemap_position(self)
    # cdef readonly list tilemap_position_list
    # cdef readonly uint8_t[:,:] tilemap_position_list
    cdef readonly uint32_t[:,:] raw_buffer
    cdef readonly (int, int) raw_buffer_dims
    cdef readonly str raw_buffer_format
    # cdef readonly uint8_t[144][160][4] memoryview
    # cpdef np.ndarray[np.uint8_t, ndim=3] get_ndarray(self)
    cdef readonly object ndarray
    cdef readonly object image
