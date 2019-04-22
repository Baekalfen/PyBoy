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
HOR_LIMIT = 32


# Mask colors:
COLOR = 0x00000000
MASK = 0xC0C0C0

# Additive colors
HOVER = 0xFF0000
MARK = 0x0000FF
MARK2 = 0x00FF00

# Unique value, out of bounds of tiles
NO_TILE = 0xFFFF


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
    def __init__(self, lcd, w, h, scale, title, pos=(sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED)):
        self.lcd = lcd
        self.width = w
        self.height = h
        self.mouse_hover_x = -1
        self.mouse_hover_y = -1
        self.mouse_x = -1
        self.mouse_y = -1
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

    def reset_hover(self):
        self.mouse_hover_x = -1
        self.mouse_hover_y = -1

    def reset_mouse(self):
        self.mouse_x = -1
        self.mouse_y = -1

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

    def mouse(self, click, window_id, x, y):
        x, y = x//self.scale, y//self.scale
        if (0 < x <= self.width) and (0 < y <= self.height):
            self.mouse_hover_x = x
            self.mouse_hover_y = y
            if click:
                self.mouse_x = x
                self.mouse_y = y

            return self._mouse(click, window_id, x, y)
        return NO_TILE

    # Overwriting and calling super() for `mouse` can be cumbersome in Cython.
    # Overwrite the following method instead:
    def _mouse(self, click, window_id, x, y):
        return NO_TILE

    def mark_tile(self, x, y, color):
        if (0 <= x < self.width) and (0 <= y < self.height): # Test that we are inside screen area
            ts = 8 # Tile size
            xx = x - (x % ts)
            yy = y - (y % ts)
            for i in range(ts):
                self.buf0[yy+i][xx] = color
            for i in range(ts):
                self.buf0[yy][xx+i] = color
            for i in range(ts):
                self.buf0[yy+ts-1][xx+i] = color
            for i in range(ts):
                self.buf0[yy+i][xx+ts-1] = color


class TileWindow(Window):

    def __init__(self, lcd, w, h, scale, title, pos=(sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED)):
        super().__init__(lcd, w, h, scale, title, pos)

    def update(self, tile_cache0):
        for t in range(TILES):
            xx = (t * 8) % self.width
            yy = ((t * 8) // self.width)*8
            self.copy_tile(tile_cache0, t, (xx, yy), self.buf0)

    def draw_overlay(self, marked_tile, scanline_parameters):
        # Mark selected tiles
        if marked_tile != NO_TILE:
            if self.lcd.LCDC.tiledata_select == 0:
                marked_tile += 256

            for t in range(TILES):
                if t == marked_tile:
                    xx = (t * 8) % self.width
                    yy = ((t * 8) // self.width)*8
                    self.mark_tile(xx, yy, MARK2)

        self.mark_tile(self.mouse_hover_x, self.mouse_hover_y, HOVER)
        self.mark_tile(self.mouse_x, self.mouse_y, MARK)

    def _mouse(self, click, window_id, x, y):
        if click:
            tile_x, tile_y = x // 8, y // 8
            hor_limit = self.width / 8
            tile_index = tile_y * hor_limit + tile_x
            if self.lcd.LCDC.tiledata_select == 0:
                if tile_index < 128:
                    print("Index tile out of bounds, when using signed index")
                    return NO_TILE # Invalid index with tiledata select
                # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset
                if tile_index > 255:
                    tile_index -= 256
                tile_index = (tile_index ^ 0x80) - 128
                print(f"Location: ({tile_x}, {tile_y})\nTile index: {tile_index}\nMemory area: 0x8800-0x97FF (signed index)")
            else:
                if tile_index > 255:
                    print("Index tile out of bounds, when using unsigned index")
                    return NO_TILE # Invalid index with tiledata select
                print(f"Location: ({tile_x}, {tile_y})\nTile index: {tile_index}\nMemory area: 0x8000-0x8FFF (unsigned index)")
            return tile_index
        return NO_TILE

class TileViewWindow(Window):

    def __init__(self, lcd, w, h, scale, title, offset, pos=(sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED)):
        super().__init__(lcd, w, h, scale, title, pos)
        self.offset = offset

    def update(self, lcd, tile_cache0):
        # ver_limit = 32

        for n in range(self.offset, self.offset + 0x400):
            tile_index = lcd.VRAM[n]

            # Check the tile source and add offset
            # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
            # BG & Window Tile Data Select   (0=8800-97FF, 1=8000-8FFF)
            if lcd.LCDC.tiledata_select == 0:
                # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset (reduces to + 128)
                tile_index = (tile_index ^ 0x80) + 128

            tile_column = (n-self.offset) % HOR_LIMIT # Horizontal tile number wrapping on 16
            tile_row = (n-self.offset) // HOR_LIMIT # Vertical time number based on tile_column

            des = (tile_column * 8, tile_row * 8)
            self.copy_tile(tile_cache0, tile_index, des, self.buf0)

    def draw_overlay(self, marked_tile, scanline_parameters, ix, iy):
        # Mark screen area
        for y in range(GAMEBOY_RESOLUTION[1]):
            xx = scanline_parameters[y][ix]
            yy = scanline_parameters[y][iy]
            if y == 0 or y == GAMEBOY_RESOLUTION[1]-1:
                for x in range(GAMEBOY_RESOLUTION[0]):
                    self.buf0[(yy+y) % 0xFF][(xx+x) % 0xFF] = COLOR

            else:
                self.buf0[(yy+y) % 0xFF][xx] = COLOR
                for x in range(GAMEBOY_RESOLUTION[0]):
                    self.buf0[(yy+y) % 0xFF][(xx+x) % 0xFF] &= MASK
                self.buf0[(yy+y) % 0xFF][(xx+GAMEBOY_RESOLUTION[0]) % 0xFF] = COLOR

        # Mark selected tiles
        if marked_tile != NO_TILE:
            for n in range(self.offset, self.offset + 0x400):
                t = self.lcd.VRAM[n]
                if self.lcd.LCDC.tiledata_select == 0:
                    # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset
                    t = (t ^ 0x80) - 128

                if t == marked_tile:
                    xx = (t * 8) % self.width
                    yy = ((t * 8) // self.width)*8
                    tile_column = (n-self.offset) % HOR_LIMIT # Horizontal tile number wrapping on 16
                    tile_row = (n-self.offset) // HOR_LIMIT # Vertical time number based on tile_column

                    self.mark_tile(tile_column * 8, tile_row * 8, MARK2)
            # input()
            self.mark_tile(self.mouse_hover_x, self.mouse_hover_y, HOVER)
            self.mark_tile(self.mouse_x, self.mouse_y, MARK)

    def _mouse(self, click, window_id, x, y):
        if click:
            tile_x, tile_y = x // 8, y // 8
            tile = tile_y * 32 + tile_x
            tile_index = self.lcd.VRAM[self.offset+tile]
            if self.lcd.LCDC.tiledata_select == 0:
                # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset
                tile_index = (tile_index ^ 0x80) - 128
                print(f"Location: ({tile_x}, {tile_y})\nTile index: {tile_index}\nMemory area: 0x8800-0x97FF (signed index)")
            else:
                print(f"Location: ({tile_x}, {tile_y})\nTile index: {tile_index}\nMemory area: 0x8000-0x8FFF (unsigned index)")
            return tile_index
        return NO_TILE


class DebugWindow():
    def __init__(self, scale=2):
        # self.tiles_changed = set([])
        self.scale = scale
        self.color_palette = (0xFFFFFFFF, 0xFF999999, 0xFF555555, 0xFF000000)

        self.tile_cache, self.tile_cache0, self.tile_cache_p = make_buffer(8, 384*8)

        # https://wiki.libsdl.org/SDL_Scancode#Related_Enumerations
        sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) # Should be less... https://wiki.libsdl.org/SDL_Init
        # sdl2.SDL_SetHint(sdl2.SDL_HINT_MOUSE_FOCUS_CLICKTHROUGH, "1")
        self.scanline_parameters = [[0, 0, 0, 0] for _ in range(GAMEBOY_RESOLUTION[1])];
        self.marked_tile = NO_TILE

    # Rest of the __init__, when we have the lcd instance
    def set_lcd(self, lcd):
        self.lcd = lcd
        self.tile1 = TileViewWindow(lcd, 0x100, 0x100, self.scale, b"Tile View 1", 0x1800, (0, 0))
        self.tile2 = TileViewWindow(lcd, 0x100, 0x100, self.scale, b"Tile View 2", 0x1C00, (0x100*self.scale, 0))
        self.sprite = Window(lcd, 64, 40*2, self.scale, b"Sprites", (0x200*self.scale, 0))

        self.tile_data_width = 16*8 # Change the 16 to however wide you want the tile window
        self.tile_data_height = ((TILES*8) // self.tile_data_width)*8
        self.tile = TileWindow(
            lcd, self.tile_data_width, self.tile_data_height, self.scale, b"Tile Data", (0x240*self.scale, 0))

    def stop(self):
        self.tile.stop()
        self.tile1.stop()
        self.tile2.stop()
        self.sprite.stop()
        sdl2.SDL_Quit()

    def update_cache(self):
        # Update cache
        for t in range(0x8000, 0x9800, 16):
            for k in range(0, 16, 2):  # 2 bytes for each line
                byte1 = self.lcd.VRAM[t+k-0x8000]
                byte2 = self.lcd.VRAM[t+k+1-0x8000]
                y = (t+k-0x8000) // 2

                for x in range(8):
                    color_code = get_color_code(byte1, byte2, 7-x)
                    self.tile_cache0[y][x] = self.lcd.BGP.getcolor(color_code)

    def update(self):
        self.tile.update(self.tile_cache0)
        self.tile1.update(self.lcd, self.tile_cache0)
        self.tile2.update(self.lcd, self.tile_cache0)
        # self.sprite.update(self.lcd)

        self.tile.draw_overlay(self.marked_tile, self.scanline_parameters)
        self.tile1.draw_overlay(self.marked_tile, self.scanline_parameters, 0, 1)
        self.tile2.draw_overlay(self.marked_tile, self.scanline_parameters, 2, 3)

        self.tile.update_display()
        self.tile1.update_display()
        self.tile2.update_display()
        self.sprite.update_display()

    def scanline(self, y): # Just recording states of LCD registers
        view_pos = self.lcd.getviewport()
        window_pos = self.lcd.getwindowpos()
        self.scanline_parameters[y][0] = view_pos[0]
        self.scanline_parameters[y][1] = view_pos[1]
        self.scanline_parameters[y][2] = window_pos[0]
        self.scanline_parameters[y][3] = window_pos[1]

    def window_focus(self, window_id, focus):
        if not focus:
            if window_id == sdl2.SDL_GetWindowID(self.tile1.window):
                self.tile1.reset_hover()
            elif window_id == sdl2.SDL_GetWindowID(self.tile2.window):
                self.tile2.reset_hover()
            elif window_id == sdl2.SDL_GetWindowID(self.sprite.window):
                self.sprite.reset_hover()
            elif window_id == sdl2.SDL_GetWindowID(self.tile.window):
                self.tile.reset_hover()

    def mouse(self, click, window_id, x, y):

        # The marked tile
        mt = NO_TILE

        # Forward mouse event to appropriate handlers
        if window_id == sdl2.SDL_GetWindowID(self.tile1.window):
            mt = self.tile1.mouse(click, window_id, x, y)
        elif window_id == sdl2.SDL_GetWindowID(self.tile2.window):
            mt = self.tile2.mouse(click, window_id, x, y)
        elif window_id == sdl2.SDL_GetWindowID(self.sprite.window):
            mt = self.sprite.mouse(click, window_id, x, y)
        elif window_id == sdl2.SDL_GetWindowID(self.tile.window):
            mt = self.tile.mouse(click, window_id, x, y)
        else: # Game window
            # TODO: Detect which sprites, tiles, etc. is below cursor and highlight in other views
            print(click, window_id, x, y)

        # Test if there is a new marked tile
        if mt != NO_TILE:
            self.marked_tile = mt

            # Reset selection on other windows
            if window_id != sdl2.SDL_GetWindowID(self.tile1.window):
                self.tile1.reset_mouse()
            if window_id != sdl2.SDL_GetWindowID(self.tile2.window):
                self.tile2.reset_mouse()
            if window_id != sdl2.SDL_GetWindowID(self.sprite.window):
                self.sprite.reset_mouse()
            if window_id != sdl2.SDL_GetWindowID(self.tile.window):
                self.tile.reset_mouse()


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
