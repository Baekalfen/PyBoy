# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from GbEvent.GbEvent import GbEvent
from .. import GbEventId


class QuitEvent(GbEvent):
    """Event to handle clean exit"""

    _ID = GbEventId.QUIT

    def __init__(self, system, eventHandler, saveState=None, stateFileName=None):
        """
        :param system: GB System state
        :param eventHandler: Input handler
        :param saveState: Set to True to save Motherboard state on exit
        :param stateFileName: Save-state filename
        """
        super(self.__class__, self).__init__(system, eventHandler)

        self._saveState = saveState
        self._stateFileName = stateFileName

    def do_call(self):
        """Event callback"""
        self._system.quit = True
