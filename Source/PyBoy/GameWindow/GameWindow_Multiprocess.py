# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys
import time
import numpy as np
import warnings

import multiprocessing
from multiprocessing import Process, Pipe, Queue
from .. import shmarray

from .. import CoreDump
from ..WindowEvent import WindowEvent
from ..GameWindow import AbstractGameWindow
from ..GameWindow import SdlGameWindow

from ..LCD import VIDEO_RAM, OBJECT_ATTRIBUTE_MEMORY, PaletteRegister, LCDCRegister
from ..Logger import logger

gameboyResolution = (160, 144)

class MultiprocessGameWindow(AbstractGameWindow):
    def __init__(self, scale=1):
        super(self.__class__, self).__init__(scale)

        self.count = 0

        Window = SdlGameWindow # TODO: Works with any GameWindow

        CoreDump.windowHandle = self
        logger.debug("GameWindow Multiprocess initialization")

        self.scanlineParameters = np.zeros(shape=(gameboyResolution[0],4), dtype='uint8')

        self.scanlineParameters_clone = shmarray.zeros(shape=(gameboyResolution[0],4), dtype='uint8')
        self.VRAM_clone = shmarray.zeros(shape=(VIDEO_RAM,), dtype='uint8')
        self.OAM_clone = shmarray.zeros(shape=(OBJECT_ATTRIBUTE_MEMORY,), dtype='uint8')

        self.pipe_slave, self.pipe = Pipe(True) # Bidirectional pipe for slave
        self.process = Process(target=MultiprocessSlave, args=(Window, self.scanlineParameters_clone, self.VRAM_clone, self.OAM_clone, self.pipe_slave, self._scale))
        self.process.start()

    def dump(self,filename):
        self.pipe.send(('dump', filename))

    def setTitle(self,title):
        self.pipe.send(('setTitle', (title,)))

    def getEvents(self):
        self.pipe.send(('getEvents', tuple()))
        return self.pipe.recv() # Using events as a synchronization point

    def updateDisplay(self):
        self.pipe.send(('updateDisplay', tuple()))

    def VSync(self):
        self.pipe.send(('VSync', tuple()))

    def stop(self):
        self.pipe.send(('stop', tuple()))

    def scanline(self, y, lcd):
        self.scanlineParameters[y] = lcd.get_view_port() + lcd.get_window_pos()

    def renderScreen(self, lcd):
        self.scanlineParameters_clone[:] = self.scanlineParameters

        if self.VRAM_changed:
            self.VRAM_clone[:] = lcd.VRAM

        if self.OAM_changed:
            self.OAM_clone[:] = lcd.OAM

        self.pipe.send(('renderScreen', (self.tiles_changed, self.flush_cache, lcd.LCDC.value, lcd.BGP.value, lcd.OBP0.value, lcd.OBP1.value)))
        self.tiles_changed.clear()
        self.flush_cache = False

        self.VRAM_changed = False
        self.OAM_changed = False

    def blankScreen(self):
        self.pipe.send(('blankScreen', tuple()))

    def getScreenBuffer(self):
        self.pipe.send(('getScreenBuffer', tuple()))
        return self.pipe.recv()

    def refreshDebugWindows(self, lcd):
        self.pipe.send(('refreshDebugWindows', tuple()))


def MultiprocessSlave(Window, scanlineParameters, VRAM, OAM, pipe, scale):
    window = Window(scale)
    window.scanlineParameters = scanlineParameters
    lcdDummy = LCDDummy(VRAM, OAM)

    running = True
    while(running):
        (command, args) = pipe.recv()

        if command == 'dump':
            window.dump(*args)
        elif command == 'setTitle':
            window.setTitle(*args)
        elif command == 'getEvents':
            events = window.getEvents(*args)
            pipe.send(events)
        elif command == 'updateDisplay':
            window.updateDisplay(*args)
        elif command == 'VSync':
            window.VSync(*args)
        elif command == 'stop':
            window.stop(*args)
            running = False
        elif command == 'renderScreen':
            lcdDummy.update(*args[2:])
            window.tiles_changed = args[0]
            window.flush_cache = args[1]
            window.renderScreen(lcdDummy)
        elif command == 'blankScreen':
            window.blankScreen(*args)
        elif command == 'getScreenBuffer':
            pipe.send(window.getScreenBuffer(*args))
        elif command == 'refreshDebugWindows':
            window.refreshDebugWindows(lcdDummy)
        else:
            raise Exception("Unknown command: %s" % command)

class LCDDummy():
    def __init__(self, VRAM, OAM):
        self.VRAM = VRAM
        self.OAM = OAM

        self.LCDC = LCDCRegister(0)
        self.BGP = PaletteRegister(0xFC)
        self.OBP0 = PaletteRegister(0xFF)
        self.OBP1 = PaletteRegister(0xFF)

    def update(self, LCDCvalue, BGPvalue, OBP0value, OBP1value):
        self.LCDC.set(LCDCvalue)
        self.BGP.set(BGPvalue)
        self.OBP0.set(OBP0value)
        self.OBP1.set(OBP1value)

