# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from PyBoy.MB.MB cimport Motherboard
cimport opcodes
import cython

cdef unsigned short IF_address, IE_address
cdef short flagC, flagH, flagN, flagZ
cdef short VBlank, LCDC, TIMER, Serial, HightoLow

# cdef unsigned char getA(CPU)
# cdef unsigned char getF(CPU)
# cdef unsigned char getB(CPU)
# cdef unsigned char getC(CPU)
# cdef unsigned char getD(CPU)
# cdef unsigned char getE(CPU)
cdef unsigned char getH(CPU)
cdef unsigned char getL(CPU)
# cdef unsigned int getHL(CPU)
# cdef unsigned int getSP(CPU)
# cdef unsigned int getPC(CPU)
cdef unsigned int getAF(CPU)
cdef unsigned int getBC(CPU)
cdef unsigned int getDE(CPU)

# cdef void setA(CPU, int x)
# cdef void setF(CPU, int x)
# cdef void setB(CPU, int x)
# cdef void setC(CPU, int x)
# cdef void setD(CPU, int x)
# cdef void setE(CPU, int x)
cdef void setH(CPU, int x)
cdef void setL(CPU, int x)
# cdef void setHL(CPU, int x)
# cdef void setSP(CPU, int x)
# cdef void setPC(CPU, int x)
cdef void setAF(CPU, int x)
cdef void setBC(CPU, int x)
cdef void setDE(CPU, int x)


cdef (int, int) _dummy_declaration

cdef class CPU:

    cdef public bint interruptMasterEnable, breakAllow, breakOn, halted, stopped, lala, profiling
    cdef unsigned int oldPC, breakNext

    cdef object debugCallStack
    # cdef void getDump(self, instruction=*)

    @cython.locals(intr_flag_enabled=cython.bint, intr_flag=cython.bint)
    cdef bint testInterrupt(self, unsigned char, unsigned char, short)

    @cython.locals(anyInterruptToHandle=cython.bint, ie_v=cython.uchar, if_v=cython.uchar, v=cython.uchar, intr_flag=cython.bint, intr_flag_enabled=cython.bint, flag=cython.short, vector=cython.ushort)
    cdef int checkForInterrupts(self)

    @cython.locals(opcode=cython.ushort)
    cdef char fetchAndExecuteInstruction(self, unsigned int)
    # cdef int executeInstruction(self, object)
    # cdef object fetchInstruction(self, int pc)
    cdef int tick(self)

    cdef short A, F, B, C, D, E # Only char (8-bit) needed, but I'm not sure all intermittent results do not overflow
    cdef int HL, SP, PC # Only short (16-bit) needed, but I'm not sure all intermittent results do not overflow
    cdef Motherboard mb

    cdef bint fC(self)
    cdef bint fH(self)
    cdef bint fN(self)
    cdef bint fZ(self)
    cdef bint fNC(self)
    cdef bint fNZ(self)

    ### CPU Flags
    # cdef extern short flagC, flagH, flagN, flagZ
    # cdef extern short VBlank, LCDC, TIMER, Serial, HightoLow

    cdef bint testFlag(self, int flag)
    cdef void setFlag(self, int flag, bint value=*)
    cdef void clearFlag(self, int flag)

    # ### Interrupt flags

    cdef void setInterruptFlag(self, int flag)

    @cython.locals(v=cython.int)
    cdef bint testRAMRegisterFlag(self, int address, int flag)
    cdef void setRAMRegisterFlag(self, int address, int flag, bint value=*)
    cdef void clearRAMRegisterFlag(self, int address, int flag)
    @cython.locals(v=cython.int)
    cdef bint testRAMRegisterFlagEnabled(self, int address, int flag)


