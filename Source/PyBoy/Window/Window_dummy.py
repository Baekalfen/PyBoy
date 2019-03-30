# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys
import time
import numpy as np

from ..Logger import logger
from .GenericWindow import GenericWindow

class DummyWindow(GenericWindow):
    def __init__(self, scale):
        super(self.__class__, self).__init__(scale)

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

