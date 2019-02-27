# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# Author: Kristian Sims
# License: See LICENSE file
# GitHub: https://github.com/krs013/PyBoy
#


import ctypes
import sdl2.ext.colorpalettes  # Implicitly imports sdl2 and sdl2.ext

from .. import CoreDump
from ..MathUint8 import getSignedInt8
from ..WindowEvent import WindowEvent
from ..LCD import color_palette
from .FrameBuffer import SimpleFrameBuffer, ScaledFrameBuffer
from ..GameWindow import AbstractGameWindow

from ..Logger import logger


class ScalableGameWindow(AbstractGameWindow):

    gameboyResolution = (160, 144)

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

    # range is better for Python3 compatibility than xrange, but in
    # Python2, range produces a list instead of a generator, so it's
    # best to just pregenerate and reuse it won't change anyway
    xs = range(gameboyResolution[0])

    # In the end, we're just converting back to 32 bits anyway...
    palette = list(map(long, reversed(sdl2.ext.colorpalettes.GRAY2PALETTE)))

    def __init__(self, scale=1):
        super(self.__class__, self).__init__(scale)

        CoreDump.windowHandle = self

        logger.debug("SDL Scalable Window initialization")

        sdl2.ext.init()

        start_size = tuple(map(lambda x: scale * x, self.gameboyResolution))
        self._window = sdl2.ext.Window("PyBoy", size=start_size,
                                       flags=sdl2.SDL_WINDOW_RESIZABLE)

        self._renderer = sdl2.ext.Renderer(self._window, -1,
                                           self.gameboyResolution)
        self._sdlrenderer = self._renderer.sdlrenderer
        self._screenbuf = sdl2.SDL_CreateTexture(self._sdlrenderer,
                                                 sdl2.SDL_PIXELFORMAT_ARGB32,
                                                 sdl2.SDL_TEXTUREACCESS_STATIC,
                                                 *self.gameboyResolution)
        self._linebuf = [0] * self.gameboyResolution[0]
        self._linerect = sdl2.rect.SDL_Rect(0, 0, self.gameboyResolution[0], 1)

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
        # window.refresh is only needed for direct pixel surface access
        pass

    def VSync(self):
        # Not really sure what this is supposed to do, but the frame
        # limiter isn't implemented anyway yet, so I'll leave this alone
        pass

    def stop(self):
        sdl2.SDL_DestroyWindow(self._window.window)
        sdl2.ext.quit()
    
    def scanline(self, y, lcd):
        # Instead of recording and rendering at vblank, I'm going to try
        # writing to the double buffer with the Renderer in real time as
        # the GB actually does, and then swap at the call to renderScreen

        # Background and Window View Address (offset into VRAM...)
        bOffset = 0x1C00 if lcd.LCDC.background_map_select else 0x1800 
        wOffset = 0x1C00 if lcd.LCDC.window_map_select else 0x1800

        bx, by = lcd.get_view_port()
        wx, wy = lcd.get_window_pos()

        # Single line, so we can save some math with the tile indices
        bOffset += (((y + by) / 8 ) * 32) % 0x400
        wOffset += ((y - wy) / 8 ) * 32

        # Class access costs, so do some quick caching
        tile_select = lcd.LCDC.tile_select == 0
        window_enabled_and_y = lcd.LCDC.window_enabled and wy <= y
        bgp = [self.palette[lcd.BGP.get_code(x)] for x in range(4)]

        for x in self.xs:

            # Window gets priority, otherwise it's the background
            # TODO: This is done almost 8x as much as needed
            if window_enabled_and_y and wx <= x:
                tile = lcd.VRAM[wOffset + (((x - wx) / 8) % 32)]
                dx = (x - wx) % 8
                dy = (y - wy) % 8
            elif lcd.LCDC.background_enable:
                tile = lcd.VRAM[bOffset + (((x + bx) / 8) % 32)]
                dx = (x + bx) % 8
                dy = (y + by) % 8
            else:  # White if blank
                self._linebuf[x] = self.palette[0]
                continue

            # If using the second Tile Data Table, convert to signed
            # by adding 128, masking, and subtracting 128, then add an
            # offset of 256 (the subtract and add become +128)
            if tile_select:
                tile = ((tile + 128) & 0xFF) + 128

            # Get the color from the Tile Data Table... bit by bit
            # TODO: This is horribly inefficient
            bit0 = lcd.VRAM[(tile << 4) + (dy << 1)] & (0x80 >> dx)
            bit1 = lcd.VRAM[(tile << 4) + (dy << 1) + 1] & (0x80 >> dx)

            # Draw the pixel to the frame buffer
            # self._renderer.draw_point((x, y), bgp[((bit1<<1)+bit0)>>(7-dx)])
            self._linebuf[x] = bgp[((bit1<<1)+bit0)>>(7-dx)]

        # Copy into the screen buffer from the list
        self._linerect.y = y
        buf, _ = sdl2.ext.array.to_ctypes(self._linebuf, ctypes.c_uint32,
                                          self.gameboyResolution[0])
        sdl2.SDL_UpdateTexture(self._screenbuf, self._linerect,
                               ctypes.byref(buf), self.gameboyResolution[0])

    def renderScreen(self, lcd):
        # Copy from internal buffer to screen
        sdl2.render.SDL_RenderCopy(self._sdlrenderer, self._screenbuf, None, None)
        self._renderer.present()

    def blankScreen(self):
        # Make the screen white
        self._renderer.clear(self.palette[0])
        self._renderer.present()

    def getScreenBuffer(self):
        # I think that calling get_surface() on the window breaks the
        # Renderer, so except for core dump, I'm not going to use it.
        # Not sure how to handle screen recording in this case.
        raise NotImplementedError()
