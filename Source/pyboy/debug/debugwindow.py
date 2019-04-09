#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False

import ctypes
import sdl2
import sdl2.ext
from array import array

TILES = 384
GAMEBOY_RESOLUTION = (160, 144)
COLOR = 0x00000000
MASK = 0xC0C0C0


def get_color_code(byte1, byte2, offset):
    # The colors are 2 bit and are found like this:
    #
    # Color of the first pixel is 0b10
    # | Color of the second pixel is 0b01
    # v v
    # 1 0 0 1 0 0 0 1 <- byte1
    # 0 1 1 1 1 1 0 0 <- byte2
    return (((byte2 >> (offset)) & 0b1) << 1) + ((byte1 >> (offset)) & 0b1) # 2bit color code


def make_buffer(w, h):
    buf = array('B', [0x55] * (w*h*4))
    if cythonmode:
        buf0 = memoryview(buf).cast('I', shape=(h, w))
        buf_p = None
    else:
        view = memoryview(buf).cast('I')
        buf0 = [view[i:i+w] for i in range(0, w*h, w)]
        buf_p = ctypes.c_void_p(buf.buffer_info()[0])
    return buf, buf0, buf_p


class Window():
    def __init__(self, w, h, scale, title, pos=(sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED)):
        self.width = w
        self.height = h
        self.scale = scale
        self.window = sdl2.SDL_CreateWindow(
            title,
            pos[0],
            pos[1],
            w*scale,
            h*scale,
            sdl2.SDL_WINDOW_RESIZABLE)

        self.buf, self.buf0, self.buf_p = make_buffer(w, h)

        self.sdlrenderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_ACCELERATED)
        self.sdl_texture_buffer = sdl2.SDL_CreateTexture(
            self.sdlrenderer,
            sdl2.SDL_PIXELFORMAT_RGBA32,
            sdl2.SDL_TEXTUREACCESS_STATIC,
            w,
            h
        )

        sdl2.SDL_ShowWindow(self.window)

    def stop(self):
        sdl2.SDL_DestroyWindow(self.window)

    def update_display(self):
        self._update_display()
        # sdl2.SDL_UpdateTexture(self.sdl_texture_buffer, None, self.buf_p, self.width*4)
        # sdl2.SDL_RenderCopy(self.sdlrenderer, self.sdl_texture_buffer, None, None)
        # sdl2.SDL_RenderPresent(self.sdlrenderer)

    def copy_tile(self, tile_cache0, t, des, to_buffer):
        xx, yy = des

        for y in range(8):
            for x in range(8):
                to_buffer[yy+y][xx+x] = tile_cache0[y + t*8][x]


class TileWindow(Window):

    def __init__(self, w, h, scale, title, pos=(sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED)):
        super().__init__(w, h, scale, title, pos)

    def update(self, tile_cache0):
        for t in range(TILES):
            xx = (t * 8) % self.width
            yy = ((t * 8) // self.width)*8
            self.copy_tile(tile_cache0, t, (xx, yy), self.buf0)


class TileViewWindow(Window):

    def __init__(self, w, h, scale, title, offset, pos=(sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED)):
        super().__init__(w, h, scale, title, pos)
        self.offset = offset

    def update(self, lcd, tile_cache0):
        for y in range(self.height):
            for x in range(self.width):
                self.buf0[y][x] = 0xFF998844
        # return
        # tile_size = 8
        hor_limit = 32
        ver_limit = 32

        for n in range(self.offset, self.offset + 0x400):
            tile_index = lcd.VRAM[n] # TODO: Simplify this reference -- and reoccurences

            # Check the tile source and add offset
            # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
            # BG & Window Tile Data Select   (0=8800-97FF, 1=8000-8FFF)
            if lcd.LCDC.tiledata_select == 0: # TODO: use correct flag
                # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset (reduces to + 128)
                tile_index = (tile_index ^ 0x80) + 128

            tile_column = (n-self.offset) % hor_limit # Horizontal tile number wrapping on 16
            tile_row = (n-self.offset) // ver_limit # Vertical time number based on tile_column

            des = (tile_column * 8, tile_row * 8)
            self.copy_tile(tile_cache0, tile_index, des, self.buf0)


class DebugWindow():
    def __init__(self, scale=2):
        # self.tiles_changed = set([])
        self.scale = scale
        self.color_palette = (0xFFFFFFFF, 0xFF999999, 0xFF555555, 0xFF000000)

        self.tile_cache, self.tile_cache0, self.tile_cache_p = make_buffer(8, 384*8)

        # https://wiki.libsdl.org/SDL_Scancode#Related_Enumerations
        sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) # Should be less... https://wiki.libsdl.org/SDL_Init

        self.tile1 = TileViewWindow(0x100, 0x100, self.scale, b"Tile View 1", 0x1800, (0, 0))
        self.tile2 = TileViewWindow(0x100, 0x100, self.scale, b"Tile View 2", 0x1C00, (0x100*self.scale, 0))
        self.sprite = Window(64, 40*2, self.scale, b"Sprites", (0x200*self.scale, 0))

        self.tile_data_width = 16*8 # Change the 16 to however wide you want the tile window
        self.tile_data_height = ((TILES*8) // self.tile_data_width)*8
        self.tile = TileWindow(
            self.tile_data_width, self.tile_data_height, self.scale, b"Tile Data", (0x240*self.scale, 0))

        self.scanline_parameters = [[0, 0, 0, 0] for _ in range(GAMEBOY_RESOLUTION[1])]

    def stop(self):
        self.tile.stop()
        self.tile1.stop()
        self.tile2.stop()
        self.sprite.stop()
        sdl2.SDL_Quit()

    def update(self, lcd):
        # Update cache
        for t in range(0x8000, 0x9800, 16):
            for k in range(0, 16, 2):  # 2 bytes for each line
                byte1 = lcd.VRAM[t+k-0x8000]
                byte2 = lcd.VRAM[t+k+1-0x8000]
                y = (t+k-0x8000) // 2

                for x in range(8):
                    color_code = get_color_code(byte1, byte2, 7-x)
                    # print("0x%0.2x" % lcd.BGP.get_color(color_code))
                    self.tile_cache0[y][x] = lcd.BGP.getcolor(color_code)

        self.tile.update(self.tile_cache0)
        self.tile1.update(lcd, self.tile_cache0)
        self.tile2.update(lcd, self.tile_cache0)
        # self.sprite.update(lcd)

        self.draw_screen_port()

        self.tile.update_display()
        self.tile1.update_display()
        self.tile2.update_display()
        self.sprite.update_display()

    def scanline(self, y, lcd): # Just recording states of LCD registers
        view_pos = lcd.getviewport()
        window_pos = lcd.getwindowpos()
        self.scanline_parameters[y][0] = view_pos[0]
        self.scanline_parameters[y][1] = view_pos[1]
        self.scanline_parameters[y][2] = window_pos[0]
        self.scanline_parameters[y][3] = window_pos[1]

    def draw_screen_port(self):
        buf1 = self.tile1.buf0
        buf2 = self.tile2.buf0
        for y in range(GAMEBOY_RESOLUTION[1]):
            bx, by, wx, wy = self.scanline_parameters[y]
            if y == 0 or y == GAMEBOY_RESOLUTION[1]-1:
                # Background
                for x in range(GAMEBOY_RESOLUTION[0]):
                    buf1[(by+y) % 0xFF][(bx+x) % 0xFF] = COLOR

                # Window
                for x in range(GAMEBOY_RESOLUTION[0]):
                    buf2[(wy+y) % 0xFF][(wx+x) % 0xFF] = COLOR
            else:
                # Background
                buf1[(by+y) % 0xFF][bx] = COLOR
                for x in range(GAMEBOY_RESOLUTION[0]):
                    buf1[(by+y) % 0xFF][(bx+x) % 0xFF] &= MASK
                buf1[(by+y) % 0xFF][(bx+GAMEBOY_RESOLUTION[0]) % 0xFF] = COLOR

                # Window
                buf2[(wy+y) % 0xFF][wx] = COLOR
                for x in range(GAMEBOY_RESOLUTION[0]):
                    buf2[(wy+y) % 0xFF][(wx+x) % 0xFF] &= MASK
                buf2[(wy+y) % 0xFF][(wx+GAMEBOY_RESOLUTION[0]) % 0xFF] = COLOR


#     def refresh_sprite_view(self, lcd):
#         self.sprite_buffer.fill(0x00ABC4FF)
#         for n in range(0x00,0xA0,4):
#             tile_index = lcd.OAM[n+2] # TODO: Simplify this reference
#             # attributes = lcd.OAM[n+3]
#             from_XY = (tile_index * 8, 0)

#             i = n*2
#             self.copy_tile(from_XY, (i%self.sprite_width, (i/self.sprite_width)*16), lcd.sprite_cache_OBP0,
#                 self.sprite_buffer)
#             if lcd.LCDC.sprite_size:
#                 self.copy_tile((tile_index * 8+8, 0), (i%self.sprite_width, (i/self.sprite_width)*16 + 8),
#                     lcd.sprite_cache_OBP0, self.sprite_buffer)


# Unfortunately CPython/PyPy code has to be hidden in an exec call to
# prevent Cython from trying to parse it. This block provides the
# functions that are otherwise implemented as inlined cdefs in the pxd
if not cythonmode:
    exec("""
def _update_display(self):
    sdl2.SDL_UpdateTexture(self.sdl_texture_buffer, None, self.buf_p, self.width*4)
    sdl2.SDL_RenderCopy(self.sdlrenderer, self.sdl_texture_buffer, None, None)
    sdl2.SDL_RenderPresent(self.sdlrenderer)
    sdl2.SDL_RenderClear(self.sdlrenderer)

Window.update_display = _update_display
""", globals(), locals())
