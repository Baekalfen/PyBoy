# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEvent, GbEventId


class QuitEvent(GbEvent):

    _ID = GbEventId.QUIT

    def __init__(self, system, eventHandler, saveState=False, stateFileName=None):
        super(self.__class__, self).__init__(system, eventHandler)

        self._saveState = saveState
        self._stateFileName = stateFileName

    def do_call(self):
        self._system.quit = True
