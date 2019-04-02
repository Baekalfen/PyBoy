# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys
import sdl2
import sdl2.ext

from ..Logger import logger
from .. import WindowEvent
from .GenericWindow import GenericWindow

gameboyResolution = (160, 144)

def getColorCode(byte1,byte2,offset):
    # The colors are 2 bit and are found like this:
    #
    # Color of the first pixel is 0b10
    # | Color of the second pixel is 0b01
    # v v
    # 1 0 0 1 0 0 0 1 <- byte1
    # 0 1 1 1 1 1 0 0 <- byte2
    return (((byte2 >> (offset)) & 0b1) << 1) + ((byte1 >> (offset)) & 0b1) # 2bit color code

class SdlWindow(GenericWindow):
    def __init__(self, scale=1):
        GenericWindow.__init__(self, scale)

        self._screenBuffer = bytearray([0] * (gameboyResolution[0]*gameboyResolution[1]*4))
        self.screenBuffer = memoryview(self._screenBuffer).cast('I', shape=gameboyResolution[::-1])
        self._tileCache = bytearray([0] * (384*8*8*4))
        self.tileCache = memoryview(self._tileCache).cast('I', shape=[384*8, 8])
        self._spriteCacheOBP0 = bytearray([0] * (384*8*8*4))
        self.spriteCacheOBP0 = memoryview(self._spriteCacheOBP0).cast('I', shape=[384*8, 8])
        self._spriteCacheOBP1 = bytearray([0] * (384*8*8*4))
        self.spriteCacheOBP1 = memoryview(self._spriteCacheOBP1).cast('I', shape=[384*8, 8])

        self.scanlineParameters = [[0,0,0,0] for _ in range(gameboyResolution[1])]

    def init(self):
        self.ticks = sdl2.SDL_GetTicks()

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

        sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) # Should be less... https://wiki.libsdl.org/SDL_Init

        self._window = sdl2.SDL_CreateWindow(
                b"PyBoy",
                sdl2.SDL_WINDOWPOS_CENTERED,
                sdl2.SDL_WINDOWPOS_CENTERED,
                self._scaledResolution[0],
                self._scaledResolution[1],
                sdl2.SDL_WINDOW_RESIZABLE)
        self._sdlrenderer = sdl2.SDL_CreateRenderer(self._window, -1, sdl2.SDL_RENDERER_ACCELERATED)

        self._sdlTextureBuffer = sdl2.SDL_CreateTexture(self._sdlrenderer, sdl2.SDL_PIXELFORMAT_RGBA32, sdl2.SDL_TEXTUREACCESS_STATIC, gameboyResolution[0], gameboyResolution[1])

        self.blankScreen()
        sdl2.SDL_ShowWindow(self._window)

    def dump(self,filename):
        pass

    def setTitle(self, title):
        sdl2.SDL_SetWindowTitle(self._window, title.encode())

    def getEvents(self):
        events = []

        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                events.append(WindowEvent.Quit)
            elif event.type == sdl2.SDL_KEYDOWN:
                events.append(self.windowEventsDown.get(event.key.keysym.sym, WindowEvent.Pass))
            elif event.type == sdl2.SDL_KEYUP:
                events.append(self.windowEventsUp.get(event.key.keysym.sym, WindowEvent.Pass))

        return events

    def updateDisplay(self):
        self._updateDisplay()

    def framelimiter(self, speed):
        now = sdl2.SDL_GetTicks()
        delay = int(1/(60.0 * speed)*1000-(now-self.ticks))
        if delay < 0: # Cython doesn't suppport max()
            delay = 0
        sdl2.SDL_Delay(delay)
        self.ticks = sdl2.SDL_GetTicks()

    def stop(self):
        sdl2.SDL_DestroyWindow(self._window)
        sdl2.SDL_Quit()

    def scanline(self, y, lcd): # Just recording states of LCD registers
        viewPos = lcd.getViewPort()
        windowPos = lcd.getWindowPos()
        self.scanlineParameters[y][0] = viewPos[0]
        self.scanlineParameters[y][1] = viewPos[1]
        self.scanlineParameters[y][2] = windowPos[0]
        self.scanlineParameters[y][3] = windowPos[1]

    def renderScreen(self, lcd):
        # All VRAM addresses are offset by 0x8000
        # Following addresses are 0x9800 and 0x9C00
        backgroundViewAddress = 0x1800 if lcd.LCDC.backgroundMapSelect == 0 else 0x1C00
        windowViewAddress = 0x1800 if lcd.LCDC.windowMapSelect == 0 else 0x1C00

        for y in range(gameboyResolution[1]):
            bx, by, wx, wy = self.scanlineParameters[y]
            offset = bx & 0b111 # Used for the half tile at the left side when scrolling

            for x in range(gameboyResolution[0]):
                if lcd.LCDC.windowEnabled and wy <= y and wx <= x:
                    windowTileIndex = lcd.VRAM[windowViewAddress + (((x-wx)//8)%32 + ((y-wy)//8)*32)%0x400]

                    if lcd.LCDC.tileSelect == 0: # If using signed tile indices
                        # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset (reduces to + 128)
                        windowTileIndex = (windowTileIndex ^ 0x80) + 128

                    self.screenBuffer[y, x] = self.tileCache[8*windowTileIndex + (y-wy)%8, (x-wx)%8]

                elif lcd.LCDC.backgroundEnable:
                    backgroundTileIndex = lcd.VRAM[backgroundViewAddress + (((bx + x)//8)%32 + ((y+by)//8)*32)%0x400]

                    if lcd.LCDC.tileSelect == 0: # If using signed tile indices
                        # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset (reduces to + 128)
                        backgroundTileIndex = (backgroundTileIndex ^ 0x80) + 128

                    self.screenBuffer[y, x] = self.tileCache[8*backgroundTileIndex + (y+by)%8, (x+offset)%8]
                else:
                    # If background is disabled, it becomes white
                    self.screenBuffer[y, x] = self.colorPalette[0]

        ### RENDER SPRITES
        # Doesn't restrict 10 sprite pr. scan line.
        # Prioritizes sprite in inverted order
        spriteSize = 16 if lcd.LCDC.spriteSize else 8
        BGPkey = lcd.BGP.getColor(0)

        for n in range(0x00,0xA0,4):
            y = lcd.OAM[n] - 16
            x = lcd.OAM[n+1] - 8
            tileIndex = lcd.OAM[n+2]
            attributes = lcd.OAM[n+3]
            xFlip = attributes & 0b100000
            yFlip = attributes & 0b1000000
            spritePriority = attributes & 0b10000000

            spriteCache = self.spriteCacheOBP1 if attributes & 0b10000 else self.spriteCacheOBP0

            if x < 160 and y < 144:
                for yy in reversed(range(spriteSize)) if yFlip else range(spriteSize):
                    if 0 <= y < 144:
                        for xx in reversed(range(8)) if xFlip else range(8):
                            pixel = spriteCache[8*tileIndex+yy, xx]

                            if 0 <= x < 160:
                                if (spritePriority and not self.screenBuffer[y, x] == BGPkey):
                                    # Add a fake alphachannel to the sprite for BG pixels. We can't just merge
                                    # this with the next if, as sprites can have an alpha channel in other ways
                                    pixel |= self.alphaMask

                                if not (pixel & self.alphaMask):
                                    self.screenBuffer[y, x] = pixel
                            x += 1
                        x -= 8
                    y += 1

        # Copy happens in Window_SDL2.pxd

    def updateCache(self, lcd):
        if self.clearCache:
            self.tiles_changed.clear()
            for x in range(0x8000,0x9800,16):
                self.tiles_changed.add(x)
            self.clearCache = False

        for t in self.tiles_changed:
            for k in range(0, 16 ,2):  # 2 bytes for each line
                byte1 = lcd.VRAM[t + k - 0x8000]
                byte2 = lcd.VRAM[t + k + 1 - 0x8000]

                for pixelOnLine in range(7,-1,-1):
                    y = (t + k - 0x8000)//2
                    x = 7-pixelOnLine

                    colorCode = getColorCode(byte1, byte2, pixelOnLine)

                    self.tileCache[y, x] = lcd.BGP.getColor(colorCode)
                    # TODO: Find a more optimal way to do this
                    alpha = 0x00000000
                    if colorCode == 0:
                        alpha = self.alphaMask  # Add alpha channel
                    self.spriteCacheOBP0[y, x] = lcd.OBP0.getColor(colorCode) + alpha
                    self.spriteCacheOBP1[y, x] = lcd.OBP1.getColor(colorCode) + alpha

        self.tiles_changed.clear()

    def blankScreen(self):
        # If the screen is off, fill it with a color.
        color = self.colorPalette[0]
        for y in range(144):
            for x in range(160):
                self.screenBuffer[y, x] = color
        # self._sdlrenderer.clear(0)

    def getScreenBuffer(self):
        return self._screenBuffer
