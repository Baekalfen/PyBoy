# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from MathUint8 import getSignedInt8

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
        # p. 54 of GBCPUman.pdf says 70224 clks per frame. We calculate 69905 clks
        # self.CYCLE_INTERVAL = 4194304/60  # 4Mhz divided by 60 fps = cycles per frame (rounded down)

    def setIORegister(self, register, v):
        self.ram[register] = v

    def getIORegister(self, register):
        return self.ram[register]

    def tick(self):
        #TODO: Cache the all of this. The TileData and TileViews are rarely cleared completely between frames
        self.refreshTileData()
        self.refreshTileView1()
        self.refreshTileView2()
        if __debug__:
            
            self.window.blitBuffer(self.window.tileDataWindowSurfaceBuffer, self.window.tileDataBuffer)
            self.window.blitBuffer(self.window.tileView1WindowSurfaceBuffer, self.window.tileView1Buffer)
            self.window.blitBuffer(self.window.tileView2WindowSurfaceBuffer, self.window.tileView2Buffer)

            self.drawTileView1ScreenPort()

        # Check LCDC to see if display is on
        # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
        if self.ram[LCDC] >> 7 == 1:
            xx, yy = self.getViewPort()
            for x in xrange(gameboyResolution[0]):
                for y in xrange(gameboyResolution[1]):
                    self.window._screenBuffer[x, y] = self.window.tileView1Buffer[(x+xx)%0xFF, (y+yy)%0xFF]
                    # self._screenBuffer[x, y] = self.tileView2Buffer[x+xx, y+yy]

            self.window.blitBuffer(self.window._windowSurfaceBuffer,self.window._screenBuffer)
        else:
            self.window._windowSurfaceBuffer.fill(0x00403245)


    def getViewPort(self):
        return self.ram[SCX],self.ram[SCY]

    def copyTile(self, fromXY, toXY, fromBuffer, toBuffer):
        x1,y1 = fromXY
        x2,y2 = toXY

        for y in xrange(8):
            for x in xrange(8):
                toBuffer[x2+x, y2+y] = fromBuffer[x1+x, y1+y]

    def refreshOAMView(self):
        pass

    def refreshTileView1(self):
        self.window.tileView1Buffer.fill(0x00ABC4FF)
        
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
        self.window.tileView2Buffer.fill(0x00ABC4FF)
         
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



    def refreshTileData(self):
        # http://gameboy.mongenel.com/dmg/asmmemmap.html
        if __debug__:
            self.window.tileDataBuffer.fill(0x00ABC4FF)
        tileSize = 16 #Tile is 16 bytes
        horTileLimit = 32#self.window.tileDataWidth/8
        verTileLimit = 32#self.window.tileDataHeight/8
        for n in xrange(0x8000,0x9800,tileSize): #Tile is 16 bytes
            n -= 0x8000

            horTileNumb = (n/tileSize)%horTileLimit # Horizontal tile number wrapping on 16
            verTileNumb = (n/tileSize)/verTileLimit # Vertical time number
            for k in xrange(0,tileSize,2): #2 bytes for each line
                byte1 = self.ram[0x8000+n+k]
                byte2 = self.ram[0x8000+n+k+1]

                for pixelOnLine in xrange(7,-1,-1):
                    lineNumb = k/2

                    #TODO: Make a single getColor call for the whole for-loop
                    self.window.tileDataBuffer[horTileNumb*8 + 7-pixelOnLine, verTileNumb*8 + lineNumb] = colorPalette[getColor(byte1, byte2, pixelOnLine)]

    def drawTileView1ScreenPort(self):
        xx, yy = self.getViewPort()

        width = gameboyResolution[0]
        height = gameboyResolution[1]

        self.drawHorLine(xx       , yy        ,width  , self.window.tileView1WindowSurfaceBuffer)
        self.drawHorLine(xx       , yy+height ,width  , self.window.tileView1WindowSurfaceBuffer)

        self.drawVerLine(xx       , yy        ,height , self.window.tileView1WindowSurfaceBuffer)
        self.drawVerLine(xx+width , yy        ,height , self.window.tileView1WindowSurfaceBuffer)

    def drawHorLine(self,xx,yy,length,screen,color = 0):
        for x in xrange(length):
            screen[(xx+x)%0xFF,yy&0xFF] = color

    def drawVerLine(self,xx,yy,length,screen,color = 0):
        for y in xrange(length):
            screen[xx&0xFF,(yy+y)&0xFF] = color