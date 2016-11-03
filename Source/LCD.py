# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from MathUint8 import getSignedInt8, getBit
import numpy

LCDC, STAT, SCY, SCX, LY, LYC, DMA, BGPalette, OBP0, OBP1, WY, WX = range(0xFF40, 0xFF4C)

# LCDC bit descriptions
BG_WinEnable, SpriteEnable, SpriteSize, BGTileDataDisSel, BG_WinTileDataSel, WinEnable, WinTileDataSel, Enable = range(8)

# STAT bit descriptions
# ModeFlag0, ModeFlag1, Coincidence, Mode00, Mode01, Mode10, LYC_LY = range(7)

gameboyResolution = (160, 144)
colorPalette = (0x00FFFFFF,0x00999999,0x00555555,0x00000000)


def getColor(byte1,byte2,offset):
    # The colors are 2 bit and are found like this:
    #
    # Color of the first pixel is 0b10
    # | Color of the second pixel is 0b01
    # v v
    # 1 0 0 1 0 0 0 1 <- byte1
    # 0 1 1 1 1 1 0 0 <- byte2
    return (((byte2 >> (offset)) & 0b1) << 1) + ((byte1 >> (offset)) & 0b1) # 2bit color code

class LCD():
    def __init__(self, ram, window):
        self.ram = ram
        self.tileCache = numpy.ndarray((384 * 8, 8), dtype='int32')

        window.init(self, ram.VRAM, ram.OAM)
        self.window = window
        self.LCDC = 0x00

        # For optimizing LCDC access in Window. LCDC is rarely changed,
        # but bits are checked several times every frame
        self.LCDC_enabled = 0
        self.LCDC_windowMapSelect = 0
        self.LCDC_windowEnabled = 0
        self.LCDC_tileSelect = 0
        self.LCDC_backgroundMapSelect = 0
        self.LCDC_spriteSize = 0
        self.LCDC_spriteEnable = 0
        self.LCDC_backgroundEnable = 0

        # self.STAT = 0x00
        # self.SCY = 0x00
        # self.SCX = 0x00
        # self.LY = 0x00
        # self.LYC = 0x00
        # self.DMA = 0x00
        # self.BGPalette = 0x00
        # self.OBP0 = 0x00
        # self.OBP1 = 0x00
        # self.WY = 0x00
        # self.WX = 0x00

    def tick(self):
        if __debug__:
            self.window.refreshTileView1()
            self.window.refreshTileView2()
            self.window.refreshSpriteView()
            self.window.drawTileCacheView()
            self.window.drawTileView1ScreenPort()
            self.window.drawTileView2WindowPort()

        if self.LCDC_enabled:
            if self.ram.updateVRAMCache:
                self.refreshTileDataAdaptive()
                # self.refreshTileData()
                self.ram.updateVRAMCache = False
            self.window.renderSprites()
        else:
            self.window.blankScreen()

    def setLCDC(self, value):
        self.LCDC = value

        # No need to convert to bool. Any non-zero value is evaluated as True
        self.LCDC_enabled             = value & (1 << 7)
        self.LCDC_windowMapSelect     = value & (1 << 6)
        self.LCDC_windowEnabled       = value & (1 << 5)
        self.LCDC_tileSelect          = value & (1 << 4)
        self.LCDC_backgroundMapSelect = value & (1 << 3)
        self.LCDC_spriteSize          = value & (1 << 2)
        self.LCDC_spriteEnable        = value & (1 << 1)
        self.LCDC_backgroundEnable    = value & (1 << 0)

    def getWindowPos(self):
        return self.ram[WX]-7, self.ram[WY]

    def getViewPort(self):
        return self.ram[SCX], self.ram[SCY]

    def scanline(self, y):
        self.window.scanline(y)

    def refreshTileData(self):
        # http://gameboy.mongenel.com/dmg/asmmemmap.html
        print "Updating tile Data"
        tileCount = 0
        for n in xrange(0x8000,0x9800,16): #Tile is 16 bytes
            for k in xrange(0, 16 ,2): #2 bytes for each line
                byte1 = self.ram[n+k]
                byte2 = self.ram[n+k+1]

                for pixelOnLine in xrange(7,-1,-1):
                    y = k/2
                    x = tileCount*8 + 7-pixelOnLine
                    self.tileCache[x, y] = colorPalette[getColor(byte1, byte2, pixelOnLine)]

            tileCount += 1
        self.ram.tilesChanged.clear()

    def refreshTileDataAdaptive(self):
        # print "Updating tile data for :", [hex(x) for x in self.ram.tilesChanged]

        for t in self.ram.tilesChanged:
            for k in xrange(0, 16 ,2): #2 bytes for each line
                byte1 = self.ram[t+k]
                byte2 = self.ram[t+k+1]

                for pixelOnLine in xrange(7,-1,-1):
                    y = k/2
                    x = (t - 0x8000)/2 + 7-pixelOnLine

                    self.tileCache[x, y] = colorPalette[getColor(byte1, byte2, pixelOnLine)]

        self.ram.tilesChanged.clear()

