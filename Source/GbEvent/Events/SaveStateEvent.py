# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEvent, GbEventId


def SaveStateEvent(GbEvent):

    _ID = GbEventId.STATE_IO

    def __init__(self, system, fname):
        super(self.__class__, self).__init__(system)
        self._fname = fname

    def do_call(self):
        pass

