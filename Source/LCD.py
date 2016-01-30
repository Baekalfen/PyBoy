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

    def tick(self):
        if __debug__:
            self.refreshTileView1()
            self.refreshTileView2()
            self.drawTileView1ScreenPort()
            self.drawTileView2WindowPort()

        # Check LCDC to see if display is on
        # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
        # print "LCD Tick",bin(self.ram[LCDC]),hex(self.ram[LCDC])
        if self.ram[LCDC] >> 7 == 1:
            if self.ram.updateVRAMCache:
                self.refreshTileData()
                self.ram.updateVRAMCache = False
            self.renderSprites()
        else:
            # If the screen is off, fill it with a color.
            # Currently, it's dark purple, but the Game Boy had a white screen
            self.window._screenBuffer.fill(0x00403245)


    def getWindowPos(self):
        return self.ram[WX]-7, self.ram[WY]

    def getViewPort(self):
        return self.ram[SCX], self.ram[SCY]

    def scanline(self, y):
        backgroundViewAddress = 0x9800 if getBit(self.ram[LCDC], 3) == 0 else 0x9C00
        windowViewAddress = 0x9800 if getBit(self.ram[LCDC], 6) == 0 else 0x9C00
        tileDataSelect = getBit(self.ram[LCDC], 4)

        xx, yy = self.getViewPort()
        wx, wy = self.getWindowPos()
        wx -= 7
        wy -= 1

        offset = (xx - (xx & 0b11111000)) # Difference between absolute xx and rounded down to nearest tile

        for x in xrange(-offset, gameboyResolution[0]): # For the 20 (+1 overlap) tiles on a line
            tileX = x+offset
            if tileX % 8 == 0:
                backgroundTileIndex = self.ram[backgroundViewAddress + ((xx)/8 + tileX/8)%32 + ((y+yy)/8)*32]
                windowTileIndex = self.ram[windowViewAddress + ((-wx)/8 + x/8)%32 + ((y-wy)/8)*32]

                if tileDataSelect == 0: # If using signed tile indices
                    backgroundTileIndex = getSignedInt8(backgroundTileIndex)+256
                    windowTileIndex = getSignedInt8(windowTileIndex)+256


            #TODO: Possibly utilize NumPy to copy 8 pixels at a time?
            # if screenX < 160:#TODO: Check if background is turned on
            self.window._screenBuffer[x,y] = self.tileCache[backgroundTileIndex*8 + tileX%8, (y+yy)%8]

            if wy <= y and wx <= x and (self.ram[LCDC] >> 5) & 1 == 1: # Check if Window is on
                self.window._screenBuffer[x, y] = self.tileCache[windowTileIndex*8 + (x+offset)%8, (y+wy)%8]


        # if wy <= y and (self.ram[LCDC] >> 5) & 1 == 1:
        #     for x in xrange(wx,gameboyResolution[0]):
        #         print x
        #         if x % 8 == 0:
        #             windowTileIndex = self.ram[windowViewAddress + ((-wx)/8 + x/8)%32 + ((y-wy)/8)*32]
        #             windowTileIndex = getSignedInt8(windowTileIndex)+256
        #         self.window._screenBuffer[x, y] = self.tileCache[windowTileIndex*8 + (x)%8, (y+wy)%8]


        # for x in xrange((gameboyResolution[0]/8)+1): # For the 20 (+1 overlap) tiles on a line
        #     backgroundTileIndex = self.ram[backgroundViewAddress + ((xx)/8 + x)%32 + ((y+yy)/8)*32]
        #     windowTileIndex = self.ram[windowViewAddress + ((-wx)/8 + x)%32 + ((y-wy)/8)*32]

        #     if tileDataSelect == 0: # If using signed tile indices
        #         backgroundTileIndex = getSignedInt8(backgroundTileIndex)+256
        #         windowTileIndex = getSignedInt8(windowTileIndex)+256

        #     for n in xrange(8): # For the 8 pixels in each tile
        #         screenX = (x * 8) + n - offset

        #         if screenX < 160:#TODO: Check if background is turned on
        #             self.window._screenBuffer[screenX,y] = self.tileCache[backgroundTileIndex*8 + n, (y+yy)%8]

        #         windowX = x*8+n
        #         if wy <= y and wx <= windowX and windowX < 160 and (self.ram[LCDC] >> 5) & 1 == 1: # Check if Window is on
        #             self.window._screenBuffer[windowX, y] = self.tileCache[windowTileIndex*8 + n, (y+wy)%8]


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
        # print "Rendering Sprites"
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
            #TODO: -0x8000 is unnecessary
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




    #################################################################
    #
    # Drawing debug tile views
    #
    #################################################################

    def copyTile(self, fromXY, toXY, fromBuffer, toBuffer):
        x1,y1 = fromXY
        x2,y2 = toXY

        for y in xrange(8):
            for x in xrange(8):
                toBuffer[x2+x, y2+y] = fromBuffer[x1+x, y1+y]

    def refreshTileView1(self):
        # self.window.tileView1Buffer.fill(0x00ABC4FF)
        
        tileSize = 8
        winHorTileView1Limit = 32
        winVerTileView1Limit = 32

        for n in xrange(0x9800,0x9C00):
            tileIndex = self.ram[n]

            # Check the tile source and add offset
            # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
            # BG & Window Tile Data Select   (0=8800-97FF, 1=8000-8FFF)
            if (self.ram[LCDC] >> 4) & 1 == 0:
                tileIndex = 256 + getSignedInt8(tileIndex)

            tileColumn = (n-0x9800)%winHorTileView1Limit # Horizontal tile number wrapping on 16
            tileRow = (n-0x9800)/winVerTileView1Limit # Vertical time number based on tileColumn
            
            fromXY = ((tileIndex*8)%self.window.tileDataWidth, ((tileIndex*8)/self.window.tileDataWidth)*8)
            toXY = (tileColumn*8, tileRow*8)

            self.copyTile(fromXY, toXY, self.window.tileDataBuffer, self.window.tileView1Buffer)

    def refreshTileView2(self):
        # self.window.tileView2Buffer.fill(0x00ABC4FF)
         
        tileSize = 8
        winHorTileView2Limit = 32
        winVerTileView2Limit = 32

        for n in xrange(0x9C00,0xA000):
            tileIndex = self.ram[n]

            # Check the tile source and add offset
            # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
            # BG & Window Tile Data Select   (0=8800-97FF, 1=8000-8FFF)
            if (self.ram[LCDC] >> 4) & 1 == 0:
                tileIndex = 256 + getSignedInt8(tileIndex)

            tileColumn = (n-0x9C00)%winHorTileView2Limit # Horizontal tile number wrapping on 16
            tileRow = (n-0x9C00)/winVerTileView2Limit # Vertical time number based on tileColumn
            
            fromXY = ((tileIndex*8)%self.window.tileDataWidth, ((tileIndex*8)/self.window.tileDataWidth)*8)
            toXY = (tileColumn*8, tileRow*8)

            self.copyTile(fromXY, toXY, self.window.tileDataBuffer, self.window.tileView2Buffer)

    def drawTileView1ScreenPort(self):
        xx, yy = self.getViewPort()

        width = gameboyResolution[0]
        height = gameboyResolution[1]

        self.drawHorLine(xx       , yy        ,width  , self.window.tileView1Buffer)
        self.drawHorLine(xx       , yy+height ,width  , self.window.tileView1Buffer)

        self.drawVerLine(xx       , yy        ,height , self.window.tileView1Buffer)
        self.drawVerLine(xx+width , yy        ,height , self.window.tileView1Buffer)

    def drawTileView2WindowPort(self):
        xx, yy = self.getWindowPos()

        xx = -xx
        yy = -yy

        width = gameboyResolution[0]
        height = gameboyResolution[1]

        self.drawHorLine(xx       , yy        ,width  , self.window.tileView2Buffer)
        self.drawHorLine(xx       , yy+height ,width  , self.window.tileView2Buffer)

        self.drawVerLine(xx       , yy        ,height , self.window.tileView2Buffer)
        self.drawVerLine(xx+width , yy        ,height , self.window.tileView2Buffer)


    def drawHorLine(self,xx,yy,length,screen,color = 0):
        for x in xrange(length):
            screen[(xx+x)%0xFF,yy&0xFF] = color

    def drawVerLine(self,xx,yy,length,screen,color = 0):
        for y in xrange(length):
            screen[xx&0xFF,(yy+y)&0xFF] = color
