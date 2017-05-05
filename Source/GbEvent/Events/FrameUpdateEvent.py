# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

import time

from GbEvent.GbEvent import GbEvent
from .. import GbEventId

SPF = 1/60. # inverse FPS (frame-per-second)

class FrameUpdateEvent(GbEvent):
    """Event for handling frame update"""

    _ID = GbEventId.FRAME_UPDATE

    def __init__(self, system, eventHandler, window):
        """
        :param system: GB System state
        :param eventHandler: Input handler
        :param window:
        """
        super(self.__class__, self).__init__(system, eventHandler)
        self._window = window

    def do_call(self):
        """Event callback"""

        self._system.updateFrame = True
        self._system.t_VSynced = time.clock()

        if True:
            text = str(int(((self._system.exp_avg_emu)/SPF*100))) + "%"
            self._system.windowText = (True, text)


