#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from pyboy.logger import addconsolehandler, logger

addconsolehandler()


ROWS, COLS = 144, 160


class BaseWindow:
    color_format = u""

    def __init__(self, renderer, scale, color_palette, hide_window):
        self._scale = scale
        logger.info("%s initialization" % self.__class__.__name__)

        self._scaledresolution = (scale * COLS, scale * ROWS)
        logger.info('Scale: x%s %s' % (self._scale, self._scaledresolution))

        self.enable_title = True
        self.renderer = renderer

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

    def blank_screen(self):
        pass

    def disable_title(self):
        self.enable_title = False

    def set_lcd(self, lcd):
        pass
