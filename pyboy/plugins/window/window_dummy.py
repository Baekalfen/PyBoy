#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.window.base_window import BaseWindow

from ..logger import logger


class DummyWindow(BaseWindow):
    def __init__(self, renderer, scale, color_palette, hide_window):
        super(self.__class__, self).__init__(renderer, scale, color_palette, hide_window)

    def dump(self, filename):
        pass

    def set_title(self, title):
        if self.enable_title:
            logger.info("DummyWindow set title: %s" % title)

    def get_events(self):
        return []

    def update_display(self, paused):
        pass

    def frame_limiter(self, speed):
        pass

    def stop(self):
        logger.info("DummyWindow stopping")

    def scanline(self, y, lcd):
        pass

    def render_screen(self, lcd):
        pass

    def blank_screen(self):
        pass
