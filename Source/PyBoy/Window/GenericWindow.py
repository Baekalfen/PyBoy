# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from ..Logger import logger

gameboyResolution = (160, 144)

class GenericWindow():

    def __init__(self, scale=1):
        self._scale = scale
        logger.debug("%s initialization" % self.__class__.__name__)

        self._scaledResolution = tuple([int(x * self._scale) for x in gameboyResolution])
        logger.debug('Scale: x%s %s' % (self._scale, self._scaledResolution))

        self.colorPalette = (0x00FFFFFF,0x00999999,0x00555555,0x00000000)
        self.alphaMask = 0x7F000000

        self.clearCache = False
        self.tiles_changed = set([])

        self.enable_title = True

    def init(self):
        pass

    def dump(self, filename):
        raise NotImplementedError()

    def setTitle(self, title):
        raise NotImplementedError()

    def getEvents(self):
        raise NotImplementedError()

    def updateDisplay(self):
        raise NotImplementedError()

    def framelimiter(self, speed):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def scanline(self, y, lcd):
        raise NotImplementedError()

    def renderScreen(self, lc):
        raise NotImplementedError()

    def blankScreen(self):
        pass

    def getScreenBuffer(self):
        raise NotImplementedError()

    def updateCache(self, lcd):
        pass

    def disableTitle(self):
        pass

