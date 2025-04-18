#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

__pdoc__ = {
    "PyBoyPlugin": False,
    "PyBoyWindowPlugin": False,
    "PyBoyGameWrapper.post_tick": False,
    "PyBoyGameWrapper.enabled": False,
    "PyBoyGameWrapper.argv": False,
}

import io
import random
import time
from array import array

import numpy as np

import pyboy
from pyboy.api.constants import SPRITES, TILES_CGB
from pyboy.core.lcd import CGBRenderer
from pyboy import utils

logger = pyboy.logging.get_logger(__name__)

ROWS, COLS = 144, 160


class PyBoyPlugin:
    argv = []

    def __init__(self, pyboy, mb, pyboy_argv):
        self.cgb = mb.cgb
        self.pyboy = pyboy
        self.mb = mb
        self.pyboy_argv = pyboy_argv
        self.renderer = self.mb.lcd.renderer
        self.is_cgb_renderer = isinstance(self.mb.lcd.renderer, CGBRenderer)
        if self.is_cgb_renderer:
            self.cgb_renderer = self.mb.lcd.renderer

    def handle_events(self, events):
        return events

    def post_tick(self):
        pass

    def window_title(self):
        return ""

    def stop(self):
        pass

    def enabled(self):
        return True


class PyBoyWindowPlugin(PyBoyPlugin):
    def __init__(self, pyboy, mb, pyboy_argv, *args, **kwargs):
        super().__init__(pyboy, mb, pyboy_argv, *args, **kwargs)

        self._ftime = time.perf_counter_ns()
        self.sound_support = False

        if not self.enabled():
            return

        scale = pyboy_argv.get("scale")
        self.scale = scale
        logger.debug("%s initialization" % self.__class__.__name__)

        self._scaledresolution = (scale * COLS, scale * ROWS)
        logger.debug("Scale: x%d (%d, %d)", self.scale, self._scaledresolution[0], self._scaledresolution[1])

        self.enable_title = True
        if not utils.cython_compiled:
            self.renderer = mb.lcd.renderer
        self.sound = self.mb.sound

    def frame_limiter(self, speed):
        self._ftime += int((1.0 / (60.0 * speed)) * 1_000_000_000)
        now = time.perf_counter_ns()
        if speed > 0 and self._ftime > now:
            delay = (self._ftime - now) // 1_000_000
            time.sleep(delay / 1000)
        else:
            self._ftime = now
        return True

    def paused(self, pause):
        pass

    def set_title(self, title):
        pass


class PyBoyGameWrapper(PyBoyPlugin):
    """
    This is the base-class for the game-wrappers. It provides some generic game-wrapping functionality, like `game_area`
    , which shows both sprites and tiles on the screen as a simple matrix.
    """

    cartridge_title = None

    mapping_one_to_one = np.arange(TILES_CGB, dtype=np.uint8)
    """
    Example mapping of 1:1
    """

    def __init__(self, *args, game_area_section=(0, 0, 32, 32), game_area_follow_scxy=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not utils.cython_compiled:
            self.tilemap_background = self.pyboy.tilemap_background
            self.tilemap_window = self.pyboy.tilemap_window
        self.tilemap_use_background = True
        self.mapping = np.arange(TILES_CGB, dtype=np.uint32)
        self.sprite_offset = 0
        self.game_has_started = False
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        self.shape = None
        """
        The shape of the game area. This can be modified with `pyboy.PyBoy.game_area_dimensions`.

        Example:
        ```python
        >>> pyboy.game_wrapper.shape
        (32, 32)
        ```
        """
        self._set_dimensions(*game_area_section, game_area_follow_scxy)
        width, height = self.shape
        self._cached_game_area_tiles_raw = array("B", [0xFF] * (width * height * 4))
        self._cached_game_area_tiles = memoryview(self._cached_game_area_tiles_raw).cast("I", shape=(width, height))

        self.saved_state = io.BytesIO()

        self.tilemap_background = self.pyboy.tilemap_background
        self.tilemap_window = self.pyboy.tilemap_window

    def enabled(self):
        return self.cartridge_title is None or self.pyboy.cartridge_title == self.cartridge_title

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

    def _set_timer_div(self, timer_div):
        if timer_div is None:
            self.mb.timer.DIV = random.getrandbits(8)
        else:
            self.mb.timer.DIV = timer_div & 0xFF

    def start_game(self, timer_div=None):
        """
        Call this function right after initializing PyBoy. This will navigate through menus to start the game at the
        first playable state.

        A value can be passed to set the timer's DIV register. Some games depend on it for randomization.

        The state of the emulator is saved, and using `reset_game`, you can get back to this point of the game
        instantly.

        Args:
            timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """

        self.game_has_started = True
        self.saved_state.seek(0)
        self.pyboy.save_state(self.saved_state)
        self._set_timer_div(timer_div)

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, you can call this method at any time to reset the game.

        Args:
            timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """

        if self.game_has_started:
            self.saved_state.seek(0)
            self.pyboy.load_state(self.saved_state)
            self._set_timer_div(timer_div)
            self.post_tick()
        else:
            raise utils.PyBoyException("Tried to reset game, but it hasn't been started yet!")

    def game_over(self):
        """
        After calling `start_game`, you can call this method at any time to know if the game is over.
        """
        raise NotImplementedError("game_over not implemented in game wrapper")

    def _sprites_on_screen(self):
        if self._sprite_cache_invalid:
            self._cached_sprites_on_screen = []
            for s in range(SPRITES):
                sprite = self.pyboy.get_sprite(s)
                if sprite.on_screen:
                    self._cached_sprites_on_screen.append(sprite)
            self._sprite_cache_invalid = False
        return self._cached_sprites_on_screen

    def _game_area_tiles(self):
        if self._tile_cache_invalid:
            xx, yy, width, height = self.game_area_section
            scanline_parameters = self.pyboy.screen.tilemap_position_list

            if self.game_area_follow_scxy:
                self._cached_game_area_tiles = np.ndarray(shape=(height, width), dtype=np.uint32)
                for y in range(height):
                    SCX = scanline_parameters[(yy + y) * 8][0] // 8
                    SCY = scanline_parameters[(yy + y) * 8][1] // 8
                    for x in range(width):
                        _x = (xx + x + SCX) % 32
                        _y = (yy + y + SCY) % 32
                        if self.tilemap_use_background:
                            self._cached_game_area_tiles[y, x] = self.tilemap_background.tile_identifier(_x, _y)
                        else:
                            self._cached_game_area_tiles[y, x] = self.tilemap_window.tile_identifier(_x, _y)
            else:
                if self.tilemap_use_background:
                    self._cached_game_area_tiles = np.asarray(
                        self.tilemap_background[xx : xx + width, yy : yy + height], dtype=np.uint32
                    )
                else:
                    self._cached_game_area_tiles = np.asarray(
                        self.tilemap_window[xx : xx + width, yy : yy + height], dtype=np.uint32
                    )
            self._tile_cache_invalid = False
        return self._cached_game_area_tiles

    def use_background(self, value):
        self.tilemap_use_background = value

    def game_area(self):
        """
        This method returns a cut-out of the screen as a simplified matrix for use in machine learning applications.

        Returns
        -------
        memoryview:
            Simplified 2-dimensional memoryview of the screen
        """
        tiles_matrix = self.mapping[self._game_area_tiles()]
        sprites = self._sprites_on_screen()
        xx, yy, width, height = self.game_area_section
        for s in sprites:
            _x = (s.x // 8) - xx
            _y = (s.y // 8) - yy
            if 0 <= _x < width:
                # Adding offset to try to seperate sprites from tiles
                if 0 <= _y < height:
                    tiles_matrix[_y][_x] = self.mapping[s.tile_identifier] + self.sprite_offset
                if len(s.tiles) == 2 and 0 <= _y + 1 < height:  # Sprite has two tiles
                    tiles_matrix[_y + 1][_x] = self.mapping[s.tile_identifier + 1] + self.sprite_offset

        return tiles_matrix

    def game_area_mapping(self, mapping, sprite_offest):
        self.mapping = np.asarray(mapping, dtype=np.uint32)
        self.sprite_offset = sprite_offest

    def _set_dimensions(self, x, y, width, height, follow_scrolling=True):
        self.shape = (width, height)
        self.game_area_section = (x, y, width, height)
        self.game_area_follow_scxy = follow_scrolling

    def _sum_number_on_screen(self, x, y, length, blank_tile_identifier, tile_identifier_offset):
        number = 0
        for i, x in enumerate(self.tilemap_background[x : x + length, y]):
            if x != blank_tile_identifier:
                number += (x + tile_identifier_offset) * (10 ** (length - 1 - i))
        return number

    def __repr__(self):
        adjust = 4

        sprites = "\n".join([str(s) for s in self._sprites_on_screen()])

        tiles_header = (
            " " * 4 + "".join([f"{i: >4}" for i in range(self.shape[0])]) + "\n" + "_" * (adjust * self.shape[0] + 4)
        )

        tiles = "\n".join(
            [
                (f"{i: <3}|" + "".join([str(tile).rjust(adjust) for tile in line])).strip()
                for i, line in enumerate(self.game_area())
            ]
        )

        return "Sprites on screen:\n" + sprites + "\n" + "Tiles on screen:\n" + tiles_header + "\n" + tiles
