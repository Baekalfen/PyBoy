#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from pyboy.logger import logger


class PyBoyPlugin:
    argv = []

    def __init__(self, pyboy, argv):
        self.pyboy = pyboy
        self.argv = argv

    def handle_events(self, events):
        return events

    def post_tick(self):
        pass

    def pre_tick(self):
        pass

    def window_title(self):
        return ""

    def stop(self):
        pass

    def enabled(self):
        return True


ROWS, COLS = 144, 160


class BaseWindowPlugin(PyBoyPlugin):
    def __init__(self, pyboy, argv):
        super().__init__(pyboy, argv)

        if not self.enabled():
            return

        scale = argv.get("scale")
        self._scale = scale
        logger.info("%s initialization" % self.__class__.__name__)

        self._scaledresolution = (scale * COLS, scale * ROWS)
        logger.info('Scale: x%s %s' % (self._scale, self._scaledresolution))

        self.enable_title = True
        self.renderer = pyboy.mb.renderer
