#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import cython
from libc.stdint cimport uint8_t, uint32_t


cdef unsigned short LCDC, STAT, SCY, SCX, LY, LYC, DMA, BGPalette, OBP0, OBP1, WY, WX

# LCDC bit descriptions
cdef char BACKGROUND_ENABLE, SPRITE_ENABLE, SPRITE_SIZE, BACKGROUNDMAP_SELECT
cdef char TILEDATA_SELELECT, WINDOW_ENABLE, WINDOWMAP_SELECT, LCD_ENABLE


cdef int ROWS, COLS


cdef class LCD:
    cdef uint8_t[8 * 1024] VRAM
    cdef uint8_t[0xA0] OAM

    cdef int SCY
    cdef int SCX
    cdef int WY
    cdef int WX
    cdef public LCDCRegister LCDC
    cdef public PaletteRegister BGP
    cdef public PaletteRegister OBP0
    cdef public PaletteRegister OBP1

    cdef void save_state(self, file)
    cdef void load_state(self, file)

    cdef (int, int) get_windowpos(self)
    cdef (int, int) get_viewport(self)


cdef class PaletteRegister:
    cdef LCD lcd

    cdef unsigned char value
    cdef uint32_t[4] lookup
    cdef uint32_t[4] colorpalette

    @cython.locals(x=cython.ushort)
    cdef bint set(self, unsigned int)
    cdef uint32_t get_color(self, unsigned char)


cdef class LCDCRegister:
    cdef unsigned char value

    cdef void set(self, unsigned int)

    cdef public bint lcd_enable
    cdef public bint windowmap_select
    cdef public bint window_enable
    cdef public bint tiledata_select
    cdef public bint backgroundmap_select
    cdef public bint sprite_size
    cdef public bint sprite_enable
    cdef public bint background_enable
