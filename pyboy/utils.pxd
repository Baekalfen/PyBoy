#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython

from libc.stdint cimport uint8_t, int64_t

##############################################################
# Buffer classes

cdef class IntIOInterface:
    cdef int64_t write(self, uint8_t)
    cdef uint8_t read(self)
    cdef void seek(self, int64_t)
    cdef void flush(self)


cdef class IntIOWrapper(IntIOInterface):
    cdef object buffer

##############################################################
# Misc

cpdef uint8_t get_color_code(uint8_t, uint8_t, uint8_t)
