#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import cython
cimport pyboy.motherboard.cpu
cimport pyboy.motherboard.timer
cimport pyboy.cartridge.genericmbc
cimport pyboy.bootrom
cimport pyboy.ram
cimport pyboy.lcd
cimport pyboy.interaction
cimport pyboy.window.genericwindow


cdef unsigned short STAT, LY, LYC
cdef short VBlank, LCDC, TIMER, Serial, HightoLow

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2


cdef class Motherboard:
    cdef object debugger
    cdef pyboy.interaction.Interaction interaction
    cdef pyboy.bootrom.BootROM bootROM
    cdef pyboy.ram.RAM ram
    cdef pyboy.lcd.LCD lcd
    cdef pyboy.motherboard.cpu.CPU cpu
    cdef pyboy.motherboard.timer.Timer timer
    cdef pyboy.window.genericwindow.GenericWindow window
    cdef pyboy.cartridge.genericmbc.GenericMBC cartridge
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
