# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/krs013/PyBoy
#

import array
import sdl2.ext

from PyBoy import WindowEvent
from PyBoy.Window.GenericWindow import GenericWindow


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


class ScanlineWindow(GenericWindow):

    def __init__(self, scale=1):
        GenericWindow.__init__(self, scale)

        self._linebuf = array.array('I', [0] * gameboyResolution[0])
        self._linerect = {'x': 0, 'y': 0, 'w': gameboyResolution[0], 'h': 1}

    def init(self):
        sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING)
        self.ticks = sdl2.SDL_GetTicks()

        self._window = sdl2.SDL_CreateWindow(
            b"PyBoy",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            self._scaledResolution[0],
            self._scaledResolution[1],
            sdl2.SDL_WINDOW_RESIZABLE)

        self._sdlrenderer = sdl2.SDL_CreateRenderer(
            self._window, -1, sdl2.SDL_RENDERER_ACCELERATED)

        self._screenbuf = sdl2.SDL_CreateTexture(
            self._sdlrenderer,
            sdl2.SDL_PIXELFORMAT_BGRA32,
            sdl2.SDL_TEXTUREACCESS_STREAMING,
            gameboyResolution[0], gameboyResolution[1])

        self.blankScreen()
        sdl2.SDL_ShowWindow(self._window)

    def dump(self, filename):
        raise NotImplementedError()

    def setTitle(self, title):
        sdl2.SDL_SetWindowTitle(self._window, title.encode())

    def getEvents(self):
        events = []

        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                events.append(WindowEvent.Quit)
            elif event.type == sdl2.SDL_KEYDOWN:
                events.append(windowEventsDown.get(event.key.keysym.sym, None))
            elif event.type == sdl2.SDL_KEYUP:
                events.append(windowEventsUp.get(event.key.keysym.sym, None))

        return events

    def updateDisplay(self):
        self._renderPresent()

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

    def scanline(self, y, lcd):
        # Instead of recording parameters and rendering at vblank, we
        # write to the double buffer with the Renderer in real time as
        # the GB actually does, and then swap buffers at the call to
        # renderScreen

        # Background and Window View Address (offset into VRAM...)
        bOffset = 0x1C00 if lcd.LCDC.backgroundMapSelect else 0x1800
        wOffset = 0x1C00 if lcd.LCDC.windowMapSelect else 0x1800

        bx, by = lcd.getViewPort()
        wx, wy = lcd.getWindowPos()

        bdy = (y + by) % 8
        wdy = (y - wy) % 8

        # Single line, so we can save some math with the tile indices
        bOffset += (((y + by) / 8 ) * 32) % 0x400
        wOffset += ((y - wy) / 8 ) * 32

        # Dict lookups cost, so do some quick caching
        tile_select = lcd.LCDC.tileSelect == 0
        window_enabled_and_y = lcd.LCDC.windowEnabled and wy <= y

        # Set to an impossible value to signal first loop. This could
        # break if we switch to an actual signed offset from a
        # pointer, so be careful.
        tile = -1

        for x in range(gameboyResolution[0]):

            # Window gets priority, otherwise it's the background
            if window_enabled_and_y and wx <= x:
                dx = (x - wx) % 8
                if dx == 0 or tile < 0:
                    tile = lcd.VRAM[wOffset + (((x - wx) / 8) % 32)]

                    # Convert to signed and offset (-128+256=+128)
                    if tile_select:
                        tile = (tile ^ 0x80) + 128

                    # Get the color from the Tile Data Table
                    byte0 = lcd.VRAM[16 * tile + 2 * wdy]
                    byte1 = lcd.VRAM[16 * tile + 2 * wdy + 1]

            elif lcd.LCDC.backgroundEnable:
                dx = (x + bx) % 8
                if dx == 0 or tile < 0:
                    tile = lcd.VRAM[bOffset + (((x + bx) / 8) % 32)]

                    # Convert to signed and offset (-128+256=+128)
                    if tile_select:
                        tile = (tile ^ 0x80) + 128

                    # Get the color from the Tile Data Table
                    byte0 = lcd.VRAM[16 * tile + 2 * bdy]
                    byte1 = lcd.VRAM[16 * tile + 2 * bdy + 1]

            else:  # White if blank
                self._linebuf[x] = self.colorPalette[0]
                continue

            pixel = 2 * (byte1 & 0x80 >> dx) + (byte0 & 0x80 >> dx)
            self._linebuf[x] = lcd.BGP.getColor(pixel >> 7-dx)

        # Limit to 10 sprites per line, could optionally disable later
        nsprites = 10

        # I took out the sorting part, so sprites are now rendered in
        # GBC order instead. It may be worth adding an option to sort
        # them in noncolor mode later, but for any normal game it
        # shouldn't matter.

        # Iterate through the sprites and update the buffer
        for n in range(0x00, 0xA0, 4):
            sy = lcd.OAM[n]
            sx = lcd.OAM[n+1]
            tile = lcd.OAM[n+2]
            sf = lcd.OAM[n+3]

            # Get the row of the sprite, accounting for flipping
            dy = sy - y - 1 if sf & 0x40 else y - sy + 16

            if lcd.LCDC.spriteSize:
                # Check if this is our line
                if sy - 16 <= y < sy and 0 < sx < 168:
                    nsprites -= 1
                    if nsprites == 0:
                        break
                else:
                    continue

                # Double sprites start on an even index
                tile &= 0xFE
            else:
                # Check if this is our line
                if sy - 16 <= y < sy - 8 and 0 < sx < 168:
                    nsprites -= 1
                    if nsprites == 0:
                        break
                else:
                    continue

                # Single sprites have y index from 0-7
                dy &= 0x07

            byte0 = lcd.VRAM[16 * tile + 2 * dy]
            byte1 = lcd.VRAM[16 * tile + 2 * dy + 1]

            for dx in range(8):
                x = sx - dx if sf & 0x20 else sx - 8 + dx
                pixel = 2 * (byte1 & 0x80 >> dx) + (byte0 & 0x80 >> dx)

                if 0 <= x < gameboyResolution[0]:
                    if pixel and (not sf & 0x80 or
                                  self._linebuf[x] == lcd.BGP.getColor(0)):
                        if sf & 0x10:
                            self._linebuf[x] = lcd.OBP1.getColor(pixel >> 7-dx)
                        else:
                            self._linebuf[x] = lcd.OBP0.getColor(pixel >> 7-dx)

        # Copy into the screen buffer from the list
        self._linerect.y = y

        self._scanlineCopy()
        # sdl2.SDL_UpdateTexture(self._screenbuf, self._linerect,
        #                        self._linebuf_p, gameboyResolution[0])

    def renderScreen(self, lcd):
        # Copy from internal buffer to screen
        # sdl2.render.SDL_RenderCopy(self._sdlrenderer, self._screenbuf, None, None)
        self._renderCopy()

    def blankScreen(self):
        # Make the screen white
        sdl2.SDL_SetRenderDrawColor(self._sdlrenderer, 0xff, 0xff, 0xff, 0xff)
        sdl2.SDL_RenderClear(self._sdlrenderer)

    def getScreenBuffer(self):
        # I think that calling get_surface() on the window breaks the
        # Renderer, so except for core dump, I'm not going to use it.
        # Not sure how to handle screen recording in this case.
        raise NotImplementedError()
