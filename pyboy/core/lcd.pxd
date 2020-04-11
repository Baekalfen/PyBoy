#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import cython
from cpython.array cimport array
from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t
cimport pyboy.utils
from pyboy.utils cimport IntIOInterface

cdef uint16_t LCDC, STAT, SCY, SCX, LY, LYC, DMA, BGP, OBP0, OBP1, WY, WX
cdef int ROWS, COLS, TILES, VIDEO_RAM, OBJECT_ATTRIBUTE_MEMORY


cdef class LCD:
    cdef uint8_t[8 * 1024] VRAM
    cdef uint8_t[0xA0] OAM

    cdef int SCY
    cdef int SCX
    cdef int WY
    cdef int WX
    cdef LCDCRegister LCDC
    cdef PaletteRegister BGP
    cdef PaletteRegister OBP0
    cdef PaletteRegister OBP1

    cdef void save_state(self, IntIOInterface)
    cdef void load_state(self, IntIOInterface, int)

    cdef (int, int) getwindowpos(self)
    cdef (int, int) getviewport(self)


cdef class PaletteRegister:
    cdef LCD lcd

    cdef uint8_t value
    cdef uint32_t[4] lookup
    cdef uint32_t[4] color_palette

    @cython.locals(x=cython.ushort)
    cdef bint set(self, uint64_t)
    cdef uint32_t getcolor(self, uint8_t)


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

    cdef array _screenbuffer_raw
    cdef array _tilecache_raw, _spritecache0_raw, _spritecache1_raw
    cdef uint32_t[:,:] _screenbuffer
    cdef uint32_t[:,:] _tilecache, _spritecache0, _spritecache1

    cdef int[144][5] _scanlineparameters

    @cython.locals(bx=int, by=int, wx=int, wy=int)
    cdef void scanline(self, int, LCD)

    @cython.locals(
        y=int,
        x=int,
        wmap=int,
        background_offset=int,
        bx=int,
        by=int,
        wx=int,
        wy=int,
        wt=int,
        bt=int,
        offset=int,
    )
    cdef void render_screen(self, LCD)

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
