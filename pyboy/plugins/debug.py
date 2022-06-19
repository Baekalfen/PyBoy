#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import logging
import os
import re
import zlib
from array import array
from base64 import b64decode
from ctypes import c_void_p

from pyboy.botsupport import constants, tilemap
from pyboy.botsupport.sprite import Sprite
from pyboy.logger import logger
from pyboy.plugins.base_plugin import PyBoyWindowPlugin
from pyboy.plugins.window_sdl2 import sdl2_event_pump
from pyboy.utils import WindowEvent

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False

try:
    import sdl2
except ImportError:
    sdl2 = None

logger = logging.getLogger(__name__)

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
    argv = [("-d", "--debug", {
        "action": "store_true",
        "help": "Enable emulator debugging mode"
    }), ("--breakpoints", {
        "type": str,
        "help": "Add breakpoints on start-up (internal use)"
    })]

    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        self.cgb = mb.cgb

        self.rom_symbols = {}
        if pyboy_argv.get("ROM"):
            gamerom_file_no_ext, rom_ext = os.path.splitext(pyboy_argv.get("ROM"))
            for sym_ext in [".sym", rom_ext + ".sym"]:
                sym_path = gamerom_file_no_ext + sym_ext
                if os.path.isfile(sym_path):
                    with open(sym_path) as f:
                        for _line in f.readlines():
                            line = _line.strip()
                            if line == "":
                                continue
                            elif line.startswith(";"):
                                continue
                            elif line.startswith("["):
                                # Start of key group
                                # [labels]
                                # [definitions]
                                continue

                            try:
                                bank, addr, sym_label = re.split(":| ", line.strip())
                                bank = int(bank, 16)
                                addr = int(addr, 16)
                                if not bank in self.rom_symbols:
                                    self.rom_symbols[bank] = {}

                                self.rom_symbols[bank][addr] = sym_label
                            except ValueError as ex:
                                logger.warning(f"Skipping .sym line: {line.strip()}")

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

        self.memory = MemoryWindow(
            pyboy, mb, pyboy_argv, scale=1, title="Memory", width=8 * 60, height=16 * 36, pos_x=window_pos, pos_y=0
        )
        window_pos += 8 * 60

        window_pos = 0
        tile_data_width = 16 * 8 # Change the 16 to however wide you want the tile window
        tile_data_height = ((constants.TILES * 8) // tile_data_width) * 8
        self.tiledata0 = TileDataWindow(
            pyboy,
            mb,
            pyboy_argv,
            scale=3,
            title="Tile Data0",
            width=tile_data_width,
            height=tile_data_height,
            pos_x=window_pos,
            pos_y=(256 * self.tile1.scale) + 128
        )
        if self.cgb:
            window_pos += 512
            self.tiledata1 = TileDataWindow(
                pyboy,
                mb,
                pyboy_argv,
                scale=3,
                title="Tile Data1",
                width=tile_data_width,
                height=tile_data_height,
                pos_x=window_pos,
                pos_y=(256 * self.tile1.scale) + 128
            )

        for _b in (self.pyboy_argv.get("breakpoints") or "").split(","):
            b = _b.strip()
            if b == "":
                continue

            bank_addr = self.parse_bank_addr_sym_label(b)
            if bank_addr is None:
                logger.error(f"Couldn't parse address or label: {b}")
            else:
                self.mb.add_breakpoint(*bank_addr)
                logger.info(f"Added breakpoint for address or label: {b}")

    def post_tick(self):
        self.tile1.post_tick()
        self.tile2.post_tick()
        self.tiledata0.post_tick()
        if self.cgb:
            self.tiledata1.post_tick()
        self.sprite.post_tick()
        self.spriteview.post_tick()
        self.memory.post_tick()

    def handle_events(self, events):
        if self.sdl2_event_pump:
            events = sdl2_event_pump(events)
        events = self.tile1.handle_events(events)
        events = self.tile2.handle_events(events)
        events = self.tiledata0.handle_events(events)
        if self.cgb:
            events = self.tiledata1.handle_events(events)
        events = self.sprite.handle_events(events)
        events = self.spriteview.handle_events(events)
        events = self.memory.handle_events(events)
        return events

    def stop(self):
        if self.sdl2_event_pump:
            sdl2.SDL_Quit()

    def enabled(self):
        if self.pyboy_argv.get("debug"):
            if not sdl2:
                logger.error("Failed to import sdl2, needed for debug window")
                return False
            else:
                return True
        else:
            return False

    def parse_bank_addr_sym_label(self, command):
        if ":" in command:
            bank, addr = command.split(":")
            bank = int(bank, 16)
            addr = int(addr, 16)
            return bank, addr
        else:
            for bank, addresses in self.rom_symbols.items():
                for addr, label in addresses.items():
                    if label == command:
                        return bank, addr
        return None

    def handle_breakpoint(self):
        while True:
            self.post_tick()

            if self.mb.cpu.PC < 0x4000:
                bank = 0
            else:
                bank = self.mb.cartridge.rombank_selected
            sym_label = self.rom_symbols.get(bank, {}).get(self.mb.cpu.PC, "")

            print(self.mb.cpu.dump_state(sym_label))
            cmd = input()

            if cmd == "c" or cmd.startswith("c "):
                # continue
                if cmd.startswith("c "):
                    _, command = cmd.split(" ", 1)
                    bank_addr = self.parse_bank_addr_sym_label(command)
                    if bank_addr is None:
                        print("Couldn't parse address or label!")
                    else:
                        # TODO: Possibly add a counter of 1, and remove the breakpoint after hitting it the first time
                        self.mb.add_breakpoint(*bank_addr)
                        break
                else:
                    break
            elif cmd == "sl":
                for bank, addresses in self.rom_symbols.items():
                    for addr, label in addresses.items():
                        print(f"{bank:02X}:{addr:04X} {label}")
            elif cmd == "bl":
                for bank, addr in self.mb.breakpoints_list:
                    print(f"{bank:02X}:{addr:04X} {self.rom_symbols.get(bank, {}).get(addr, '')}")
            elif cmd == "b" or cmd.startswith("b "):
                if cmd.startswith("b "):
                    _, command = cmd.split(" ", 1)
                else:
                    command = input(
                        'Write address in the format of "00:0150" or search for a symbol label like "Main"\n'
                    )

                bank_addr = self.parse_bank_addr_sym_label(command)
                if bank_addr is None:
                    print("Couldn't parse address or label!")
                else:
                    self.mb.add_breakpoint(*bank_addr)

            elif cmd == "d":
                # Remove current breakpoint

                # TODO: Share this code with breakpoint_reached
                for i, (bank, pc) in enumerate(self.mb.breakpoints_list):
                    if self.mb.cpu.PC == pc and (
                        (pc < 0x4000 and bank == 0 and not self.mb.bootrom_enabled) or \
                        (0x4000 <= pc < 0x8000 and self.mb.cartridge.rombank_selected == bank) or \
                        (0xA000 <= pc < 0xC000 and self.mb.cartridge.rambank_selected == bank) or \
                        (pc < 0x100 and bank == -1 and self.mb.bootrom_enabled)
                    ):
                        break
                else:
                    print("Breakpoint couldn't be deleted for current PC. Not Found.")
                    continue
                print(f"Removing breakpoint: {bank}:{pc}")
                self.mb.remove_breakpoint(i)
            elif cmd == "pdb":
                # Start pdb
                import pdb
                pdb.set_trace()
                break
            else:
                # Step once
                self.mb.breakpoint_latch = 1
                self.mb.tick()


def make_buffer(w, h):
    buf = array("B", [0x55] * (w*h*4))
    if cythonmode:
        buf0 = memoryview(buf).cast("I", shape=(h, w))
    else:
        view = memoryview(buf).cast("I")
        buf0 = [view[i:i + w] for i in range(0, w * h, w)]
    buf_p = c_void_p(buf.buffer_info()[0])
    return buf, buf0, buf_p


class BaseDebugWindow(PyBoyWindowPlugin):
    def __init__(self, pyboy, mb, pyboy_argv, *, scale, title, width, height, pos_x, pos_y):
        super().__init__(pyboy, mb, pyboy_argv)
        self.cgb = mb.cgb
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
        sdl2.SDL_RenderSetLogicalSize(self._sdlrenderer, width, height)
        self._sdltexturebuffer = sdl2.SDL_CreateTexture(
            self._sdlrenderer, sdl2.SDL_PIXELFORMAT_RGBA8888, sdl2.SDL_TEXTUREACCESS_STATIC, width, height
        )

    def handle_events(self, events):
        # Feed events into the loop
        for event in events:
            if event == WindowEvent._INTERNAL_MOUSE:
                if event.window_id == self.window_id:
                    self.hover_x = event.mouse_x
                    self.hover_y = event.mouse_y
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
        sdl2.SDL_UpdateTexture(self._sdltexturebuffer, None, self.buf_p, self.width * 4)
        sdl2.SDL_RenderCopy(self._sdlrenderer, self._sdltexturebuffer, None, None)
        sdl2.SDL_RenderPresent(self._sdlrenderer)
        sdl2.SDL_RenderClear(self._sdlrenderer)

    ##########################
    # Internal functions
    def copy_tile(self, from_buffer, t, xx, yy, to_buffer, hflip, vflip, palette):
        for y in range(8):
            _y = 7 - y if vflip else y
            for x in range(8):
                _x = 7 - x if hflip else x
                to_buffer[yy + y][xx + x] = palette[from_buffer[_y + t*8][_x]]

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
        # Updating screen buffer by copying tiles from cache
        mem_offset = self.tilemap.map_offset - constants.VRAM_OFFSET
        for n in range(mem_offset, mem_offset + 0x400):
            tile_index = self.mb.lcd.VRAM0[n]

            # Check the tile source and add offset
            # http://problemkaputt.de/pandocs.htm#lcdcontrolregister
            # BG & Window Tile Data Select   (0=8800-97FF, 1=8000-8FFF)
            if self.mb.lcd._LCDC.tiledata_select == 0:
                # (x ^ 0x80 - 128) to convert to signed, then add 256 for offset (reduces to + 128)
                tile_index = (tile_index ^ 0x80) + 128

            tile_column = (n-mem_offset) % 32
            tile_row = (n-mem_offset) // 32

            # tilecache = None
            # palette_rgb = None
            if self.cgb:
                palette, vbank, horiflip, vertflip, bg_priority = self.renderer._cgb_get_background_map_attributes(
                    self.mb.lcd, n
                )
                self.renderer.update_tilecache1(self.mb.lcd, tile_index, 1)
                self.tilecache = (self.renderer._tilecache1 if vbank else self.renderer._tilecache0)
                self.palette_rgb = self.mb.lcd.ocpd.palette_mem_rgb # TODO: Select palette by adding offset
            else:
                # Fake palette index
                palette = 0
                self.renderer.update_tilecache0(self.mb.lcd, tile_index, 0)
                self.tilecache = self.renderer._tilecache0
                horiflip, vertflip = False, False
                self.palette_rgb = self.mb.lcd.BGP.palette_mem_rgb

            self.copy_tile(
                self.tilecache, tile_index, tile_column * 8, tile_row * 8, self.buf0, horiflip, vertflip,
                self.palette_rgb
            )

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
                    tile_x, tile_y = event.mouse_x // 8, event.mouse_y // 8
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

        background_view = self.scanline_x == 0

        # TODO: Refactor this
        # Mark screen area
        for y in range(constants.ROWS):
            xx = int(scanlineparameters[y][self.scanline_x])
            yy = int(scanlineparameters[y][self.scanline_y])

            if background_view: # Background
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

        # Mark current scanline directly from LY,SCX,SCY,WX,WY
        if background_view:
            for x in range(constants.COLS):
                self.buf0[(self.mb.lcd.SCY + self.mb.lcd.LY) % 0xFF][(self.mb.lcd.SCX + x) % 0xFF] = 0xFF00CE12
        else:
            for x in range(constants.COLS):
                self.buf0[(self.mb.lcd.WY + self.mb.lcd.LY) % 0xFF][(self.mb.lcd.WX + x) % 0xFF] = 0xFF00CE12


class TileDataWindow(BaseDebugWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tilecache_select = 0 if "0" in kwargs.get("title") else 1

    def post_tick(self):
        # TODO: We could select different palettes on CGB
        if self.tilecache_select:
            tilecache = self.renderer._tilecache1
        else:
            tilecache = self.renderer._tilecache0

        if self.cgb:
            self.palette_rgb = self.mb.lcd.bcpd.palette_mem_rgb # TODO: Select palette by adding offset
        else:
            self.palette_rgb = self.mb.lcd.BGP.palette_mem_rgb

        for t in range(constants.TILES):
            if self.tilecache_select:
                self.renderer.update_tilecache1(self.mb.lcd, t, 1)
            else:
                self.renderer.update_tilecache0(self.mb.lcd, t, 0)
            xx = (t*8) % self.width
            yy = ((t*8) // self.width) * 8
            self.copy_tile(tilecache, t, xx, yy, self.buf0, False, False, self.palette_rgb)

        self.draw_overlay()
        BaseDebugWindow.post_tick(self)

    def handle_events(self, events):
        global mark_counter, marked_tiles
        # Feed events into the loop
        events = BaseDebugWindow.handle_events(self, events)
        for event in events:
            if event == WindowEvent._INTERNAL_MOUSE and event.window_id == self.window_id:
                if event.mouse_button == 0:
                    tile_x, tile_y = event.mouse_x // 8, event.mouse_y // 8
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

        # TODO: Could we use scanline_sprites with modified arguments to render all of this?
        sprite_height = 16 if self.mb.lcd._LCDC.sprite_height else 8
        for n in range(0, 0xA0, 4):
            # x = lcd.OAM[n]
            # y = lcd.OAM[n+1]
            t = self.mb.lcd.OAM[n + 2]
            attributes = self.mb.lcd.OAM[n + 3]
            xx = ((n//4) * 8) % self.width
            yy = (((n//4) * 8) // self.width) * sprite_height

            if self.cgb:
                palette = attributes & 0b111
                if attributes & 0b1000:
                    self.renderer.update_spritecache1(self.mb.lcd, t, 1)
                    if self.mb.lcd._LCDC.sprite_height:
                        self.renderer.update_spritecache1(self.mb.lcd, t + 1, 1)
                    self.spritecache = self.renderer._spritecache1
                else:
                    self.renderer.update_spritecache0(self.mb.lcd, t, 0)
                    if self.mb.lcd._LCDC.sprite_height:
                        self.renderer.update_spritecache0(self.mb.lcd, t + 1, 0)
                    self.spritecache = self.renderer._spritecache0
                self.palette_rgb = self.mb.lcd.ocpd.palette_mem_rgb # TODO: Select palette by adding offset
            else:
                # Fake palette index
                palette = 0
                if attributes & 0b10000:
                    self.renderer.update_spritecache1(self.mb.lcd, t, 0)
                    if self.mb.lcd._LCDC.sprite_height:
                        self.renderer.update_spritecache1(self.mb.lcd, t + 1, 0)
                    self.spritecache = self.renderer._spritecache1
                    self.palette_rgb = self.mb.lcd.OBP1.palette_mem_rgb
                else:
                    self.renderer.update_spritecache0(self.mb.lcd, t, 0)
                    if self.mb.lcd._LCDC.sprite_height:
                        self.renderer.update_spritecache0(self.mb.lcd, t + 1, 0)
                    self.spritecache = self.renderer._spritecache0
                    self.palette_rgb = self.mb.lcd.OBP0.palette_mem_rgb

            self.copy_tile(self.spritecache, t, xx, yy, self.buf0, False, False, self.palette_rgb)
            if sprite_height:
                self.copy_tile(self.spritecache, t + 1, xx, yy + 8, self.buf0, False, False, self.palette_rgb)

        self.draw_overlay()
        BaseDebugWindow.post_tick(self)

    def handle_events(self, events):
        global mark_counter, marked_tiles

        # Feed events into the loop
        events = BaseDebugWindow.handle_events(self, events)

        sprite_height = 16 if self.mb.lcd._LCDC.sprite_height else 8
        for event in events:
            if event == WindowEvent._INTERNAL_MOUSE and event.window_id == self.window_id:
                if event.mouse_button == 0:
                    tile_x, tile_y = event.mouse_x // 8, event.mouse_y // sprite_height
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
        sprite_height = 16 if self.mb.lcd._LCDC.sprite_height else 8
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
        title += " [8x16]" if self.mb.lcd._LCDC.sprite_height else " [8x8]"
        sdl2.SDL_SetWindowTitle(self._window, title.encode("utf8"))


class SpriteViewWindow(BaseDebugWindow):
    def post_tick(self):
        for y in range(constants.ROWS):
            for x in range(constants.COLS):
                self.buf0[y][x] = SPRITE_BACKGROUND

        for ly in range(144):
            self.mb.lcd.renderer.scanline_sprites(self.mb.lcd, ly, self.buf0, True)

        self.draw_overlay()
        BaseDebugWindow.post_tick(self)

    def draw_overlay(self):
        sprite_height = 16 if self.mb.lcd._LCDC.sprite_height else 8
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
        title += " " if self.mb.lcd._LCDC.sprite_enable else " [Disabled]"
        sdl2.SDL_SetWindowTitle(self._window, title.encode("utf8"))


class MemoryWindow(BaseDebugWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.NCOLS = 60
        self.NROWS = 36
        self.shift_down = False
        self.start_address = 0x0000
        self.bg_color = [0xFF, 0xFF, 0xFF]
        self.fg_color = [0x00, 0x00, 0x00]

        self._text_buffer_raw = array("B", [0x20] * (self.NROWS * self.NCOLS))
        if cythonmode:
            self.text_buffer = memoryview(self._text_buffer_raw).cast("B", shape=(self.NROWS, self.NCOLS))
        else:
            view = memoryview(self._text_buffer_raw)
            self.text_buffer = [view[i:i + self.NCOLS] for i in range(0, self.NROWS * self.NCOLS, self.NCOLS)]
        # self.text_buffer = [bytearray([0x20]*self.NCOLS) for _ in range(self.NROWS)]
        self.write_border()
        self.write_addresses()

        font_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "font.txt")
        with open(font_path) as font_file:
            font_lines = font_file.readlines()
        font_blob = "".join(line.strip() for line in font_lines[font_lines.index("BASE64DATA:\n") + 1:])
        font_bytes = zlib.decompress(b64decode(font_blob.encode()))

        self.fbuf, self.fbuf0, self.fbuf_p = make_buffer(8, 16 * 256)
        for y, b in enumerate(font_bytes):
            for x in range(8):
                self.fbuf0[y][x] = 0xFFFFFFFF if ((0x80 >> x) & b) else 0x00000000

        self.font_texture = sdl2.SDL_CreateTexture(
            self._sdlrenderer, sdl2.SDL_PIXELFORMAT_RGBA32, sdl2.SDL_TEXTUREACCESS_STATIC, 8, 16 * 256
        )

        sdl2.SDL_UpdateTexture(self.font_texture, None, self.fbuf_p, 4 * 8)
        sdl2.SDL_SetTextureBlendMode(self.font_texture, sdl2.SDL_BLENDMODE_BLEND)
        sdl2.SDL_SetTextureColorMod(self.font_texture, *self.fg_color)
        sdl2.SDL_SetRenderDrawColor(self._sdlrenderer, *self.bg_color, 0xFF)

        # Persistent to make Cython happy...
        self.src = sdl2.SDL_Rect(0, 0, 8, 16)
        self.dst = sdl2.SDL_Rect(0, 0, 8, 16)

    def write_border(self):
        for x in range(self.NCOLS):
            self.text_buffer[0][x] = 0xCD
            self.text_buffer[2][x] = 0xCD
            self.text_buffer[self.NROWS - 1][x] = 0xCD

        for y in range(3, self.NROWS):
            self.text_buffer[y][0] = 0xBA
            self.text_buffer[y][9] = 0xB3
            self.text_buffer[y][self.NCOLS - 1] = 0xBA

        self.text_buffer[0][0] = 0xC9
        self.text_buffer[1][0] = 0xBA
        self.text_buffer[0][self.NCOLS - 1] = 0xBB
        self.text_buffer[1][self.NCOLS - 1] = 0xBA

        self.text_buffer[2][0] = 0xCC
        self.text_buffer[2][9] = 0xD1
        self.text_buffer[2][self.NCOLS - 1] = 0xB9

        self.text_buffer[self.NROWS - 1][0] = 0xC8
        self.text_buffer[self.NROWS - 1][9] = 0xCF
        self.text_buffer[self.NROWS - 1][self.NCOLS - 1] = 0xBC

    def write_addresses(self):
        header = (f"Memory from 0x{self.start_address:04X} " f"to 0x{self.start_address+0x3FF:04X}").encode("cp437")
        if cythonmode:
            for x in range(28):
                self.text_buffer[1][x + 2] = header[x]
        else:
            self.text_buffer[1][2:30] = header
        for y in range(32):
            addr = f"0x{self.start_address + (0x20*y):04X}".encode("cp437")
            if cythonmode:
                for x in range(6):
                    self.text_buffer[y + 3][x + 2] = addr[x]
            else:
                self.text_buffer[y + 3][2:8] = addr

    def write_memory(self):
        for y in range(32):
            for x in range(16):
                mem = self.mb.getitem(self.start_address + 16*y + x)
                if cythonmode:
                    a = hex(mem)[2:].zfill(2).encode("cp437")
                    self.text_buffer[y + 3][3*x + 11] = a[0]
                    self.text_buffer[y + 3][3*x + 12] = a[1]
                else:
                    self.text_buffer[y + 3][3*x + 11:3*x + 13] = bytes([mem]).hex().encode("cp437")

    def render_text(self):
        for y in range(self.NROWS):
            self.draw_text(0, 16 * y, self.text_buffer[y])

    def draw_text(self, x, y, text):
        self.dst.x = x
        self.dst.y = y
        for i, c in enumerate(text):
            if not 0 <= c < 256:
                logger.warn(f"Invalid character {c} in {bytes(text).decode('cp437')}") # This may error too...
                c = 0
            self.src.y = 16 * c
            if self.dst.x > self.width - 8:
                logger.warn(f"Text overrun while printing {bytes(text).decode('cp437')}")
                break
            sdl2.SDL_RenderCopy(self._sdlrenderer, self.font_texture, self.src, self.dst)
            self.dst.x += 8

    def post_tick(self):
        sdl2.SDL_RenderClear(self._sdlrenderer)
        self.write_memory()
        self.render_text()
        sdl2.SDL_RenderPresent(self._sdlrenderer)

    def _scroll_view(self, movement):
        self.start_address += movement
        self.start_address = max(0, min(self.start_address, 0x10000 - 0x400))
        # if self.start_address + 0x400 > 0x10000:
        #     self.start_address = 0x10000 - 0x400
        # if self.start_address < 0:
        #     self.start_address = 0
        self.write_addresses()

    def handle_events(self, events):
        events = BaseDebugWindow.handle_events(self, events)

        for event in events:
            # j - Next 256 bytes
            if event == WindowEvent.DEBUG_MEMORY_SCROLL_DOWN:
                if self.shift_down:
                    self._scroll_view(0x1000)
                else:
                    self._scroll_view(0x100)
            # k - Last 256 bytes
            elif event == WindowEvent.DEBUG_MEMORY_SCROLL_UP:
                if self.shift_down:
                    self._scroll_view(-0x1000)
                else:
                    self._scroll_view(-0x100)
            # shift tracking
            elif event == WindowEvent.MOD_SHIFT_ON:
                self.shift_down = True
            elif event == WindowEvent.MOD_SHIFT_OFF:
                self.shift_down = False
            elif event == WindowEvent._INTERNAL_MOUSE:
                # Scrolling
                if event.window_id == self.window_id and event.mouse_x == -1 and event.mouse_y == -1:
                    self._scroll_view(event.mouse_scroll_y * -0x100)

        return events
