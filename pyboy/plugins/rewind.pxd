#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython
from libc.stdint cimport int64_t, uint8_t, uint64_t

from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyPlugin
from pyboy.utils cimport IntIOInterface, malloc, free


cdef Logger logger

cdef class Rewind(PyBoyPlugin):
    cdef double rewind_speed
    cdef FixedAllocBuffers rewind_buffer


##############################################################
# Homogeneous cyclic buffer
##############################################################

cdef int64_t FIXED_BUFFER_SIZE = 8 * 1024 * 1024
cdef int64_t FIXED_BUFFER_MIN_ALLOC = 256*1024
cdef int64_t FILL_VALUE

DEF FIXED_BUFFER_SIZE = 8 * 1024 * 1024
DEF FIXED_BUFFER_MIN_ALLOC = 256*1024

cdef class FixedAllocBuffers(IntIOInterface):
    cdef uint8_t[:] buffer
    cdef list sections
    cdef int64_t current_section
    cdef int64_t tail_pointer
    # cdef int64_t head_pointer
    cdef int64_t section_head
    cdef int64_t section_tail
    cdef int64_t section_pointer
    cdef double avg_section_size

    @cython.locals(section_size=double)
    cdef void new(self) noexcept
    cdef void commit(self) noexcept
    @cython.locals(_=int64_t, abs_frames=int64_t, head=int64_t, tail=int64_t)
    cdef bint seek_frame(self, int64_t) noexcept

cdef class CompressedFixedAllocBuffers(FixedAllocBuffers):
    cdef uint64_t zeros

    @cython.locals(chunks=int64_t, rest=int64_t)
    cpdef int flush(self) except -1

cdef class DeltaFixedAllocBuffers(CompressedFixedAllocBuffers):
    cdef int64_t internal_pointer
    cdef int64_t prev_internal_pointer
    cdef uint8_t[:] internal_buffer
    cdef bint internal_buffer_dirty
    cdef int64_t base_frame
    cdef int64_t injected_zero_frame

    cdef void flush_internal_buffer(self) noexcept
