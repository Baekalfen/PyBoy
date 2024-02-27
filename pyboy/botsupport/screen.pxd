#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
cimport numpy as cnp
from pyboy.core.mb cimport Motherboard

cnp.import_array()


cdef class Screen:
    cdef Motherboard mb
    cpdef cnp.ndarray[cnp.uint8_t, ndim=3] screen_ndarray(self)
