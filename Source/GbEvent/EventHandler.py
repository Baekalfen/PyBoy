# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

import time
from GbSystemState import GbSystemState
from GbEventLoop import GbEventLoop

from GbLogger import gblogger

from . import Events

class EventLoop(object):

    def __init__(self, window):

        self.window = window

        self.system = GbSystemState()
        self.eventHandler = GbEventLoop(self.system)


    def hasExitCondition(self):
        return self.system.quit

    def cycle(self):

        # 1. Handle events
        # 2. Tick MB/debugger
        # 3. Update display

        self.system.update()

        buttons = self.window.getEvents()

        # FIXME: This registerEvent-call does not belong here
        if len(buttons) > 0:
            self.eventHandler.registerEvent(GbEventId.INPUT_UPDATE, buttons)

        self.eventHandler.cycle()

        if self.system.updateFrame:
            self.window.updateDisplay()
            self.system.updateFrame = False

        if self.system.windowText[0]:
            self.window._window.title = self.system.windowText[1]

        self.system.t_VSynced = time.clock()

    def getEventHandler(self):
        return self.eventHandler
