#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.botsupport.sprite import Sprite
from pyboy.logger import logger

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tilemap_background = self.pyboy.get_tilemap_background()
        self.game_has_started = False
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

    def enabled(self):
        return self.pyboy_argv.get('game_wrapper') and self.pyboy.get_cartridge_title() == self.cartridge_title

    def screen_matrix(self):
        raise NotImplementedError("screen_matrix not implemented in game wrapper")

    def tiles_on_screen(self):
        raise NotImplementedError("tiles_on_screen not implemented in game wrapper")

    def sprites_on_screen(self):
        if self._sprite_cache_invalid:
            self._cached_sprites_on_screen = []
            for s in range(40):
                sprite = Sprite(self.mb, s)
                if sprite.on_screen:
                    self._cached_sprites_on_screen.append(sprite)
            self._sprite_cache_invalid = False
        return self._cached_sprites_on_screen

    def post_tick(self):
        raise NotImplementedError("post_tick not implemented in game wrapper")
