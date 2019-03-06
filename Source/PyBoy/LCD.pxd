# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cdef unsigned short LCDC, STAT, SCY, SCX, LY, LYC, DMA, BGPalette, OBP0, OBP1, WY, WX

# LCDC bit descriptions
# from PyBoy.MB.MB cimport Motherboard
cimport PyBoy.RAM
# from PyBoy.RAM cimport allocateRAM, VIDEO_RAM, OBJECT_ATTRIBUTE_MEMORY
cdef char BG_WinEnable, SpriteEnable, SpriteSize, BGTileDataDisSel, BG_WinTileDataSel, WinEnable, WinTileDataSel, Enable

cdef tuple gameboyResolution
cdef public tuple colorPalette
cdef unsigned int alphaMask

cdef unsigned char getColorCode(unsigned char, unsigned char, unsigned char)

import cython

import numpy as np
cimport numpy as np
ctypedef np.uint8_t DTYPE_t

cdef class LCD:
    cdef object mb
    cdef public bint clearCache
    cdef public set tilesChanged
    cdef np.uint32_t[:, :] tileCache
    cdef public DTYPE_t[:] VRAM
    cdef public DTYPE_t[:] OAM

    # TODO: Numpy
    cdef np.uint32_t[:, :] spriteCacheOBP0
    cdef np.uint32_t[:, :] spriteCacheOBP1

    cdef public LCDCRegister LCDC
    cdef public PaletteRegister BGP
    cdef public PaletteRegister OBP0
    cdef public PaletteRegister OBP1

    cdef tuple getWindowPos(self)
    cdef tuple getViewPort(self)
    @cython.locals(x=cython.ushort, y=cython.ushort)
    cdef void refreshTileDataAdaptive(self)

cdef class PaletteRegister:
    cdef LCD lcd

    cdef unsigned char value
    cdef unsigned char[4] lookup

    cdef void set(self, unsigned int)
    cdef unsigned int getColor(self, char)

    cdef char getCode(self, unsigned char)

cdef class LCDCRegister:
    cdef unsigned char value

    # TODO: Cythonize
    # cdef void set(self, unsigned int)

    cdef public bint enabled
    cdef public bint windowMapSelect
    cdef public bint windowEnabled
    cdef public bint tileSelect
    cdef public bint backgroundMapSelect
    cdef public bint spriteSize
    cdef public bint spriteEnable
    cdef public bint backgroundEnable
