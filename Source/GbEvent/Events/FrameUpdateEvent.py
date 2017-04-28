# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from . import GbEvent, GbEventId
import time

from GbLogger import gblogger

SPF = 1/60. # inverse FPS (frame-per-second)

class FrameUpdateEvent(GbEvent):

    _ID = GbEventId.FRAME_UPDATE

    def __init__(self, system, eventHandler, window):
        super(self.__class__, self).__init__(system, eventHandler)
        self._window = window

    def do_call(self):
        self._system.updateFrame = True
        self._system.t_VSynced = time.clock()

        if True:
            text = str(int(((self._system.exp_avg_emu)/SPF*100))) + "%"
            self._system.windowText = (True, text)


