# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from .Events import GbEvent
import time


class GbEventLoop(object):
    """GB event loop and handler class"""

    def __init__(self, system, eventHandlers=None):
        self._eventStack = []
        self._system = system

        if eventHandlers:
            self._eventHandlers = eventHandlers
        else:
            self._eventHandlers = {}

    def pushEvent(self, eventId, *args, **kwargs):
        """Push event to event-stack"""
        try:
            eventClass = self._eventHandlers[eventId]
        except KeyError:
            raise RuntimeError('Unrecognized eventId: {}'.format(eventId))

        self._eventStack.append(eventClass(self._system, *args, **kwargs))

    def registerEventHandler(self, eventHandler):
        """Register event-handler"""

        if not issubclass(eventHandler, GbEvent):
            raise TypeError('eventHandler must be a subclass of GbEvent')

        eventId = eventHandler.getId()
        if eventId in self._eventHandlers:
            raise RuntimeError('Eventhandler already excists')

        self._eventHandlers[eventId] = eventHandler


    def __popEvent(self):
        """Pop event from event-stack by execution do_call-method"""

        if len(self._eventStack == 0):
            return 0

        event = self._eventStack.pop()
        event.do_call()

        return len(self._eventStack)

    def cycle(self, debugger=None):

        while self.__popEvent():
            continue
