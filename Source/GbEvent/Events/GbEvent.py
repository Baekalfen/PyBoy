# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEventId



class GbEvent(object):
    """Abstract GB event-class"""

    _ID = GbEventId.NULL_EVENT

    def __init__(self, system, eventHandler):
        self._system = system
        self._eventHandler = eventHandler

    @classmethod
    def getId(cls):
        return cls._ID

    def do_call(self):
        raise RuntimeError('Attempted to call NULL_EVENT')
