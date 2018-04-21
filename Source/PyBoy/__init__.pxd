#! /usr/local/bin/python2
# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython
cimport PyBoy.Cartridge
cimport PyBoy.MB
cimport PyBoy.WindowEvent
from PyBoy.GameWindow.GameWindow_SDL2 cimport SdlGameWindow
# from PyBoy.GameWindow.GameWindow_PyGame cimport PyGameGameWindow
from PyBoy.GameWindow.GameWindow_dummy cimport DummyGameWindow

# cimport PyBoy.Global


cdef float SPF

cdef class PyBoy():
    cdef object debugger
    cdef object mb
    cdef object window

    cdef bint profiling
    cdef float exp_avg_emu
    cdef float exp_avg_cpu
    cdef unsigned int t_start
    cdef unsigned int t_start_
    cdef unsigned int t_VSynced
    cdef unsigned int t_frameDone
    cdef unsigned int counter
    cdef bint limitEmulationSpeed

    @cython.locals(done=cython.bint)
    cpdef bint tick(self)

    cdef object getWindow(self, str, unsigned int)

    cdef void stop(self, save=*)


#    ###########################
#    #
#    # Scripts and bot methods

    cpdef object getScreenBuffer(self)
    cpdef unsigned char getMemoryValue(self, unsigned short)
    cpdef void setMemoryValue(self, unsigned short, unsigned char)
    cpdef void sendInput(self, unsigned int)
    cpdef object getMotherBoard(self)
    cpdef object getSprite(self, unsigned int)
    cpdef object getTileView(self, bint)
    cpdef tuple getScreenPosition(self)
