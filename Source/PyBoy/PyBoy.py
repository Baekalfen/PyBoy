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

        self.exp_avg_emu = 0
        self.exp_avg_cpu = 0
        self.t_start = 0
        self.t_start_ = 0
        self.t_VSynced = 0
        self.t_frameDone = 0
        self.counter = 0
        self.limitEmulationSpeed = True
        self.screen_recorder = None


    def tick(self):
        done = False
        self.exp_avg_emu = 0.9 * self.exp_avg_emu + 0.1 * (self.t_VSynced-self.t_start)
        self.exp_avg_cpu = 0.9 * self.exp_avg_cpu + 0.1 * (self.t_frameDone-self.t_start_)

        self.t_start_ = time.time() # Real-world time
        self.t_start = time.clock() # Time on the CPU
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

        if self.debugger is None:
            self.mb.tickFrame()
        else:
            if not self.debugger.tick(): # Returns false on keyboard interrupt
                done = True

            if not self.debugger.running:
                self.mb.tickFrame()
        self.window.updateDisplay()

        if self.screen_recorder:
            self.screen_recorder.add_frame(self.window.getScreenBuffer())

        self.t_VSynced = time.clock()

        # Trying to avoid VSync'ing on a frame, if we are out of time
        if self.limitEmulationSpeed:
            # This one makes time and frame syncing work, but messes with time.clock()
            self.window.framelimiter()
        self.t_frameDone = time.time()

        if self.counter % 60 == 0:
            text = "%0.0f %0.0f" % ((self.exp_avg_emu)/SPF*100, (self.exp_avg_cpu)/SPF*100)
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

    def setLimitEmulationSpeed(self, v):
        self.limitEmulationSpeed = v
