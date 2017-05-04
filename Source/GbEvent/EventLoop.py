# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

import time
from GbSystemState import GbSystemState
from GbEventLoop import GbEventLoop
from . import GbEventId

from GbLogger import gblogger

from . import Events

class EventLoop(object):
    """System event loop"""

    def __init__(self, window):
        """Initialize system and event-handler

        :param window: Game window
        """

        self.window = window

        self.system = GbSystemState()
        self.eventHandler = GbEventLoop(self.system)


    def hasExitCondition(self):
        """True if system has reach an exit-state, false otherwise"""
        return self.system.quit

    def cycle(self, mb):
        """Single loop cycle

        :param mb: System motherboard-object
        """

        # 1. Route input-events from game-window to event-handler
        # 2. Handle events
        # 3. Update display

        self.system.update()

        buttons = self.window.getEvents()

        # FIXME: This registerEvent-call does not belong here
        if len(buttons) > 0:
            self.eventHandler.registerEvent(GbEventId.INPUT_UPDATE, mb, buttons)

        self.eventHandler.cycle()

        if self.system.updateFrame:
            self.window.updateDisplay()
            self.system.updateFrame = False

        if self.system.windowText[0]:
            self.window._window.title = self.system.windowText[1]

        self.system.t_VSynced = time.clock()

    def getEventHandler(self):
        """Returns current event-handler object"""
        return self.eventHandler
