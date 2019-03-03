# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# Author: Kristian Sims
# License: See LICENSE file
# GitHub: https://github.com/krs013/PyBoy
#
# Cacheless GameWindow that renders screen line-by-line in scanline()
# It's closer to the hardware and maybe easier to understand, but not
# fast enough to replace GameWindow_SDL2

import ctypes
import sdl2
import sdl2.ext
import sdl2.ext.colorpalettes

from .. import CoreDump
from ..WindowEvent import WindowEvent
from ..GameWindow import AbstractGameWindow

from ..Logger import logger

gameboyResolution = (160, 144)

# Bit conversion for tiles using a lookup table
# TODO: profile this vs just looping for the conversion
# This creates a zip and generator object, so it may be slow
lookup2bits = {b: tuple(b >> 2*s & 0x3 for s in reversed(range(4)))
               for b in range(256)}
def bytes2bits(byte0, byte1):
    bits7531 = lookup2bits[0b10101010 & byte1 | 0b01010101 & byte0 >> 1]
    bits6420 = lookup2bits[0b10101010 & byte1 << 1 | 0b01010101 & byte0]
    for odd, even in zip(bits7531, bits6420):
        yield odd
        yield even

class ScanlineGameWindow(AbstractGameWindow):

    windowEventsDown = {
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
    windowEventsUp = {
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

    palette = list(map(long, reversed(sdl2.ext.colorpalettes.GRAY2PALETTE)))

    def __init__(self, scale=1):
        super(self.__class__, self).__init__(scale)

        CoreDump.windowHandle = self

        logger.debug("Scanline Window initialization")

        sdl2.ext.init()

        start_size = tuple(map(lambda x: scale * x, gameboyResolution))
        self._window = sdl2.ext.Window("PyBoy", size=start_size,
                                       flags=sdl2.SDL_WINDOW_RESIZABLE)

        self._renderer = sdl2.ext.Renderer(self._window, -1,
                                           gameboyResolution)
        self._sdlrenderer = self._renderer.sdlrenderer
        self._screenbuf = sdl2.SDL_CreateTexture(self._sdlrenderer,
                                                 sdl2.SDL_PIXELFORMAT_ARGB32,
                                                 sdl2.SDL_TEXTUREACCESS_STATIC,
                                                 *gameboyResolution)
        self._linebuf = [0] * gameboyResolution[0]
        self._linerect = sdl2.rect.SDL_Rect(0, 0, gameboyResolution[0], 1)

        self.ticks = sdl2.SDL_GetTicks()

        self.blankScreen()
        self._window.show()

    def dump(self, filename):
        # This will probably break the renderer
        sdl2.surface.SDL2_SaveBMP(self._window.get_surface(), filename + ".bmp")

    def setTitle(self, title):
        self._window.title = title

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
        self._renderer.present()
        pass

    def frameLimiter(self):
        now = sdl2.SDL_GetTicks()
        sdl2.SDL_Delay(max(0, int(1/60.0*1000-(now-self.ticks))))
        self.ticks = sdl2.SDL_GetTicks()

    def stop(self):
        sdl2.SDL_DestroyWindow(self._window.window)
        sdl2.ext.quit()

    def scanline(self, y, lcd):
        # Instead of recording parameters and rendering at vblank, we
        # write to the double buffer with the Renderer in real time as
        # the GB actually does, and then swap buffers at the call to
        # renderScreen

        # Background and Window View Address (offset into VRAM...)
        bOffset = 0x1C00 if lcd.LCDC.background_map_select else 0x1800
        wOffset = 0x1C00 if lcd.LCDC.window_map_select else 0x1800

        bx, by = lcd.get_view_port()
        wx, wy = lcd.get_window_pos()

        bdy = (y + by) % 8
        wdy = (y - wy) % 8

        # Single line, so we can save some math with the tile indices
        bOffset += (((y + by) / 8 ) * 32) % 0x400
        wOffset += ((y - wy) / 8 ) * 32

        # Dict lookups cost, so do some quick caching
        tile_select = lcd.LCDC.tile_select == 0
        window_enabled_and_y = lcd.LCDC.window_enabled and wy <= y
        bgp = [self.palette[lcd.BGP.get_code(x)] for x in range(4)]

        byte0 = None

        for x in range(gameboyResolution[0]):

            # Window gets priority, otherwise it's the background
            if window_enabled_and_y and wx <= x:
                dx = (x - wx) % 8
                if dx == 0 or byte0 is None:
                    tile = lcd.VRAM[wOffset + (((x - wx) / 8) % 32)]

                    # Convert to signed (-128+256=+128)
                    if tile_select:
                        tile = ((tile + 128) & 0xFF) + 128

                    # Get the color from the Tile Data Table
                    byte0 = lcd.VRAM[16 * tile + 2 * wdy]
                    byte1 = lcd.VRAM[16 * tile + 2 * wdy + 1]

            elif lcd.LCDC.background_enable:
                dx = (x + bx) % 8
                if dx == 0 or byte0 is None:
                    tile = lcd.VRAM[bOffset + (((x + bx) / 8) % 32)]

                    # Convert to signed (-128+256=+128)
                    if tile_select:
                        tile = ((tile + 128) & 0xFF) + 128

                    # Get the color from the Tile Data Table
                    byte0 = lcd.VRAM[16 * tile + 2 * bdy]
                    byte1 = lcd.VRAM[16 * tile + 2 * bdy + 1]

            else:  # White if blank
                self._linebuf[x] = self.palette[0]
                continue

            pixel = 2 * (byte1 & 0x80 >> dx) + (byte0 & 0x80 >> dx)
            self._linebuf[x] = bgp[pixel >> 7-dx]

        # Get the sprites for this line (probably pretty slow?)
        # This finds all the sprites on the line, then sorts them by x
        # list.sort() is stable, so order will be correct
        # (Although in GBC this is different, it's by memory only)
        spritesAddresses = range(0x00, 0xA0, 4)
        if lcd.LCDC.sprite_size:
            sprites = sorted(filter(
                lambda n: lcd.OAM[n]-16 <= y < lcd.OAM[n], spritesAddresses),
                             key=lambda n: lcd.OAM[n+1])[:10]
        else:
            sprites = sorted(filter(
                lambda n: lcd.OAM[n]-16 <= y < lcd.OAM[n]-8, spritesAddresses),
                             key=lambda n: lcd.OAM[n+1])[:10]

        # Iterate through the sprites and update the buffer
        for n in sprites:
            sy, sx, tile, sf = lcd.OAM[n:n+4]

            # Get the row of the sprite, accounting for flipping
            dy = sy - y - 1 if sf & 0x40 else y - sy + 16

            if lcd.LCDC.sprite_size:
                # Double sprites start on an even index
                tile &= 0xFE
            else:
                # Single sprites have y index from 0-7
                dy &= 0x07

            # Combine bytes into generator of 2-bit pixels
            pixels = bytes2bits(*lcd.VRAM[16 * tile + 2 * dy:
                                          16 * tile + 2 * dy + 2])

            # Flip if needed
            if sf & 0x20:
                pixels = reversed(tuple(pixels))

            # Get the palette
            if sf & 0x10:
                obp = [self.palette[lcd.OBP1.get_code(x)] for x in range(4)]
            else:
                obp = [self.palette[lcd.OBP0.get_code(x)] for x in range(4)]

            for x, pixel in zip(xrange(sx - 8, sx), pixels):
                if 0 <= x < gameboyResolution[0]:
                    if pixel and (not sf & 0x80 or self._linebuf[x] == bgp[0]):
                        self._linebuf[x] = obp[pixel]

        # Copy into the screen buffer from the list
        self._linerect.y = y
        buf, _ = sdl2.ext.array.to_ctypes(self._linebuf, ctypes.c_uint32,
                                          gameboyResolution[0])
        sdl2.SDL_UpdateTexture(self._screenbuf, self._linerect,
                               ctypes.byref(buf), gameboyResolution[0])

    def renderScreen(self, lcd):
        # Copy from internal buffer to screen
        sdl2.render.SDL_RenderCopy(self._sdlrenderer, self._screenbuf, None, None)

    def blankScreen(self):
        # Make the screen white
        self._renderer.clear(self.palette[0])

    def getScreenBuffer(self):
        # I think that calling get_surface() on the window breaks the
        # Renderer, so except for core dump, I'm not going to use it.
        # Not sure how to handle screen recording in this case.
        raise NotImplementedError()
