# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/krs013/PyBoy
#


try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False

if not cythonmode:
    import ctypes

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
        if not cythonmode:
            self._linerect = sdl2.SDL_Rect(0, 0, gameboyResolution[0], 1)
            self._linebuf_p = ctypes.c_void_p(self._linebuf.buffer_info()[0])

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
        bOffset += (((y + by) >> 3) << 5) % 0x400
        wOffset += ((y - wy) >> 3) << 5

        # Dict lookups cost, so do some quick caching
        tile_select = lcd.LCDC.tileSelect == 0
        window_enabled_and_y = lcd.LCDC.windowEnabled and wy <= y

        # Set to an impossible value to signal first loop. This could
        # break if we switch to an actual signed offset from a
        # pointer, so be careful.
        bt = -1
        wt = -1

        # Limit to 10 sprites per line, could optionally disable later
        sprites = [0] * 10
        ymin = y if lcd.LCDC.spriteSize else y + 8
        ymax = y + 16
        nsprites = 0
        for n in range(0x00, 0xA0, 4):
            if ymin < lcd.OAM[n] <= ymax:
                sprites[nsprites] = n
                nsprites += 1
                if nsprites == 10:
                    break
        # I took out the sorting part, so sprites are now rendered in
        # GBC order instead. It may be worth adding an option to sort
        # them in noncolor mode later, but for any normal game it
        # shouldn't matter.

        # As in hardware, compute each pixel one-by-one
        for x in range(gameboyResolution[0]):

            # Window gets priority, otherwise it's the background
            if window_enabled_and_y and wx <= x:
                dx = (x - wx) % 8
                if dx == 0 or bt < 0:
                    bt = lcd.VRAM[wOffset + ((x - wx) >> 3)]

                    # Convert to signed and offset (-128+256=+128)
                    if tile_select:
                        bt = (bt ^ 0x80) + 128

                    # Get the color from the Tile Data Table
                    bbyte0 = lcd.VRAM[16 * bt + 2 * wdy]
                    bbyte1 = lcd.VRAM[16 * bt + 2 * wdy + 1]

                bpixel = 2 * (bbyte1 & 0x80 >> dx) + (bbyte0 & 0x80 >> dx)
                bpixel >>= 7 - dx

            elif lcd.LCDC.backgroundEnable:
                dx = (x + bx) % 8
                if dx == 0 or wt < 0:
                    wt = lcd.VRAM[bOffset + (((x + bx) >> 3) % 32)]

                    # Convert to signed and offset (-128+256=+128)
                    if tile_select:
                        wt = (wt ^ 0x80) + 128

                    # Get the color from the Tile Data Table
                    bbyte0 = lcd.VRAM[16 * wt + 2 * bdy]
                    bbyte1 = lcd.VRAM[16 * wt + 2 * bdy + 1]

                bpixel = 2 * (bbyte1 & 0x80 >> dx) + (bbyte0 & 0x80 >> dx)
                bpixel >>= 7 - dx

            else:  # White if blank
                bpixel = 0

            # Iterate through the sprites and look for the first match
            for n in sprites[:nsprites]:
                sx = lcd.OAM[n+1]

                # Check for sprite collision
                if sx - 8 <= x < sx:
                    sy = lcd.OAM[n]
                    st = lcd.OAM[n+2]
                    sf = lcd.OAM[n+3]

                    # Get the row of the sprite, accounting for flipping
                    dy = sy - y - 1 if sf & 0x40 else y - sy + 16

                    if lcd.LCDC.spriteSize:
                        # Double sprites start on an even index
                        st &= 0xFE
                    else:
                        # Single sprites have y index from 0-7
                        dy &= 0x07

                    sbyte0 = lcd.VRAM[16 * st + 2 * dy]
                    sbyte1 = lcd.VRAM[16 * st + 2 * dy + 1]

                    dx = sx - x - 1 if sf & 0x20 else x - sx + 8
                    spixel = 2 * (sbyte1 & 0x80 >> dx) + (sbyte0 & 0x80 >> dx)
                    spixel >>= 7 - dx

                    # If the sprite is transparent, check for more
                    if spixel == 0:
                        continue

                    # Draw the highest priority sprite pixel
                    if not sf & 0x80 or bpixel == 0:
                        if sf & 0x10:
                            self._linebuf[x] = lcd.OBP1.getColor(spixel)
                        else:
                            self._linebuf[x] = lcd.OBP0.getColor(spixel)
                    else:
                        self._linebuf[x] = lcd.BGP.getColor(bpixel)

                    break
            else:
                self._linebuf[x] = lcd.BGP.getColor(bpixel)

        # Copy into the screen buffer stored in a Texture
        self._linerect.y = y
        self._scanlineCopy()

    def renderScreen(self, lcd):
        self._renderCopy()

    def updateDisplay(self):
        self._renderPresent()

    def blankScreen(self):
        sdl2.SDL_SetRenderDrawColor(self._sdlrenderer, 0xff, 0xff, 0xff, 0xff)
        sdl2.SDL_RenderClear(self._sdlrenderer)

    def getScreenBuffer(self):
        raise NotImplementedError()


# Unfortunately CPython/PyPy code has to be hidden in an exec call to
# prevent Cython from trying to parse it. This block provides the
# functions that are otherwise implemented as inlined cdefs in the pxd
if not cythonmode:
    exec("""
def _scanlineCopy(self):
    sdl2.SDL_UpdateTexture(self._screenbuf, self._linerect,
                           self._linebuf_p, gameboyResolution[0])

def _renderCopy(self):
    sdl2.SDL_RenderCopy(self._sdlrenderer, self._screenbuf, None, None)

def _renderPresent(self):
    sdl2.SDL_RenderPresent(self._sdlrenderer)

ScanlineWindow._scanlineCopy = _scanlineCopy
ScanlineWindow._renderCopy = _renderCopy
ScanlineWindow._renderPresent = _renderPresent
""", globals(), locals())
