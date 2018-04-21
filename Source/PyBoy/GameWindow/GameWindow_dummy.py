# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
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

        self.scanlineParameters = np.ndarray(shape=(gameboyResolution[0],4), dtype='int32')

    def dump(self,filename):
        pass

    def setTitle(self,title):
        logger.info("DummyWindow set title: %s" % title)

    def getEvents(self):
        return []

    def updateDisplay(self):
        pass

    def VSync(self):
        pass

    def stop(self):
        logger.info("DummyWindow stopping")

    def scanline(self, y, viewPos, windowPos):
        self.scanlineParameters[y, 0] = viewPos[0]
        self.scanlineParameters[y, 1] = viewPos[1]
        self.scanlineParameters[y, 2] = windowPos[0]
        self.scanlineParameters[y, 3] = windowPos[1]

    def renderScreen(self, lcd):
        pass

    def blankScreen(self):
        pass

