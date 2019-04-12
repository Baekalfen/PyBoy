#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


cimport pyboy.motherboard.motherboard
cimport opcodes
import cython


cdef unsigned short IF_ADDRESS, IE_ADDRESS
cdef short FLAGC, FLAGH, FLAGN, FLAGZ
cdef short VBLANK, LCDC, TIMER, SERIAL, HIGHTOLOW

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2


cdef class CPU:

    cdef public bint interruptmasterenable, breakAllow, breakOn, halted, stopped, lala, profiling
    cdef unsigned int oldPC, breakNext

    cdef object debugCallStack
    cdef int[512] hitRate

    @cython.locals(intr_flag_enabled=cython.bint, intr_flag=cython.bint)
    cdef bint test_interrupt(self, unsigned char, unsigned char, short)

    @cython.locals(
        anyInterruptToHandle=cython.bint,
        ie_v=cython.uchar,
        if_v=cython.uchar,
        v=cython.uchar,
        intr_flag=cython.bint,
        intr_flag_enabled=cython.bint,
        flag=cython.short,
        vector=cython.ushort)
    cdef int checkforinterrupts(self)

    @cython.locals(opcode=cython.ushort)
    cdef char fetch_and_execute(self, unsigned int)
    cdef int tick(self)
    cdef void save_state(self, file)
    cdef void load_state(self, file)

    # Only char (8-bit) needed, but I'm not sure all intermittent
    # results do not overflow
    cdef short A, F, B, C, D, E

    # Only short (16-bit) needed, but I'm not sure all intermittent
    # results do not overflow
    cdef int HL, SP, PC

    cdef pyboy.motherboard.motherboard.Motherboard motherboard

    cdef void setBC(CPU, int x)
    cdef void setDE(CPU, int x)

    cdef bint fC(self)
    cdef bint fH(self)
    cdef bint fN(self)
    cdef bint fZ(self)
    cdef bint fNC(self)
    cdef bint fNZ(self)

    ### CPU Flags
    cdef bint test_flag(self, int flag)
    cdef void set_flag(self, int flag, bint value=*)
    cdef void clear_flag(self, int flag)

    ### Interrupt flags
    cdef void set_interruptflag(self, int flag)

    @cython.locals(v=cython.int)
    cdef bint test_ramregisterflag(self, int address, int flag)
    cdef void set_ramregisterflag(self, int address, int flag, bint value=*)
    cdef void clear_ramregisterflag(self, int address, int flag)
    @cython.locals(v=cython.int)
    cdef bint test_ramregisterflag_enabled(self, int address, int flag)
