#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import ctypes
from array import array

import sdl2
from pyboy.botsupport import constants, tilemap
from pyboy.botsupport.sprite import Sprite
from pyboy.plugins.base_plugin import PyBoyWindowPlugin
from pyboy.plugins.window_sdl2 import sdl2_event_pump
from pyboy.utils import WindowEvent
from pyboy.logger import logger


try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False

# Mask colors:
COLOR = 0x00000000
# MASK = 0x00C0C000
COLOR_BACKGROUND = 0x00C0C000
COLOR_WINDOW = 0xC179D400

# Additive colors
HOVER = 0xFF0000
mark_counter = 0
# By using a set, we avoid duplicates
marked_tiles = set([])
MARK = array("I", [0xFF000000, 0xFFC00000, 0xFFFC0000, 0x00FFFF00, 0xFF00FF00])

SPRITE_BACKGROUND = COLOR_BACKGROUND


class MarkedTile:
    def __init__(
        self,
        event=WindowEvent._INTERNAL_MARK_TILE,
        tile_identifier=-1,
        mark_id="",
        mark_color=0,
        sprite_height=8,
        sprite=False
    ):
        self.tile_identifier = tile_identifier
        self.mark_id = mark_id
        self.mark_color = mark_color
        self.sprite_height = sprite_height
        if mark_id == "TILE":
            # TODO: Use __str__ of the Tile and Sprite classes
            logger.info(f"Marked Tile - identifier: {tile_identifier}")
        elif mark_id == "SPRITE":
            logger.info(f"Marked Sprite - tile identifier: {tile_identifier}, sprite height: {sprite_height}")
        else:
            logger.info(f"Marked {mark_id} - tile identifier: {tile_identifier}")

    def __hash__(self):
        return hash(self.tile_identifier)


class Debug(PyBoyWindowPlugin):
    argv = [("-d", "--debug", {"action": "store_true", "help": "Enable emulator debugging mode"})]

    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        self.sdl2_event_pump = self.pyboy_argv.get("window_type") != "SDL2"
        if self.sdl2_event_pump:
            sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

        # self.scale = 2
        window_pos = 0

        self.tile1 = TileViewWindow(
            pyboy,
            mb,
            pyboy_argv,
            scale=2,
            title="Background",
            width=256,
            height=256,
            pos_x=0,
            pos_y=0,
            window_map=False,
            scanline_x=0,
            scanline_y=1
        )
        window_pos += (256 * self.tile1.scale)

        self.tile2 = TileViewWindow(
            pyboy,
            mb,
            pyboy_argv,
            scale=2,
            title="Window",
            width=256,
            height=256,
            pos_x=window_pos,
            pos_y=0,
            window_map=True,
            scanline_x=2,
            scanline_y=3
        )
        window_pos += (256 * self.tile2.scale)

        self.spriteview = SpriteViewWindow(
            pyboy,
            mb,
            pyboy_argv,
            scale=2,
            title="Sprite View",
            width=constants.COLS,
            height=constants.ROWS,
            pos_x=window_pos,
            pos_y=0
        )

        self.sprite = SpriteWindow(
            pyboy,
            mb,
            pyboy_argv,
            scale=3,
            title="Sprite Data",
            width=8 * 10,
            height=16 * 4,
            pos_x=window_pos,
            pos_y=self.spriteview.height * 2 + 68
        )
        window_pos += (constants.COLS * self.spriteview.scale)

        tile_data_width = 16 * 8 # Change the 16 to however wide you want the tile window
        tile_data_height = ((constants.TILES * 8) // tile_data_width) * 8
        self.tiledata = TileDataWindow(
            pyboy,
            mb,
            pyboy_argv,
            scale=3,
            title="Tile Data",
            width=tile_data_width,
            height=tile_data_height,
            pos_x=window_pos,
            pos_y=0
        )

    def post_tick(self):
        self.tile1.post_tick()
        self.tile2.post_tick()
        self.tiledata.post_tick()
        self.sprite.post_tick()
        self.spriteview.post_tick()

    def handle_events(self, events):
        if self.sdl2_event_pump:
            events = sdl2_event_pump(events)
        events = self.tile1.handle_events(events)
        events = self.tile2.handle_events(events)
        events = self.tiledata.handle_events(events)
        events = self.sprite.handle_events(events)
        events = self.spriteview.handle_events(events)
        return events

    def stop(self):
        if self.sdl2_event_pump:
            sdl2.SDL_Quit()

    def enabled(self):
        return self.pyboy_argv.get("debug")


def make_buffer(w, h):
    buf = array("B", [0x55] * (w*h*4))
    if cythonmode:
        buf0 = memoryview(buf).cast("I", shape=(h, w))
        buf_p = None
    else:
        view = memoryview(buf).cast("I")
        buf0 = [view[i:i + w] for i in range(0, w * h, w)]
        buf_p = ctypes.c_void_p(buf.buffer_info()[0])
    return buf, buf0, buf_p


class BaseDebugWindow(PyBoyWindowPlugin):
    def __init__(self, pyboy, mb, pyboy_argv, *, scale, title, width, height, pos_x, pos_y):
        super().__init__(pyboy, mb, pyboy_argv)
        self.scale = scale
        self.width, self.height = width, height
        self.base_title = title
        self.hover_x = -1
        self.hover_y = -1

        self._window = sdl2.SDL_CreateWindow(
            self.base_title.encode("utf8"), pos_x, pos_y, width * scale, height * scale, sdl2.SDL_WINDOW_RESIZABLE
        )
        self.window_id = sdl2.SDL_GetWindowID(self._window)

        self.buf, self.buf0, self.buf_p = make_buffer(width, height)

        self._sdlrenderer = sdl2.SDL_CreateRenderer(self._window, -1, sdl2.SDL_RENDERER_ACCELERATED)
        self._sdltexturebuffer = sdl2.SDL_CreateTexture(
            self._sdlrenderer, sdl2.SDL_PIXELFORMAT_RGBA8888, sdl2.SDL_TEXTUREACCESS_STATIC, width, height
        )

    def handle_events(self, events):
        # Feed events into the loop
        for event in events:
            if event == WindowEvent._INTERNAL_MOUSE:
                if event.window_id == self.window_id:
                    self.hover_x = event.mouse_x // self.scale
                    self.hover_y = event.mouse_y // self.scale
                else:
                    self.hover_x = -1
                    self.hover_y = -1

        return events

    def stop(self):
        sdl2.SDL_DestroyWindow(self._window)

    def update_title(self):
        pass

    def post_tick(self):
        self.update_title()
        self._update_display()

    ##########################
    # Internal functions
    def copy_tile(self, tile_cache0, t, xx, yy, to_buffer):
        for y in range(8):
            for x in range(8):
                to_buffer[yy + y][xx + x] = tile_cache0[y + t*8][x]

    def mark_tile(self, x, y, color, height, width, grid):
        tw = width # Tile width
        th = height # Tile height
        if grid:
            xx = x - (x%tw)
            yy = y - (y%th)
        else:
            xx = x
            yy = y
        for i in range(th):
            if 0 <= (yy + i) < self.height and 0 <= xx < self.width:
                self.buf0[yy + i][xx] = color
        for i in range(tw):
            if 0 <= (yy) < self.height and 0 <= xx + i < self.width:
                self.buf0[yy][xx + i] = color
        for i in range(tw):
            if 0 <= (yy + th - 1) < self.height and 0 <= xx + i < self.width:
                self.buf0[yy + th - 1][xx + i] = color
        for i in range(th):
            if 0 <= (yy + i) < self.height and 0 <= xx + tw - 1 < self.width:
                self.buf0[yy + i][xx + tw - 1] = color


class TileViewWindow(BaseDebugWindow):
    def __init__(self, *args, window_map, scanline_x, scanline_y, **kwargs):
        super().__init__(*args, **kwargs)
        self.scanline_x, self.scanline_y = scanline_x, scanline_y
        self.color = COLOR_WINDOW if window_map else COLOR_BACKGROUND

        if not cythonmode:
            self.tilemap = tilemap.TileMap(self.mb, "WINDOW" if window_map else "BACKGROUND")

    def __cinit__(self, pyboy, mb, *args, window_map, **kwargs):
        self.tilemap = tilemap.TileMap(self.mb, "WINDOW" if window_map else "BACKGROUND")

    def post_tick(self):
        tile_cache0 = self.renderer._tilecache

        # Updating screen buffer by copying tiles from cache
        mem_offset = self.tilemap.map_offset - constants.VRAM_OFFSET
        for n in range(mem_offset, mem_offset + 0x400):
            tile_index = self.mb.lcd.VRAM[n]

            # Check the tile source and add offset
            # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
            # BG & Window Tile Data Select   (0=8800-97FF, 1=8000-8FFF)
            if self.mb.lcd.LCDC.tiledata_select == 0:
                # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset (reduces to + 128)
                tile_index = (tile_index ^ 0x80) + 128

            tile_column = (n-mem_offset) % 32
            tile_row = (n-mem_offset) // 32

            self.copy_tile(tile_cache0, tile_index, tile_column * 8, tile_row * 8, self.buf0)

        self.draw_overlay()
        BaseDebugWindow.post_tick(self)

    def handle_events(self, events):
        global mark_counter, marked_tiles

        self.tilemap.refresh_lcdc()

        # Feed events into the loop
        events = BaseDebugWindow.handle_events(self, events)
        for event in events:
            if event == WindowEvent._INTERNAL_MOUSE and event.window_id == self.window_id:
                if event.mouse_button == 0:
                    tile_x, tile_y = event.mouse_x // self.scale // 8, event.mouse_y // self.scale // 8
                    tile_identifier = self.tilemap.tile_identifier(tile_x, tile_y)
                    logger.info(f"Tile clicked on {tile_x}, {tile_y}")
                    marked_tiles.add(
                        MarkedTile(tile_identifier=tile_identifier, mark_id="TILE", mark_color=MARK[mark_counter])
                    )
                    mark_counter += 1
                    mark_counter %= len(MARK)
                elif event.mouse_button == 1:
                    marked_tiles.clear()
            elif event == WindowEvent._INTERNAL_MARK_TILE:
                marked_tiles.add(event.tile_identifier)

        return events

    def update_title(self):
        title = self.base_title
        title += " [HIGH MAP 0x9C00-0x9FFF]" if self.tilemap.map_offset == constants.HIGH_TILEMAP else \
            " [LOW MAP 0x9800-0x9BFF]"
        title += " [HIGH DATA (SIGNED) 0x8800-0x97FF]" if self.tilemap.signed_tile_data else \
            " [LOW DATA (UNSIGNED) 0x8000-0x8FFF]"
        if self.tilemap._select == "WINDOW":
            title += " [Window]"
        if self.tilemap._select == "BACKGROUND":
            title += " [Background]"
        sdl2.SDL_SetWindowTitle(self._window, title.encode("utf8"))

    def draw_overlay(self):
        global marked_tiles
        scanlineparameters = self.pyboy.botsupport_manager().screen().tilemap_position_list()

        # TODO: Refactor this
        # Mark screen area
        for y in range(constants.ROWS):
            xx = int(scanlineparameters[y][self.scanline_x])
            yy = int(scanlineparameters[y][self.scanline_y])

            if self.scanline_x == 0: # Background
                # Wraps around edges of the screen
                if y == 0 or y == constants.ROWS - 1: # Draw top/bottom bar
                    for x in range(constants.COLS):
                        self.buf0[(yy+y) % 0xFF][(xx+x) % 0xFF] = COLOR
                else: # Draw body
                    self.buf0[(yy+y) % 0xFF][xx % 0xFF] = COLOR
                    for x in range(constants.COLS):
                        self.buf0[(yy+y) % 0xFF][(xx+x) % 0xFF] &= self.color
                    self.buf0[(yy+y) % 0xFF][(xx + constants.COLS) % 0xFF] = COLOR
            else: # Window
                # Takes a cut of the screen
                xx = -xx
                yy = -yy
                if yy + y == 0 or y == constants.ROWS - 1: # Draw top/bottom bar
                    for x in range(constants.COLS):
                        if 0 <= xx + x < constants.COLS:
                            self.buf0[yy + y][xx + x] = COLOR
                else: # Draw body
                    if 0 <= yy + y:
                        self.buf0[yy + y][max(xx, 0)] = COLOR
                        for x in range(constants.COLS):
                            if 0 <= xx + x < constants.COLS:
                                self.buf0[yy + y][xx + x] &= self.color
                        self.buf0[yy + y][xx + constants.COLS] = COLOR

        # Mark selected tiles
        for t, match in zip(
            marked_tiles, self.tilemap.search_for_identifiers([m.tile_identifier for m in marked_tiles])
        ):
            for row, column in match:
                self.mark_tile(column * 8, row * 8, t.mark_color, 8, 8, True)
        if self.hover_x != -1:
            self.mark_tile(self.hover_x, self.hover_y, HOVER, 8, 8, True)


class TileDataWindow(BaseDebugWindow):
    def post_tick(self):
        tile_cache0 = self.renderer._tilecache

        for t in range(constants.TILES):
            xx = (t*8) % self.width
            yy = ((t*8) // self.width) * 8
            self.copy_tile(tile_cache0, t, xx, yy, self.buf0)

        self.draw_overlay()
        BaseDebugWindow.post_tick(self)

    def handle_events(self, events):
        global mark_counter, marked_tiles
        # Feed events into the loop
        events = BaseDebugWindow.handle_events(self, events)
        for event in events:
            if event == WindowEvent._INTERNAL_MOUSE and event.window_id == self.window_id:
                if event.mouse_button == 0:
                    tile_x, tile_y = event.mouse_x // self.scale // 8, event.mouse_y // self.scale // 8
                    tile_identifier = tile_y * (self.width // 8) + tile_x
                    marked_tiles.add(
                        MarkedTile(tile_identifier=tile_identifier, mark_id="TILE", mark_color=MARK[mark_counter])
                    )
                    mark_counter += 1
                    mark_counter %= len(MARK)
                elif event.mouse_button == 1:
                    marked_tiles.clear()
            elif event == WindowEvent._INTERNAL_MARK_TILE:
                marked_tiles.add(event.tile_identifier)
        return events

    def draw_overlay(self):
        # Mark selected tiles
        for t in marked_tiles:
            column = t.tile_identifier % (self.width // 8)
            row = t.tile_identifier // (self.width // 8)
            # Yes, we are using the height as width. This is because we present the tile data from left to right,
            # but the sprites with a height of 16, renders them stacked ontop of each other.
            self.mark_tile(column * 8, row * 8, t.mark_color, t.sprite_height, 8, True)


class SpriteWindow(BaseDebugWindow):
    def post_tick(self):
        tile_cache0 = self.renderer._tilecache

        sprite_height = 16 if self.mb.lcd.LCDC.sprite_height else 8
        for n in range(0, 0xA0, 4):
            # x = lcd.OAM[n]
            # y = lcd.OAM[n+1]
            t = self.mb.lcd.OAM[n + 2]
            # attributes = lcd.OAM[n+3]
            xx = ((n//4) * 8) % self.width
            yy = (((n//4) * 8) // self.width) * sprite_height
            self.copy_tile(tile_cache0, t, xx, yy, self.buf0)
            if sprite_height:
                self.copy_tile(tile_cache0, t + 1, xx, yy + 8, self.buf0)

        self.draw_overlay()
        BaseDebugWindow.post_tick(self)

    def handle_events(self, events):
        global mark_counter, marked_tiles

        # Feed events into the loop
        events = BaseDebugWindow.handle_events(self, events)

        sprite_height = 16 if self.mb.lcd.LCDC.sprite_height else 8
        for event in events:
            if event == WindowEvent._INTERNAL_MOUSE and event.window_id == self.window_id:
                if event.mouse_button == 0:
                    tile_x, tile_y = event.mouse_x // self.scale // 8, event.mouse_y // self.scale // sprite_height
                    sprite_identifier = tile_y * (self.width // 8) + tile_x
                    if sprite_identifier > constants.SPRITES:
                        # Out of bounds
                        continue
                    sprite = Sprite(self.mb, sprite_identifier)
                    marked_tiles.add(
                        MarkedTile(
                            tile_identifier=sprite.tile_identifier,
                            mark_id="SPRITE",
                            mark_color=MARK[mark_counter],
                            sprite_height=sprite_height,
                            sprite=True,
                        )
                    )
                    mark_counter += 1
                    mark_counter %= len(MARK)
                elif event.mouse_button == 1:
                    marked_tiles.clear()
            elif event == WindowEvent._INTERNAL_MARK_TILE:
                marked_tiles.add(event.tile_identifier)
        return events

    def draw_overlay(self):
        sprite_height = 16 if self.mb.lcd.LCDC.sprite_height else 8
        # Mark selected tiles
        for m, matched_sprites in zip(
            marked_tiles,
            self.pyboy.botsupport_manager().sprite_by_tile_identifier([m.tile_identifier for m in marked_tiles])
        ):
            for sprite_index in matched_sprites:
                xx = (sprite_index*8) % self.width
                yy = ((sprite_index*8) // self.width) * sprite_height
                self.mark_tile(xx, yy, m.mark_color, sprite_height, 8, True)

        if self.hover_x != -1:
            self.mark_tile(self.hover_x, self.hover_y, HOVER, sprite_height, 8, True)

    def update_title(self):
        title = self.base_title
        title += " [8x16]" if self.mb.lcd.LCDC.sprite_height else " [8x8]"
        sdl2.SDL_SetWindowTitle(self._window, title.encode("utf8"))


class SpriteViewWindow(BaseDebugWindow):
    def post_tick(self):
        for y in range(constants.ROWS):
            for x in range(constants.COLS):
                self.buf0[y][x] = SPRITE_BACKGROUND

        self.mb.renderer.render_sprites(self.mb.lcd, self.buf0, True)
        self.draw_overlay()
        BaseDebugWindow.post_tick(self)

    def draw_overlay(self):
        sprite_height = 16 if self.mb.lcd.LCDC.sprite_height else 8
        # Mark selected tiles
        for m, matched_sprites in zip(
            marked_tiles,
            self.pyboy.botsupport_manager().sprite_by_tile_identifier([m.tile_identifier for m in marked_tiles])
        ):
            for sprite_index in matched_sprites:
                sprite = Sprite(self.mb, sprite_index)
                self.mark_tile(sprite.x, sprite.y, m.mark_color, sprite_height, 8, False)

    def update_title(self):
        title = self.base_title
        title += " " if self.mb.lcd.LCDC.sprite_enable else " [Disabled]"
        sdl2.SDL_SetWindowTitle(self._window, title.encode("utf8"))


# Unfortunately CPython/PyPy code has to be hidden in an exec call to
# prevent Cython from trying to parse it. This block provides the
# functions that are otherwise implemented as inlined cdefs in the pxd
if not cythonmode:
    exec(
        """
def _update_display(self):
    sdl2.SDL_UpdateTexture(self._sdltexturebuffer, None, self.buf_p, self.width*4)
    sdl2.SDL_RenderCopy(self._sdlrenderer, self._sdltexturebuffer, None, None)
    sdl2.SDL_RenderPresent(self._sdlrenderer)
    sdl2.SDL_RenderClear(self._sdlrenderer)

BaseDebugWindow._update_display = _update_display
""", globals(), locals()
    )
