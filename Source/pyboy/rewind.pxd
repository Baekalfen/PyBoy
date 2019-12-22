#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython

from libc.stdint cimport uint8_t, uint64_t, int64_t

cdef int64_t FIXED_BUFFER_SIZE = 64*1024*128
cdef int64_t FIXED_BUFFER_MIN_ALLOC = 64*1024
cdef int64_t FILL_VALUE

DEF FIXED_BUFFER_SIZE = 64*1024*128
DEF FIXED_BUFFER_MIN_ALLOC = 64*1024

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

##############################################################
# Homogeneous cyclic buffer
##############################################################

cdef class FixedAllocBuffers(IntIOInterface):
    cdef uint8_t[FIXED_BUFFER_SIZE] buffer
    cdef list sections
    cdef int64_t current_section
    cdef int64_t tail_pointer
    # cdef int64_t head_pointer
    cdef int64_t section_head
    cdef int64_t section_tail
    cdef int64_t section_pointer
    cdef float avg_section_size

    @cython.locals(section_size=float)
    cdef void new(self)
    cdef void commit(self)
    @cython.locals(_=int64_t, abs_frames=int64_t, head=int64_t, tail=int64_t)
    cdef bint seek_frame(self, int64_t)

cdef class CompressedFixedAllocBuffers(FixedAllocBuffers):
    cdef uint64_t zeros

    @cython.locals(chunks=int64_t, rest=int64_t)
    cdef void flush(self)

cdef class DeltaFixedAllocBuffers(CompressedFixedAllocBuffers):
    cdef int64_t internal_pointer
    cdef int64_t prev_internal_pointer
    cdef uint8_t[FIXED_BUFFER_MIN_ALLOC] internal_buffer
    cdef bint internal_buffer_dirty
    cdef int64_t base_frame
    cdef int64_t injected_zero_frame

    cdef void flush_internal_buffer(self)
