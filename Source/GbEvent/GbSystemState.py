# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

import time


class GbSystemState(object):
    """GB system state

    Simplified system state
    """

    def __init__(self):
        self._frameCount = 0
        self._quit = False
        self._debug = False
        self._updateFrame = False
        self._dpadControl = 0xF
        self._buttonControl = 0xF
        self._speedMultiplier = 1.0
        self._exp_avg_emu = 0
        self._t_start = 0
        self._t_VSynced = 0
        self._windowText = (False, '[PyBoy]')

    @property
    def frameCount(self):
        return self._frameCount

    @frameCount.setter
    def frameCount(self, val):
        self._frameCount = val

    @property
    def quit(self):
        return self._quit

    @quit.setter
    def quit(self, val):
        self._quit = quit

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, val):
        self._debug = val

    @property
    def updateFrame(self):
        return self._updateFrame

    @updateFrame.setter
    def updateFrame(self, val):
        self._updateFrame = val

    @property
    def dpadControl(self):
        return self._dpadControl

    @dpadControl.setter
    def dpadControl(self, val):
        self._dpadControl = val

    @property
    def buttonControl(self):
        return self._buttonControl

    @buttonControl.setter
    def buttonControl(self, val):
        self._buttonControl = val

    @property
    def speedMultiplier(self):
        return self._speedMultiplier

    @speedMultiplier.setter
    def speedMultiplier(self, val):
        self._speedMultiplier = val

    @property
    def exp_avg_emu(self):
        return self._exp_avg_emu

    @exp_avg_emu.setter
    def exp_avg_emu(self, val):
        self._exp_avg_emu = val

    @property
    def t_start(self):
        return self._t_start

    @t_start.setter
    def t_start(self, val):
        self._t_start = val

    @property
    def t_VSynced(self):
        return self._t_VSynced

    @t_VSynced.setter
    def t_VSynced(self, val):
        self._t_VSynced = val

    @property
    def windowText(self):
        return self._windowText

    @windowText.setter
    def windowText(self, val):
        self._windowText = val

    def update(self):
        self._exp_avg_emu = 0.9 * self._exp_avg_emu + 0.1 * (self._t_VSynced-self._t_start)
        self._t_start = time.clock()

    def getInputState(self, input_reg):

        P14 = (input_reg >> 4) & 1
        P15 = (input_reg >> 5) & 1

        input_reg = 0xFF & (input_reg | 0b11001111)
        if P14 == 1 and P15 == 1:
            pass
        elif P14 == 0 and P15 == 0:
            pass
        elif P14 == 0:
            input_reg &= self._dpadControl
        elif P15 == 0:
            input_reg &= self._buttonControl

        return input_reg
