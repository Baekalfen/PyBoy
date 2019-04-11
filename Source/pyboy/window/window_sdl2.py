#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import ctypes
from array import array

import sdl2
import sdl2.ext

from .. import windowevent
from .genericwindow import GenericWindow

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False


ROWS, COLS = 144, 160
TILES = 384


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


class SDLWindow(GenericWindow):
    def __init__(self, scale=1):
        GenericWindow.__init__(self, scale)

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
            self._screenbuffer_ptr = ctypes.c_void_p(
                self._screenbuffer_raw.buffer_info()[0])

        self._scanlineparameters = [[0, 0, 0, 0] for _ in range(ROWS)]

        # TODO: Instance variables should all start out in __init__,
        # but some SDL objects are still in init()
        self._ticks = 0
        self._key_down = {}
        self._key_up = {}

    def init(self):
        self._ticks = sdl2.SDL_GetTicks()

        # https://wiki.libsdl.org/SDL_Scancode#Related_Enumerations
        self._key_down = {
            sdl2.SDLK_UP: windowevent.PressArrowUp,
            sdl2.SDLK_DOWN: windowevent.PressArrowDown,
            sdl2.SDLK_RIGHT: windowevent.PressArrowRight,
            sdl2.SDLK_LEFT: windowevent.PressArrowLeft,
            sdl2.SDLK_a: windowevent.PressButtonA,
            sdl2.SDLK_s: windowevent.PressButtonB,
            sdl2.SDLK_RETURN: windowevent.PressButtonStart,
            sdl2.SDLK_BACKSPACE: windowevent.PressButtonSelect,
            sdl2.SDLK_ESCAPE: windowevent.Quit,
            sdl2.SDLK_d: windowevent.DebugToggle,
            sdl2.SDLK_SPACE: windowevent.PressSpeedUp,
            sdl2.SDLK_i: windowevent.ScreenRecordingToggle,
        }
        self._key_up = {
            sdl2.SDLK_UP: windowevent.ReleaseArrowUp,
            sdl2.SDLK_DOWN: windowevent.ReleaseArrowDown,
            sdl2.SDLK_RIGHT: windowevent.ReleaseArrowRight,
            sdl2.SDLK_LEFT: windowevent.ReleaseArrowLeft,
            sdl2.SDLK_a: windowevent.ReleaseButtonA,
            sdl2.SDLK_s: windowevent.ReleaseButtonB,
            sdl2.SDLK_RETURN: windowevent.ReleaseButtonStart,
            sdl2.SDLK_BACKSPACE: windowevent.ReleaseButtonSelect,
            sdl2.SDLK_z: windowevent.SaveState,
            sdl2.SDLK_x: windowevent.LoadState,
            sdl2.SDLK_SPACE: windowevent.ReleaseSpeedUp,
        }

        # Should be less... https://wiki.libsdl.org/SDL_Init
        sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING)

        self._window = sdl2.SDL_CreateWindow(
            b"PyBoy",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            self._scaledResolution[0],
            self._scaledResolution[1],
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
                events.append(windowevent.Quit)
            elif event.type == sdl2.SDL_KEYDOWN:
                events.append(self._key_down.get(event.key.keysym.sym,
                                                 windowevent.Pass))
            elif event.type == sdl2.SDL_KEYUP:
                events.append(self._key_up.get(event.key.keysym.sym,
                                               windowevent.Pass))
        return events

    def update_display(self):
        self._update_display()

    def frame_limiter(self, speed):
        now = sdl2.SDL_GetTicks()
        delay = int(1000.0/(60.0*speed) - (now-self.ticks))
        sdl2.SDL_Delay(delay if delay > 0 else 0)
        self.ticks = sdl2.SDL_GetTicks()

    def stop(self):
        sdl2.SDL_DestroyWindow(self._window)
        sdl2.SDL_Quit()

    def scanline(self, y, lcd):
        viewpos = lcd.getViewPort()
        windowpos = lcd.getWindowPos()
        self._scanlineparameters[y][0] = viewpos[0]
        self._scanlineparameters[y][1] = viewpos[1]
        self._scanlineparameters[y][2] = windowpos[0]
        self._scanlineparameters[y][3] = windowpos[1]

    def render_screen(self, lcd):
        # All VRAM addresses are offset by 0x8000
        # Following addresses are 0x9800 and 0x9C00
        bmap = 0x1800 if lcd.LCDC.backgroundMapSelect == 0 else 0x1C00
        wmap = 0x1800 if lcd.LCDC.windowMapSelect == 0 else 0x1C00

        for y in range(ROWS):
            bx, by, wx, wy = self._scanlineparameters[y]
            # Used for the half tile at the left side when scrolling
            offset = bx & 0b111

            for x in range(COLS):
                if lcd.LCDC.windowEnabled and wy <= y and wx <= x:
                    wtileindex = lcd.VRAM[(y-wy) // 8 * 32 % 0x400 +
                                          (x-wx) // 8 % 32 + wmap]
                    # If using signed tile indices, modify index
                    if not lcd.LCDC.tileSelect:
                        # (x ^ 0x80 - 128) to convert to signed, then
                        # add 256 for offset (reduces to + 128)
                        wtileindex = (wtileindex ^ 0x80) + 128

                    self._screenbuffer[y][x] = self._tilecache[
                        8*wtileindex + (y-wy) % 8][(x-wx) % 8]

                elif lcd.LCDC.backgroundEnable:
                    btileindex = lcd.VRAM[(y+by) // 8 * 32 % 0x400 +
                                          (x+bx) // 8 % 32 + bmap]
                    # If using signed tile indices, modify index
                    if not lcd.LCDC.tileSelect:
                        # (x ^ 0x80 - 128) to convert to signed, then
                        # add 256 for offset (reduces to + 128)
                        btileindex = (btileindex ^ 0x80) + 128

                    self._screenbuffer[y][x] = self._tilecache[
                        8*btileindex + (y+by) % 8][(x+offset) % 8]
                else:
                    # If background is disabled, it becomes white
                    self._screenbuffer[y][x] = self.colorpalette[0]

        # Render sprites
        # - Doesn't restrict 10 sprites per scan line
        # - Prioritizes sprite in inverted order
        spritesize = 16 if lcd.LCDC.spriteSize else 8
        bgpkey = lcd.BGP.getColor(0)

        for n in range(0x00, 0xA0, 4):
            y = lcd.OAM[n] - 16
            x = lcd.OAM[n+1] - 8
            tileindex = lcd.OAM[n+2]
            attributes = lcd.OAM[n+3]
            xflip = attributes & 0b00100000
            yflip = attributes & 0b01000000
            spritepriority = attributes & 0b10000000
            spritecache = (self._spritecache1 if attributes & 0b10000 else
                           self._spritecache0)

            if x < 160 and y < 144:
                for dy in range(spritesize):
                    yy = spritesize - dy - 1 if yflip else dy
                    if 0 <= y < 144:
                        for dx in range(8):
                            xx = 7 - dx if xflip else dx
                            pixel = spritecache[8*tileindex+yy][xx]

                            if 0 <= x < 160:
                                if (spritepriority and
                                    not self._screenbuffer[y][x] == bgpkey):
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
            for k in range(0, 16, 2):  # 2 bytes for each line
                byte1 = lcd.VRAM[t + k - 0x8000]
                byte2 = lcd.VRAM[t + k + 1 - 0x8000]
                y = (t + k - 0x8000)//2

                for x in range(8):
                    colorcode = getcolorcode(byte1, byte2, 7-x)

                    self._tilecache[y][x] = lcd.BGP.getColor(colorcode)
                    self._spritecache0[y][x] = lcd.OBP0.getColor(colorcode)
                    self._spritecache1[y][x] = lcd.OBP1.getColor(colorcode)

                    if colorcode == 0:
                        self._spritecache0[y][x] &= ~self.alphamask
                        self._spritecache1[y][x] &= ~self.alphamask

        self.tiles_changed.clear()

    def blank_screen(self):
        # If the screen is off, fill it with a color.
        color = self.colorpalette[0]
        for y in range(144):
            for x in range(160):
                self._screenbuffer[y][x] = color

    def getscreenbuffer(self):
        if cythonmode:
            return self._screenbuffer_raw.tobytes()
        else:
            return self._screenbuffer_raw


# Unfortunately CPython/PyPy code has to be hidden in an exec call to
# prevent Cython from trying to parse it. This block provides the
# functions that are otherwise implemented as inlined cdefs in the pxd
if not cythonmode:
    exec("""
def _update_display(self):
    sdl2.SDL_UpdateTexture(self._sdltexturebuffer, None,
                           self._screenbuffer_ptr, COLS*4)
    sdl2.SDL_RenderCopy(self._sdlrenderer, self._sdltexturebuffer,
                        None, None)
    sdl2.SDL_RenderPresent(self._sdlrenderer)
    sdl2.SDL_RenderClear(self._sdlrenderer)

SDLWindow._update_display = _update_display
""", globals(), locals())
