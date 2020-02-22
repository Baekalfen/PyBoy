#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython

from libc.stdint cimport uint8_t, int64_t


cdef class IntIOInterface:
    cdef int64_t write(self, uint8_t)
    cdef uint8_t read(self)
    cdef void seek(self, int64_t)
    cdef void flush(self)

##############################################################
# Buffer wrappers
##############################################################

cdef class IntIOWrapper(IntIOInterface):
    cdef object buffer

