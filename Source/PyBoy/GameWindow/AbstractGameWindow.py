# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from abc import abstractmethod


class AbstractGameWindow(object):

    def __init__(self, scale=1):
        self._scale = scale

    @abstractmethod
    def dump(self, filename):
        raise NotImplementedError()

    @abstractmethod
    def setTitle(self, title):
        raise NotImplementedError()

    @abstractmethod
    def getEvents(self):
        raise NotImplementedError()

    @abstractmethod
    def updateDisplay(self):
        raise NotImplementedError()

    @abstractmethod
    def VSync(self):
        raise NotImplementedError()

    @abstractmethod
    def stop(self):
        raise NotImplementedError()

    @abstractmethod
    def scanline(self, y, viewPos, windowPos):
        raise NotImplementedError()

    @abstractmethod
    def renderScreen(self, lc):
        raise NotImplementedError()

    @abstractmethod
    def copySprite(self, fromXY, toXY, fromBuffer, toBuffer, spriteSize,
            spritePriority, BGPkey, xFlip=0, yFlip=0):
        raise NotImplementedError()

    @abstractmethod
    def blankScreen(self):
        raise NotImplementedError()

    @abstractmethod
    def getScreenBuffer(self):
        raise NotImplementedError()

