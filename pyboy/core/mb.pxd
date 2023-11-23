#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport int64_t, uint8_t, uint16_t, uint32_t, uint64_t

import cython

cimport pyboy.core.bootrom
cimport pyboy.core.cartridge.base_mbc
cimport pyboy.core.cpu
cimport pyboy.core.interaction
cimport pyboy.core.lcd
cimport pyboy.core.ram
cimport pyboy.core.sound
cimport pyboy.core.timer
from pyboy.logging.logging cimport Logger
from pyboy.utils cimport IntIOInterface, WindowEvent


cdef Logger logger

cdef uint16_t STAT, LY, LYC
cdef short VBLANK, LCDC, TIMER, SERIAL, HIGHTOLOW
cdef int INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW
cdef int STATE_VERSION


cdef class Motherboard:
    cdef pyboy.core.interaction.Interaction interaction
    cdef pyboy.core.bootrom.BootROM bootrom
    cdef pyboy.core.ram.RAM ram
    cdef pyboy.core.lcd.LCD lcd
    cdef pyboy.core.cpu.CPU cpu
    cdef pyboy.core.timer.Timer timer
    cdef pyboy.core.sound.Sound sound
    cdef pyboy.core.cartridge.base_mbc.BaseMBC cartridge
    cdef bint bootrom_enabled
    cdef char[1024] serialbuffer
    cdef uint16_t serialbuffer_count

    # CGB
    cdef HDMA hdma
    cdef uint8_t key1
    cdef bint double_speed
    cdef public bint cgb

    cdef bint breakpoints_enabled
    cdef list breakpoints_list
    cdef int breakpoint_latch

    cdef inline bint processing_frame(self) noexcept nogil

    cdef void buttonevent(self, WindowEvent) noexcept
    cdef void stop(self, bint) noexcept
    @cython.locals(cycles=int64_t, escape_halt=cython.int, mode0_cycles=int64_t)
    cdef bint tick(self) noexcept nogil

    cdef void switch_speed(self) noexcept nogil

    @cython.locals(pc=cython.int, bank=cython.int)
    cdef bint breakpoint_reached(self) noexcept with gil

    cdef uint8_t getitem(self, uint16_t) noexcept nogil
    cdef void setitem(self, uint16_t, uint8_t) noexcept nogil

    @cython.locals(offset=cython.int, dst=cython.int, n=cython.int)
    cdef void transfer_DMA(self, uint8_t) noexcept nogil
    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface) except -1

cdef class HDMA:
    cdef uint8_t hdma1
    cdef uint8_t hdma2
    cdef uint8_t hdma3
    cdef uint8_t hdma4
    cdef uint8_t hdma5
    cdef uint8_t _hdma5

    cdef bint transfer_active
    cdef uint16_t curr_src
    cdef uint16_t curr_dst

    cdef void set_hdma5(self, uint8_t, Motherboard) noexcept nogil
    cdef int tick(self, Motherboard) noexcept nogil

    cdef void save_state(self, IntIOInterface) noexcept
    cdef void load_state(self, IntIOInterface, int) noexcept
