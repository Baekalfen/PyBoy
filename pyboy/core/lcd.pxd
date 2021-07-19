#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

include "debug.pxi"

import cython
from cpython.array cimport array
from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t, int16_t
cimport pyboy.utils
from pyboy.utils cimport color_code
from pyboy.utils cimport IntIOInterface
cdef uint8_t INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW
cdef uint16_t LCDC, STAT, SCY, SCX, LY, LYC, DMA, BGP, OBP0, OBP1, WY, WX
cdef int ROWS, COLS, TILES, FRAME_CYCLES, VIDEO_RAM, OBJECT_ATTRIBUTE_MEMORY


cdef class LCD:
    cdef uint8_t[8 * 1024] VRAM
    cdef uint8_t[0xA0] OAM

    cdef uint8_t SCY
    cdef uint8_t SCX
    cdef uint8_t WY
    cdef uint8_t WX
    cdef uint8_t next_stat_mode
    cdef bint frame_done
    cdef uint8_t max_ly
    IF DEBUG:
        cdef public uint8_t LY
        cdef public uint8_t LYC
        cdef public uint64_t clock
        cdef public uint64_t clock_target
        cdef public LCDCRegister _LCDC
        cdef public STATRegister _STAT
    ELSE:
        cdef uint8_t LY
        cdef uint8_t LYC
        cdef uint64_t clock
        cdef uint64_t clock_target
        cdef LCDCRegister _LCDC
        cdef STATRegister _STAT
    cdef PaletteRegister BGP
    cdef PaletteRegister OBP0
    cdef PaletteRegister OBP1
    cdef Renderer renderer

    @cython.locals(interrupt_flag=uint8_t)
    cdef uint8_t tick(self, int)
    cdef uint64_t cyclestointerrupt(self)

    cdef void save_state(self, IntIOInterface)
    cdef void load_state(self, IntIOInterface, int)

    cdef (int, int) getwindowpos(self)
    cdef (int, int) getviewport(self)


cdef class PaletteRegister:
    cdef LCD lcd

    cdef uint8_t value
    cdef uint32_t[4] lookup
    cdef uint32_t[4] color_palette

    @cython.locals(x=uint16_t)
    cdef bint set(self, uint64_t)
    cdef uint32_t getcolor(self, uint8_t)

cdef class STATRegister:
    IF DEBUG:
        cdef public uint8_t value
        cdef public uint8_t _mode
        cpdef uint8_t set_mode(self, uint8_t)
        cpdef uint8_t update_LYC(self, uint8_t, uint8_t)
    ELSE:
        cdef uint8_t value
        cdef uint8_t _mode
        cdef uint8_t set_mode(self, uint8_t)
        cdef uint8_t update_LYC(self, uint8_t, uint8_t)
    cdef void set(self, uint64_t)
    cdef uint8_t next_mode(self, uint8_t)

cdef class LCDCRegister:
    cdef uint8_t value

    cdef void set(self, uint64_t)

    cdef public bint lcd_enable
    cdef public bint windowmap_select
    cdef public bint window_enable
    cdef public bint tiledata_select
    cdef public bint backgroundmap_select
    cdef public bint sprite_height
    cdef public bint sprite_enable
    cdef public bint background_enable


cdef class Renderer:
    cdef uint8_t alphamask
    cdef uint32_t[4] color_palette
    cdef str color_format
    cdef tuple buffer_dims
    cdef bint clearcache
    cdef set tiles_changed
    cdef bint disable_renderer
    cdef int old_stat_mode

    cdef array _screenbuffer_raw
    cdef array _tilecache_raw, _spritecache0_raw, _spritecache1_raw
    cdef uint32_t[:,:] _screenbuffer
    cdef uint32_t[:,:] _tilecache, _spritecache0, _spritecache1

    cdef int[144][5] _scanlineparameters

    @cython.locals(bx=int, by=int, wx=int, wy=int)
    cdef void scanline(self, int, LCD)

    cdef list sprites_to_render_n
    cdef list sprites_to_render_x
    cdef int ly_window

    @cython.locals(
        y=int,
        x=int,
        bgpkey=uint32_t,
        spriteheight=int,
        n=int,
        tileindex=int,
        attributes=int,
        xflip=bint,
        yflip=bint,
        spritepriority=bint,
        spritecache=uint32_t[:,:],
        sprites_priority=list,
        dy=int,
        dx=int,
        yy=int,
        xx=int,
        pixel=uint32_t,
    )
    cdef void scanline_sprites(self, LCD, int, uint32_t[:,:], bint)

    @cython.locals(
        y=int,
        x=int,
        bgpkey=uint32_t,
        spriteheight=int,
        n=int,
        tileindex=int,
        attributes=int,
        xflip=bint,
        yflip=bint,
        spritepriority=bint,
        spritecache=uint32_t[:,:],
        dy=int,
        dx=int,
        yy=int,
        xx=int,
        pixel=uint32_t,
    )
    cdef void render_sprites(self, LCD, uint32_t[:,:], bint)

    @cython.locals(
        x=int,
        t=int,
        k=int,
        y=int,
        byte1=uint8_t,
        byte2=uint8_t,
        colorcode=uint32_t,
        alpha=uint32_t
        )
    cdef void update_cache(self, LCD)

    cdef void save_state(self, IntIOInterface)
    cdef void load_state(self, IntIOInterface, int)
