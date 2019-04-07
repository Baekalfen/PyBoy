#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .Window_SDL2 import SdlWindow
from ..Logger import logger

gameboyResolution = (160, 144)

class HeadlessWindow(SdlWindow):
    def __init__(self, scale=1):
        super(self.__class__, self).__init__(scale)
        self.lcd = None

    def init(self):
        self.blankScreen()

    def setTitle(self,title):
        if self.enable_title:
            logger.info("HeadlessWindow set title: %s" % title)

    def getEvents(self):
        return []

    def updateDisplay(self):
        pass

    def getScreenBuffer(self):
        return self._screenBuffer

    def framelimiter(self, speed):
        pass

    def stop(self):
        pass

