#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from array import array
from ctypes import c_void_p

import sdl2
import sdl2.ext

from .. import windowevent
from ..logger import logger
from .base_window import BaseWindow

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False

try:
    from PIL import Image
except ImportError:
    Image = None

ROWS, COLS = 144, 160
TILES = 384

# https://wiki.libsdl.org/SDL_Scancode#Related_Enumerations
KEY_DOWN = {
    sdl2.SDLK_UP        : windowevent.PRESS_ARROW_UP,
    sdl2.SDLK_DOWN      : windowevent.PRESS_ARROW_DOWN,
    sdl2.SDLK_RIGHT     : windowevent.PRESS_ARROW_RIGHT,
    sdl2.SDLK_LEFT      : windowevent.PRESS_ARROW_LEFT,
    sdl2.SDLK_a         : windowevent.PRESS_BUTTON_A,
    sdl2.SDLK_s         : windowevent.PRESS_BUTTON_B,
    sdl2.SDLK_RETURN    : windowevent.PRESS_BUTTON_START,
    sdl2.SDLK_BACKSPACE : windowevent.PRESS_BUTTON_SELECT,
    sdl2.SDLK_SPACE     : windowevent.PRESS_SPEED_UP,
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
    sdl2.SDLK_p         : windowevent.PAUSE_TOGGLE,
    sdl2.SDLK_i         : windowevent.SCREEN_RECORDING_TOGGLE,
    sdl2.SDLK_ESCAPE    : windowevent.QUIT,
    sdl2.SDLK_d         : windowevent.DEBUG_TOGGLE,
}


def getcolorcode(byte1, byte2, offset):
    """Convert 2 bytes into color code at a given offset.

    The colors are 2 bit and are found like this:

    Color of the first pixel is 0b10
    | Color of the second pixel is 0b01
    v v
    1 0 0 1 0 0 0 1 <- byte1
    0 1 1 1 1 1 0 0 <- byte2
    """
    return (((byte2 >> (offset)) & 0b1) << 1) + ((byte1 >> (offset)) & 0b1)


class SDLWindow(BaseWindow):
    def __init__(self, scale):
        BaseWindow.__init__(self, scale)

        self._screenbuffer_raw = array('B', [0] * (ROWS*COLS*4))
        self._tilecache_raw = array('B', [0] * (TILES*8*8*4))
        self._spritecache0_raw = array('B', [0] * (TILES*8*8*4))
        self._spritecache1_raw = array('B', [0] * (TILES*8*8*4))

        if cythonmode:
            self._screenbuffer = memoryview(
                self._screenbuffer_raw).cast('I', shape=(144, 160))
            self._tilecache = memoryview(
                self._tilecache_raw).cast('I', shape=(384*8, 8))
            self._spritecache0 = memoryview(
                self._spritecache0_raw).cast('I', shape=(384*8, 8))
            self._spritecache1 = memoryview(
                self._spritecache1_raw).cast('I', shape=(384*8, 8))
        else:
            v = memoryview(self._screenbuffer_raw).cast('I')
            self._screenbuffer = [v[i:i+160] for i in range(0, 160*144, 160)]
            v = memoryview(self._tilecache_raw).cast('I')
            self._tilecache = [v[i:i+8] for i in range(0, 384*8*8, 8)]
            v = memoryview(self._spritecache0_raw).cast('I')
            self._spritecache0 = [v[i:i+8] for i in range(0, 384*8*8, 8)]
            v = memoryview(self._spritecache1_raw).cast('I')
            self._spritecache1 = [v[i:i+8] for i in range(0, 384*8*8, 8)]
            self._screenbuffer_ptr = c_void_p(self._screenbuffer_raw.buffer_info()[0])

        self._scanlineparameters = [[0, 0, 0, 0] for _ in range(ROWS)]

    def init(self):
        self._ticks = sdl2.SDL_GetTicks()

        # Should be less... https://wiki.libsdl.org/SDL_Init
        sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING)

        self._window = sdl2.SDL_CreateWindow(
            b"PyBoy",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            self._scaledresolution[0],
            self._scaledresolution[1],
            sdl2.SDL_WINDOW_RESIZABLE)

        self._sdlrenderer = sdl2.SDL_CreateRenderer(
            self._window, -1, sdl2.SDL_RENDERER_ACCELERATED)

        self._sdltexturebuffer = sdl2.SDL_CreateTexture(
            self._sdlrenderer, sdl2.SDL_PIXELFORMAT_RGBA32,
            sdl2.SDL_TEXTUREACCESS_STATIC, COLS, ROWS)

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
            elif event.type == sdl2.SDL_WINDOWEVENT:
                if event.window.windowID == 1:
                    if event.window.event == sdl2.SDL_WINDOWEVENT_FOCUS_LOST:
                        events.append(windowevent.PAUSE)
                    elif event.window.event == sdl2.SDL_WINDOWEVENT_FOCUS_GAINED:
                        events.append(windowevent.UNPAUSE)

        return events

    def update_display(self, paused):
        if not paused:
            self._update_display()

    def frame_limiter(self, speed):
        now = sdl2.SDL_GetTicks()
        delay = int(1000.0/(60.0*speed) - (now-self._ticks))
        sdl2.SDL_Delay(delay if delay > 0 else 0)
        self._ticks = sdl2.SDL_GetTicks()

    def stop(self):
        sdl2.SDL_DestroyWindow(self._window)
        sdl2.SDL_Quit()

    def scanline(self, y, lcd):
        viewpos = lcd.getviewport()
        windowpos = lcd.getwindowpos()
        self._scanlineparameters[y][0] = viewpos[0]
        self._scanlineparameters[y][1] = viewpos[1]
        self._scanlineparameters[y][2] = windowpos[0]
        self._scanlineparameters[y][3] = windowpos[1]

    def render_screen(self, lcd):
        # All VRAM addresses are offset by 0x8000
        # Following addresses are 0x9800 and 0x9C00
        background_offset = 0x1800 if lcd.LCDC.backgroundmap_select == 0 else 0x1C00
        wmap = 0x1800 if lcd.LCDC.windowmap_select == 0 else 0x1C00

        for y in range(ROWS):
            bx, by, wx, wy = self._scanlineparameters[y]
            # Used for the half tile at the left side when scrolling
            offset = bx & 0b111

            for x in range(COLS):
                if lcd.LCDC.window_enable and wy <= y and wx <= x:
                    wt = lcd.VRAM[wmap + (y-wy) // 8 * 32 % 0x400 + (x-wx) // 8 % 32]
                    # If using signed tile indices, modify index
                    if not lcd.LCDC.tiledata_select:
                        # (x ^ 0x80 - 128) to convert to signed, then
                        # add 256 for offset (reduces to + 128)
                        wt = (wt ^ 0x80) + 128
                    self._screenbuffer[y][x] = self._tilecache[8*wt + (y-wy) % 8][(x-wx) % 8]
                elif lcd.LCDC.background_enable:
                    bt = lcd.VRAM[background_offset + (y+by) // 8 * 32 % 0x400 + (x+bx) // 8 % 32]
                    # If using signed tile indices, modify index
                    if not lcd.LCDC.tiledata_select:
                        # (x ^ 0x80 - 128) to convert to signed, then
                        # add 256 for offset (reduces to + 128)
                        bt = (bt ^ 0x80) + 128
                    self._screenbuffer[y][x] = self._tilecache[8*bt + (y+by) % 8][(x+offset) % 8]
                else:
                    # If background is disabled, it becomes white
                    self._screenbuffer[y][x] = self.color_palette[0]

        # Render sprites
        # - Doesn't restrict 10 sprites per scan line
        # - Prioritizes sprite in inverted order
        spriteheight = 16 if lcd.LCDC.sprite_height else 8
        bgpkey = lcd.BGP.getcolor(0)

        for n in range(0x00, 0xA0, 4):
            y = lcd.OAM[n] - 16
            x = lcd.OAM[n+1] - 8
            tileindex = lcd.OAM[n+2]
            attributes = lcd.OAM[n+3]
            xflip = attributes & 0b00100000
            yflip = attributes & 0b01000000
            spritepriority = attributes & 0b10000000
            spritecache = (self._spritecache1 if attributes & 0b10000 else self._spritecache0)

            if x < 160 and y < 144:
                for dy in range(spriteheight):
                    yy = spriteheight - dy - 1 if yflip else dy
                    if 0 <= y < 144:
                        for dx in range(8):
                            xx = 7 - dx if xflip else dx
                            pixel = spritecache[8*tileindex+yy][xx]

                            if 0 <= x < 160:
                                if (spritepriority and not self._screenbuffer[y][x] == bgpkey):
                                    # Add a fake alphachannel to the
                                    # sprite for BG pixels. We can't
                                    # just merge this with the next
                                    # if, as sprites can have an alpha
                                    # channel in other ways
                                    pixel &= ~self.alphamask

                                if pixel & self.alphamask:
                                    self._screenbuffer[y][x] = pixel
                            x += 1
                        x -= 8
                    y += 1

    def update_cache(self, lcd):
        if self.clearcache:
            self.tiles_changed.clear()
            for x in range(0x8000, 0x9800, 16):
                self.tiles_changed.add(x)
            self.clearcache = False

        for t in self.tiles_changed:
            for k in range(0, 16, 2): # 2 bytes for each line
                byte1 = lcd.VRAM[t + k - 0x8000]
                byte2 = lcd.VRAM[t + k + 1 - 0x8000]
                y = (t + k - 0x8000)//2

                for x in range(8):
                    colorcode = getcolorcode(byte1, byte2, 7-x)

                    self._tilecache[y][x] = lcd.BGP.getcolor(colorcode)
                    self._spritecache0[y][x] = lcd.OBP0.getcolor(colorcode)
                    self._spritecache1[y][x] = lcd.OBP1.getcolor(colorcode)

                    if colorcode == 0:
                        self._spritecache0[y][x] &= ~self.alphamask
                        self._spritecache1[y][x] &= ~self.alphamask

        self.tiles_changed.clear()

    def blank_screen(self):
        # If the screen is off, fill it with a color.
        color = self.color_palette[0]
        for y in range(144):
            for x in range(160):
                self._screenbuffer[y][x] = color

    def get_screen_buffer(self):
        return self._screenbuffer_raw.tobytes()

    def get_screen_buffer_as_ndarray(self):
        import numpy as np
        return np.frombuffer(self.get_screen_buffer(), dtype=np.uint8).reshape(144, 160, 4)[:, :, :-1]

    def get_screen_image(self):
        if not Image:
            logger.warning("Cannot generate screen image. Missing dependency \"Pillow\".")
            return None

        return Image.frombytes(
                self.color_format,
                self.buffer_dims,
                self.get_screen_buffer())


# Unfortunately CPython/PyPy code has to be hidden in an exec call to
# prevent Cython from trying to parse it. This block provides the
# functions that are otherwise implemented as inlined cdefs in the pxd
if not cythonmode:
    exec("""
def _update_display(self):
    sdl2.SDL_UpdateTexture(self._sdltexturebuffer, None, self._screenbuffer_ptr, COLS*4)
    sdl2.SDL_RenderCopy(self._sdlrenderer, self._sdltexturebuffer, None, None)
    sdl2.SDL_RenderPresent(self._sdlrenderer)
    sdl2.SDL_RenderClear(self._sdlrenderer)

SDLWindow._update_display = _update_display
""", globals(), locals())
