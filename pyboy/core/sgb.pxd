#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t
import cython
from pyboy.utils cimport IntIOInterface
from pyboy.core.mb cimport Motherboard
from pyboy.core.lcd cimport LCD

# SGB Command Constants
# Based on https://gbdev.io/pandocs/SGB_Functions.html (SGB Command Summary)
cdef class SGB:
    cdef readonly bint enabled
    cdef readonly Motherboard mb
    cdef readonly object state
    cdef uint8_t packet_buffer[16]
    cdef uint8_t completed_packet[16]
    cdef uint8_t bit_count
    cdef bint pulse_armed
    cdef bint write_armed
    cdef bint packet_complete
    cdef bint collecting
    cdef bint command_ready
    cdef bint multiplayer
    cdef uint8_t player_count
    cdef uint8_t active_player
    cdef void reset(self) except *
    @cython.locals(pulse=uint8_t, byte_pos=cython.int, bit_pos=cython.int, i=cython.int)
    cdef uint8_t process_p1_write(self, uint8_t) noexcept nogil
    cdef uint8_t process_p1_read(self, uint8_t) except *
    cdef void process_command(self) except *
    cdef void handle_mlt_req(self) except *
    cdef void handle_pal_set(self) except *
    cdef void handle_chr_trn(self) except *
    cdef void handle_pct_trn(self) except *
    cdef void handle_mask_en(self) except *
    cdef void handle_obj_trn(self) except *
    cdef void handle_pal_trn(self) except *
    cdef void handle_attr_trn(self) except *
    cdef void handle_attr_set(self) except *
    cdef void handle_icon_en(self) except *
    cdef void tick_frame(self) except *
    cdef void _run_pending_capture(self) except *
    cdef void _capture_chr(self, object, object, bint) except *
    cdef void _capture_pct(self, object, object) except *

    cpdef tuple get_border_data(self)
    cpdef void set_joypad_data(self, uint8_t, uint8_t) noexcept
    cpdef void set_current_joypad(self, uint8_t) noexcept
    
    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1
    cdef void stop(self) noexcept