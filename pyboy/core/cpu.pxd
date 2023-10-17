#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#


cimport pyboy.core.mb
from . cimport opcodes

from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t
from libc.stdint cimport int16_t
from pyboy.utils cimport IntIOInterface

import cython


cdef uint16_t IF_ADDRESS, IE_ADDRESS
cdef int16_t FLAGC, FLAGH, FLAGN, FLAGZ
cdef uint8_t INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW



cdef class CPU:
    cdef bint is_stuck
    cdef bint interrupt_master_enable, interrupt_queued, halted, stopped

    cdef uint8_t interrupts_flag, interrupts_enabled, interrupts_flag_register, interrupts_enabled_register

    cdef inline int check_interrupts(self) noexcept
    cdef void set_interruptflag(self, int) noexcept
    cdef bint handle_interrupt(self, uint8_t, uint16_t) noexcept

    @cython.locals(opcode=uint16_t)
    cdef inline uint8_t fetch_and_execute(self) noexcept
    cdef int tick(self) noexcept
    cdef void save_state(self, IntIOInterface) noexcept
    cdef void load_state(self, IntIOInterface, int) noexcept

    # Only char (8-bit) needed, but I'm not sure all intermittent
    # results do not overflow
    cdef int16_t A, F, B, C, D, E

    # Only short (16-bit) needed, but I'm not sure all intermittent
    # results do not overflow
    cdef int HL, SP, PC

    cdef pyboy.core.mb.Motherboard mb

    cdef void set_bc(CPU, uint16_t) noexcept
    cdef void set_de(CPU, uint16_t) noexcept
