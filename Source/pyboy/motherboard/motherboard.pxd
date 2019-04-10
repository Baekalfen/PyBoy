#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import cython
cimport PyBoy.MB.CPU
cimport PyBoy.MB.Timer
cimport PyBoy.Cartridge.GenericMBC
cimport PyBoy.BootROM
cimport PyBoy.RAM
cimport PyBoy.LCD
cimport PyBoy.Interaction
cimport PyBoy.Window.GenericWindow

cdef unsigned short STAT, LY, LYC
cdef short VBlank, LCDC, TIMER, Serial, HightoLow

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef class Motherboard:
    cdef object debugger
    cdef PyBoy.Interaction.Interaction interaction
    cdef PyBoy.BootROM.BootROM bootROM
    cdef PyBoy.RAM.RAM ram
    cdef PyBoy.LCD.LCD lcd
    cdef PyBoy.MB.CPU.CPU cpu
    cdef PyBoy.MB.Timer.Timer timer
    cdef PyBoy.Window.GenericWindow.GenericWindow window
    cdef PyBoy.Cartridge.GenericMBC.GenericMBC cartridge
    cdef bint bootROMEnabled
    cdef unicode serialBuffer

    cdef void buttonEvent(self, int)
    cdef void stop(self, bint)
    cdef void setSTATMode(self, int)
    cdef void checkLYC(self, int)
    @cython.locals(cycles=cython.int)
    cdef void calculateCycles(self, int)
    cdef void tickFrame(self)

    cpdef unsigned char getitem(self, unsigned short)
    cpdef void setitem(self, unsigned short, unsigned char)

    @cython.locals(offset=cython.int, dst=cython.int, n=cython.int)
    cdef void transferDMAtoOAM(self, unsigned char)
    cdef void saveState(self, unicode)
    cdef void loadState(self, unicode)
    # cdef void saveState(self, char*)
    # cdef void loadState(self, char*)

