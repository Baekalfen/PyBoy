#! /usr/local/bin/python2
# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc cimport time
cimport cython
cimport PyBoy.Cartridge
cimport PyBoy.Window.Window
# cimport PyBoy.WindowEvent
from PyBoy.MB.MB cimport Motherboard
from PyBoy.Window.GenericWindow cimport GenericWindow

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef float SPF

cdef class PyBoy:
    cdef object debugger
    cdef unicode ROM
    cdef Motherboard mb
    cdef GenericWindow window

    cdef bint profiling
    cdef double avg_emu
    cdef double avg_cpu
    cdef unsigned int counter
    cdef bint limitEmulationSpeed
    cdef int maxEmulationSpeed
    cdef object screen_recorder

    @cython.locals(done=cython.bint, event=int, t_start=long, t_cpu=long, t_emu=long, secs=float)
    cpdef bint tick(self)
    cpdef void stop(self, save=*)


#    ###########################
#    #
#    # Scripts and bot methods

#    cpdef object getScreenBuffer(self)
#    cpdef unsigned char getMemoryValue(self, unsigned short)
#    cpdef void setMemoryValue(self, unsigned short, unsigned char)
#    cpdef void sendInput(self, unsigned int)
#    cpdef object getMotherBoard(self)
#    cpdef object getSprite(self, unsigned int)
#    cpdef object getTileView(self, bint)
#    cpdef tuple getScreenPosition(self)
