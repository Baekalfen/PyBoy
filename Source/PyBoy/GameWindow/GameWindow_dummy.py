# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys
import time
import numpy as np

from .. import CoreDump
from .. import WindowEvent
from ..GameWindow import AbstractGameWindow
from ..Logger import logger

gameboyResolution = (160, 144)


# TODO: class DummyGameWindow(AbstractGameWindow):
class DummyGameWindow():
    def __init__(self, scale):
        scale = 1
        # super(self.__class__, self).__init__(scale)
        logger.debug("DummyWindow initialization")

        CoreDump.windowHandle = self

        self.enable_title = True

    def dump(self,filename):
        pass

    def setTitle(self,title):
        if self.enable_title:
            logger.info("DummyWindow set title: %s" % title)

    def getEvents(self):
        return []

    def updateDisplay(self):
        pass

    def framelimiter(self):
        pass

    def stop(self):
        logger.info("DummyWindow stopping")

    def scanline(self, y, lcd):
        pass

    def renderScreen(self, lcd):
        pass

    def blankScreen(self):
        pass

