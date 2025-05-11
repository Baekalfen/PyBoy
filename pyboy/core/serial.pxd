#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport int64_t, uint8_t, uint16_t, uint32_t, uint64_t

from pyboy.utils cimport IntIOInterface

import cython

from pyboy.logging.logging cimport Logger

cdef uint64_t MAX_CYCLES, CYCLES_8192HZ
cdef Logger logger

cdef class Serial:
    cdef uint64_t SB, SC
    cdef int64_t _cycles_to_interrupt
    cdef uint64_t last_cycles, clock, clock_target
    cdef bint transfer_enabled, double_speed, internal_clock

    cdef bint tick(self, uint64_t) noexcept nogil

    cdef void set_SB(self, uint8_t) noexcept nogil
    cdef void set_SC(self, uint8_t) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1
