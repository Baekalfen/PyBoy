#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from ..logger import logger
from .window_sdl2 import SDLWindow

ROWS, COLS = 144, 160


class HeadlessWindow(SDLWindow):
    def __init__(self, scale=1):
        super(self.__class__, self).__init__(scale)
        self.lcd = None

    def init(self):
        self.blank_screen()

    def set_title(self, title):
        if self.enable_title:
            logger.info("HeadlessWindow set title: %s" % title)

    def get_events(self):
        return []

    def update_display(self, paused):
        pass

    def frame_limiter(self, speed):
        pass

    def stop(self):
        pass
