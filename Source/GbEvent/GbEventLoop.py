# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from GbEvent import GbEvent
import time

from GbLogger import gblogger


class GbEventCallbacks(object):
    """GB callback handler"""

    def __init__(self):
        self.__callbacks = []
        self.__called = False
        self.__args = None
        self.__kwargs = None

    def registerCallback(self, callback):
        self.__callbacks.append(callback)

    def prepare_call(self, *args, **kwargs):
        if self.__called:
            return
        self.__args = args
        self.__kwargs = kwargs
        self.__called = True

    def do_call(self):
        if not self.__called:
            return

        for cb in self.__callbacks:
            cb(*self.__args, **self.__kwargs).do_call()

        self.__called = False
        self.__args = None
        self.__kwargs = None


class GbEventLoop(object):
    """GB event loop and handler class"""

    def __init__(self, system, eventHandlers=None):
        self._system = system

        if eventHandlers:
            self._eventHandlers = eventHandlers
        else:
            self._eventHandlers = {}

    def registerEvent(self, event, *args, **kwargs):
        """Register event"""

        # Get event ID
        try:
            eventId = event.getId()
        except AttributeError:
            eventId = event

        # Get callbacks
        try:
            callbacks = self._eventHandlers[eventId]
        except KeyError:
            raise RuntimeError('Unrecognized eventId: {}'.format(eventId))

        # Register event with callbacks
        callbacks.prepare_call(self._system, self, *args, **kwargs)

    def registerEventHandler(self, eventHandler):
        """Register event-handler"""

        if not issubclass(eventHandler, GbEvent):
            raise TypeError('eventHandler must be a subclass of GbEvent')

        eventId = eventHandler.getId()

        try:
            callbacks = self._eventHandlers[eventId]
        except KeyError:
            callbacks = GbEventCallbacks()

        callbacks.registerCallback(eventHandler)
        self._eventHandlers[eventId] = callbacks

    def cycle(self):

        for event in self._eventHandlers:
            self._eventHandlers[event].do_call()

