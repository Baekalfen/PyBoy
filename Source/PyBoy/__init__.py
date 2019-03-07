#! /usr/local/bin/python2
# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys
import time
import numpy as np
from PyBoy.ScreenRecorder import ScreenRecorder
import platform

from .MB import Motherboard
from .WindowEvent import WindowEvent
from .Logger import logger, addConsoleHandler
from . import BotSupport
from . import Logger
from .OpcodeToName import CPU_COMMANDS, CPU_COMMANDS_EXT


SPF = 1/60. # inverse FPS (frame-per-second)

class PyBoy():
    def __init__(self, window, ROM, bootROM = None):
        self.debugger = None
        self.mb = None
        self.window = window

        if "debug" in sys.argv and platform.system() != "Windows":
            self.debugger = Debug()
            self.debugger.tick()
        else:
            addConsoleHandler()

        self.profiling = "profiling" in sys.argv
        self.mb = Motherboard(ROM, bootROM, window, profiling = self.profiling, debugger = self.debugger)

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
                self.mb.saveState(self.mb.cartridge.filename+".state")
            elif event == WindowEvent.LoadState:
                self.mb.loadState(self.mb.cartridge.filename+".state")
            elif event == WindowEvent.DebugToggle:
                # mb.cpu.breakAllow = True
                self.debugger.running ^= True
                # mb.cpu.breakOn ^= True
            elif event == WindowEvent.ScreenRecordingToggle:
                if not self.screen_recorder:
                    self.screen_recorder = ScreenRecorder()
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
            self.screen_recorder.add_frame(self.window.getScreenBuffer().copy())

        self.t_VSynced = time.clock()

        if self.limitEmulationSpeed:
            self.window.frameLimiter()
        self.t_frameDone = time.time()


        if self.counter % 60 == 0:
            text = "%d %d" % ((self.exp_avg_emu)/SPF*100, (self.exp_avg_cpu)/SPF*100)
            self.window.setTitle(text)
            self.counter = 0
        self.counter += 1

        return done

    def stop(self, save=True):
        logger.info("###########################")
        logger.info("# Emulator is turning off #")
        logger.info("###########################")
        self.window.stop()
        self.mb.stop(save)

        if self.profiling:
            np.set_printoptions(threshold=np.inf)
            argMax = np.argsort(self.mb.cpu.hitRate)
            for n in argMax[::-1]:
                if self.mb.cpu.hitRate[n] != 0:
                    print("%3x %16s %s" % (n, CPU_COMMANDS[n] if n<0x100 else CPU_COMMANDS_EXT[n-0x100], self.mb.cpu.hitRate[n]))


    ###########################
    #
    # Scripts and bot methods

    def getScreenBuffer(self):
        return self.window.getScreenBuffer()

    def getMemoryValue(self, addr):
        return self.mb[addr]

    def setMemoryValue(self, addr, value):
        self.mb[addr] = value

    def sendInput(self, event_list):
        for event in event_list:
            self.mb.buttonEvent(event)

    def getMotherBoard(self):
        return self.mb

    def getSprite(self, index):
        return BotSupport.Sprite(self.mb.lcd, index)

    def getTileView(self, high):
        return BotSupport.TileView(self.mb.lcd, high)

    def getScreenPosition(self):
        return (self.mb[0xFF43], self.mb[0xFF42])
