#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import ctypes
from array import array

import sdl2
from pyboy.botsupport import constants, sprite, tile, tilemap
from pyboy.plugins.base_plugin import PyBoyPlugin, PyBoyWindowPlugin

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False



ROWS, COLS = 144, 160
TILES = 384
SPRITES = 40
GAMEBOY_RESOLUTION = (COLS, ROWS)
HOR_LIMIT = 32


# Mask colors:
COLOR = 0x00000000
MASK = 0x00C0C000

# Additive colors
HOVER = 0xFF0000
MARK = 0x0000FF
MARK2 = 0x00FF00

SPRITE_BACKGROUND = MASK

class Debug(PyBoyWindowPlugin):
    argv = [('-d', '--debug', {"action":'store_true', "help": 'Enable emulator debugging mode'})]

    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

        self.scale = 2
        window_pos = 0

        self.tile1 = TileViewWindow(pyboy, mb, pyboy_argv, scale=2, title="Tile View", width=256, height=256, pos_x=0, pos_y=0, high_tilemap=False, scanline_x=0, scanline_y=1)
        window_pos += (256*self.scale)

        self.tile2 = TileViewWindow(pyboy, mb, pyboy_argv, scale=2, title="Tile View", width=256, height=256, pos_x=window_pos, pos_y=0, high_tilemap=True, scanline_x=2, scanline_y=3)
        window_pos += (256*self.scale)

        self.sprite = SpriteWindow(pyboy, mb, pyboy_argv, scale=2, title="Sprite Data", width=8*10, height=16*4, pos_x=window_pos, pos_y=0)
        window_pos += (8*10*self.scale)

        tile_data_width = 16*8 # Change the 16 to however wide you want the tile window
        tile_data_height = ((TILES*8) // tile_data_width)*8
        self.tiledata = TileDataWindow(pyboy, mb, pyboy_argv, scale=2, title="Tile Data", width=tile_data_width, height=tile_data_height, pos_x=window_pos, pos_y=0)
        window_pos += (tile_data_width*self.scale)

        self.spriteview = SpriteViewWindow(pyboy, mb, pyboy_argv, scale=2, title="Sprite View", width=COLS, height=ROWS, pos_x=window_pos, pos_y=0)

    def post_tick(self):
        self.tile1.post_tick()
        self.tile2.post_tick()
        self.tiledata.post_tick()
        self.sprite.post_tick()
        self.spriteview.post_tick()

    def stop(self):
        # sdl2.SDL_DestroyWindow(self._window)
        sdl2.SDL_Quit()

    def enabled(self):
        return self.pyboy_argv.get('debug')


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


class DebugWindow(PyBoyPlugin):
    def __init__(self, pyboy, mb, pyboy_argv, *, scale, title, width, height, pos_x, pos_y):
        super().__init__(pyboy, mb, pyboy_argv)
        self.scale = scale
        self.width, self.height = width, height
        self.marked_tile = -1
        self.base_title = title

        self.window = sdl2.SDL_CreateWindow(
            self.base_title.encode('utf8'),
            pos_x,
            pos_y,
            width*scale,
            height*scale,
            sdl2.SDL_WINDOW_RESIZABLE)

        self.buf, self.buf0, self.buf_p = make_buffer(width, height)

        self.sdlrenderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_ACCELERATED)
        self.sdl_texture_buffer = sdl2.SDL_CreateTexture(
            self.sdlrenderer,
            sdl2.SDL_PIXELFORMAT_RGBA8888,
            sdl2.SDL_TEXTUREACCESS_STATIC,
            width,
            height
        )

        if not cythonmode:
            self.renderer = mb.renderer

    def __cinit__(self, mb, *args):
        self.mb = mb
        self.renderer = mb.renderer

    def stop(self):
        sdl2.SDL_DestroyWindow(self.window)

    def post_tick(self):
        self._update_display()

    def _update_display(self):
        sdl2.SDL_UpdateTexture(self.sdl_texture_buffer, None, self.buf_p, self.width*4)
        sdl2.SDL_RenderCopy(self.sdlrenderer, self.sdl_texture_buffer, None, None)
        sdl2.SDL_RenderPresent(self.sdlrenderer)
        sdl2.SDL_RenderClear(self.sdlrenderer)

    ##########################
    # Internal functions

    def copy_tile(self, tile_cache0, t, des, to_buffer):
        xx, yy = des

        for y in range(8):
            for x in range(8):
                to_buffer[yy+y][xx+x] = tile_cache0[y + t*8][x]

    def mark_tile(self, x, y, color, height=8, width=8):
        if (0 <= x < self.width) and (0 <= y < self.height): # Test that we are inside screen area
            tw = width # Tile width
            th = height # Tile height
            xx = x - (x % tw)
            yy = y - (y % th)
            for i in range(th):
                self.buf0[yy+i][xx] = color
            for i in range(tw):
                self.buf0[yy][xx+i] = color
            for i in range(tw):
                self.buf0[yy+th-1][xx+i] = color
            for i in range(th):
                self.buf0[yy+i][xx+tw-1] = color



class TileViewWindow(DebugWindow):
    def __init__(self, *args, high_tilemap, scanline_x, scanline_y, **kwargs):
        super().__init__(*args, **kwargs)
        self.high_tilemap = high_tilemap
        self.offset = 0x1C00 if high_tilemap else 0x1800
        self.scanline_x, self.scanline_y = scanline_x, scanline_y

    def post_tick(self):
        tile_cache0 = self.renderer._tilecache

        for n in range(self.offset, self.offset + 0x400):
            tile_index = self.mb.lcd.VRAM[n]

            # Check the tile source and add offset
            # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
            # BG & Window Tile Data Select   (0=8800-97FF, 1=8000-8FFF)
            if self.mb.lcd.LCDC.tiledata_select == 0:
                # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset (reduces to + 128)
                tile_index = (tile_index ^ 0x80) + 128

            tile_column = (n-self.offset) % HOR_LIMIT # Horizontal tile number wrapping on 16
            tile_row = (n-self.offset) // HOR_LIMIT # Vertical time number based on tile_column

            des = (tile_column * 8, tile_row * 8)
            self.copy_tile(tile_cache0, tile_index, des, self.buf0)

        self.draw_overlay()
        self.update_title()
        super().post_tick()

    def update_title(self):
        title = self.base_title
        title += " [0x9C00-0x9FFF]" if self.high_tilemap else " [0x9800-0x9BFF]"
        if bool(self.mb.lcd.LCDC.windowmap_select) == self.high_tilemap:
            title += " [Window]"
        if bool(self.mb.lcd.LCDC.backgroundmap_select) == self.high_tilemap:
            title += " [Background]"
        sdl2.SDL_SetWindowTitle(self.window, title.encode('utf8'))

    def draw_overlay(self):
        scanlineparameters = self.pyboy.get_screen_position_list()

        # Mark screen area
        for y in range(GAMEBOY_RESOLUTION[1]):
            xx = int(scanlineparameters[y][self.scanline_x])
            yy = int(scanlineparameters[y][self.scanline_y])
            if y == 0 or y == GAMEBOY_RESOLUTION[1]-1:
                for x in range(GAMEBOY_RESOLUTION[0]):
                    self.buf0[(yy+y) % 0xFF][(xx+x) % 0xFF] = COLOR

            else:
                self.buf0[(yy+y) % 0xFF][xx % 0xFF] = COLOR
                for x in range(GAMEBOY_RESOLUTION[0]):
                    self.buf0[(yy+y) % 0xFF][(xx+x) % 0xFF] &= MASK
                self.buf0[(yy+y) % 0xFF][(xx+GAMEBOY_RESOLUTION[0]) % 0xFF] = COLOR

        #Mark selected tiles
        if self.marked_tile != -1:
            for n in range(self.offset, self.offset + 0x400):
                t = self.lcd.VRAM[n]
                if self.lcd.LCDC.tiledata_select == 0:
                    # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset
                    t = (t ^ 0x80) - 128

                if t == self.marked_tile:
                    xx = (t * 8) % self.width
                    yy = ((t * 8) // self.width)*8
                    tile_column = (n-self.offset) % HOR_LIMIT # Horizontal tile number wrapping on 16
                    tile_row = (n-self.offset) // HOR_LIMIT # Vertical time number based on tile_column

                    self.mark_tile(tile_column * 8, tile_row * 8, MARK2)
        # self.mark_tile(self.mouse_hover_x, self.mouse_hover_y, HOVER)
        # self.mark_tile(self.mouse_x, self.mouse_y, MARK)

    # def _mouse(self, click, window_id, x, y):
    #     if click:
    #         tile_x, tile_y = x // 8, y // 8
    #         tile = tile_y * 32 + tile_x
    #         tile_index = self.lcd.VRAM[self.offset+tile]
    #         if self.lcd.LCDC.tiledata_select == 0:
    #             # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset
    #             tile_index = (tile_index ^ 0x80) - 128
    #             print(f"Location: ({tile_x}, {tile_y})\nTile index: {tile_index}\n"
    #                   f"Memory area: 0x8800-0x97FF (signed index)")
    #         else:
    #             print(f"Location: ({tile_x}, {tile_y})\nTile index: {tile_index}\n"
    #                   f"Memory area: 0x8000-0x8FFF (unsigned index)")
    #         return tile_index
    #     return NO_TILE


class TileDataWindow(DebugWindow):
    def post_tick(self):
        tile_cache0 = self.renderer._tilecache

        for t in range(TILES):
            xx = (t * 8) % self.width
            yy = ((t * 8) // self.width)*8
            self.copy_tile(tile_cache0, t, (xx, yy), self.buf0)

        self.draw_overlay()
        super().post_tick()

    def draw_overlay(self):
        sprite_height = 16 if self.mb.lcd.LCDC.sprite_height else 8

        # Mark selected tiles
        if self.marked_tile != -1:
            if self.mb.lcd.LCDC.tiledata_select == 0:
                self.marked_tile += 256

            for t in range(TILES):
                if t == self.marked_tile:
                    xx = (t * 8) % self.width
                    yy = ((t * 8) // self.width)*8
                    self.mark_tile(xx, yy, MARK2, width=sprite_height, height=8)

        # self.mark_tile(self.mouse_hover_x, self.mouse_hover_y, HOVER, width=sprite_height, height=8)
        # self.mark_tile(self.mouse_x, self.mouse_y, MARK, width=sprite_height, height=8)

    # def _mouse(self, click, window_id, x, y):
    #     if click:
    #         tile_x, tile_y = x // 8, y // 8
    #         hor_limit = self.width // 8
    #         tile_index = tile_y * hor_limit + tile_x
    #         if self.lcd.LCDC.tiledata_select == 0:
    #             if tile_index < 128:
    #                 print("Index tile out of bounds, when using signed index")
    #                 return NO_TILE # Invalid index with tiledata select
    #             # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset
    #             if tile_index > 255:
    #                 tile_index -= 256
    #             tile_index = (tile_index ^ 0x80) - 128
    #             print(
    #                 f"Location: ({tile_x}, {tile_y})\nTile index: {tile_index}\n"
    #                 f"Memory area: 0x8800-0x97FF (signed index)"
    #             )
    #         else:
    #             if tile_index > 255:
    #                 print("Index tile out of bounds, when using unsigned index")
    #                 return NO_TILE # Invalid index with tiledata select
    #             print(
    #                 f"Location: ({tile_x}, {tile_y})\nTile index: {tile_index}\n"
    #                 f"Memory area: 0x8000-0x8FFF (unsigned index)"
    #             )
    #         return tile_index
    #     return NO_TILE


class SpriteWindow(DebugWindow):
    def post_tick(self):
        tile_cache0 = self.renderer._tilecache

        sprite_height = 16 if self.mb.lcd.LCDC.sprite_height else 8
        for n in range(0, 0xA0, 4):
            # x = lcd.OAM[n]
            # y = lcd.OAM[n+1]
            t = self.mb.lcd.OAM[n+2]
            # attributes = lcd.OAM[n+3]
            xx = ((n//4) * 8) % self.width
            yy = (((n//4) * 8) // self.width)*sprite_height
            self.copy_tile(tile_cache0, t, (xx, yy), self.buf0)
            if self.mb.lcd.LCDC.sprite_height:
                self.copy_tile(tile_cache0, t+1, (xx, yy+8), self.buf0)

        self.draw_overlay()
        super().post_tick()


    def draw_overlay(self):
        sprite_height = 16 if self.mb.lcd.LCDC.sprite_height else 8
        # Mark selected tiles
        if self.marked_tile != -1:
            if self.mb.lcd.LCDC.tiledata_select == 0:
                self.marked_tile += 256

            for n in range(0, 0xA0, 4):
                # x = lcd.OAM[n]
                # y = lcd.OAM[n+1]
                t = self.mb.lcd.OAM[n+2]
                # attributes = lcd.OAM[n+3]
                # for t in range(TILES):
                if t == self.marked_tile:
                    xx = (t * 8) % self.width
                    yy = ((t * 8) // self.width)*8
                    self.mark_tile(xx, yy, MARK2, height=sprite_height)

            self.mark_tile(self.mouse_hover_x, self.mouse_hover_y, HOVER, height=sprite_height)
            self.mark_tile(self.mouse_x, self.mouse_y, MARK, height=sprite_height)


    # def _mouse(self, click, window_id, x, y):
    #     sprite_height = 16 if self.lcd.LCDC.sprite_height else 8
    #     print(sprite_height)
    #     if click:
    #         tile_x, tile_y = x // 8, y // sprite_height
    #         hor_limit = self.width // 8
    #         tile_index = tile_y * hor_limit + tile_x
    #         if self.lcd.LCDC.tiledata_select == 0:
    #             if tile_index < 128:
    #                 print("Index tile out of bounds, when using signed index")
    #                 return NO_TILE # Invalid index with tiledata select
    #             # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset
    #             if tile_index > 255:
    #                 tile_index -= 256
    #             tile_index = (tile_index ^ 0x80) - 128
    #             print(
    #                 f"Location: ({tile_x}, {tile_y})\nTile index: {tile_index}\n"
    #                 f"Memory area: 0x8800-0x97FF (signed index)"
    #             )
    #         else:
    #             if tile_index > 255:
    #                 print("Index tile out of bounds, when using unsigned index")
    #                 return NO_TILE # Invalid index with tiledata select
    #             print(
    #                 f"Location: ({tile_x}, {tile_y})\nTile index: {tile_index}\n"
    #                 f"Memory area: 0x8000-0x8FFF (unsigned index)"
    #             )
    #         return tile_index
    #     return NO_TILE

class SpriteViewWindow(DebugWindow):
    def post_tick(self):
        for y in range(ROWS):
            for x in range(COLS):
                self.buf0[y][x] = SPRITE_BACKGROUND

        self.mb.renderer.render_sprites(self.mb.lcd, self.buf0)
        self.update_title()
        super().post_tick()

    def update_title(self):
        title = self.base_title
        title += " [8x16]" if self.mb.lcd.LCDC.sprite_height else " [8x8]"
        title += " " if self.mb.lcd.LCDC.sprite_enable else " [Disabled]"
        sdl2.SDL_SetWindowTitle(self.window, title.encode('utf8'))
