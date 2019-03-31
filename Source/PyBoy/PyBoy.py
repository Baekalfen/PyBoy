#! /usr/local/bin/python2
# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import sys
import platform
import time

from . import BotSupport
from .ScreenRecorder import ScreenRecorder
from .MB.MB import Motherboard
from . import WindowEvent
from . import Window

from .opcodeToName import CPU_COMMANDS, CPU_COMMANDS_EXT
from .Logger import logger, addConsoleHandler
addConsoleHandler()


SPF = 1/60. # inverse FPS (frame-per-second)


class PyBoy():
    def __init__(self, win_type, scale, ROM, bootROM = None):
        self.ROM = ROM
        self.debugger = None
        self.window = Window.Window.getWindow(win_type, scale)

        self.profiling = "profiling" in sys.argv
        self.mb = Motherboard(ROM, bootROM, self.window, profiling = self.profiling, debugger = self.debugger)

        if not self.debugger is None:
            self.debugger.mb = self.mb

        self.avg_emu = 0
        self.avg_cpu = 0
        self.counter = 0
        self.setLimitEmulationSpeed(True, 0)
        self.screen_recorder = None


    def tick(self):
        done = False

        t_start = time.perf_counter() # Change to _ns when PyPy supports it

        for event in self.window.getEvents():
            if event == WindowEvent.Quit:
                done = True
            elif event == WindowEvent.ReleaseSpeedUp:
                self.limitEmulationSpeed ^= True
                logger.info("Speed limit: %s" % self.limitEmulationSpeed)
            elif event == WindowEvent.SaveState:
                self.mb.saveState(self.ROM + ".state")
            elif event == WindowEvent.LoadState:
                self.mb.loadState(self.ROM + ".state")
            elif event == WindowEvent.DebugToggle:
                # mb.cpu.breakAllow = True
                self.debugger.running ^= True
                # mb.cpu.breakOn ^= True
            elif event == WindowEvent.Pass:
                pass # Used in place of None in Cython, when key isn't mapped to anything
            elif event == WindowEvent.ScreenRecordingToggle:
                if not self.screen_recorder:
                    self.screen_recorder = ScreenRecorder(self.getScreenBufferFormat())
                else:
                    self.screen_recorder.save()
                    self.screen_recorder = None
            else:  # Right now, everything else is a button press
                self.mb.buttonEvent(event)

        self.mb.tickFrame()
        self.window.updateDisplay()

        if self.screen_recorder:
            self.screen_recorder.add_frame(self.window.getScreenBuffer())

        t_cpu = time.perf_counter()

        if self.limitEmulationSpeed:
            self.window.framelimiter(1)
        elif self.maxEmulationSpeed > 0:
            self.window.framelimiter(self.maxEmulationSpeed)

        t_emu = time.perf_counter()

        secs = t_emu-t_start
        self.avg_emu = 0.9 * self.avg_emu + 0.1 * secs

        secs = t_cpu-t_start
        self.avg_cpu = 0.9 * self.avg_cpu + 0.1 * secs

        if self.counter % 60 == 0:
            text = "CPU/frame: %0.2f%% Emulation: x%d" % (self.avg_cpu/SPF*100, round(SPF/self.avg_emu))
            self.window.setTitle(text)
            self.counter = 0
        self.counter += 1

        return done

    def stop(self, save=True):
        logger.info("###########################")
        logger.info("# Emulator is turning off #")
        logger.info("###########################")
        self.mb.stop(save)

        if self.profiling:
            import numpy as np
            np.set_printoptions(threshold=np.inf)
            argMax = np.argsort(self.mb.cpu.hitRate)
            for n in argMax[::-1]:
                if self.mb.cpu.hitRate[n] != 0:
                    print("%3x %16s %s" % (n, CPU_COMMANDS[n] if n<0x100 else CPU_COMMANDS_EXT[n-0x100], self.mb.cpu.hitRate[n]))


    ###########################
    #
    # Scripts and bot methods

    def getScreenBuffer(self):
        return self.window

    def getScreenBufferFormat(self):
        return "RGBA" if self.mb.window.alphaMask == 0x0000007F else "ARGB"

    def getMemoryValue(self, addr):
        return self.mb.getitem(addr)

    def setMemoryValue(self, addr, value):
        self.mb.setitem(addr, value)

    def sendInput(self, event):
        self.mb.buttonEvent(event)

    def getMotherBoard(self):
        return self.mb

    def getSprite(self, index):
        return BotSupport.Sprite(self.mb, index)

    def getTileView(self, high):
        return BotSupport.TileView(self.mb, high)

    def getScreenPosition(self):
        return (self.mb.getitem(0xFF43), self.mb.getitem(0xFF42))

    def saveState(self, filename):
        self.mb.saveState(filename)

    def loadState(self, filename):
        self.mb.loadState(filename)

    def getSerial(self):
        return self.mb.getSerial()

    def disableTitle(self):
        self.window.disableTitle()

    def setLimitEmulationSpeed(self, v, max_speed=0):
        self.limitEmulationSpeed = v
        if max_speed > 5:
            logger.warning("The emulation speed might not be accurate, when higher than 5")
        self.maxEmulationSpeed = max_speed
