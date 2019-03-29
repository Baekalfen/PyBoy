# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from ..Logger import logger

gameboyResolution = (160, 144)

class GenericWindow(object):

    def __init__(self, scale=1):
        self._scale = scale
        logger.debug("%s initialization" % self.__class__.__name__)

        self._scaledResolution = tuple(x * self._scale for x in gameboyResolution)
        logger.debug('Scale: x%s %s' % (self._scale, self._scaledResolution))

        self.enable_title = True


    def dump(self, filename):
        raise NotImplementedError()

    def setTitle(self, title):
        raise NotImplementedError()

    def getEvents(self):
        raise NotImplementedError()

    def updateDisplay(self):
        raise NotImplementedError()

    def framelimiter(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def scanline(self, y, lcd):
        raise NotImplementedError()

    def renderScreen(self, lc):
        raise NotImplementedError()

    def copySprite(self, fromXY, toXY, fromBuffer, toBuffer, spriteSize,
            spritePriority, BGPkey, xFlip=0, yFlip=0):
        raise NotImplementedError()

    def blankScreen(self):
        raise NotImplementedError()

    def getScreenBuffer(self):
        raise NotImplementedError()

