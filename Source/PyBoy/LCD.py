# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import CoreDump
# import RAM
# from RAM import allocateRAM, VIDEO_RAM, OBJECT_ATTRIBUTE_MEMORY
import array
import numpy as np

VIDEO_RAM = 8 * 1024  # 8KB
OBJECT_ATTRIBUTE_MEMORY = 0xA0

# LCDC,
STAT, SCY, SCX, LY, LYC, DMA, BGPalette, OBP0, OBP1, WY, WX = range(0xFF41, 0xFF4C)

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
    def __init__(self):
        self.clearCache = False
        self.tilesChanged = set([])
        assert isinstance(self.tilesChanged, set)

        self.VRAM = array.array('B', [0]*(VIDEO_RAM))
        self.OAM = array.array('B', [0]*(OBJECT_ATTRIBUTE_MEMORY))

        self.tileCache = np.ndarray((384 * 8, 8), dtype='uint32')
        # TODO: Find a more optimal way to do this
        self.spriteCacheOBP0 = np.ndarray((384 * 8, 8), dtype='uint32')
        self.spriteCacheOBP1 = np.ndarray((384 * 8, 8), dtype='uint32')

        self.LCDC = LCDCRegister(0)
        self.BGP = PaletteRegister(0xFC)
        self.OBP0 = PaletteRegister(0xFF)
        self.OBP1 = PaletteRegister(0xFF)
        # self.STAT = 0x00
        # self.LY = 0x00
        # self.LYC = 0x00
        # self.DMA = 0x00
        self.SCY = 0x00
        self.SCX = 0x00
        self.WY = 0x00
        self.WX = 0x00

    def saveState(self, f):
        for n in range(VIDEO_RAM):
            f.write(chr(self.VRAM[n]))

        for n in range(OBJECT_ATTRIBUTE_MEMORY):
            f.write(chr(self.OAM[n]))

        f.write(chr(self.LCDC.value))
        f.write(chr(self.BGP.value))
        f.write(chr(self.OBP0.value))
        f.write(chr(self.OBP1.value))

        f.write(chr(self.SCY))
        f.write(chr(self.SCX))
        f.write(chr(self.WY))
        f.write(chr(self.WX))

    def loadState(self, f):
        for n in range(VIDEO_RAM):
            self.VRAM[n] = ord(f.read(1))

        for n in range(OBJECT_ATTRIBUTE_MEMORY):
            self.OAM[n] = ord(f.read(1))

        self.LCDC.set(ord(f.read(1)))
        self.BGP.set(ord(f.read(1)))
        self.OBP0.set(ord(f.read(1)))
        self.OBP1.set(ord(f.read(1)))

        self.SCY = ord(f.read(1))
        self.SCX = ord(f.read(1))
        self.WY = ord(f.read(1))
        self.WX = ord(f.read(1))

    def getWindowPos(self):
        return (self.WX-7, self.WY)

    def getViewPort(self):
        return (self.SCX, self.SCY)

    def refreshTileDataAdaptive(self):
        if self.clearCache:
            self.tilesChanged.clear()
            for x in xrange(0x8000,0x9800,16):

                self.tilesChanged.add(x)
            self.clearCache = False

        for t in self.tilesChanged:
            for k in xrange(0, 16 ,2): #2 bytes for each line
                byte1 = self.VRAM[t+k - 0x8000]
                byte2 = self.VRAM[t+k+1 - 0x8000]

                for pixelOnLine in xrange(7,-1,-1):
                    y = k/2
                    x = (t - 0x8000)/2 + 7-pixelOnLine

                    colorCode = getColorCode(byte1, byte2, pixelOnLine)

                    self.tileCache[x][y] = self.BGP.getColor(colorCode)
                    # TODO: Find a more optimal way to do this
                    alpha = 0x00000000
                    if colorCode == 0:
                        alpha = alphaMask # Add alpha channel
                    self.spriteCacheOBP0[x][y] = self.OBP0.getColor(colorCode) + alpha
                    self.spriteCacheOBP1[x][y] = self.OBP1.getColor(colorCode) + alpha

        self.tilesChanged.clear()

class PaletteRegister():
    def __init__(self, value):
        self.value = 0 # None
        self.set(value)

    def set(self, value):
        if self.value == value: # Pokemon Blue continously sets this without changing the value
            return False

        self.value = value
        self.lookup = [0] * 4
        for x in xrange(4):
            self.lookup[x] = (value >> x*2) & 0b11
        # self.lcd.clearCache = True
        return True

    def getColor(self, i):
        return colorPalette[self.lookup[i]]

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

