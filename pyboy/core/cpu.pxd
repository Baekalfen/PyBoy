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
cdef short FLAGC, FLAGH, FLAGN, FLAGZ
cdef short VBLANK, LCDC, TIMER, SERIAL, HIGHTOLOW



cdef class CPU:

    cdef bint interrupt_master_enable, break_allow, break_on, halted, stopped, profiling
    cdef uint64_t old_pc, break_next

    cdef object debug_callstack
    cdef int[512] hitrate

    @cython.locals(intr_flag_enabled=cython.bint, intr_flag=cython.bint)
    cdef bint test_interrupt(self, uint8_t, uint8_t, int16_t)

    @cython.locals(
        ie_v=cython.uchar,
        if_v=cython.uchar,
        v=cython.uchar,
        intr_flag=cython.bint,
        intr_flag_enabled=cython.bint,
        flag=cython.short,
        vector=cython.ushort)
    cdef int check_interrupts(self)

    @cython.locals(opcode=cython.ushort)
    cdef char fetch_and_execute(self, uint64_t)
    cdef int tick(self)
    cdef void save_state(self, IntIOInterface)
    cdef void load_state(self, IntIOInterface, int)

    # Only char (8-bit) needed, but I'm not sure all intermittent
    # results do not overflow
    cdef short A, F, B, C, D, E

    # Only short (16-bit) needed, but I'm not sure all intermittent
    # results do not overflow
    cdef int HL, SP, PC

    cdef pyboy.core.mb.Motherboard mb

    cdef void set_bc(CPU, int)
    cdef void set_de(CPU, int)

    cdef bint f_c(self)
    cdef bint f_h(self)
    cdef bint f_n(self)
    cdef bint f_z(self)
    cdef bint f_nc(self)
    cdef bint f_nz(self)

    ### CPU Flags
    cdef bint test_flag(self, int)
    cdef void set_flag(self, int, bint value=*)
    cdef void clear_flag(self, int)

    ### Interrupt flags
    cdef void set_interruptflag(self, int)

    @cython.locals(v=cython.int)
    cdef bint test_ramregisterflag(self, int, int)
    cdef void clear_ramregisterflag(self, int, int)
