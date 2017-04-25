# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEvent, GbEventId


def DebugToggleEvent(GbEvent):

    _ID = GbEventId.DEBUG_TOGGLE

    def __init__(self, system, debugEnable=None):
        super(self.__class__, self).__init__(system)
        self._debugEnable = debugEnable

    def do_call(self):
        if self._debugEnable is None:
            self._system.debug = not self._system.debug
        else:
            self._system.debug = self._debugEnable


