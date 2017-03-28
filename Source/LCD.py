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
    def __init__(self, logger, MB):
        self.logger = logger
        self.MB = MB
        self.tilesChanged = set([])
        assert isinstance(self.tilesChanged, set)

        self.tileCache = numpy.ndarray((384 * 8, 8), dtype='int32')
        self.LCDC = LCDCRegister()
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

    def prepareFrame(self):
        self.refreshTileDataAdaptive(self.tilesChanged)

        if __debug__:
            self.MB.MainWindow.refreshTileView1(self)
            self.MB.MainWindow.refreshTileView2(self)
            self.MB.MainWindow.refreshSpriteView(self)
            self.MB.MainWindow.drawTileCacheView(self)
            self.MB.MainWindow.drawTileView1ScreenPort(self)
            self.MB.MainWindow.drawTileView2WindowPort(self)


    def tick(self):
        if self.LCDC.enabled:
            self.MB.MainWindow.renderSprites(self)
        else:
            self.MB.MainWindow.blankScreen()

    def getWindowPos(self):
        return self.MB[WX]-7, self.MB[WY]

    def getViewPort(self):
        return self.MB[SCX], self.MB[SCY]

    def refreshTileData(self):
        # http://gameboy.mongenel.com/dmg/asmmemmap.html
        # TODO: Can this be merged with the adaptive function,
        # by just providing refreshTileDataAdaptive(xrange(0x8000,0x9800,16))?
        self.logger("Updating tile Data")
        tileCount = 0
        for n in xrange(0x8000,0x9800,16): #Tile is 16 bytes
            for k in xrange(0, 16 ,2): #2 bytes for each line
                byte1 = self.MB[n+k]
                byte2 = self.MB[n+k+1]

                for pixelOnLine in xrange(7,-1,-1):
                    y = k/2
                    x = tileCount*8 + 7-pixelOnLine
                    self.tileCache[x, y] = colorPalette[getColor(byte1, byte2, pixelOnLine)]

            tileCount += 1
        self.tilesChanged.clear()

    def refreshTileDataAdaptive(self, updatedTiles):
        for t in updatedTiles:
            for k in xrange(0, 16 ,2): #2 bytes for each line
                byte1 = self.MB[t+k]
                byte2 = self.MB[t+k+1]

                for pixelOnLine in xrange(7,-1,-1):
                    y = k/2
                    x = (t - 0x8000)/2 + 7-pixelOnLine

                    self.tileCache[x, y] = colorPalette[getColor(byte1, byte2, pixelOnLine)]

        updatedTiles.clear()

class LCDCRegister():
    def __init__(self):
        self.value = 0x00

        # For optimizing LCDC access in Window. LCDC is rarely changed,
        # but bits are checked several times every frame
        self.enabled = 0
        self.windowMapSelect = 0
        self.windowEnabled = 0
        self.tileSelect = 0
        self.backgroundMapSelect = 0
        self.spriteSize = 0
        self.spriteEnable = 0
        self.backgroundEnable = 0


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

