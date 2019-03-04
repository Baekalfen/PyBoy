# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport PyBoy.MB

cdef short IF_address, IE_address, NoInterrupt, InterruptVector

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
    cdef PyBoy.MB mb
