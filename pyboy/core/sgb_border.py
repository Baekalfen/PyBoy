#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""
SGB Border rendering module.

Renders SGB borders around the Game Boy screen. The SGB border uses
4bpp SNES tiles (4 bitplanes, 32 bytes per tile), a 32x28 tile map
(only 28 rows of the 32x32 map are used for the 256x224 border),
and 4 palettes of 16 colors each in RGB555 format.
"""

from array import array

import pyboy

logger = pyboy.logging.get_logger(__name__)

SGB_SCREEN_WIDTH = 256
SGB_SCREEN_HEIGHT = 224
GB_SCREEN_X = 48
GB_SCREEN_Y = 40
GB_SCREEN_WIDTH = 160
GB_SCREEN_HEIGHT = 144


class SGBBorderRenderer:
    """Renders SGB borders around the Game Boy screen."""

    def __init__(self, sgb_module):
        self.sgb = sgb_module
        # Border buffer (RGBA, 256x224)
        self.border_buffer = array("B", [0] * (SGB_SCREEN_WIDTH * SGB_SCREEN_HEIGHT * 4))
        # Tile cache: 256 tiles * 8x8 * 1 byte (color index 0-15)
        self.border_tile_cache = array("B", [0] * (256 * 8 * 8))
        # Pre-allocated composited frame buffer
        self._composited = array("B", [0] * (SGB_SCREEN_WIDTH * SGB_SCREEN_HEIGHT * 4))
        # Frozen frame for MASK_FREEZE mode
        self._frozen_frame = None
        self.border_dirty = True
        self.tiles_dirty = True
        self.palettes_dirty = True
        self._border_copied = False
        self._prev_mask_mode = 0
        # Palettes as RGBA: 4 palettes * 16 colors * 4 bytes
        self.palettes_rgba = array("B", [0] * (4 * 16 * 4))

    def reset(self):
        self.border_buffer = array("B", [0] * (SGB_SCREEN_WIDTH * SGB_SCREEN_HEIGHT * 4))
        self.border_tile_cache = array("B", [0] * (256 * 8 * 8))
        self._composited = array("B", [0] * (SGB_SCREEN_WIDTH * SGB_SCREEN_HEIGHT * 4))
        self._frozen_frame = None
        self.border_dirty = True
        self.tiles_dirty = True
        self.palettes_dirty = True
        self._border_copied = False
        self._prev_mask_mode = 0
        self.palettes_rgba = array("B", [0] * (4 * 16 * 4))

    def update(self):
        """Rebuild the border buffer if data has changed."""
        if not self.sgb.enabled or not self.sgb.state.border_enabled:
            return

        border_tiles, border_map, border_palettes = self.sgb.get_border_data()
        if border_tiles is None or border_map is None or border_palettes is None:
            return

        if self.sgb.state.border_data_changed:
            self.sgb.state.border_data_changed = False
            self.palettes_dirty = True
            self.tiles_dirty = True
            self.border_dirty = True

        if self.palettes_dirty:
            self.update_palettes(border_palettes)
            self.palettes_dirty = False
            self.tiles_dirty = True
            self.border_dirty = True

        if self.tiles_dirty:
            self.update_tiles(border_tiles)
            self.tiles_dirty = False
            self.border_dirty = True

        if self.border_dirty:
            self.render_border(border_map)
            # Keep border_dirty True so get_composited_frame knows to copy

    def update_palettes(self, palette_data):
        """Convert 4 palettes of 16 colors from RGB555 to RGBA."""
        if palette_data is None:
            return
        for pal in range(4):
            for color in range(16):
                idx = (pal * 16 + color) * 2
                if idx + 1 < len(palette_data):
                    rgb555 = palette_data[idx] | (palette_data[idx + 1] << 8)
                    r = (rgb555 & 0x1F) * 255 // 31
                    g = ((rgb555 >> 5) & 0x1F) * 255 // 31
                    b = ((rgb555 >> 10) & 0x1F) * 255 // 31
                    rgba_idx = (pal * 16 + color) * 4
                    self.palettes_rgba[rgba_idx] = r
                    self.palettes_rgba[rgba_idx + 1] = g
                    self.palettes_rgba[rgba_idx + 2] = b
                    self.palettes_rgba[rgba_idx + 3] = 0xFF

    def update_tiles(self, tile_data):
        """Convert 4bpp border tiles to color index cache.

        Each border tile is 32 bytes (4 bitplanes). A pixel row spans
        two byte pairs: the first holds bitplanes 0-1, the second pair
        (16 bytes further into the tile) holds bitplanes 2-3. The four
        plane bits combine into the 4-bit palette index of each pixel,
        stored here as one byte per pixel. Palette lookup happens in
        render_border.
        """
        if tile_data is None:
            return

        cache = self.border_tile_cache
        for tile_num in range(256):
            tile_base = tile_num * 32
            if tile_base + 31 >= len(tile_data):
                continue
            cache_base = tile_num * 64  # 8x8 = 64 bytes
            for row in range(8):
                row_base = tile_base + row * 2
                plane0 = tile_data[row_base]
                plane1 = tile_data[row_base + 1]
                plane2 = tile_data[row_base + 16]
                plane3 = tile_data[row_base + 17]
                cache_row = cache_base + row * 8
                for x in range(8):
                    shift = 7 - x
                    cache[cache_row + x] = (
                        ((plane0 >> shift) & 1)
                        | (((plane1 >> shift) & 1) << 1)
                        | (((plane2 >> shift) & 1) << 2)
                        | (((plane3 >> shift) & 1) << 3)
                    )

    def render_border(self, map_data):
        """Paint the border map into the RGBA border buffer.

        The map is 32x32 entries; the top 28 rows cover the 256x224
        border. Each 16-bit little-endian entry picks one of 256 tiles,
        one of four palettes and optional X/Y mirroring. Bits 8-9 are
        unused, and entries that set them are skipped. Color 0 is
        transparent: inside the Game Boy window it is left untouched so
        the game shows through; elsewhere it is painted with the game's
        backdrop color.
        """
        if map_data is None:
            return

        # Clear border buffer
        composited_mv = memoryview(self.border_buffer)
        composited_mv[:] = b"\x00" * len(composited_mv)

        # The Game Boy window covers map columns 6-25 and rows 5-22
        for map_row in range(28):
            for map_col in range(32):
                offset = (map_row * 32 + map_col) * 2
                if offset + 1 >= len(map_data):
                    continue

                entry = map_data[offset] | (map_data[offset + 1] << 8)
                if entry & 0x0300:
                    continue

                in_window = 6 <= map_col < 26 and 5 <= map_row < 23
                self._blit_tile(
                    map_col * 8,
                    map_row * 8,
                    entry & 0xFF,
                    (entry >> 10) & 3,
                    entry & 0x4000,
                    entry & 0x8000,
                    in_window,
                )

    def _blit_tile(self, dst_x, dst_y, tile_num, palette_num, mirror_x, mirror_y, in_window):
        """Draw one 8x8 border tile into the border buffer.

        Color 0 is transparent: skipped inside the Game Boy window,
        painted with the game's backdrop color elsewhere.
        """
        tiles = self.border_tile_cache
        palettes = self.palettes_rgba
        buffer = self.border_buffer

        # The game supplies the backdrop colour used by transparent border pixels.
        bg_color = self.sgb.state.bg_color_0
        backdrop = (bg_color & 0xFF, (bg_color >> 8) & 0xFF, (bg_color >> 16) & 0xFF)

        tile_base = tile_num * 64
        palette_base = palette_num * 16 * 4

        for ty in range(8):
            src_y = 7 - ty if mirror_y else ty
            dst_row = (dst_y + ty) * SGB_SCREEN_WIDTH
            for tx in range(8):
                src_x = 7 - tx if mirror_x else tx
                color = tiles[tile_base + src_y * 8 + src_x]
                dst = (dst_row + dst_x + tx) * 4

                if color == 0:
                    if in_window:
                        continue
                    r, g, b = backdrop
                else:
                    pal = palette_base + color * 4
                    r = palettes[pal]
                    g = palettes[pal + 1]
                    b = palettes[pal + 2]

                buffer[dst] = r
                buffer[dst + 1] = g
                buffer[dst + 2] = b
                buffer[dst + 3] = 0xFF

    def get_composited_frame(self, game_frame):
        """Composite the SGB border with the Game Boy frame.

        Applies SGB screen masking (MASK_EN) to the GB screen area:
        - mode 0: normal (show game frame)
        - mode 1: freeze (show last unmasked frame)
        - mode 2: black
        - mode 3: color 0
        """
        if not self.sgb.enabled:
            composited = array("B", [0] * (SGB_SCREEN_WIDTH * SGB_SCREEN_HEIGHT * 4))
            self._copy_game_to_center(game_frame, composited)
            return composited

        mask_mode = self.sgb.state.mask_mode

        # Store frozen frame only on transition from mode 0 to mode 1
        if mask_mode != 0 and self._prev_mask_mode == 0:
            self._frozen_frame = bytes(game_frame)
        self._prev_mask_mode = mask_mode

        # Update border if we have one
        if self.sgb.state.border_enabled:
            self.update()
            composited = self._composited
            if self.border_dirty or not self._border_copied:
                composited_mv = memoryview(composited)
                composited_mv[: len(self.border_buffer)] = self.border_buffer
                self._border_copied = True
                self.border_dirty = False
        else:
            # No border yet: black border area
            composited = self._composited
            composited_mv = memoryview(composited)
            composited_mv[:] = b"\x00" * len(composited_mv)
            self._border_copied = False

        # Apply masking to the GB screen area
        if mask_mode == 0:
            self._overlay_game_on_border(game_frame, composited)
        elif mask_mode == 1 and self._frozen_frame is not None:
            self._overlay_game_on_border(self._frozen_frame, composited)
        # mask_mode 2 (black) and 3 (color 0): leave GB area as-is from border buffer

        return composited

    def _copy_game_to_center(self, game_frame, composited):
        """Copy game frame to center of composited frame."""
        game_mv = memoryview(game_frame)
        composited_mv = memoryview(composited)
        row_bytes = GB_SCREEN_WIDTH * 4
        for y in range(GB_SCREEN_HEIGHT):
            src_start = y * row_bytes
            dst_start = ((GB_SCREEN_Y + y) * SGB_SCREEN_WIDTH + GB_SCREEN_X) * 4
            composited_mv[dst_start : dst_start + row_bytes] = game_mv[src_start : src_start + row_bytes]

    def _overlay_game_on_border(self, game_frame, composited):
        """Overlay game frame on top of border."""
        game_mv = memoryview(game_frame)
        composited_mv = memoryview(composited)
        row_bytes = GB_SCREEN_WIDTH * 4
        for y in range(GB_SCREEN_HEIGHT):
            src_start = y * row_bytes
            dst_start = ((GB_SCREEN_Y + y) * SGB_SCREEN_WIDTH + GB_SCREEN_X) * 4
            composited_mv[dst_start : dst_start + row_bytes] = game_mv[src_start : src_start + row_bytes]

    def stop(self):
        pass
