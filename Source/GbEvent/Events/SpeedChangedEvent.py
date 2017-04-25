# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEvent, GbEventId


def SpeedChangedEvent(GbEvent):

    _ID = GbEventId.SPEED_CHANGED

    def __init__(self, system, speedMultiplier=1.0):
        super(self.__class__, self).__init__(system)

        self._speedMultiplier = speedMultiplier

    def do_call(self):
        self._system.speedMultiplier = self._speedMultiplier

