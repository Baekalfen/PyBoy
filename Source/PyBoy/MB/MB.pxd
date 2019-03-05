# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


# from .. cimport Cartridge
# from ..Cartridge cimport MBC3
cimport CPU
# from PyBoy cimport RAM, Cartridge, BootROM, LCD, Interaction
cimport Timer
from PyBoy.GameWindow.GameWindow_SDL2 cimport SdlGameWindow

cimport PyBoy.Cartridge.GenericMBC
# from PyBoy.Cartridge import GenericMBC
# from CPU.flags cimport VBlank, TIMER, HightoLow, LCDC


cdef short IF_address, IE_address, NoInterrupt, InterruptVector
cdef unsigned short STAT, LY, LYC
cdef short VBlank, LCDC, TIMER, Serial, HightoLow

cdef class Motherboard:
    cdef object debugger
    cdef object interaction
    cdef object bootROM
    cdef object ram
    cdef object lcd
    cdef CPU.CPU cpu
    cdef Timer.Timer timer
    cdef SdlGameWindow MainWindow
    cdef PyBoy.Cartridge.GenericMBC.GenericMBC cartridge
    cdef bint bootROMEnabled

    cdef void buttonEvent(self, object)
    cdef void stop(self, bint)
    cdef setSTATMode(self, int)
    cdef void checkLYC(self, int)
    cdef void calculateCycles(self, int)
    cpdef void tickFrame(self)

    cdef object get(self, unsigned short)
    cdef void set(self, unsigned short, unsigned char)

    cdef void transferDMAtoOAM(self, char, unsigned short dst=*)
    cdef void saveState(self, char*)
    cdef void loadState(self, char*)

