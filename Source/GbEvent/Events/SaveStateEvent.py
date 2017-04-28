# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEvent, GbEventId


class SaveStateEvent(GbEvent):
    """Event to handle motherboard save/load"""

    _ID = GbEventId.STATE_IO

    def __init__(self, system, eventHandler, fname, operation):
        """
        :param system: GB System state
        :param eventHandler: Input handler
        :param fname: Save-state filename
        :param operation: 'save'/'load'
        """
        super(self.__class__, self).__init__(system, eventHandler)
        self._fname = fname
        if not operation in ('save', 'load'):
            raise RuntimeError('Invalid IO operation')
        self._operation = operation

    def do_call(self):
        """Event callback"""
        pass

