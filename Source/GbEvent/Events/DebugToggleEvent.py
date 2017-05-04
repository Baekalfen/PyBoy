# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEvent
from .. import GbEventId


class DebugToggleEvent(GbEvent):
    """Event for handling debug-mode toggling"""

    _ID = GbEventId.DEBUG_TOGGLE

    def __init__(self, system, eventHandler, debugEnable=None):
        """__init__

        :param system: GB System state
        :param eventHandler: Input handler
        :param debugEnable: New debug-mode state. Toggle current state if None
        """
        super(self.__class__, self).__init__(system, eventHandler)
        self._debugEnable = debugEnable

    def do_call(self):
        """Event callback"""
        if self._debugEnable is None:
            self._system.debug = not self._system.debug
        else:
            self._system.debug = self._debugEnable


