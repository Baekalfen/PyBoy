#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import cython

from cpython.array cimport array
from libc.stdint cimport int16_t, int64_t, uint8_t, uint16_t, uint32_t, uint64_t

cimport pyboy.utils
from pyboy cimport utils
from pyboy.logging.logging cimport Logger
from pyboy.utils cimport IntIOInterface


cdef uint8_t INTR_VBLANK, INTR_LCDC
cdef uint16_t LCDC, STAT, SCY, SCX, LY, LYC, DMA, BGP, OBP0, OBP1, WY, WX
cdef int ROWS, COLS, TILES, FRAME_CYCLES, VIDEO_RAM, OBJECT_ATTRIBUTE_MEMORY
cdef uint32_t COL0_FLAG, BG_PRIORITY_FLAG
cdef uint8_t CGB_NUM_PALETTES

cdef Logger logger

@cython.locals(a=uint32_t, r=uint32_t, g=uint32_t, b=uint32_t)
cpdef uint32_t rgb_to_bgr(uint32_t) noexcept

cdef class LCD:
    cdef bint disable_renderer
    cdef uint8_t[8 * 1024] VRAM0
    cdef uint8_t[0xA0] OAM

    cdef uint8_t SCY
    cdef uint8_t SCX
    cdef uint8_t WY
    cdef uint8_t WX
    cdef uint8_t next_stat_mode
    cdef bint frame_done
    cdef bint first_frame
    cdef bint reset
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
    cdef uint8_t[144][5] _scanlineparameters
    cdef uint64_t last_cycles
    cdef int64_t _cycles_to_interrupt, _cycles_to_frame

    @cython.locals(interrupt_flag=uint8_t,bx=int,by=int,wx=int,wy=int)
    cdef uint8_t tick(self, uint64_t) noexcept nogil

    cdef void set_lcdc(self, uint8_t) noexcept nogil

    cdef int64_t cycles_to_mode0(self) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1

    cdef inline (int, int) getwindowpos(self) noexcept nogil
    cdef inline (int, int) getviewport(self) noexcept nogil

    # CGB
    cdef bint cgb
    cdef uint8_t speed_shift
    cdef uint8_t[8 * 1024] VRAM1
    cdef VBKregister vbk
    cdef PaletteIndexRegister bcps
    cdef PaletteColorRegister bcpd
    cdef PaletteIndexRegister ocps
    cdef PaletteColorRegister ocpd


cdef class PaletteRegister:
    cdef uint8_t value
    cdef uint32_t[4] lookup
    cdef uint32_t[4] palette_mem_rgb

    @cython.locals(x=uint16_t)
    cdef bint set(self, uint64_t) noexcept nogil
    cdef uint8_t get(self) noexcept nogil
    cdef inline uint32_t getcolor(self, uint8_t) noexcept nogil

cdef class STATRegister:
    cdef uint8_t value
    cdef uint8_t _mode
    cdef uint8_t set_mode(self, uint8_t) noexcept nogil
    cdef uint8_t update_LYC(self, uint8_t, uint8_t) noexcept nogil
    cdef void set(self, uint64_t) noexcept nogil
    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1

cdef class LCDCRegister:
    cdef uint8_t value

    cdef void set(self, uint64_t) noexcept nogil

    cdef bint lcd_enable
    cdef bint windowmap_select
    cdef bint window_enable
    cdef bint tiledata_select
    cdef bint backgroundmap_select
    cdef readonly bint sprite_height
    cdef bint sprite_enable
    cdef bint background_enable
    cdef bint cgb_master_priority

    cdef uint16_t backgroundmap_offset
    cdef uint16_t windowmap_offset

cdef class Renderer:
    cdef uint8_t[:] _tilecache0_state, _tilecache1_state, _spritecache0_state, _spritecache1_state
    cdef str color_format
    cdef tuple buffer_dims
    cdef bint cgb

    cdef array _screenbuffer_raw
    cdef array _screenbuffer_attributes_raw
    cdef object _screenbuffer_ptr
    cdef array _tilecache0_raw, _spritecache0_raw, _spritecache1_raw
    cdef uint32_t[:,:] _screenbuffer
    cdef uint8_t[:,:] _screenbuffer_attributes
    cdef uint8_t[:,:] _tilecache0, _spritecache0, _spritecache1
    cdef uint64_t[:] _tilecache0_64, _tilecache1_64, _spritecache0_64, _spritecache1_64
    cdef uint32_t[:] colorcode_table

    cdef int[10] sprites_to_render
    cdef int ly_window
    cdef void invalidate_tile(self, int, int) noexcept nogil

    cdef void blank_screen(self, LCD) noexcept nogil

    # CGB
    cdef array _tilecache1_raw
    cdef uint8_t[:,:] _tilecache1

    @cython.locals(
        bx=int,
        by=int,
        wx=int,
        wy=int,
        palette=uint8_t,
        vbank=bint,
        horiflip=bint,
        vertflip=bint,
        bg_priority=bint,
        xx=int,
        yy=int,
        tilecache=uint8_t[:,:],
        bg_priority_apply=uint32_t,
        col0=uint8_t,
        pixel=uint32_t,
    )
    cdef void scanline(self, LCD, int) noexcept nogil

    @cython.locals(tile_addr=uint64_t, tile=int)
    cdef inline (int, int, uint16_t) _get_tile(self, uint8_t, uint8_t, uint16_t, LCD) noexcept nogil
    @cython.locals(col0=uint8_t)
    cdef inline void _pixel(self, uint8_t[:,:], uint32_t, int, int, int, int, uint32_t) noexcept nogil
    cdef int scanline_background(self, int, int, int, int, int, LCD) noexcept nogil
    cdef int scanline_window(self, int, int, int, int, int, LCD) noexcept nogil
    cdef int scanline_blank(self, int, int, int, LCD) noexcept nogil

    @cython.locals(
        spriteheight=int,
        spritecount=int,
        n=int,
        x=int,
        y=int,
        _n=int,
        tileindex=int,
        attributes=int,
        xflip=bint,
        yflip=bint,
        spritepriority=bint,
        palette=uint8_t,
        spritecache=uint8_t[:,:],
        dy=int,
        dx=int,
        yy=int,
        xx=int,
        color_code=uint8_t,
        pixel=uint32_t,
        bgmappriority=bint,
    )
    cdef void scanline_sprites(self, LCD, int, uint32_t[:,:], uint8_t[:,:], bint) noexcept nogil
    cdef void sort_sprites(self, int) noexcept nogil

    cdef void clear_cache(self) noexcept nogil
    cdef void clear_tilecache0(self) noexcept nogil
    cdef void clear_tilecache1(self) noexcept nogil # CGB Only
    cdef void clear_spritecache0(self) noexcept nogil
    cdef void clear_spritecache1(self) noexcept nogil
    @cython.locals(
        x=int,
        t=int,
        k=int,
        y=int,
        byte1=uint8_t,
        byte2=uint8_t,
        colorcode_low=uint64_t,
        colorcode_high=uint64_t,
    )
    cdef void update_tilecache0(self, LCD, int, int) noexcept nogil
    @cython.locals(
        x=int,
        t=int,
        k=int,
        y=int,
        byte1=uint8_t,
        byte2=uint8_t,
        colorcode_low=uint64_t,
        colorcode_high=uint64_t,
    )
    cdef void update_tilecache1(self, LCD, int, int) noexcept nogil # CGB Only
    @cython.locals(
        x=int,
        t=int,
        k=int,
        y=int,
        byte1=uint8_t,
        byte2=uint8_t,
        colorcode_low=uint64_t,
        colorcode_high=uint64_t,
    )
    cdef void update_spritecache0(self, LCD, int, int) noexcept nogil
    @cython.locals(
        x=int,
        t=int,
        k=int,
        y=int,
        byte1=uint8_t,
        byte2=uint8_t,
        colorcode_low=uint64_t,
        colorcode_high=uint64_t,
    )
    cdef void update_spritecache1(self, LCD, int, int) noexcept nogil

    @cython.locals(colorcode_low=uint64_t, colorcode_high=uint64_t)
    cdef inline uint64_t colorcode(self, uint64_t, uint64_t) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1


cdef class CGBLCD(LCD):
    pass
    # cdef uint8_t[8 * 1024] VRAM1
    # cdef VBKregister vbk
    # cdef PaletteIndexRegister bcps
    # cdef PaletteColorRegister bcpd
    # cdef PaletteIndexRegister ocps
    # cdef PaletteColorRegister ocpd

cdef class CGBRenderer(Renderer):

    @cython.locals(
        tile_num = uint8_t,
        palette = uint8_t,
        vbank = uint8_t,
        horiflip = uint8_t,
        vertflip = uint8_t,
        bg_priority = uint8_t,
    )
    cdef inline (int, int, int, int, int) _cgb_get_background_map_attributes(self, LCD, int) noexcept nogil
    cdef inline (int, int, uint8_t, bint, uint32_t, bint) _get_tile_cgb(self, uint8_t, uint8_t, uint16_t, LCD) noexcept nogil

cdef class VBKregister:
    cdef uint8_t active_bank

    cdef void set(self, uint8_t) noexcept nogil
    cdef uint8_t get(self) noexcept nogil

cdef class PaletteIndexRegister:
    cdef uint8_t value
    cdef int auto_inc
    cdef int index
    cdef int hl

    cdef void set(self, uint8_t) noexcept nogil
    cdef uint8_t get(self) noexcept nogil
    cdef int getindex(self) noexcept nogil
    cdef void shouldincrement(self) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1

cdef class PaletteColorRegister:
    cdef uint16_t[8 * 4] palette_mem
    cdef uint32_t[8 * 4] palette_mem_rgb
    cdef PaletteIndexRegister index_reg

    cdef uint32_t cgb_to_rgb(self, uint16_t, uint8_t) noexcept nogil
    cdef void set(self, uint16_t) noexcept nogil
    cdef uint16_t get(self) noexcept nogil
    cdef inline uint32_t getcolor(self, uint8_t, uint8_t) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1
