#! /usr/local/bin/python2
# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cdef enum WindowEvent:
    Quit, PressArrowUp, PressArrowDown, PressArrowRight, PressArrowLeft, PressButtonA, PressButtonB, PressButtonSelect, PressButtonStart, ReleaseArrowUp, ReleaseArrowDown, ReleaseArrowRight, ReleaseArrowLeft, ReleaseButtonA, ReleaseButtonB, ReleaseButtonSelect, ReleaseButtonStart, DebugToggle, PressSpeedUp, ReleaseSpeedUp, SaveState, LoadState, Pass

cimport cython
cimport PyBoy.Cartridge
# cimport PyBoy.WindowEvent
from PyBoy.MB.MB cimport Motherboard
from PyBoy.GameWindow.GameWindow_SDL2 cimport SdlGameWindow
from PyBoy.GameWindow.GameWindow_dummy cimport DummyGameWindow

# cimport PyBoy.Global


cdef float SPF

cdef class PyBoy:
    cdef object debugger
    cdef Motherboard mb
    cdef SdlGameWindow window

    cdef bint profiling
    cdef float exp_avg_emu
    cdef float exp_avg_cpu
    cdef float t_start
    cdef float t_start_
    cdef float t_VSynced
    cdef float t_frameDone
    cdef unsigned int counter
    cdef bint limitEmulationSpeed

    @cython.locals(done=cython.bint, event=WindowEvent)
    cpdef bint tick(self)

    cdef SdlGameWindow getWindow(self, str, unsigned int)

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
