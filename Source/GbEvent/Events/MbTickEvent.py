# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEvent
from .. import GbEventId

from GbLogger import gblogger


class MbTickEvent(GbEvent):
    """Event to handle motherboard ticks with optional debugger"""

    _ID = GbEventId.MB_TICK

    def __init__(self, system, eventHandler, mb, debugger=None):
        """
        :param system: GB System state
        :param eventHandler: Input handler
        :param mb: Motherboard-object
        :param debugger: Debugger-object
        """
        super(self.__class__, self).__init__(system, eventHandler)

        self._mb = mb
        self._debugger = debugger

    def do_call(self):
        """Event callback"""

        if self._system.debug is not None and self._debugger:
            self._debugger.tick()
        else:
            self._mb.tickFrame()


