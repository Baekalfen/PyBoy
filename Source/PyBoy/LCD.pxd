# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cdef unsigned short LCDC, STAT, SCY, SCX, LY, LYC, DMA, BGPalette, OBP0, OBP1, WY, WX

# LCDC bit descriptions
# from PyBoy.MB.MB cimport Motherboard
# cimport PyBoy.RAM
# from PyBoy.RAM cimport allocateRAM, VIDEO_RAM, OBJECT_ATTRIBUTE_MEMORY
cdef char BG_WinEnable, SpriteEnable, SpriteSize, BGTileDataDisSel, BG_WinTileDataSel, WinEnable, WinTileDataSel, Enable

# cdef public int VIDEO_RAM, OBJECT_ATTRIBUTE_MEMORY

cdef (int, int) gameboyResolution
cdef public int[4] colorPalette
cdef unsigned int alphaMask

cdef unsigned char getColorCode(unsigned char, unsigned char, unsigned char)

import cython

import numpy as np
cimport numpy as np
ctypedef np.uint8_t DTYPE_t

cdef class LCD:
    cdef public bint clearCache
    cdef public set tilesChanged
    cdef np.uint32_t[384 * 8][8] tileCache
    cpdef public DTYPE_t[8 * 1024] VRAM
    cdef public DTYPE_t[0xA0] OAM
    cdef np.uint32_t[384 * 8][8] spriteCacheOBP0
    cdef np.uint32_t[384 * 8][8] spriteCacheOBP1

    cdef int SCY
    cdef int SCX
    cdef int WY
    cdef int WX
    cdef public LCDCRegister LCDC
    cdef public PaletteRegister BGP
    cdef public PaletteRegister OBP0
    cdef public PaletteRegister OBP1

    cdef void saveState(self, file)
    cdef void loadState(self, file)

    cdef (int, int) getWindowPos(self)
    cdef (int, int) getViewPort(self)
    @cython.locals(
            x=cython.ushort,
            y=cython.ushort,
            t=cython.int,
            k=cython.int,
            pixelOnLine=cython.int,
            colorCode=cython.int,
            alpha=cython.int,
            )
    cdef void refreshTileDataAdaptive(self)

cdef class PaletteRegister:
    cdef LCD lcd

    cdef unsigned char value
    cdef unsigned char[4] lookup

    @cython.locals(x=cython.ushort)
    cdef void set(self, unsigned int)
    cdef unsigned int getColor(self, unsigned char)

    cdef char getCode(self, unsigned char)

cdef class LCDCRegister:
    cdef unsigned char value

    cdef void set(self, unsigned int)

    cdef public bint enabled
    cdef public bint windowMapSelect
    cdef public bint windowEnabled
    cdef public bint tileSelect
    cdef public bint backgroundMapSelect
    cdef public bint spriteSize
    cdef public bint spriteEnable
    cdef public bint backgroundEnable
