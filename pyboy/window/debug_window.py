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
from array import array

import sdl2
import sdl2.ext

from .. import windowevent
from .window_sdl2 import KEY_DOWN, KEY_UP, SDLWindow

# from ..botsupport import Sprite

TILES = 384
SPRITES = 40
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
    def __init__(self, lcd, w, h, scale, title, pos=(sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED),
                 hide_window=False):
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

        if hide_window:
            sdl2.SDL_HideWindow(self.window)
        else:
            sdl2.SDL_ShowWindow(self.window)

    def reset_hover(self):
        self.mouse_hover_x = -1
        self.mouse_hover_y = -1

    def reset_mouse(self):
        self.mouse_x = -1
        self.mouse_y = -1

    def stop(self):
        sdl2.SDL_DestroyWindow(self.window)

    def update_display(self, paused):
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


class SpriteWindow(Window):

    def __init__(self, lcd, w, h, scale, title, pos=(sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED),
                 hide_window=False):
        super().__init__(lcd, w, h, scale, title, pos, hide_window)

    def update(self, tile_cache0, marked_tile, _scanlineparameters):
        sprite_height = 16 if self.lcd.LCDC.sprite_height else 8
        for n in range(0, 0xA0, 4):
            # x = lcd.OAM[n]
            # y = lcd.OAM[n+1]
            t = self.lcd.OAM[n+2]
            # attributes = lcd.OAM[n+3]
            xx = ((n//4) * 8) % self.width
            yy = (((n//4) * 8) // self.width)*sprite_height
            self.copy_tile(tile_cache0, t, (xx, yy), self.buf0)
            if self.lcd.LCDC.sprite_height:
                self.copy_tile(tile_cache0, t+1, (xx, yy+8), self.buf0)

        self.draw_overlay(marked_tile, _scanlineparameters)

    def draw_overlay(self, marked_tile, _scanlineparameters):
        sprite_height = 16 if self.lcd.LCDC.sprite_height else 8
        # Mark selected tiles
        if marked_tile != NO_TILE:
            if self.lcd.LCDC.tiledata_select == 0:
                marked_tile += 256

            for n in range(0, 0xA0, 4):
                # x = lcd.OAM[n]
                # y = lcd.OAM[n+1]
                t = self.lcd.OAM[n+2]
                # attributes = lcd.OAM[n+3]
                # for t in range(TILES):
                if t == marked_tile:
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


class SpriteViewWindow(Window):

    def __init__(self, lcd, w, h, scale, title, pos=(sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED),
                 hide_window=False):
        super().__init__(lcd, w, h, scale, title, pos, hide_window)


class TileWindow(Window):

    def __init__(self, lcd, w, h, scale, title, pos=(sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED),
                 hide_window=False):
        super().__init__(lcd, w, h, scale, title, pos, hide_window)

    def update(self, tile_cache0, marked_tile, _scanlineparameters):

        for t in range(TILES):
            xx = (t * 8) % self.width
            yy = ((t * 8) // self.width)*8
            self.copy_tile(tile_cache0, t, (xx, yy), self.buf0)

        self.draw_overlay(marked_tile, _scanlineparameters)

    def draw_overlay(self, marked_tile, _scanlineparameters):
        sprite_height = 16 if self.lcd.LCDC.sprite_height else 8

        # Mark selected tiles
        if marked_tile != NO_TILE:
            if self.lcd.LCDC.tiledata_select == 0:
                marked_tile += 256

            for t in range(TILES):
                if t == marked_tile:
                    xx = (t * 8) % self.width
                    yy = ((t * 8) // self.width)*8
                    self.mark_tile(xx, yy, MARK2, width=sprite_height, height=8)

        self.mark_tile(self.mouse_hover_x, self.mouse_hover_y, HOVER, width=sprite_height, height=8)
        self.mark_tile(self.mouse_x, self.mouse_y, MARK, width=sprite_height, height=8)

    def _mouse(self, click, window_id, x, y):
        if click:
            tile_x, tile_y = x // 8, y // 8
            hor_limit = self.width // 8
            tile_index = tile_y * hor_limit + tile_x
            if self.lcd.LCDC.tiledata_select == 0:
                if tile_index < 128:
                    print("Index tile out of bounds, when using signed index")
                    return NO_TILE # Invalid index with tiledata select
                # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset
                if tile_index > 255:
                    tile_index -= 256
                tile_index = (tile_index ^ 0x80) - 128
                print(
                    f"Location: ({tile_x}, {tile_y})\nTile index: {tile_index}\n"
                    f"Memory area: 0x8800-0x97FF (signed index)"
                )
            else:
                if tile_index > 255:
                    print("Index tile out of bounds, when using unsigned index")
                    return NO_TILE # Invalid index with tiledata select
                print(
                    f"Location: ({tile_x}, {tile_y})\nTile index: {tile_index}\n"
                    f"Memory area: 0x8000-0x8FFF (unsigned index)"
                )
            return tile_index
        return NO_TILE


class TileViewWindow(Window):

    def __init__(self, lcd, w, h, scale, title, offset, pos=(sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED),
                 hide_window=False):
        super().__init__(lcd, w, h, scale, title, pos, hide_window)
        self.offset = offset

    def update(self, tile_cache0, marked_tile, _scanlineparameters, ix, iy):
        # ver_limit = 32

        for n in range(self.offset, self.offset + 0x400):
            tile_index = self.lcd.VRAM[n]

            # Check the tile source and add offset
            # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
            # BG & Window Tile Data Select   (0=8800-97FF, 1=8000-8FFF)
            if self.lcd.LCDC.tiledata_select == 0:
                # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset (reduces to + 128)
                tile_index = (tile_index ^ 0x80) + 128

            tile_column = (n-self.offset) % HOR_LIMIT # Horizontal tile number wrapping on 16
            tile_row = (n-self.offset) // HOR_LIMIT # Vertical time number based on tile_column

            des = (tile_column * 8, tile_row * 8)
            self.copy_tile(tile_cache0, tile_index, des, self.buf0)

        self.draw_overlay(marked_tile, _scanlineparameters, ix, iy)

    def draw_overlay(self, marked_tile, _scanlineparameters, ix, iy):
        # Mark screen area
        for y in range(GAMEBOY_RESOLUTION[1]):
            xx = _scanlineparameters[y][ix]
            yy = _scanlineparameters[y][iy]
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
                print(f"Location: ({tile_x}, {tile_y})\nTile index: {tile_index}\n"
                      f"Memory area: 0x8800-0x97FF (signed index)")
            else:
                print(f"Location: ({tile_x}, {tile_y})\nTile index: {tile_index}\n"
                      f"Memory area: 0x8000-0x8FFF (unsigned index)")
            return tile_index
        return NO_TILE


class DebugWindow(SDLWindow):
    def __init__(self, scale):
        super(self.__class__, self).__init__(scale)
        self.scale = scale
        self.marked_tile = NO_TILE

        self.tile1_update = True
        self.tile2_update = True
        self.sprite_update = True
        self.tile_update = True

        self.hide_window = True

    # def init(self, hide_window):
    #     self.hide_window = hide_window
    #     super(self.__class__, self).__init__(hide_window)

    # Rest of the __init__, when we have the lcd instance
    def set_lcd(self, lcd):
        self.lcd = lcd
        self.tile1 = TileViewWindow(lcd, 0x100, 0x100, self.scale, b"Tile View 1", 0x1800, (0, 0), self.hide_window)
        self.tile2 = TileViewWindow(lcd, 0x100, 0x100, self.scale, b"Tile View 2", 0x1C00, (0x100*self.scale, 0),
                                    self.hide_window)
        self.sprite = SpriteWindow(lcd, 8*10, 16*4, self.scale, b"Sprites", (0x200*self.scale, 0), self.hide_window)

        self.tile_data_width = 16*8 # Change the 16 to however wide you want the tile window
        self.tile_data_height = ((TILES*8) // self.tile_data_width)*8
        self.tile = TileWindow(lcd, self.tile_data_width, self.tile_data_height,
                               self.scale, b"Tile Data", (0x240*self.scale, 0), self.hide_window)

    def stop(self):
        self.tile.stop()
        self.tile1.stop()
        self.tile2.stop()
        self.sprite.stop()
        sdl2.SDL_Quit()

    def update_display(self, paused):
        if self.tile_update or not paused:
            self.tile.update(self._tilecache, self.marked_tile, self._scanlineparameters)
            self.tile.update_display(paused)

        if self.tile1_update or not paused:
            self.tile1.update(self._tilecache, self.marked_tile, self._scanlineparameters, 0, 1)
            self.tile1.update_display(paused)

        if self.tile2_update or not paused:
            self.tile2.update(self._tilecache, self.marked_tile, self._scanlineparameters, 2, 3)
            self.tile2.update_display(paused)

        if self.sprite_update or not paused:
            self.sprite.update(self._tilecache, self.marked_tile, self._scanlineparameters)
            self.sprite.update_display(paused)

        self.tile1_update = False
        self.tile2_update = False
        self.sprite_update = False
        self.tile_update = False

        if not paused:
            self._update_display()

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
                elif event.window.event == sdl2.SDL_WINDOWEVENT_LEAVE:
                    self.window_focus(event.window.windowID, False)
            else:
                click = event.type == sdl2.SDL_MOUSEBUTTONUP and event.button.button == sdl2.SDL_BUTTON_LEFT
                if ((0 <= event.motion.x < 2**16) and
                    (0 <= event.motion.y < 2**16) and
                        (0 <= event.motion.windowID < 2**16)):
                    self.mouse(click, event.motion.windowID, event.motion.x, event.motion.y)

        return events

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
            self.tile1_update = True
        elif window_id == sdl2.SDL_GetWindowID(self.tile2.window):
            mt = self.tile2.mouse(click, window_id, x, y)
            self.tile2_update = True
        elif window_id == sdl2.SDL_GetWindowID(self.sprite.window):
            mt = self.sprite.mouse(click, window_id, x, y)
            self.sprite_update = True
        elif window_id == sdl2.SDL_GetWindowID(self.tile.window):
            mt = self.tile.mouse(click, window_id, x, y)
            self.tile_update = True
        else: # Game window
            # TODO: Detect which sprites, tiles, etc. is below cursor and highlight in other views
            print(click, window_id, x, y)

        # Test if there is a new marked tile
        if mt != NO_TILE:
            self.tile1_update = True
            self.tile2_update = True
            self.sprite_update = True
            self.tile_update = True

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
#             if lcd.LCDC.sprite_height:
#                 self.copy_tile((tile_index * 8+8, 0), (i%self.sprite_width, (i/self.sprite_width)*16 + 8),
#                     lcd.sprite_cache_OBP0, self.sprite_buffer)


# Unfortunately CPython/PyPy code has to be hidden in an exec call to
# prevent Cython from trying to parse it. This block provides the
# functions that are otherwise implemented as inlined cdefs in the pxd
if not cythonmode:
    exec("""
def _update_display(self, paused):
    sdl2.SDL_UpdateTexture(self.sdl_texture_buffer, None, self.buf_p, self.width*4)
    sdl2.SDL_RenderCopy(self.sdlrenderer, self.sdl_texture_buffer, None, None)
    sdl2.SDL_RenderPresent(self.sdlrenderer)
    sdl2.SDL_RenderClear(self.sdlrenderer)

Window.update_display = _update_display
""", globals(), locals())
