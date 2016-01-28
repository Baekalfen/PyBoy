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
colorPalette = (0x00FFFFFF,0x00777777,0x00333333,0x00000000)
# colorPalette = (0x00FFFFFF,0x00777777,0x00555555,0x00303030)
# colorPalette = (0x00FF0000,0x000000FF,0x0000FFFF,0x00777777)


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
        self.window = window
        self.tileCache = numpy.ndarray((384 * 8, 8), dtype='int32')

        self.offsetOld = -1

    def tick(self):
        # Check LCDC to see if display is on
        # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
        if self.ram[LCDC] >> 7 == 1:
            if self.ram.updateVRAMCache:
                self.refreshTileData()
                self.ram.updateVRAMCache = False
            self.renderSprites()
        else:
            self.window._screenBuffer.fill(0x00403245)


    def getWindowPos(self):
        return self.ram[WX],self.ram[WY]

    def getViewPort(self):
        return self.ram[SCX],self.ram[SCY]

    def scanline(self, y):
        xx, yy = self.getViewPort()
        wx, wy = self.getWindowPos()

        offset = (xx - (xx & 0b11111000)) # Difference between absolute xx and rounded down to nearest tile

        backgroundViewAddress = 0x9800 if getBit(self.ram[LCDC], 6) == 0 else 0x9C00
        windowViewAddress = 0x9800 if getBit(self.ram[LCDC], 3) == 0 else 0x9C00
        tileDataSelect = getBit(self.ram[LCDC], 4)

        for x in xrange((gameboyResolution[0]/8)+1): # For the 20 (+2 overlaps) tiles on a line
            backgroundTileIndex = self.ram[0x9800 + ((xx)/8 + x)%32 + ((y+yy)/8)*32]
            # windowTileIndex = self.ram[0x9C00 + (xx)/8 + x + ((y+yy)/8)*32] # TODO: Find and load only if necessary
            for n in xrange(8): # For the 8 pixels in each tile
                # self.window._screenBuffer[x+n,y] = self.tileCache[backgroundTileIndex + offset + n, y%8]
                screenX = (x * 8) + n - offset
                if screenX < 160:
                    tileIndex = backgroundTileIndex if tileDataSelect == 1 else (getSignedInt8(backgroundTileIndex)+256)
                    self.window._screenBuffer[screenX,y] = self.tileCache[tileIndex*8 + n, (y+yy)%8]
                    # if wy <= y and wx <= x+7 and (self.ram[LCDC] >> 5) & 1 == 1: # Check if Window is on
                    #     windowTileIndex = self.ram[0x9C00 + (xx) / 8 + x + ((y + yy) / 8) * 32]
                    #     self.window._screenBuffer[x, y] = self.tileCache[windowTileIndex*8 + n, (y+wy)%8] # -7 is just a specification

        # for x in xrange(gameboyResolution[0]):
        #     slef.window.window._screenBuffer[x, y] = self.window.tileView1Buffer[(x+xx)%0xFF, (y+yy)%0xFF]
        #     if wy <= y and wx <= x+7 and (self.ram[LCDC] >> 5) & 1 == 1: # Check if Window is on
        #         self.window._screenBuffer[x, y] = self.window.tileView2Buffer[x-wx+7, y-wy] # -7 is just a specification

    def copySprite(self, fromXY, toXY, fromBuffer, toBuffer, colorKey = colorPalette[0], xFlip = 0, yFlip = 0):
        x1,y1 = fromXY
        x2,y2 = toXY

        for y in xrange(8):
            for x in xrange(8):
                xx = x1 + ((7-x) if xFlip == 1 else x)
                yy = (7-y) if yFlip == 1 else y

                pixel = fromBuffer[xx, yy]
                if not colorKey == pixel and 0 <= x2+x < 160 and 0 <= y2+y < 144:
                    toBuffer[x2+x, y2+y] = pixel


    def renderSprites(self):
        # Doesn't restrict 10 sprite pr. scan line.
        # Prioritizes sprite in inverted order
        for n in xrange(0xFE00,0xFEA0,4):
            y = self.ram[n] - 16
            x = self.ram[n+1] - 8
            tileIndex = self.ram[n+2]
            attributes = self.ram[n+3]
            xFlip = getBit(attributes, 5)
            yFlip = getBit(attributes, 6)

            fromXY = (tileIndex * 8, 0)
            toXY = (x, y)

            if x < 160 and y < 144:
                self.copySprite(fromXY, toXY, self.tileCache, self.window._screenBuffer, xFlip = xFlip, yFlip = yFlip)


    def refreshTileData(self):
        # http://gameboy.mongenel.com/dmg/asmmemmap.html
        print "Updating tile Data"
        tileCount = 0
        for n in xrange(0x8000,0x9800,16): #Tile is 16 bytes
            n -= 0x8000

            for k in xrange(0, 16 ,2): #2 bytes for each line
                byte1 = self.ram[0x8000+n+k]
                byte2 = self.ram[0x8000+n+k+1]

                for pixelOnLine in xrange(7,-1,-1):
                    y = k/2
                    x = tileCount*8 + 7-pixelOnLine
                    self.tileCache[x, y] = colorPalette[getColor(byte1, byte2, pixelOnLine)]

            tileCount += 1

        if __debug__:
            for n in xrange(self.window.tileDataHeight/8):
                self.window.tileDataBuffer[0:self.window.tileDataWidth,n*8:(n+1)*8] = self.tileCache[n*self.window.tileDataWidth:(n+1)*self.window.tileDataWidth,0:8]

