#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
cimport numpy as np

from pyboy.core.mb cimport Motherboard


cdef class Screen:
    cdef Motherboard mb
    cpdef np.ndarray[np.uint8_t, ndim=3] screen_ndarray(self)
