# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from .. import GbEventId



class GbEvent(object):
    """Abstract GB event-class"""

    _ID = GbEventId.NULL_EVENT

    def __init__(self, system, eventHandler):
        """
        :param system: GB System state
        :param eventHandler: Input handler
        """
        self._system = system
        self._eventHandler = eventHandler

    @classmethod
    def getId(cls):
        """Static method to get class event ID"""
        return cls._ID

    def do_call(self):
        """Event callback - overload when implementing a new event"""
        raise RuntimeError('Attempted to call NULL_EVENT')
