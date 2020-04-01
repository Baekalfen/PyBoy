#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

__pdoc__ = {
   'PyBoyPlugin': False,
   'PyBoyWindowPlugin': False,
}

import logging
from array import array

import numpy as np
from pyboy.botsupport.sprite import Sprite

logger = logging.getLogger(__name__)

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
        logger.info("%s initialization" % self.__class__.__name__)

        self._scaledresolution = (scale * COLS, scale * ROWS)
        logger.info('Scale: x%s %s' % (self.scale, self._scaledresolution))

        self.enable_title = True
        if not cythonmode:
            self.renderer = mb.renderer

    def __cinit__(self, *args, **kwargs):
        self.renderer = self.mb.renderer

    def frame_limiter(self, speed):
        return False

    def set_title(self, title):
        pass


class PyBoyGameWrapper(PyBoyPlugin):
    argv = [('--game-wrapper', {"action": 'store_true', "help": 'Enable game wrapper for the current game'})]

    def __init__(self, *args, game_area_section=(0,0,32,32), game_area_wrap_around=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.tilemap_background = self.pyboy.botsupport_manager().tilemap_background()
        self.game_has_started = False
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        self.game_area_section = game_area_section
        self.game_area_wrap_around = game_area_wrap_around
        width = self.game_area_section[2] - self.game_area_section[0]
        height = self.game_area_section[3] - self.game_area_section[1]
        self._cached_tiles_on_screen_raw = array('B', [0xFF] * (width*height*4))

        if cythonmode:
            self._cached_tiles_on_screen = memoryview(self._cached_tiles_on_screen_raw).cast('I', shape=(width, height))
        else:
            v = memoryview(self._cached_tiles_on_screen_raw).cast('I')
            self._cached_tiles_on_screen = [v[i:i+height] for i in range(0, height*width, height)]

    def enabled(self):
        return self.pyboy_argv.get('game_wrapper') and self.pyboy.cartridge_title() == self.cartridge_title

    def post_tick(self):
        raise NotImplementedError("post_tick not implemented in game wrapper")

    def sprites_on_screen(self):
        """
        All sprites with their bounding box inside the screen area
        """
        if self._sprite_cache_invalid:
            self._cached_sprites_on_screen = []
            for s in range(40):
                sprite = Sprite(self.mb, s)
                if sprite.on_screen:
                    self._cached_sprites_on_screen.append(sprite)
            self._sprite_cache_invalid = False
        return self._cached_sprites_on_screen

    def tiles_on_screen(self):
        """
        All tiles visible on the screen corrected for scanline parameters. Includes HUD and stuff outside of the screen.
        """
        if self._tile_cache_invalid:
            xx = self.game_area_section[0]
            yy = self.game_area_section[1]
            width = self.game_area_section[2]
            height = self.game_area_section[3]
            scanline_parameters = self.pyboy.botsupport_manager().screen().tilemap_position_list()

            if self.game_area_wrap_around:
                self._cached_tiles_on_screen = np.ndarray(shape=(height, width), dtype=np.uint32)
                for y in range(height):
                    SCX = scanline_parameters[(yy+y)*8][0]//8
                    SCY = scanline_parameters[(yy+y)*8][1]//8
                    for x in range(width):
                        _x = (xx+x+SCX)%32
                        _y = (yy+y+SCY)%32
                        self._cached_tiles_on_screen[y][x] = self.tilemap_background.tile_identifier(_x, _y)
            else:
                self._cached_tiles_on_screen = np.asarray(self.tilemap_background[xx:xx+width, yy:yy+height], dtype=np.uint32)
            self._tile_cache_invalid = False
        return self._cached_tiles_on_screen

    def game_area(self):
        """
        Only the essential part of the screen with out HUD etc.
        """
        tiles_matrix = self.tiles_on_screen()
        sprites = self.sprites_on_screen()
        xx = self.game_area_section[0]
        yy = self.game_area_section[1]
        width = self.game_area_section[2]
        height = self.game_area_section[3]
        for s in sprites:
            _x = (s.x//8)-xx
            _y = (s.y//8)-yy
            if 0 <= _y < height and 0 <= _x < width:
                tiles_matrix[_y][_x] = s.tile_identifier
        return tiles_matrix

    def _sum_number_on_screen(self, x, y, length, blank_tile_identifier, tile_identifier_offset):
        number = 0
        for i, x in enumerate(self.tilemap_background[x:x+length, y]):
            if x != blank_tile_identifier:
                number += (x+tile_identifier_offset)*(10**(length-1-i))
        return number


    def start_game(self):
        pass

    def reset_game(self):
        pass
