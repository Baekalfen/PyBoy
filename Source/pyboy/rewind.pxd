#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython

from libc.stdint cimport uint8_t, int64_t
cdef size_t BUFFER_LENGTH

# cdef class RewindBuffer:
#     cdef void commit(self)
#     cdef IntIOInterface next(self)
#     cdef bint seek_relative(self, int)
#     cdef IntIOInterface read(self)


cdef class IntIOInterface:
    cdef size_t write(self, uint8_t)
    cdef uint8_t read(self)
    cdef void seek(self, int)
    cdef void flush(self)

cdef class FixedAllocBuffers(IntIOInterface):
    cdef uint8_t[64*1024*128] buffer
    cdef size_t tail_pointer
    cdef size_t head_pointer
    cdef size_t read_pointer
    cdef int64_t section_head
    cdef int64_t section_tail
    cdef int64_t section_pointer

    cdef void commit(self)
    cdef void new(self)
    cdef void seek_relative(self, int)

cdef class IntIOWrapper(IntIOInterface):
    cdef object buffer

# cdef class TimeBuffers(RewindBuffer):
#     cdef list buffers
#     cdef size_t tail_buffer
#     cdef size_t head_buffer
#     cdef size_t read_pointer

#     @cython.locals(head=size_t, A=size_t, B=size_t, buf=IntIOInterface)
#     cdef IntIOInterface next(self)
#     @cython.locals(buf=IntIOInterface)
#     cdef IntIOInterface read(self)

# cdef class CompressedBuffer(IntIOInterface):
#     cdef IntIOInterface buffer
#     cdef size_t zeros

