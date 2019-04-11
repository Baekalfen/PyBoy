#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from .window_sdl2 import SDLWindow
from ..logger import logger


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

    def update_display(self):
        pass

    def getscreenbuffer(self):
        return self._screenbuffer_raw

    def frame_limiter(self, speed):
        pass

    def stop(self):
        pass
