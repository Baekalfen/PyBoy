#
# License: See LICENSE file
# GitHub: https://github.com/krs013/PyBoy
#

import array

import sdl2.ext

from pyboy import windowevent
from pyboy.window.base_window import BaseWindow

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False

if not cythonmode:
    import ctypes


ROWS, COLS = 144, 160
KEY_DOWN = {
    sdl2.SDLK_UP        : windowevent.PRESS_ARROW_UP,
    sdl2.SDLK_DOWN      : windowevent.PRESS_ARROW_DOWN,
    sdl2.SDLK_RIGHT     : windowevent.PRESS_ARROW_RIGHT,
    sdl2.SDLK_LEFT      : windowevent.PRESS_ARROW_LEFT,
    sdl2.SDLK_a         : windowevent.PRESS_BUTTON_A,
    sdl2.SDLK_s         : windowevent.PRESS_BUTTON_B,
    sdl2.SDLK_RETURN    : windowevent.PRESS_BUTTON_START,
    sdl2.SDLK_BACKSPACE : windowevent.PRESS_BUTTON_SELECT,
    sdl2.SDLK_ESCAPE    : windowevent.QUIT,
    sdl2.SDLK_d         : windowevent.DEBUG_TOGGLE,
    sdl2.SDLK_SPACE     : windowevent.PRESS_SPEED_UP,
    sdl2.SDLK_i         : windowevent.SCREEN_RECORDING_TOGGLE,
}
KEY_UP = {
    sdl2.SDLK_UP        : windowevent.RELEASE_ARROW_UP,
    sdl2.SDLK_DOWN      : windowevent.RELEASE_ARROW_DOWN,
    sdl2.SDLK_RIGHT     : windowevent.RELEASE_ARROW_RIGHT,
    sdl2.SDLK_LEFT      : windowevent.RELEASE_ARROW_LEFT,
    sdl2.SDLK_a         : windowevent.RELEASE_BUTTON_A,
    sdl2.SDLK_s         : windowevent.RELEASE_BUTTON_B,
    sdl2.SDLK_RETURN    : windowevent.RELEASE_BUTTON_START,
    sdl2.SDLK_BACKSPACE : windowevent.RELEASE_BUTTON_SELECT,
    sdl2.SDLK_z         : windowevent.SAVE_STATE,
    sdl2.SDLK_x         : windowevent.LOAD_STATE,
    sdl2.SDLK_SPACE     : windowevent.RELEASE_SPEED_UP,
}


class ScanlineWindow(BaseWindow):

    def __init__(self, scale=1):
        BaseWindow.__init__(self, scale)

        self._linebuf = array.array('I', [0] * COLS)
        self._linerect = {'x': 0, 'y': 0, 'w': COLS, 'h': 1}
        if not cythonmode:
            self._linerect = sdl2.SDL_Rect(0, 0, COLS, 1)
            self._linebuf_p = ctypes.c_void_p(self._linebuf.buffer_info()[0])

    def init(self):
        sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING)
        self._ticks = sdl2.SDL_GetTicks()

        self._window = sdl2.SDL_CreateWindow(
            b"PyBoy",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            self._scaledresolution[0],
            self._scaledresolution[1],
            sdl2.SDL_WINDOW_RESIZABLE)

        self._sdlrenderer = sdl2.SDL_CreateRenderer(
            self._window, -1, sdl2.SDL_RENDERER_ACCELERATED)

        self._screenbuf = sdl2.SDL_CreateTexture(
            self._sdlrenderer, sdl2.SDL_PIXELFORMAT_BGRA32,
            sdl2.SDL_TEXTUREACCESS_STREAMING, COLS, ROWS)

        self.blank_screen()
        sdl2.SDL_ShowWindow(self._window)

    def dump(self, filename):
        raise NotImplementedError()

    def set_title(self, title):
        sdl2.SDL_SetWindowTitle(self._window, title.encode())

    def get_events(self):
        events = []
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                events.append(windowevent.QUIT)
            elif event.type == sdl2.SDL_KEYDOWN:
                events.append(KEY_DOWN.get(event.key.keysym.sym, windowevent.PASS))
            elif event.type == sdl2.SDL_KEYUP:
                events.append(KEY_UP.get(event.key.keysym.sym, windowevent.PASS))
        return events

    def frame_limiter(self, speed):
        now = sdl2.SDL_GetTicks()
        delay = int(1000.0 / (60.0 * speed) - (now - self._ticks))
        sdl2.SDL_Delay(delay if delay > 0 else 0)
        self._ticks = sdl2.SDL_GetTicks()

    def stop(self):
        sdl2.SDL_DestroyWindow(self._window)
        sdl2.SDL_Quit()

    def scanline(self, y, lcd):
        # Instead of recording parameters and rendering at vblank, we
        # write to the double buffer with the Renderer in real time as
        # the GB actually does, and then swap buffers at the call to
        # renderScreen

        # Background and Window View Address (offset into VRAM...)
        bmap = 0x1C00 if lcd.LCDC.backgroundmap_select else 0x1800
        wmap = 0x1C00 if lcd.LCDC.windowmap_select else 0x1800

        bx, by = lcd.get_viewport()
        wx, wy = lcd.get_windowpos()

        bd = (y + by) % 8
        wd = (y - wy) % 8

        # Single line, so we can save some math with the tile indices
        bmap += (((y + by) >> 3) << 5) % 0x400
        wmap += ((y - wy) >> 3) << 5

        # Dict lookups cost, so do some quick caching
        tile_select = lcd.LCDC.tiledata_select == 0
        window_enabled_and_y = lcd.LCDC.window_enable and wy <= y

        # Set to an impossible value to signal first loop. This could
        # break if we switch to an actual signed offset from a
        # pointer, so be careful.
        bt = -1
        wt = -1

        # Limit to 10 sprites per line, could optionally disable later
        sprites = [0] * 10
        nsprites = 0
        ymin = y if lcd.LCDC.sprite_height else y + 8
        ymax = y + 16
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
        for x in range(COLS):
            # Window gets priority, otherwise it's the background
            if window_enabled_and_y and wx <= x:
                dx = (x - wx) % 8
                if dx == 0 or bt < 0:
                    bt = lcd.VRAM[wmap + ((x-wx) >> 3)]
                    # Convert to signed and offset (-128+256=+128)
                    if tile_select:
                        bt = (bt ^ 0x80) + 128

                    # Get the color from the Tile Data Table
                    bbyte0 = lcd.VRAM[16*bt + 2*wd]
                    bbyte1 = lcd.VRAM[16*bt + 2*wd + 1]

                bpixel = 2*(bbyte1 & 0x80 >> dx) + (bbyte0 & 0x80 >> dx)
                bpixel >>= 7 - dx

            elif lcd.LCDC.background_enable:
                dx = (x + bx) % 8
                if dx == 0 or wt < 0:
                    wt = lcd.VRAM[bmap + (((x + bx) >> 3) % 32)]

                    # Convert to signed and offset (-128+256=+128)
                    if tile_select:
                        wt = (wt ^ 0x80) + 128

                    # Get the color from the Tile Data Table
                    bbyte0 = lcd.VRAM[16*wt + 2*bd]
                    bbyte1 = lcd.VRAM[16*wt + 2*bd + 1]

                bpixel = 2*(bbyte1 & 0x80 >> dx) + (bbyte0 & 0x80 >> dx)
                bpixel >>= 7 - dx

            else: # White if blank
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

                    if lcd.LCDC.sprite_height:
                        # Double sprites start on an even index
                        st &= 0xFE
                    else:
                        # Single sprites have y index from 0-7
                        dy &= 0x07

                    sbyte0 = lcd.VRAM[16 * st + 2 * dy]
                    sbyte1 = lcd.VRAM[16 * st + 2 * dy + 1]

                    dx = sx-x-1 if sf & 0x20 else x-sx+8
                    spixel = 2*(sbyte1 & 0x80 >> dx) + (sbyte0 & 0x80 >> dx)
                    spixel >>= 7 - dx

                    # If the sprite is transparent, check for more
                    if spixel == 0:
                        continue

                    # Draw the highest priority sprite pixel
                    if not sf & 0x80 or bpixel == 0:
                        if sf & 0x10:
                            self._linebuf[x] = lcd.OBP1.get_color(spixel)
                        else:
                            self._linebuf[x] = lcd.OBP0.get_color(spixel)
                    else:
                        self._linebuf[x] = lcd.BGP.get_color(bpixel)

                    break
            else:
                self._linebuf[x] = lcd.BGP.get_color(bpixel)

        # Copy into the screen buffer stored in a Texture
        self._linerect.y = y
        self._scanline_copy()

    def render_screen(self, lcd):
        self._render_copy()

    def update_display(self, paused):
        self._render_present()

    def blank_screen(self):
        sdl2.SDL_SetRenderDrawColor(self._sdlrenderer, 0xff, 0xff, 0xff, 0xff)
        sdl2.SDL_RenderClear(self._sdlrenderer)

    def getscreenbuffer(self):
        raise NotImplementedError()


# Unfortunately CPython/PyPy code has to be hidden in an exec call to
# prevent Cython from trying to parse it. This block provides the
# functions that are otherwise implemented as inlined cdefs in the pxd
if not cythonmode:
    exec("""
def _scanline_copy(self):
    sdl2.SDL_UpdateTexture(self._screenbuf, self._linerect,
                           self._linebuf_p, COLS)

def _render_copy(self):
    sdl2.SDL_RenderCopy(self._sdlrenderer, self._screenbuf, None, None)

def _render_present(self):
    sdl2.SDL_RenderPresent(self._sdlrenderer)

ScanlineWindow._scanline_copy = _scanline_copy
ScanlineWindow._render_copy = _render_copy
ScanlineWindow._render_present = _render_present
""", globals(), locals())
