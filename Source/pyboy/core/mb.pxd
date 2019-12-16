#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import cython
cimport pyboy.core.cpu
cimport pyboy.core.timer
cimport pyboy.core.cartridge.base_mbc
from pyboy.rewind cimport IntIOInterface
# cimport pyboy.core.cartridge.cartridge
cimport pyboy.core.bootrom
cimport pyboy.core.ram
cimport pyboy.core.lcd
cimport pyboy.core.interaction
cimport pyboy.window.window
cimport pyboy.window.base_window


cdef unsigned short STAT, LY, LYC
cdef short VBLANK, LCDC, TIMER, SERIAL, HIGHTOLOW

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2


cdef class Motherboard:
    cdef pyboy.core.interaction.Interaction interaction
    cdef pyboy.core.bootrom.BootROM bootrom
    cdef pyboy.core.ram.RAM ram
    cdef pyboy.core.lcd.LCD lcd
    cdef pyboy.core.cpu.CPU cpu
    cdef pyboy.core.timer.Timer timer
    cdef pyboy.window.base_window.BaseWindow window
    cdef pyboy.core.cartridge.base_mbc.BaseMBC cartridge
    cdef bint bootrom_enabled
    cdef bint enable_rewind
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
    cdef void save_state(self, IntIOInterface)
    cdef void load_state(self, IntIOInterface)
