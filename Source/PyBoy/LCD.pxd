# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cdef unsigned short LCDC, STAT, SCY, SCX, LY, LYC, DMA, BGPalette, OBP0, OBP1, WY, WX

# LCDC bit descriptions
cimport PyBoy.RAM
# from PyBoy.RAM cimport allocateRAM, VIDEO_RAM, OBJECT_ATTRIBUTE_MEMORY
cdef char BG_WinEnable, SpriteEnable, SpriteSize, BGTileDataDisSel, BG_WinTileDataSel, WinEnable, WinTileDataSel, Enable

cdef tuple gameboyResolution
cdef tuple colorPalette
cdef unsigned int alphaMask

cdef unsigned char getColorCode(unsigned char, unsigned char, unsigned char)


import numpy as np
cimport numpy as np
ctypedef np.uint8_t DTYPE_t

cdef class LCD:
    cdef object mb
    cdef public bint clearCache
    cdef public set tilesChanged
    cdef unsigned int[:, :] tileCache
    cdef public DTYPE_t[:] VRAM
    cdef public DTYPE_t[:] OAM

    # TODO: Numpy
    cdef object spriteCacheOBP0
    cdef object spriteCacheOBP1

    cdef public object LCDC
    cdef public object BGP
    cdef public object OBP0
    cdef public object OBP1

    # TODO: Cythonize
    # cdef tuple getWindowPos(self)
    # cdef tuple getViewPort(self)
    # cdef public void refreshTileDataAdaptive(self)

cdef class PaletteRegister:
    cdef object lcd

    cdef unsigned char value
    cdef unsigned char[4] lookup

    # TODO: Cythonize
    # cdef public void set(self, unsigned int)
    # cdef unsigned int getColor(self, char)

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
