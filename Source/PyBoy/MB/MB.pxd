# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport CPU
cimport Timer
cimport PyBoy.Cartridge.GenericMBC
cimport PyBoy.BootROM
cimport PyBoy.RAM
cimport PyBoy.LCD
cimport PyBoy.Interaction
from PyBoy.GameWindow.GameWindow_SDL2 cimport SdlGameWindow

cdef short IF_address, IE_address, NoInterrupt, InterruptVector
cdef unsigned short STAT, LY, LYC
cdef short VBlank, LCDC, TIMER, Serial, HightoLow

cdef class Motherboard:
    cdef object debugger
    cdef PyBoy.Interaction.Interaction interaction
    cdef PyBoy.BootROM.BootROM bootROM
    cdef PyBoy.RAM.RAM ram
    cdef PyBoy.LCD.LCD lcd
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
    cdef void tickFrame(self)

    cdef unsigned char get(self, unsigned short)
    cdef void set(self, unsigned short, unsigned char)

    cdef void transferDMAtoOAM(self, char, unsigned short dst=*)
    cdef void saveState(self, unicode)
    cdef void loadState(self, unicode)
    # cdef void saveState(self, char*)
    # cdef void loadState(self, char*)

