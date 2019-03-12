# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import ctypes
import sdl2
import sdl2.ext
import numpy as np

from .. import CoreDump
from ..WindowEvent import WindowEvent
from ..GameWindow import AbstractGameWindow

from ..Logger import logger

gameboyResolution = (160, 144)

def get_color_code(byte1,byte2,offset):
    # The colors are 2 bit and are found like this:
    #
    # Color of the first pixel is 0b10
    # | Color of the second pixel is 0b01
    # v v
    # 1 0 0 1 0 0 0 1 <- byte1
    # 0 1 1 1 1 1 0 0 <- byte2
    return (((byte2 >> (offset)) & 0b1) << 1) + ((byte1 >> (offset)) & 0b1) # 2bit color code

alphaMask = 0x7F000000
tiles = 384


class SdlGameWindow(AbstractGameWindow):
    def __init__(self, scale=1):
        super(self.__class__, self).__init__(scale)

        self.tile_cache = np.ndarray((tiles * 8, 8), dtype='uint32')
        self.sprite_cacheOBP0 = np.ndarray((tiles * 8, 8), dtype='uint32')
        self.sprite_cacheOBP1 = np.ndarray((tiles * 8, 8), dtype='uint32')

        # http://pysdl2.readthedocs.org/en/latest/tutorial/pong.html
        # https://wiki.libsdl.org/SDL_Scancode#Related_Enumerations
        self.windowEventsDown = {
                sdl2.SDLK_UP        : WindowEvent.PressArrowUp,
                sdl2.SDLK_DOWN      : WindowEvent.PressArrowDown,
                sdl2.SDLK_RIGHT     : WindowEvent.PressArrowRight,
                sdl2.SDLK_LEFT      : WindowEvent.PressArrowLeft,
                sdl2.SDLK_a         : WindowEvent.PressButtonA,
                sdl2.SDLK_s         : WindowEvent.PressButtonB,
                sdl2.SDLK_RETURN    : WindowEvent.PressButtonStart,
                sdl2.SDLK_BACKSPACE : WindowEvent.PressButtonSelect,
                sdl2.SDLK_ESCAPE    : WindowEvent.Quit,
                # sdl2.SDLK_e       : self.debug = True
                sdl2.SDLK_d         : WindowEvent.DebugToggle,
                sdl2.SDLK_SPACE     : WindowEvent.PressSpeedUp,
                sdl2.SDLK_i         : WindowEvent.ScreenRecordingToggle,
        }
        self.windowEventsUp = {
                sdl2.SDLK_UP        : WindowEvent.ReleaseArrowUp,
                sdl2.SDLK_DOWN      : WindowEvent.ReleaseArrowDown,
                sdl2.SDLK_RIGHT     : WindowEvent.ReleaseArrowRight,
                sdl2.SDLK_LEFT      : WindowEvent.ReleaseArrowLeft,
                sdl2.SDLK_a         : WindowEvent.ReleaseButtonA,
                sdl2.SDLK_s         : WindowEvent.ReleaseButtonB,
                sdl2.SDLK_RETURN    : WindowEvent.ReleaseButtonStart,
                sdl2.SDLK_BACKSPACE : WindowEvent.ReleaseButtonSelect,
                sdl2.SDLK_z         : WindowEvent.SaveState,
                sdl2.SDLK_x         : WindowEvent.LoadState,
                sdl2.SDLK_SPACE     : WindowEvent.ReleaseSpeedUp,
        }

        self.debug = False

        CoreDump.windowHandle = self

        logger.debug("SDL GameWindow initialization")
        sdl2.ext.init()

        self._scaledResolution = tuple(x * self._scale for x in gameboyResolution)
        logger.debug('Scale: x%s %s' % (self._scale, self._scaledResolution))

        self._window = sdl2.ext.Window("PyBoy", size=self._scaledResolution, flags=sdl2.SDL_WINDOW_RESIZABLE)

        self._renderer = sdl2.ext.Renderer(self._window, -1, gameboyResolution, flags=sdl2.SDL_RENDERER_ACCELERATED)
        self._sdlrenderer = self._renderer.sdlrenderer

        self._sdlTextureBuffer = sdl2.SDL_CreateTexture(self._sdlrenderer, sdl2.SDL_PIXELFORMAT_RGBA32, sdl2.SDL_TEXTUREACCESS_STATIC, *gameboyResolution)
        self._screenBuffer = np.ndarray(gameboyResolution[::-1], dtype='uint32')

        self.blankScreen()
        self._window.show()

        self.ticks = sdl2.SDL_GetTicks()

        self.scanlineParameters = np.ndarray(shape=(gameboyResolution[0],4), dtype='uint8')

        if __debug__:
            self.__setDebug()

    def makeWindowAndGetBuffer(self, width, height, pos_x, pos_y, window_name):
        sdl2.ext.Window.DEFAULTPOS = (pos_x, pos_y)

        window = sdl2.ext.Window(window_name, size=(width, height))
        windowSurface = window.get_surface()
        windowBuffer = pixels2dWithoutWarning(windowSurface)
        window.show()

        return window, windowSurface, windowBuffer

    def dump(self,filename):
        sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle._windowSurface,filename+".bmp")
        if __debug__:
            sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle.tileDataWindowSurface,filename+"_tileData.bmp")
            sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle.tileView2WindowSurface,filename+"_tileView1.bmp")
            sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle.tileView1WindowSurface,filename+"_tileView2.bmp")

    def setTitle(self,title):
        self._window.title = title
        # sdl2.ext.title(self._window,title)
        # sdl2.SDL_SetWindowTitle(self._window,title)

    def __setDebug(self):
        windowOffset = 0
        # Tile Data
        self.tileDataWidth = 16*8 # Change the 16 to whatever wide you want the tile window
        self.tileDataHeight = ((tiles*8) / self.tileDataWidth)*8

        self.tileDataWindow, self.tileDataWindowSurface, self.tileDataBuffer = \
                self.makeWindowAndGetBuffer(self.tileDataWidth, self.tileDataHeight, windowOffset, 0, "Tile Data")
        windowOffset += self.tileDataWidth

        # Background View 1
        self.tileView1Width = 0x100
        self.tileView1Height = 0x100

        self.tileView1Window, self.tileView1WindowSurface, self.tileView1Buffer = \
                self.makeWindowAndGetBuffer(self.tileView1Width, self.tileView1Height, windowOffset, 0, "Tile View 1")
        windowOffset += self.tileView1Width

        # Background View 2
        self.tileView2Width = 0x100
        self.tileView2Height = 0x100

        self.tileView2Window, self.tileView2WindowSurface, self.tileView2Buffer = \
                self.makeWindowAndGetBuffer(self.tileView2Width, self.tileView2Height, windowOffset, 0, "Tile View 2")
        windowOffset += self.tileView2Width

        # Sprite View
        self.spriteWidth = 0x40
        self.spriteHeight = 0x28*2

        self.spriteWindow, self.spriteWindowSurface, self.spriteBuffer = \
                self.makeWindowAndGetBuffer(self.spriteWidth, self.spriteHeight, windowOffset, 0, "Sprite View")
        windowOffset += self.spriteWidth

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
        sdl2.render.SDL_RenderCopy(self._sdlrenderer, self._sdlTextureBuffer, None, None)
        self._renderer.present()
        if __debug__:
            self.tileDataWindow.refresh()
            self.tileView1Window.refresh()
            self.tileView2Window.refresh()
            self.spriteWindow.refresh()

    def frameLimiter(self):
        now = sdl2.SDL_GetTicks()
        sdl2.SDL_Delay(max(0, int(1/60.0*1000-(now-self.ticks))))
        self.ticks = sdl2.SDL_GetTicks()


    def stop(self):
        if __debug__:
            sdl2.SDL_DestroyWindow(self.tileDataWindow.window)
            sdl2.SDL_DestroyWindow(self.tileView1Window.window)
            sdl2.SDL_DestroyWindow(self.tileView2Window.window)
            sdl2.SDL_DestroyWindow(self.spriteWindow.window)
        sdl2.SDL_DestroyWindow(self._window.window)
        sdl2.ext.quit()

    def scanline(self, y, lcd):
        self.scanlineParameters[y] = lcd.get_view_port() + lcd.get_window_pos()

    def renderScreen(self, lcd):
        self.refreshTileData(lcd)

        # All VRAM addresses are offset by 0x8000
        # Following addresses are 0x9800 and 0x9C00
        backgroundViewAddress = 0x1800 if lcd.LCDC.background_map_select == 0 else 0x1C00
        windowViewAddress = 0x1800 if lcd.LCDC.window_map_select == 0 else 0x1C00

        for y in xrange(gameboyResolution[1]):
            xx, yy, wx, wy = self.scanlineParameters[y]
            # xx, yy = lcd.getViewPort()
            offset = xx & 0b111 # Used for the half tile at the left side when scrolling

            for x in xrange(gameboyResolution[0]):
                if lcd.LCDC.background_enable:
                    backgroundTileIndex = lcd.VRAM[backgroundViewAddress + (((xx + x)/8)%32 + ((y+yy)/8)*32)%0x400]

                    if lcd.LCDC.tile_select == 0: # If using signed tile indices
                        # ((x + 128) & 255) - 128 to convert to signed, then add 256 for offset (reduces to + 128)
                        backgroundTileIndex = ((backgroundTileIndex + 128) & 255) + 128

                    self._screenBuffer[y,x] = self.tile_cache[backgroundTileIndex*8 + (x+offset)%8, (y+yy)%8]
                else:
                    # If background is disabled, it becomes white
                    self._screenBuffer[y,x] = self.color_palette[0]

                if lcd.LCDC.window_enabled:
                    # wx, wy = lcd.get_window_pos()
                    if wy <= y and wx <= x:
                        windowTileIndex = lcd.VRAM[windowViewAddress + (((x-wx)/8)%32 + ((y-wy)/8)*32)%0x400]

                        if lcd.LCDC.tile_select == 0: # If using signed tile indices
                            # ((x + 128) & 255) - 128 to convert to signed, then add 256 for offset (reduces to + 128)
                            windowTileIndex = ((windowTileIndex + 128) & 255) + 128

                        self._screenBuffer[y,x] = self.tile_cache[windowTileIndex*8 + (x-(wx))%8, (y-wy)%8]

        ### RENDER SPRITES
        # Doesn't restrict 10 sprite pr. scan line.
        # Prioritizes sprite in inverted order
        # logger.debug("Rendering Sprites")
        spriteSize = 16 if lcd.LCDC.sprite_size else 8
        BGPkey = lcd.BGP.get_color(0)

        for n in xrange(0x00,0xA0,4):
            y = lcd.OAM[n] - 16 #TODO: Simplify reference
            x = lcd.OAM[n+1] - 8
            tileIndex = lcd.OAM[n+2]
            attributes = lcd.OAM[n+3]
            xFlip = bool(attributes & 0b100000)
            yFlip = bool(attributes & 0b1000000)
            spritePriority = bool(attributes & 0b10000000)

            fromXY = (tileIndex * 8, 0)
            toXY = (x, y)

            sprite_cache = self.sprite_cacheOBP1 if attributes & 0b10000 else self.sprite_cacheOBP0

            if x < 160 and y < 144:
                self.copySprite(fromXY, toXY, sprite_cache, self._screenBuffer, spriteSize, spritePriority, BGPkey, xFlip, yFlip)

        # Copy contents of numpy screen buffer into sdlTexture buffer, which will then get scaled to the window
        sdl2.SDL_UpdateTexture(self._sdlTextureBuffer, None, self._screenBuffer.ctypes.data_as(ctypes.c_void_p), self._screenBuffer.strides[0])

    def refreshTileData(self, lcd):
        if self.flush_cache:
            self.tiles_changed.clear()
            for x in xrange(0x8000,0x9800,16):
                self.tiles_changed.add(x)
            self.flush_cache = False

        for t in self.tiles_changed:
            t -= 0x8000
            for k in xrange(0, 16 ,2): #2 bytes for each line
                byte1 = lcd.VRAM[t+k]
                byte2 = lcd.VRAM[t+k+1]

                for pixelOnLine in xrange(7,-1,-1):
                    y = k/2
                    x = t/2 + 7-pixelOnLine

                    color_code = get_color_code(byte1, byte2, pixelOnLine)

                    self.tile_cache[x, y] = lcd.BGP.get_color(color_code)
                    # TODO: Find a more optimal way to do this
                    alpha = 0x00000000
                    if color_code == 0:
                        alpha = alphaMask # Add alpha channel
                    self.sprite_cacheOBP0[x, y] = lcd.OBP0.get_color(color_code) + alpha
                    self.sprite_cacheOBP1[x, y] = lcd.OBP1.get_color(color_code) + alpha

        self.tiles_changed.clear()

    def copySprite(self, fromXY, toXY, fromBuffer, toBuffer, spriteSize, spritePriority, BGPkey, xFlip = 0, yFlip = 0):
        x1,y1 = fromXY
        x2,y2 = toXY

        for y in xrange(spriteSize):
            yy = ((spriteSize-1)-y) if yFlip else y
            yy %= 8
            for x in xrange(8):
                xx = x1 # Base coordinate
                xx += ((7-x) if xFlip else x) # Reverse order, if sprite is x-flipped

                if spriteSize == 16: # If y-flipped on 8x16 sprites, we will have to load the sprites in reverse order
                    xx += (y&0b1000)^(yFlip<<3) # Shifting tile, when iteration past 8th line

                pixel = fromBuffer[xx, yy]

                if 0 <= x2+x < 160 and 0 <= y2+y < 144:
                    if not (not spritePriority or (spritePriority and toBuffer[y2+y, x2+x] == BGPkey)):
                        pixel += alphaMask # Add a fake alphachannel to the sprite for BG pixels.
                                            # We can't just merge this with the next if, as
                                            # sprites can have an alpha channel in other ways

                    if not (pixel & alphaMask):
                        toBuffer[y2+y, x2+x] = pixel


    def blankScreen(self):
        # If the screen is off, fill it with a color.
        if __debug__:
            # Currently, it's dark purple
            self._screenBuffer.fill(0x00403245)
        else:
            # Pan docs says it should be white, but it does fit with Pokemon?
            # self._screenBuffer.fill(0x00FFFFFF)
            self._screenBuffer.fill(0x00000000)


    def getScreenBuffer(self):
        return self._screenBuffer.T

    #################################################################
    #
    # Drawing debug tile views
    #
    #################################################################


    def refreshDebugWindows(self, lcd):
        self.refreshTileView1(lcd)
        self.refreshTileView2(lcd)
        self.refreshSpriteView(lcd)
        self.drawTileCacheView(lcd)
        # self.drawTileView1ScreenPort(lcd)
        # self.drawTileView2WindowPort(lcd)


    def copyTile(self, fromXY, toXY, fromBuffer, toBuffer):
        x1,y1 = fromXY
        x2,y2 = toXY

        tileSize = 8
        toBuffer[y2:y2+tileSize, x2:x2+tileSize] = fromBuffer[y1:y1+tileSize, x1:x1+tileSize]

    def refreshTileView1(self, lcd):
        # self.tileView1Buffer.fill(0x00ABC4FF)

        tileSize = 8
        winHorTileView1Limit = 32
        winVerTileView1Limit = 32

        for n in xrange(0x1800,0x1C00):
            tileIndex = lcd.VRAM[n] #TODO: Simplify this reference -- and reoccurences

            # Check the tile source and add offset
            # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
            # BG & Window Tile Data Select   (0=8800-97FF, 1=8000-8FFF)
            if (lcd.LCDC.value >> 4) & 1 == 0: #TODO: use correct flag
                # ((x + 128) & 255) - 128 to convert to signed, then add 256 for offset (reduces to + 128)
                tileIndex = ((tileIndex + 128) & 255) + 128

            tile_column = (n-0x1800)%winHorTileView1Limit # Horizontal tile number wrapping on 16
            tileRow = (n-0x1800)/winVerTileView1Limit # Vertical time number based on tileColumn

            fromXY = ((tileIndex*8)%self.tileDataWidth, ((tileIndex*8)/self.tileDataWidth)*8)
            toXY = (tile_column*8, tileRow*8)

            self.copyTile(fromXY, toXY, self.tileDataBuffer, self.tileView1Buffer)

    def refreshTileView2(self, lcd):
        # self.tileView2Buffer.fill(0x00ABC4FF)

        tileSize = 8
        winHorTileView2Limit = 32
        winVerTileView2Limit = 32

        for n in xrange(0x1C00,0x2000):
            tileIndex = lcd.VRAM[n]

            # Check the tile source and add offset
            # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
            # BG & Window Tile Data Select   (0=8800-97FF, 1=8000-8FFF)
            if (lcd.LCDC.value >> 4) & 1 == 0:
                # ((x + 128) & 255) - 128 to convert to signed, then add 256 for offset (reduces to + 128)
                tileIndex = ((tileIndex + 128) & 255) + 128

            tile_column = (n-0x1C00)%winHorTileView2Limit # Horizontal tile number wrapping on 16
            tileRow = (n-0x1C00)/winVerTileView2Limit # Vertical time number based on tileColumn

            fromXY = ((tileIndex*8)%self.tileDataWidth, ((tileIndex*8)/self.tileDataWidth)*8)
            toXY = (tile_column*8, tileRow*8)

            self.copyTile(fromXY, toXY, self.tileDataBuffer, self.tileView2Buffer)


    def drawTileCacheView(self, lcd):
        for n in xrange(self.tileDataHeight/8):
            self.tileDataBuffer[0:self.tileDataWidth,n*8:(n+1)*8] = self.tile_cache[n*self.tileDataWidth:(n+1)*self.tileDataWidth,0:8]

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
            tileIndex = lcd.OAM[n+2] # TODO: Simplify this reference
            attributes = lcd.OAM[n+3]
            fromXY = (tileIndex * 8, 0)

            i = n*2
            self.copyTile(fromXY, (i%self.spriteWidth, (i/self.spriteWidth)*16), self.sprite_cacheOBP0, self.spriteBuffer)
            # if lcd.LCDC.spriteSize:
            if lcd.LCDC.sprite_size:
                self.copyTile((tileIndex * 8+8, 0), (i%self.spriteWidth, (i/self.spriteWidth)*16 + 8), self.sprite_cacheOBP0, self.spriteBuffer)
