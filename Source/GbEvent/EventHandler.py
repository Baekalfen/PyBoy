# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

import time
from . import WindowEvent

SPF = 1/60. # inverse FPS (frame-per-second)

class EventHandler(object):

    def __init__(self, window, mb):

        self.window = window
        self.mb = mb
        self.exp_avg_emu = 0
        self.exp_avg_cpu = 0
        self.t_start = 0
        self.t_VSynced = 0
        self.t_frameDone = 0
        self.counter = 0
        self.limitEmulationSpeed = True

        self.exitCondition = False

    def hasExitCondition(self):
        return self.exitCondition

    def cycle(self, debugger=None):

        self.exp_avg_emu = 0.9 * self.exp_avg_emu + 0.1 * (self.t_VSynced-self.t_start)

        self.t_start = time.clock()
        for event in self.window.getEvents():
            if event == WindowEvent.Quit:
                self.window.stop()
                self.exitCondition = True
                return
            elif event == WindowEvent.ReleaseSpeedUp:
                self.limitEmulationSpeed ^= True
            # elif event == WindowEvent.PressSpeedUp:
            #     self.limitEmulationSpeed = False
            elif event == WindowEvent.SaveState:
                self.mb.saveState(self.mb.cartridge.filename+".state")
            elif event == WindowEvent.LoadState:
                self.mb.loadState(self.mb.cartridge.filename+".state")
            elif event == WindowEvent.DebugToggle and debugger is not None:
                # self.mb.cpu.breakAllow = True
                debugger.running ^= True
            else:  # Right now, everything else is a button press
                self.mb.buttonEvent(event)

        if not debugger is None and debugger.running:
            action = debugger.tick()

        else:
            self.mb.tickFrame()

        self.window.updateDisplay()


        # # Trying to avoid VSync'ing on a frame, if we are out of time
        # if self.limitEmulationSpeed or (time.clock()-self.t_start < SPF):
        #     # This one makes time and frame syncing work, but messes with time.clock()
        #     self.window.VSync()

        self.t_VSynced = time.clock()

        if self.counter % 60 == 0:
            text = str(int(((self.exp_avg_emu)/SPF*100))) + "%"
            self.window._window.title = text
            counter = 0
        self.counter += 1
