# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from MB import Motherboard
from GbEvent import WindowEvent
from GbEvent import EventHandler

from GbLogger import gblogger


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

        if self.bootRom is not None:
            gblogger.debug("Starting with boot ROM")
        self.mb = Motherboard(self.rom, self.bootRom, self.window)

        if loadState:
            self.mb.loadState(self.mb.cartridge.filename+".state")

        self.mb.cartridge.loadRAM()
        if self.mb.cartridge.rtcEnabled:
            self.mb.cartridge.rtc.load(self.mb.cartridge.filename)

        self.eventHandler = EventHandler(self.window, self.mb)

    def start(self):
        while not self.eventHandler.hasExitCondition():
            self.eventHandler.cycle(self.debugger)

        self.__on_stop()

    def __on_stop(self):
        gblogger.info("# Emulator is turning off #")

        self.mb.cartridge.saveRAM()
        if self.mb.cartridge.rtcEnabled:
            self.mb.cartridge.rtc.save(self.mb.cartridge.filename)

    def getDump(self):
        if self.mb is not None:
            self.mb.cpu.getDump()
