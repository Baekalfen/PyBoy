# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys
from random import randint
import time
import sdl2
import sdl2.ext
import numpy
import CoreDump
import time

from MathUint8 import getSignedInt8, getBit
from WindowEvent import WindowEvent
from LCD import colorPalette

gameboyResolution = (160, 144)

class Window():
    def __init__(self, logger, scale=1):
        self.logger = logger
        assert isinstance(scale, int), "Window scale has to be an integer!"
        self._scale = scale

        # http://pysdl2.readthedocs.org/en/latest/tutorial/pong.html
        # https://wiki.libsdl.org/SDL_Scancode#Related_Enumerations
        self.windowEventsDown = {
                sdl2.SDLK_UP : WindowEvent.PressArrowUp,
                sdl2.SDLK_DOWN: WindowEvent.PressArrowDown,
                sdl2.SDLK_RIGHT: WindowEvent.PressArrowRight,
                sdl2.SDLK_LEFT: WindowEvent.PressArrowLeft,
                sdl2.SDLK_a: WindowEvent.PressButtonA,
                sdl2.SDLK_s: WindowEvent.PressButtonB,
                sdl2.SDLK_RETURN: WindowEvent.PressButtonStart,
                sdl2.SDLK_BACKSPACE: WindowEvent.PressButtonSelect,
                sdl2.SDLK_ESCAPE: WindowEvent.Quit,
                # sdl2.SDLK_e: self.debug = True
                sdl2.SDLK_d: WindowEvent.DebugNext,
                sdl2.SDLK_SPACE: WindowEvent.PressSpeedUp,
        }
        self.windowEventsUp = {
                sdl2.SDLK_UP: WindowEvent.ReleaseArrowUp,
                sdl2.SDLK_DOWN: WindowEvent.ReleaseArrowDown,
                sdl2.SDLK_RIGHT: WindowEvent.ReleaseArrowRight,
                sdl2.SDLK_LEFT: WindowEvent.ReleaseArrowLeft,
                sdl2.SDLK_a: WindowEvent.ReleaseButtonA,
                sdl2.SDLK_s: WindowEvent.ReleaseButtonB,
                sdl2.SDLK_RETURN: WindowEvent.ReleaseButtonStart,
                sdl2.SDLK_BACKSPACE: WindowEvent.ReleaseButtonSelect,
                sdl2.SDLK_z: WindowEvent.SaveState,
                sdl2.SDLK_x: WindowEvent.LoadState,
                sdl2.SDLK_SPACE: WindowEvent.ReleaseSpeedUp,
        }

        self.debug = False

        CoreDump.windowHandle = self

        self.logger("SDL initialization")
        sdl2.ext.init()

        scaledResolution = tuple(x * self._scale for x in gameboyResolution)

        self._window = sdl2.ext.Window("PyBoy", size=scaledResolution)
        self._windowSurface = self._window.get_surface()

        self._screenBuffer = sdl2.ext.pixels2d(self._windowSurface)
        self._screenBuffer.fill(0x00558822)
        self._window.show()

        # Only used for VSYNC
        self.win = sdl2.SDL_CreateWindow("", 0,0,0,0, 0) # Hack doesn't work, if hidden # sdl2.SDL_WINDOW_HIDDEN)
        self.renderer = sdl2.SDL_CreateRenderer(self.win, -1, sdl2.SDL_RENDERER_PRESENTVSYNC)

        if __debug__:
            windowOffset = 0
            # Tile Data
            tiles = 384
            self.tileDataWidth = 16*8 # Change the 16 to whatever wide you want the tile window
            self.tileDataHeight = ((tiles*8) / self.tileDataWidth)*8

            # TODO: Make a function to DRY. makeWindowAndGetBuffer(etc..) or something like that
            sdl2.ext.Window.DEFAULTPOS = (windowOffset, 0)
            windowOffset += self.tileDataWidth

            self.tileDataWindow = sdl2.ext.Window("Tile Data", size=(self.tileDataWidth, self.tileDataHeight))
            self.tileDataWindowSurface = self.tileDataWindow.get_surface()
            self.tileDataBuffer = sdl2.ext.pixels2d(self.tileDataWindowSurface)
            self.tileDataWindow.show()

            # # Background View 1
            self.tileView1Width = 0x100
            self.tileView1Height = 0x100

            sdl2.ext.Window.DEFAULTPOS = (windowOffset, 0)
            windowOffset += self.tileView1Width

            self.tileView1Window = sdl2.ext.Window("Tile View 1", size=(self.tileView1Width, self.tileView1Height))
            self.tileView1WindowSurface = self.tileView1Window.get_surface()
            self.tileView1Buffer = sdl2.ext.pixels2d(self.tileView1WindowSurface)
            self.tileView1Window.show()

            # # Background View 2
            self.tileView2Width = 0x100
            self.tileView2Height = 0x100

            sdl2.ext.Window.DEFAULTPOS = (windowOffset, 0)
            windowOffset += self.tileView2Width

            self.tileView2Window = sdl2.ext.Window("Tile View 2", size=(self.tileView2Width, self.tileView2Height))
            self.tileView2WindowSurface = self.tileView2Window.get_surface()
            self.tileView2Buffer = sdl2.ext.pixels2d(self.tileView2WindowSurface)
            self.tileView2Window.show()

            # # Sprite View
            self.spriteWidth = 0x40
            self.spriteHeight = 0x28*2

            sdl2.ext.Window.DEFAULTPOS = (windowOffset, 0)
            # windowOffset += self.spriteWidth # Not necessary yet

            self.spriteWindow = sdl2.ext.Window("Sprite View", size=(self.spriteWidth, self.spriteHeight))
            self.spriteWindowSurface = self.spriteWindow.get_surface()
            self.spriteBuffer = sdl2.ext.pixels2d(self.spriteWindowSurface)
            self.spriteWindow.show()


    def dump(self,filename):
        sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle._windowSurface,filename+".bmp")
        if __debug__:
            sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle.tileDataWindowSurface,filename+"tileData.bmp")
            sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle.tileView2WindowSurface,filename+"tileView1.bmp")
            sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle.tileView1WindowSurface,filename+"tileView2.bmp")

    def setTitle(self,title):
        sdl2.ext.title(self._window,title)
        # sdl2.SDL_SetWindowTitle(self._window,title)

    def getEvents(self):
        events = []

        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                events.append(WindowEvent.Quit)
            elif event.type == sdl2.SDL_KEYDOWN:
                events.append(self.windowEventsDown.get(event.key.keysym.sym, None))
            elif event.type == sdl2.SDL_KEYUP:
                events.append(self.windowEventsUp.get(event.key.keysym.sym, None))

        return events

    def updateDisplay(self):
        # self.logger("Updating Display")
        # self.logger(self._screenBuffer.shape)
        # self.logger(self._screenBuffer[:gameboyResolution[0],:gameboyResolution[1]].shape)
        # self._screenBuffer = numpy.repeat(self._screenBuffer[:gameboyResolution[0],:gameboyResolution[1]],self._scale,axis=1)
        # self._screenBuffer[200:200+gameboyResolution[0],200:200+gameboyResolution[1]] = self._screenBuffer[:gameboyResolution[0],:gameboyResolution[1]]
        # self._screenBuffer[:,:] = numpy.repeat(numpy.repeat(self._screenBuffer[:gameboyResolution[0],:gameboyResolution[1]],self._scale, axis=0), self._scale, axis=1)
        # self._screenBuffer[:,:] = numpy.kron(self._screenBuffer[:gameboyResolution[0],:gameboyResolution[1]], [[1,1],[1,1]])

        self._window.refresh()
        if __debug__:
            self.tileDataWindow.refresh()
            self.tileView1Window.refresh()
            self.tileView2Window.refresh()
            self.spriteWindow.refresh()
        # self.VSync()

    def VSync(self):
        sdl2.SDL_RenderPresent(self.renderer)

    def stop(self):
        # self._window.stop()
        sdl2.ext.quit()

    def scanline(self, y, lcd):
        # All VRAM addresses are offset by 0x8000
        # Following addresses are 0x9800 and 0x9C00
        backgroundViewAddress = 0x1800 if lcd.LCDC.backgroundMapSelect == 0 else 0x1C00
        windowViewAddress = 0x1800 if lcd.LCDC.windowMapSelect == 0 else 0x1C00

        xx, yy = lcd.getViewPort()
        offset = xx & 0b111 # Used for the half tile at the left side when scrolling

        for x in range(gameboyResolution[0]):
            if lcd.LCDC.backgroundEnable:
                backgroundTileIndex = lcd.MB.ram.VRAM[backgroundViewAddress + (((xx + x)/8)%32 + ((y+yy)/8)*32)%0x400]

                if lcd.LCDC.tileSelect == 0: # If using signed tile indices
                    backgroundTileIndex = getSignedInt8(backgroundTileIndex)+256

                self._screenBuffer[x,y] = lcd.tileCache[backgroundTileIndex*8 + (x+offset)%8, (y+yy)%8]

            if lcd.LCDC.windowEnabled:
                wx, wy = lcd.getWindowPos()
                if wy <= y and wx <= x:
                    windowTileIndex = lcd.MB.ram.VRAM[windowViewAddress + (((x-wx)/8)%32 + ((y-wy)/8)*32)%0x400]

                    if lcd.LCDC.tileSelect == 0: # If using signed tile indices
                        windowTileIndex = getSignedInt8(windowTileIndex)+256

                    self._screenBuffer[x,y] = lcd.tileCache[windowTileIndex*8 + (x-(wx))%8, (y-wy)%8]


    def copySprite(self, fromXY, toXY, fromBuffer, toBuffer, spriteSize, colorKey, xFlip = 0, yFlip = 0):
        x1,y1 = fromXY
        x2,y2 = toXY

        for y in xrange(spriteSize):
            yy = ((spriteSize-1)-y) if yFlip else y
            yy %= 8
            for x in xrange(8):
                xx = x1 # Base coordinate
                xx += ((7-x) if xFlip == 1 else x) # Reverse order, if sprite is x-flipped
                if spriteSize == 16: # If y-flipped on 8x16 sprites, we will have to load the sprites in reverse order
                    xx += (y&0b1000)^(yFlip<<3) # Shifting tile, when iteration past 8th line


                pixel = fromBuffer[xx, yy]
                if not colorKey == pixel and 0 <= x2+x < 160 and 0 <= y2+y < 144:
                    toBuffer[x2+x, y2+y] = pixel


    def renderSprites(self, lcd):
        # Doesn't restrict 10 sprite pr. scan line.
        # Prioritizes sprite in inverted order
        # self.logger("Rendering Sprites")
        spriteSize = 16 if lcd.LCDC.spriteSize else 8

        for n in xrange(0x00,0xA0,4):
            y = lcd.MB.ram.OAM[n] - 16 #TODO: Simplify reference
            x = lcd.MB.ram.OAM[n+1] - 8
            tileIndex = lcd.MB.ram.OAM[n+2]
            attributes = lcd.MB.ram.OAM[n+3]
            xFlip = getBit(attributes, 5)
            yFlip = getBit(attributes, 6)

            fromXY = (tileIndex * 8, 0)
            toXY = (x, y)

            if x < 160 and y < 144:
                self.copySprite(fromXY, toXY, lcd.tileCache, self._screenBuffer, spriteSize, colorKey = colorPalette[0], xFlip = xFlip, yFlip = yFlip)


    def blankScreen(self):
        # If the screen is off, fill it with a color.
        # Currently, it's dark purple, but the Game Boy had a white screen
        self._screenBuffer.fill(0x00403245)

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

    def refreshTileView1(self, lcd):
        # self.tileView1Buffer.fill(0x00ABC4FF)

        tileSize = 8
        winHorTileView1Limit = 32
        winVerTileView1Limit = 32

        for n in xrange(0x1800,0x1C00):
            tileIndex = lcd.MB.ram.VRAM[n] #TODO: Simplify this reference -- and reoccurences

            # Check the tile source and add offset
            # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
            # BG & Window Tile Data Select   (0=8800-97FF, 1=8000-8FFF)
            if (lcd.LCDC.value >> 4) & 1 == 0: #TODO: use correct flag
                tileIndex = 256 + getSignedInt8(tileIndex)

            tileColumn = (n-0x1800)%winHorTileView1Limit # Horizontal tile number wrapping on 16
            tileRow = (n-0x1800)/winVerTileView1Limit # Vertical time number based on tileColumn

            fromXY = ((tileIndex*8)%self.tileDataWidth, ((tileIndex*8)/self.tileDataWidth)*8)
            toXY = (tileColumn*8, tileRow*8)

            self.copyTile(fromXY, toXY, self.tileDataBuffer, self.tileView1Buffer)

    def refreshTileView2(self, lcd):
        # self.tileView2Buffer.fill(0x00ABC4FF)

        tileSize = 8
        winHorTileView2Limit = 32
        winVerTileView2Limit = 32

        for n in xrange(0x1C00,0x2000):
            tileIndex = lcd.MB.ram.VRAM[n]

            # Check the tile source and add offset
            # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
            # BG & Window Tile Data Select   (0=8800-97FF, 1=8000-8FFF)
            if (lcd.LCDC.value >> 4) & 1 == 0:
                tileIndex = 256 + getSignedInt8(tileIndex)

            tileColumn = (n-0x1C00)%winHorTileView2Limit # Horizontal tile number wrapping on 16
            tileRow = (n-0x1C00)/winVerTileView2Limit # Vertical time number based on tileColumn

            fromXY = ((tileIndex*8)%self.tileDataWidth, ((tileIndex*8)/self.tileDataWidth)*8)
            toXY = (tileColumn*8, tileRow*8)

            self.copyTile(fromXY, toXY, self.tileDataBuffer, self.tileView2Buffer)


    def drawTileCacheView(self, lcd):
        for n in xrange(self.tileDataHeight/8):
            self.tileDataBuffer[0:self.tileDataWidth,n*8:(n+1)*8] = lcd.tileCache[n*self.tileDataWidth:(n+1)*self.tileDataWidth,0:8]

    def drawTileView1ScreenPort(self, lcd):
        xx, yy = lcd.getViewPort()

        width = gameboyResolution[0]
        height = gameboyResolution[1]

        self.drawHorLine(xx       , yy        ,width  , self.tileView1Buffer)
        self.drawHorLine(xx       , yy+height ,width  , self.tileView1Buffer)

        self.drawVerLine(xx       , yy        ,height , self.tileView1Buffer)
        self.drawVerLine(xx+width , yy        ,height , self.tileView1Buffer)

    def drawTileView2WindowPort(self, lcd):
        xx, yy = lcd.getWindowPos()

        xx = -xx
        yy = -yy

        width = gameboyResolution[0]
        height = gameboyResolution[1]

        self.drawHorLine(xx       , yy        ,width  , self.tileView2Buffer)
        self.drawHorLine(xx       , yy+height ,width  , self.tileView2Buffer)

        self.drawVerLine(xx       , yy        ,height , self.tileView2Buffer)
        self.drawVerLine(xx+width , yy        ,height , self.tileView2Buffer)


    def drawHorLine(self,xx,yy,length,screen,color = 0):
        for x in xrange(length):
            screen[(xx+x)%0xFF,yy&0xFF] = color

    def drawVerLine(self,xx,yy,length,screen,color = 0):
        for y in xrange(length):
            screen[xx&0xFF,(yy+y)&0xFF] = color


    def refreshSpriteView(self, lcd):
        self.spriteBuffer.fill(0x00ABC4FF)
        for n in xrange(0x00,0xA0,4):
            tileIndex = lcd.MB.ram.OAM[n+2] # TODO: Simplify this reference
            attributes = lcd.MB.ram.OAM[n+3]
            fromXY = (tileIndex * 8, 0)

            i = n*2
            self.copyTile(fromXY, (i%self.spriteWidth, (i/self.spriteWidth)*16), lcd.tileCache, self.spriteBuffer)
            if lcd.LCDC.spriteSize:
                self.copyTile((tileIndex * 8+8, 0), (i%self.spriteWidth, (i/self.spriteWidth)*16 + 8), lcd.tileCache, self.spriteBuffer)
