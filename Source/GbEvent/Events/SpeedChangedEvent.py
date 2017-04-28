# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEvent, GbEventId


class SpeedChangedEvent(GbEvent):
    """Event to handle GB tick-speed changes"""

    _ID = GbEventId.SPEED_CHANGED

    def __init__(self, system, eventHandler, speedMultiplier=1.0):
        """
        :param system: GB System state
        :param eventHandler: Input handler
        :param speedMultiplier: New GB tick-speed multiplier
        """
        super(self.__class__, self).__init__(system, eventHandler)

        self._speedMultiplier = speedMultiplier

    def do_call(self):
        """Event callback"""
        self._system.speedMultiplier = self._speedMultiplier

