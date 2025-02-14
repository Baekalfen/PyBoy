#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint64_t, int8_t
from pyboy.core.mb cimport Motherboard

cdef class Sound:
    cdef Motherboard mb
    cdef readonly uint64_t sample_rate

    cdef readonly int8_t[:] raw_buffer
    cdef readonly (int, int) raw_buffer_dims
    cdef readonly str raw_buffer_format
    cdef readonly int raw_buffer_length
    cdef readonly object raw_ndarray
