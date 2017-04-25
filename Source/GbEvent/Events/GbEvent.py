# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEventId



class GbEvent(object):

    _ID = GbEventId.NULL_EVENT

    def __init__(self, system):
        self._system = system

    @classmethod
    def getId(cls):
        return cls._ID

    def do_call(self):
        raise RuntimeError('Attempted to call NULL_EVENT')
