#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython

cdef size_t BUFFER_LENGTH

cdef class RewindBuffer:
    cdef list buffers
    cdef size_t tail_buffer
    cdef size_t head_buffer
    cdef size_t read_pointer

    cdef void commit(self)
    @cython.locals(head=size_t, A=size_t, B=size_t, buf=object)
    cdef object next_write_buffer(self)
    cdef bint seek_relative(self, int)
    cdef object read(self)

