# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import CoreDump
import RAM
# from RAM import allocateRAM, VIDEO_RAM, OBJECT_ATTRIBUTE_MEMORY
import numpy as np


LCDC, STAT, SCY, SCX, LY, LYC, DMA, BGPalette, OBP0, OBP1, WY, WX = range(0xFF40, 0xFF4C)

# LCDC bit descriptions
BG_WinEnable, SpriteEnable, SpriteSize, BGTileDataDisSel, BG_WinTileDataSel, WinEnable, WinTileDataSel, Enable = range(8)

# STAT bit descriptions
# ModeFlag0, ModeFlag1, Coincidence, Mode00, Mode01, Mode10, LYC_LY = range(7)

gameboyResolution = (160, 144)
colorPalette = (0x00FFFFFF,0x00999999,0x00555555,0x00000000)
alphaMask = 0x7F000000

def getColorCode(byte1,byte2,offset):
    # The colors are 2 bit and are found like this:
    #
    # Color of the first pixel is 0b10
    # | Color of the second pixel is 0b01
    # v v
    # 1 0 0 1 0 0 0 1 <- byte1
    # 0 1 1 1 1 1 0 0 <- byte2
    return (((byte2 >> (offset)) & 0b1) << 1) + ((byte1 >> (offset)) & 0b1) # 2bit color code

class LCD():
    def __init__(self, MB):
        self.mb = MB
        self.clearCache = False
        self.tilesChanged = set([])
        assert isinstance(self.tilesChanged, set)

        self.tileCache = np.ndarray((384 * 8, 8), dtype='uint32')

        self.VRAM = np.zeros(shape=(RAM.VIDEO_RAM,), dtype=np.uint8)
        self.OAM = np.zeros(shape=(RAM.OBJECT_ATTRIBUTE_MEMORY,), dtype=np.uint8)

        # TODO: Find a more optimal way to do this
        self.spriteCacheOBP0 = np.ndarray((384 * 8, 8), dtype='uint32')
        self.spriteCacheOBP1 = np.ndarray((384 * 8, 8), dtype='uint32')

        self.LCDC = LCDCRegister(0)
        self.BGP = PaletteRegister(0xFC, self)
        self.OBP0 = PaletteRegister(0xFF, self)
        self.OBP1 = PaletteRegister(0xFF, self)
        # self.STAT = 0x00
        # self.SCY = 0x00
        # self.SCX = 0x00
        # self.LY = 0x00
        # self.LYC = 0x00
        # self.DMA = 0x00
        # self.WY = 0x00
        # self.WX = 0x00

    def getWindowPos(self):
        return self.mb[WX]-7, self.mb[WY]

    def getViewPort(self):
        return self.mb[SCX], self.mb[SCY]

    def refreshTileDataAdaptive(self):
        if self.clearCache:
            self.tilesChanged.clear()
            for x in xrange(0x8000,0x9800,16):

                self.tilesChanged.add(x)
            self.clearCache = False

        for t in self.tilesChanged:
            for k in xrange(0, 16 ,2): #2 bytes for each line
                byte1 = self.mb[t+k]
                byte2 = self.mb[t+k+1]

                for pixelOnLine in xrange(7,-1,-1):
                    y = k/2
                    x = (t - 0x8000)/2 + 7-pixelOnLine

                    colorCode = getColorCode(byte1, byte2, pixelOnLine)

                    self.tileCache[x, y] = self.BGP.getColor(colorCode)
                    # TODO: Find a more optimal way to do this
                    alpha = 0x00000000
                    if colorCode == 0:
                        alpha = alphaMask # Add alpha channel
                    self.spriteCacheOBP0[x, y] = self.OBP0.getColor(colorCode) + alpha
                    self.spriteCacheOBP1[x, y] = self.OBP1.getColor(colorCode) + alpha

        self.tilesChanged.clear()

class PaletteRegister():
    def __init__(self, value, lcd):
        self.lcd = lcd
        self.value = 0 # None
        self.set(value)

    def set(self, value):
        if self.value == value: # Pokemon Blue continously sets this without changing the value
            return

        self.value = value
        self.lookup = [(value >> x) & 0b11 for x in xrange(0,8,2)]
        self.lcd.clearCache = True

    def getColor(self, i):
        return colorPalette[self.lookup[i]]
        # return colorPalette[i]

    def getCode(self, i):
        return self.lookup[i]

class LCDCRegister():
    def __init__(self, value):
        self.set(value)

    def set(self, value):
        self.value = value

        # No need to convert to bool. Any non-zero value is evaluated as True
        self.enabled             = value & (1 << 7)
        self.windowMapSelect     = value & (1 << 6)
        self.windowEnabled       = value & (1 << 5)
        self.tileSelect          = value & (1 << 4)
        self.backgroundMapSelect = value & (1 << 3)
        self.spriteSize          = value & (1 << 2)
        self.spriteEnable        = value & (1 << 1)
        self.backgroundEnable    = value & (1 << 0)

