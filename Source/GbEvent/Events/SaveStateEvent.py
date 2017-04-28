# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEvent, GbEventId


class SaveStateEvent(GbEvent):

    _ID = GbEventId.STATE_IO

    def __init__(self, system, eventHandler, fname):
        super(self.__class__, self).__init__(system, eventHandler)
        self._fname = fname

    def do_call(self):
        pass

