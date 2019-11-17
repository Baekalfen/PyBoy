#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython

from libc.stdint cimport uint8_t
cdef size_t BUFFER_LENGTH

cdef class RewindBuffer:
    cdef list buffers
    cdef size_t tail_buffer
    cdef size_t head_buffer
    cdef size_t read_pointer

    cdef void commit(self)
    @cython.locals(head=size_t, A=size_t, B=size_t, buf=IntIOInterface)
    cdef IntIOInterface next_write_buffer(self)
    cdef bint seek_relative(self, int)
    @cython.locals(buf=IntIOInterface)
    cdef IntIOInterface read(self)

cdef class IntIOInterface:
    cdef size_t write(self, uint8_t)
    cdef uint8_t read(self)
    cdef void seek(self, int)
    cdef void flush(self)

cdef class IntIOWrapper(IntIOInterface):
    cdef object buffer

cdef class CompressedBuffer(IntIOInterface):
    cdef IntIOInterface buffer
    cdef size_t zeros

