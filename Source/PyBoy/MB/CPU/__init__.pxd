# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cimport PyBoy.MB

cdef short IF_address, IE_address, NoInterrupt, InterruptVector
cdef short flagC, flagH, flagN, flagZ
cdef short VBlank, LCDC, TIMER, Serial, HightoLow

cdef void setH(self, int x)
cdef void setL(self, int x)
cdef void setAF(self, int x)
cdef void setBC(self, int x)
cdef void setDE(self, int x)

cdef class CPU:

    cdef public bint interruptMasterEnable, breakAllow, breakOn, halted, stopped, lala, profiling
    cdef unsigned short oldPC, breakNext

    cdef object debugCallStack
    # cdef void getDump(self, instruction=*)

    cdef int checkForInterrupts(self)
    cdef int testAndTriggerInterrupt(self, int, int)
    cdef int executeInstruction(self, object)
    cdef object fetchInstruction(self, int pc)
    cdef int tick(self)

    cdef unsigned char A, F, B, C, D, E
    cdef unsigned short HL, SP, PC
    cdef object mb


    ### CPU Flags
    # cdef extern short flagC, flagH, flagN, flagZ
    # cdef extern short VBlank, LCDC, TIMER, Serial, HightoLow

    cdef short testFlag(self, int flag)
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


