#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


cimport pyboy.core.mb
cimport opcodes

from libc.stdint cimport uint8_t, uint16_t, uint32_t
from pyboy.utils cimport IntIOInterface

import cython


cdef uint16_t IF_ADDRESS, IE_ADDRESS
cdef short FLAGC, FLAGH, FLAGN, FLAGZ
cdef short VBLANK, LCDC, TIMER, SERIAL, HIGHTOLOW

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2


cdef class CPU:

    cdef public bint interrupt_master_enable, break_allow, break_on, halted, stopped, profiling
    cdef unsigned int old_pc, break_next

    cdef object debug_callstack
    cdef int[512] hitrate

    @cython.locals(intr_flag_enabled=cython.bint, intr_flag=cython.bint)
    cdef bint test_interrupt(self, unsigned char, unsigned char, short)

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
    cdef char fetch_and_execute(self, unsigned int)
    cdef int tick(self)
    cdef void save_state(self, IntIOInterface)
    cdef void load_state(self, IntIOInterface)

    # Only char (8-bit) needed, but I'm not sure all intermittent
    # results do not overflow
    cdef short A, F, B, C, D, E

    # Only short (16-bit) needed, but I'm not sure all intermittent
    # results do not overflow
    cdef int HL, SP, PC

    cdef pyboy.core.mb.Motherboard mb

    cdef void set_bc(CPU, int x)
    cdef void set_de(CPU, int x)

    cdef bint f_c(self)
    cdef bint f_h(self)
    cdef bint f_n(self)
    cdef bint f_z(self)
    cdef bint f_nc(self)
    cdef bint f_nz(self)

    ### CPU Flags
    cdef bint test_flag(self, int flag)
    cdef void set_flag(self, int flag, bint value=*)
    cdef void clear_flag(self, int flag)

    ### Interrupt flags
    cdef void set_interruptflag(self, int flag)

    @cython.locals(v=cython.int)
    cdef bint test_ramregisterflag(self, int address, int flag)
    cdef void clear_ramregisterflag(self, int address, int flag)
