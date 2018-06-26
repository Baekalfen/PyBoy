# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys

from ..Logger import logger
from .. import CPU, RAM, Cartridge, BootROM, LCD, Interaction, Timer, CoreDump

class Motherboard():
    from MemoryManager import __getitem__, __setitem__, transferDMAtoOAM
    from StateManager import saveState, loadState
    from Coordinator import calculateCycles, setSTATMode, checkLYC, tickFrame
    from ..CPU.flags import TIMER

    def __init__(self, gameROMFile, bootROMFile, window, profiling = False, debugger = None):
        if bootROMFile is not None:
            logger.info("Boot-ROM file provided")

        if profiling:
            logger.info("Profiling enabled")

        self.debugger = debugger
        self.MainWindow = window
        self.timer = Timer.Timer()
        self.interaction = Interaction.Interaction()
        self.cartridge = Cartridge.Cartridge(gameROMFile)
        self.bootROM = BootROM.BootROM(bootROMFile)
        self.ram = RAM.RAM(random=False)
        self.cpu = CPU.CPU(self, profiling)
        self.lcd = LCD.LCD(self)
        self.bootROMEnabled = True

        if "loadState" in sys.argv:
            self.loadState(self.cartridge.filename+".state")

        self.cartridge.loadRAM()
        if self.cartridge.rtcEnabled:
            self.cartridge.rtc.load(self.cartridge.filename)

        CoreDump.RAM = self.ram
        CoreDump.CPU = self.cpu

        self.serial_buffer = ""

    def get_serial(self):
        b = self.serial_buffer
        self.serial_buffer = ""
        return b

    def buttonEvent(self, key):
        self.interaction.keyEvent(key)
        self.cpu.setInterruptFlag(self.cpu.HightoLow)

    def stop(self, save):
        if save:
            self.cartridge.saveRAM()
            if self.cartridge.rtcEnabled:
                self.cartridge.rtc.save(self.cartridge.filename)


