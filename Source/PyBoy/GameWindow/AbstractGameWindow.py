# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from abc import abstractmethod

class AbstractGameWindow(object):

    def __init__(self, scale=1):
        self._scale = scale

        self.VRAM_changed = True
        self.OAM_changed = True
        self.tiles_changed = set([])
        self.flush_cache = True

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
    def scanline(self, y, lcd):
        raise NotImplementedError()

    @abstractmethod
    def renderScreen(self, lcd):
        raise NotImplementedError()

    @abstractmethod
    def blankScreen(self):
        raise NotImplementedError()

    @abstractmethod
    def getScreenBuffer(self):
        raise NotImplementedError()
