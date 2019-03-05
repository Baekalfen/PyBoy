# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cimport PyBoy.MB

cimport opcodes


cdef short IF_address, IE_address, NoInterrupt, InterruptVector
cdef short flagC, flagH, flagN, flagZ
cdef short VBlank, LCDC, TIMER, Serial, HightoLow

cdef unsigned char getA(CPU)
cdef unsigned char getF(CPU)
cdef unsigned char getB(CPU)
cdef unsigned char getC(CPU)
cdef unsigned char getD(CPU)
cdef unsigned char getE(CPU)
cdef unsigned char getH(CPU)
cdef unsigned char getL(CPU)
cdef unsigned int getHL(CPU)
cdef unsigned int getSP(CPU)
cdef unsigned int getPC(CPU)
cdef unsigned int getAF(CPU)
cdef unsigned int getBC(CPU)
cdef unsigned int getDE(CPU)

cdef void setA(CPU, int x)
cdef void setF(CPU, int x)
cdef void setB(CPU, int x)
cdef void setC(CPU, int x)
cdef void setD(CPU, int x)
cdef void setE(CPU, int x)
cdef void setH(CPU, int x)
cdef void setL(CPU, int x)
cdef void setHL(CPU, int x)
cdef void setSP(CPU, int x)
cdef void setPC(CPU, int x)
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
    cdef int fetchAndExecuteInstruction(self, unsigned int)
    # cdef int executeInstruction(self, object)
    # cdef object fetchInstruction(self, int pc)
    cdef int tick(self)

    cdef unsigned char _A, _F, _B, _C, _D, _E
    cdef unsigned int _HL, _SP, _PC
    cdef object mb

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


