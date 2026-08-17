#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython
from libc.stdint cimport int64_t, uint8_t, uint16_t, uint32_t, uint64_t

from pyboy.logging.logging cimport Logger
from pyboy.utils cimport IntIOInterface

from cython cimport final

cdef uint64_t MAX_CYCLES, CYCLES_8192HZ
cdef Logger logger

cdef uint64_t SENDING, RECEIVING, PASSIVE
cdef uint64_t TRANSPORT_MASTER, HANDSHAKE_COMPLETE, CLOCK_MASTER, HANDSHAKE_STARTED

cdef class Serial:
    cdef uint64_t SB, SC
    cdef bint cgb_mode
    cdef int64_t _cycles_to_interrupt
    cdef uint64_t last_cycles, clock, clock_target
    cdef bint transfer_enabled, double_speed, internal_clock

    cdef bint tick(self, uint64_t) noexcept nogil
    cdef void stop(self) noexcept

    cdef void set_SB(self, uint8_t) noexcept nogil
    cdef void set_SC(self, uint8_t) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1


cdef class SerialSharedMemory(Serial):
    cdef object shared_memory
    cdef uint8_t shared_slot
    cdef uint8_t bits_transferred
    cdef bint interrupt_based
