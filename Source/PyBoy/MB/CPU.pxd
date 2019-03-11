# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cimport PyBoy.MB

cimport opcodes


cdef unsigned short IF_address, IE_address, NoInterrupt, InterruptVector
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



cdef class CPU:

    cdef public bint interruptMasterEnable, breakAllow, breakOn, halted, stopped, lala, profiling
    cdef unsigned int oldPC, breakNext

    cdef object debugCallStack
    # cdef void getDump(self, instruction=*)

    cdef int checkForInterrupts(self)
    cdef int testAndTriggerInterrupt(self, int, int)
    cdef char fetchAndExecuteInstruction(self, unsigned int)
    # cdef int executeInstruction(self, object)
    # cdef object fetchInstruction(self, int pc)
    cdef int tick(self)

    cdef short A, F, B, C, D, E # Only char (8-bit) needed, but I'm not sure all intermittent results do not overflow
    cdef int HL, SP, PC # Only short (16-bit) needed, but I'm not sure all intermittent results do not overflow
    cdef object mb

    cdef int fC(self)
    cdef int fH(self)
    cdef int fN(self)
    cdef int fZ(self)
    cdef int fNC(self)
    cdef int fNZ(self)

    ### CPU Flags
    # cdef extern short flagC, flagH, flagN, flagZ
    # cdef extern short VBlank, LCDC, TIMER, Serial, HightoLow

    cdef bint testFlag(self, int flag)
    cdef void setFlag(self, int flag, bint value=*)
    cdef void clearFlag(self, int flag)

    # ### Interrupt flags

    cdef bint testInterruptFlag(self, int flag)
    cdef void setInterruptFlag(self, int flag)
    cdef void clearInterruptFlag(self, int flag)

    cdef bint testInterruptFlagEnabled(self, int flag)

    cdef bint testRAMRegisterFlag(self, int address, int flag)
    cdef void setRAMRegisterFlag(self, int address, int flag, bint value=*)
    cdef void clearRAMRegisterFlag(self, int address, int flag)
    cdef bint testRAMRegisterFlagEnabled(self, int address, int flag)


