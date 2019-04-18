#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import cython
cimport pyboy.mb.cpu
cimport pyboy.mb.timer
cimport pyboy.cartridge.base_mbc
# cimport pyboy.cartridge.cartridge
cimport pyboy.bootrom
cimport pyboy.ram
cimport pyboy.lcd
cimport pyboy.interaction
cimport pyboy.window.window
cimport pyboy.window.base_window


cdef unsigned short STAT, LY, LYC
cdef short VBLANK, LCDC, TIMER, SERIAL, HIGHTOLOW

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2


cdef class Motherboard:
    cdef object debugger
    cdef pyboy.interaction.Interaction interaction
    cdef pyboy.bootrom.BootROM bootrom
    cdef pyboy.ram.RAM ram
    cdef pyboy.lcd.LCD lcd
    cdef pyboy.mb.cpu.CPU cpu
    cdef pyboy.mb.timer.Timer timer
    cdef pyboy.window.base_window.BaseWindow window
    cdef pyboy.cartridge.base_mbc.BaseMBC cartridge
    cdef bint bootrom_enabled
    cdef unicode serialbuffer

    cdef void buttonevent(self, int)
    cdef void stop(self, bint)
    cdef void set_STAT_mode(self, int)
    cdef void check_LYC(self, int)
    @cython.locals(cycles=cython.int)
    cdef void calculate_cycles(self, int)
    cdef void tickframe(self)

    cpdef unsigned char getitem(self, unsigned short)
    cpdef void setitem(self, unsigned short, unsigned char)

    @cython.locals(offset=cython.int, dst=cython.int, n=cython.int)
    cdef void transfer_DMA(self, unsigned char)
    cdef void save_state(self, unicode)
    cdef void load_state(self, unicode)
