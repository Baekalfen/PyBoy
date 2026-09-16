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

        Each border tile is 32 bytes (4 bitplanes). Store the 4-bit color
        index (0-15) per pixel in border_tile_cache (1 byte per pixel).
        Palette lookup happens in render_border.
        """
        if tile_data is None:
            return

        for tile_num in range(256):
            base = tile_num * 32
            cache_base = tile_num * 64  # 8x8 = 64 bytes
            if base + 31 >= len(tile_data):
                continue
            for y in range(8):
                row_base = base + y * 2
                bp0 = tile_data[row_base]
                bp1 = tile_data[row_base + 1]
                bp2 = tile_data[row_base + 16]
                bp3 = tile_data[row_base + 17]
                for x in range(8):
                    bit = 7 - x
                    color = (
                        ((bp0 >> bit) & 1)
                        | (((bp1 >> bit) & 1) << 1)
                        | (((bp2 >> bit) & 1) << 2)
                        | (((bp3 >> bit) & 1) << 3)
                    )
                    self.border_tile_cache[cache_base + y * 8 + x] = color

    def render_border(self, map_data):
        """Render the SGB border using the tile map.

        Map is 32x32 but only 28 rows are used (256x224 = 32x28 tiles).
        Each entry is uint16_t (little-endian):
        - Bits 0-7: tile number
        - Bits 8-9: unused (skip if non-zero)
        - Bits 10-11: palette number (0-3)
        - Bit 14: X-flip
        - Bit 15: Y-flip

        Color 0 in the GB area is skipped (game shows through).
        Color 0 in the border area uses the game's effective palette color 0
        (BGP color 0), matching SameBoy behavior. This is typically white.
        """
        if map_data is None:
            return

        # Clear border buffer
        composited_mv = memoryview(self.border_buffer)
        composited_mv[:] = b"\x00" * len(composited_mv)

        # Background color for color 0 in border area: game's BGP color 0
        # SameBoy uses effective_palettes[0] which is the game's palette color 0
        bg_color = self.sgb.state.bg_color_0
        bg_r = bg_color & 0xFF
        bg_g = (bg_color >> 8) & 0xFF
        bg_b = (bg_color >> 16) & 0xFF

        # GB area in tile coordinates: cols 6-25, rows 5-22
        gb_col_start = 6
        gb_col_end = 26
        gb_row_start = 5
        gb_row_end = 23

        for row in range(28):
            for col in range(32):
                map_offset = (row * 32 + col) * 2
                if map_offset + 1 >= len(map_data):
                    continue

                map_entry = map_data[map_offset] | (map_data[map_offset + 1] << 8)
                if map_entry & 0x0300:
                    continue

                tile_num = map_entry & 0xFF
                palette_num = (map_entry >> 10) & 3
                x_flip = (map_entry >> 14) & 1
                y_flip = (map_entry >> 15) & 1

                tile_cache_base = tile_num * 64
                pal_base = palette_num * 16 * 4
                in_gb_area = gb_col_start <= col < gb_col_end and gb_row_start <= row < gb_row_end

                for ty in range(8):
                    src_y = (7 - ty) if y_flip else ty
                    dst_y = row * 8 + ty
                    for tx in range(8):
                        src_x = (7 - tx) if x_flip else tx
                        color = self.border_tile_cache[tile_cache_base + src_y * 8 + src_x]
                        dst_x = col * 8 + tx
                        dst_idx = (dst_y * SGB_SCREEN_WIDTH + dst_x) * 4

                        if color == 0:
                            if in_gb_area:
                                continue
                            self.border_buffer[dst_idx] = bg_r
                            self.border_buffer[dst_idx + 1] = bg_g
                            self.border_buffer[dst_idx + 2] = bg_b
                            self.border_buffer[dst_idx + 3] = 0xFF
                        else:
                            pal_idx = pal_base + color * 4
                            self.border_buffer[dst_idx] = self.palettes_rgba[pal_idx]
                            self.border_buffer[dst_idx + 1] = self.palettes_rgba[pal_idx + 1]
                            self.border_buffer[dst_idx + 2] = self.palettes_rgba[pal_idx + 2]
                            self.border_buffer[dst_idx + 3] = self.palettes_rgba[pal_idx + 3]

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
