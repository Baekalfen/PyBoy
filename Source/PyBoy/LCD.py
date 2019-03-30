# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

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

class LCD():
    def __init__(self, colorPalette):
        self.VRAM = array.array('B', [0]*(VIDEO_RAM))
        self.OAM = array.array('B', [0]*(OBJECT_ATTRIBUTE_MEMORY))

        self.LCDC = LCDCRegister(0)
        self.BGP = PaletteRegister(0xFC, colorPalette)
        self.OBP0 = PaletteRegister(0xFF, colorPalette)
        self.OBP1 = PaletteRegister(0xFF, colorPalette)
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



class PaletteRegister():
    def __init__(self, value, colorPalette):
        self.colorPalette = colorPalette
        self.value = 0
        self.set(value)

    def set(self, value):
        if self.value == value: # Pokemon Blue continously sets this without changing the value
            return False

        self.value = value
        self.lookup = [0] * 4
        for x in xrange(4):
            self.lookup[x] = self.colorPalette[(value >> x*2) & 0b11]
        return True

    def getColor(self, i):
        return self.lookup[i]

    # def getCode(self, i):
    #     return self.lookup[i]

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

