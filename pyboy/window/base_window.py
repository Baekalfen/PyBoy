#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from ..logger import addconsolehandler, logger

addconsolehandler()


ROWS, COLS = 144, 160


class BaseWindow:

    def __init__(self, scale=1):
        self._scale = scale
        logger.info("%s initialization" % self.__class__.__name__)

        self._scaledresolution = (scale * COLS, scale * ROWS)
        logger.info('Scale: x%s %s' % (self._scale, self._scaledresolution))

        self.color_palette = (0xFFFFFFFF, 0xFF999999, 0xFF555555, 0xFF000000)
        self.alphamask = 0xFF000000
        self.color_format = u"RGBA"
        self.buffer_dims = (160, 144)

        self.clearcache = False
        self.tiles_changed = set([])
        self.enable_title = True

    def init(self, hide_window):
        pass

    def dump(self, filename):
        raise NotImplementedError()

    def set_title(self, title):
        raise NotImplementedError()

    def get_events(self):
        raise NotImplementedError()

    def update_display(self, paused):
        raise NotImplementedError()

    def frame_limiter(self, speed):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def scanline(self, y, lcd):
        raise NotImplementedError()

    def render_screen(self, lc):
        raise NotImplementedError()

    def blank_screen(self):
        pass

    def get_screen_buffer(self):
        raise NotImplementedError()

    def get_screen_buffer_as_ndarray(self):
        raise NotImplementedError()

    def update_cache(self, lcd):
        pass

    def disable_title(self):
        self.enable_title = False

    def set_lcd(self, lcd):
        pass

    def save_state(self, f):
        # Just to align the state between windows
        for y in range(ROWS*4):
            f.write(0)

    def load_state(self, f, state_version):
        # Just to align the state between windows
        for y in range(ROWS*4):
            f.read()
