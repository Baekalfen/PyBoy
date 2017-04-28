# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from MB import Motherboard
from GbEvent import WindowEvent
from GbEvent import EventLoop

from GbLogger import gblogger

from GbEvent import Events
from GbEvent.Events import GbEventId

from GbEvent import EventLoop

import time

class PyBoy(object):

    def __init__(self, bootROM, rom, window, loadState=False, debug=False, scale=1):
        self.debug = debug
        self.scale = scale
        self.bootRom = bootROM
        self.rom = rom
        self.window = window

        self.debugger = None
        if self.debug:
            self.debugger = Debug()
            self.debugger.tick()

        self.eventLoop = EventLoop(self.window)

        if self.bootRom is not None:
            gblogger.debug("Starting with boot ROM")
        self.mb = Motherboard(self.rom, self.bootRom, self.window,
                self.eventLoop.system)

        if loadState:
            self.mb.loadState(self.mb.cartridge.filename+".state")

        self.mb.cartridge.loadRAM()
        if self.mb.cartridge.rtcEnabled:
            self.mb.cartridge.rtc.load(self.mb.cartridge.filename)

        self.__registerEventHandlers()

    def __registerEventHandlers(self):
        eventHandler = self.eventLoop.getEventHandler()

        eventHandler.registerEventHandler(Events.DebugToggleEvent)
        eventHandler.registerEventHandler(Events.FrameUpdateEvent)
        eventHandler.registerEventHandler(Events.InputEvent)
        eventHandler.registerEventHandler(Events.MbTickEvent)
        eventHandler.registerEventHandler(Events.QuitEvent)
        eventHandler.registerEventHandler(Events.SaveStateEvent)
        eventHandler.registerEventHandler(Events.SpeedChangedEvent)

    def start(self):
        eventHandler = self.eventLoop.getEventHandler()

        try:
            while not self.eventLoop.hasExitCondition():
                self.eventLoop.cycle(self.mb)

                eventHandler.registerEvent(GbEventId.MB_TICK, self.mb,
                        self.debugger)
                eventHandler.registerEvent(GbEventId.FRAME_UPDATE,
                        self.window)

        except Exception:
            gblogger.exception('An error occured in the PyBoy main event loop')

        self.__on_stop()

    def __on_stop(self):
        gblogger.info("# Emulator is turning off #")

        self.mb.cartridge.saveRAM()
        if self.mb.cartridge.rtcEnabled:
            self.mb.cartridge.rtc.save(self.mb.cartridge.filename)

    def getDump(self):
        if self.mb is not None:
            self.mb.cpu.getDump()
