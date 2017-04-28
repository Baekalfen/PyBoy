# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEvent, GbEventId

from GbLogger import gblogger


class MbTickEvent(GbEvent):

    _ID = GbEventId.MB_TICK

    def __init__(self, system, eventHandler, mb, debugger=None):
        super(self.__class__, self).__init__(system, eventHandler)

        self._mb = mb
        self._debugger = debugger

    def do_call(self):

        if self._system.debug is not None and self._debugger:
            self._debugger.tick()
        else:
            self._mb.tickFrame()


