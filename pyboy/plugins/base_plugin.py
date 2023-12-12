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
from array import array

import numpy as np

import pyboy
from pyboy.api.sprite import Sprite

logger = pyboy.logging.get_logger(__name__)

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False

ROWS, COLS = 144, 160


class PyBoyPlugin:
    argv = []

    def __init__(self, pyboy, mb, pyboy_argv):
        if not cythonmode:
            self.pyboy = pyboy
            self.mb = mb
            self.pyboy_argv = pyboy_argv

    def __cinit__(self, pyboy, mb, pyboy_argv, *args, **kwargs):
        self.pyboy = pyboy
        self.mb = mb
        self.pyboy_argv = pyboy_argv

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

        if not self.enabled():
            return

        scale = pyboy_argv.get("scale")
        self.scale = scale
        logger.debug("%s initialization" % self.__class__.__name__)

        self._scaledresolution = (scale * COLS, scale * ROWS)
        logger.debug("Scale: x%d (%d, %d)", self.scale, self._scaledresolution[0], self._scaledresolution[1])

        self.enable_title = True
        if not cythonmode:
            self.renderer = mb.lcd.renderer

    def __cinit__(self, *args, **kwargs):
        self.renderer = self.mb.lcd.renderer

    def frame_limiter(self, speed):
        return False

    def set_title(self, title):
        pass


class PyBoyGameWrapper(PyBoyPlugin):
    """
    This is the base-class for the game-wrappers. It provides some generic game-wrapping functionality, like `game_area`
    , which shows both sprites and tiles on the screen as a simple matrix.
    """

    cartridge_title = None
    argv = [("--game-wrapper", {"action": "store_true", "help": "Enable game wrapper for the current game"})]

    def __init__(self, *args, game_area_section=(0, 0, 32, 32), game_area_wrap_around=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.tilemap_background = self.pyboy.tilemap_background
        self.tilemap_window = self.pyboy.tilemap_window
        self.tilemap_use_background = True
        self.sprite_offset = 0
        self.game_has_started = False
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        self.game_area_section = game_area_section
        self.game_area_wrap_around = game_area_wrap_around
        width = self.game_area_section[2] - self.game_area_section[0]
        height = self.game_area_section[3] - self.game_area_section[1]
        self._cached_game_area_tiles_raw = array("B", [0xFF] * (width*height*4))

        self.saved_state = io.BytesIO()

        self._cached_game_area_tiles = memoryview(self._cached_game_area_tiles_raw).cast("I", shape=(width, height))

    def enabled(self):
        return self.cartridge_title is None or self.pyboy.cartridge_title() == self.cartridge_title

    def post_tick(self):
        raise NotImplementedError("post_tick not implemented in game wrapper")

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

        if not self.pyboy.frame_count == 0:
            logger.warning("Calling start_game from an already running game. This might not work.")

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, you can call this method at any time to reset the game.

        Args:
            timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """

        if self.game_has_started:
            self.saved_state.seek(0)
            self.pyboy.load_state(self.saved_state)
            self.post_tick()
        else:
            logger.error("Tried to reset game, but it hasn't been started yet!")

    def game_over(self):
        """
        After calling `start_game`, you can call this method at any time to know if the game is over.
        """
        raise NotImplementedError("game_over not implemented in game wrapper")

    def _sprites_on_screen(self):
        if self._sprite_cache_invalid:
            self._cached_sprites_on_screen = []
            for s in range(40):
                sprite = Sprite(self.mb, s)
                if sprite.on_screen:
                    self._cached_sprites_on_screen.append(sprite)
            self._sprite_cache_invalid = False
        return self._cached_sprites_on_screen

    def _game_area_tiles(self):
        if self._tile_cache_invalid:
            xx = self.game_area_section[0]
            yy = self.game_area_section[1]
            width = self.game_area_section[2]
            height = self.game_area_section[3]
            scanline_parameters = self.pyboy.screen.tilemap_position_list

            if self.game_area_wrap_around:
                self._cached_game_area_tiles = np.ndarray(shape=(height, width), dtype=np.uint32)
                for y in range(height):
                    SCX = scanline_parameters[(yy+y) * 8][0] // 8
                    SCY = scanline_parameters[(yy+y) * 8][1] // 8
                    for x in range(width):
                        _x = (xx+x+SCX) % 32
                        _y = (yy+y+SCY) % 32
                        if self.tilemap_use_background:
                            self._cached_game_area_tiles[y, x] = self.tilemap_background.tile_identifier(_x, _y)
                        else:
                            self._cached_game_area_tiles[y, x] = self.tilemap_window.tile_identifier(_x, _y)
            else:
                if self.tilemap_use_background:
                    self._cached_game_area_tiles = np.asarray(
                        self.tilemap_background[xx:xx + width, yy:yy + height], dtype=np.uint32
                    )
                else:
                    self._cached_game_area_tiles = np.asarray(
                        self.tilemap_window[xx:xx + width, yy:yy + height], dtype=np.uint32
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
        tiles_matrix = self._game_area_tiles()
        sprites = self._sprites_on_screen()
        xx = self.game_area_section[0]
        yy = self.game_area_section[1]
        width = self.game_area_section[2]
        height = self.game_area_section[3]
        for s in sprites:
            _x = (s.x // 8) - xx
            _y = (s.y // 8) - yy
            if 0 <= _y < height and 0 <= _x < width:
                tiles_matrix[_y][
                    _x] = s.tile_identifier + self.sprite_offset # Adding offset to try to seperate sprites from tiles
        return tiles_matrix

    def _game_area_np(self, observation_type="tiles"):
        if observation_type == "tiles":
            return np.asarray(self.game_area(), dtype=np.uint16)
        elif observation_type == "compressed":
            try:
                return self.tiles_compressed[np.asarray(self.game_area(), dtype=np.uint16)]
            except AttributeError:
                raise AttributeError(
                    f"Game wrapper miss the attribute tiles_compressed for observation_type : {observation_type}"
                )
        elif observation_type == "minimal":
            try:
                return self.tiles_minimal[np.asarray(self.game_area(), dtype=np.uint16)]
            except AttributeError:
                raise AttributeError(
                    f"Game wrapper miss the attribute tiles_minimal for observation_type : {observation_type}"
                )
        else:
            raise ValueError(f"Invalid observation_type : {observation_type}")

    def _sum_number_on_screen(self, x, y, length, blank_tile_identifier, tile_identifier_offset):
        number = 0
        for i, x in enumerate(self.tilemap_background[x:x + length, y]):
            if x != blank_tile_identifier:
                number += (x+tile_identifier_offset) * (10**(length - 1 - i))
        return number
