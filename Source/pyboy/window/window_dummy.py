#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from pyboy.window.window import Window
from ..logger import logger


class DummyWindow(Window):
    def __init__(self, scale):
        super(self.__class__, self).__init__(scale)

    def dump(self, filename):
        pass

    def set_title(self, title):
        if self.enable_title:
            logger.info("DummyWindow set title: %s" % title)

    def get_events(self):
        return []

    def update_display(self):
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
