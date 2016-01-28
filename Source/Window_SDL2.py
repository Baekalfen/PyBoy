# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys
from random import randint
import time
import sdl2
import sdl2.ext
import numpy
import CoreDump
import time

from WindowEvent import WindowEvent
import colors
# from Display import SCX, SCY

white = sdl2.ext.Color(*colors.white)
black = sdl2.ext.Color(*colors.black)

gameboyResolution = (160, 144)

class Window():

    def __init__(self, scale=1, debug=False):
        assert isinstance(scale, int), "Window scale has to be an integer!"

        CoreDump.windowHandle = self

        print "SDL initialization"
        sdl2.ext.init()

        self._scale = scale
        scaledResolution = tuple(x * scale for x in gameboyResolution)

        self._window = sdl2.ext.Window("PyBoy", size=scaledResolution)
        self._windowSurface = self._window.get_surface()

        # Only used for VSYNC
        self.win = sdl2.SDL_CreateWindow("", 0,0,0,0, 0) # Hack doesn't work, if hidden # sdl2.SDL_WINDOW_HIDDEN)
        self.renderer = sdl2.SDL_CreateRenderer(self.win, -1, sdl2.SDL_RENDERER_PRESENTVSYNC)

        self._screenBuffer = sdl2.ext.pixels2d(self._windowSurface)
        self._screenBuffer.fill(0x00558822)
        self._window.show()
        self.fonts = {}

        tiles = 384
        self.tileDataWidth = 16*8 # Change the 16 to whatever wide you want the tile window
        self.tileDataHeight = ((tiles*8) / self.tileDataWidth)*8

        if __debug__:
            # Tile Data
            sdl2.ext.Window.DEFAULTPOS = (0, 0)
            self.tileDataWindow = sdl2.ext.Window("Tile Data", size=(self.tileDataWidth, self.tileDataHeight))
            self.tileDataWindowSurface = self.tileDataWindow.get_surface()
            self.tileDataBuffer = sdl2.ext.pixels2d(self.tileDataWindowSurface)
            self.tileDataWindow.show()
        # else:
        #     self.tileDataBuffer = numpy.ndarray((self.tileDataWidth,self.tileDataHeight),dtype='int32')

    def dump(self,filename, tiles=False):
        sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle._windowSurface_temp,filename+".bmp")
        if tiles:
            sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle.tileDataWindowSurface,filename+"tileData.bmp")

    def setTitle(self,title):
        sdl2.ext.title(self._window,title)
        # sdl2.SDL_SetWindowTitle(self._window,title)

    def getEvents(self):
        events = []

        # http://pysdl2.readthedocs.org/en/latest/tutorial/pong.html
        # https://wiki.libsdl.org/SDL_Scancode#Related_Enumerations

        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                events.append(WindowEvent.Quit)

            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_UP:
                    events.append(WindowEvent.PressArrowUp)
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    events.append(WindowEvent.PressArrowDown)
                elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    events.append(WindowEvent.PressArrowRight)
                elif event.key.keysym.sym == sdl2.SDLK_LEFT:
                    events.append(WindowEvent.PressArrowLeft)
                elif event.key.keysym.sym == sdl2.SDLK_a:
                    events.append(WindowEvent.PressButtonA)
                elif event.key.keysym.sym == sdl2.SDLK_s:
                    events.append(WindowEvent.PressButtonB)
                elif event.key.keysym.sym == sdl2.SDLK_RETURN:
                    events.append(WindowEvent.PressButtonStart)
                elif event.key.keysym.sym == sdl2.SDLK_BACKSPACE:
                    events.append(WindowEvent.PressButtonSelect)
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym == sdl2.SDLK_UP:
                    events.append(WindowEvent.ReleaseArrowUp)
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    events.append(WindowEvent.ReleaseArrowDown)
                elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    events.append(WindowEvent.ReleaseArrowRight)
                elif event.key.keysym.sym == sdl2.SDLK_LEFT:
                    events.append(WindowEvent.ReleaseArrowLeft)
                elif event.key.keysym.sym == sdl2.SDLK_a:
                    events.append(WindowEvent.ReleaseButtonA)
                elif event.key.keysym.sym == sdl2.SDLK_s:
                    events.append(WindowEvent.ReleaseButtonB)
                elif event.key.keysym.sym == sdl2.SDLK_RETURN:
                    events.append(WindowEvent.ReleaseButtonStart)
                elif event.key.keysym.sym == sdl2.SDLK_BACKSPACE:
                    events.append(WindowEvent.ReleaseButtonSelect)

        return events

    def updateDisplay(self):
        # print "Updating Display"
        if __debug__:
            self.tileDataWindow.refresh()
        self._window.refresh()

        # self.VSync()

    def VSync(self):
        sdl2.SDL_RenderPresent(self.renderer)

    def stop(self):
        # self._window.stop()
        sdl2.ext.quit()

if __name__ == "__main__":
    debug = False
    window = Window(4, debug)

    sdl2.ext.fill(window._windowSurface,white)

    print type(window._windowSurfaceBuffer)
    print window._windowSurfaceBuffer[100,100]
    for x in xrange(100,200):
        window._windowSurfaceBuffer[x,100] = 0x00000000

    window.updateDisplay()

    done = False
    while not done:
        if window.getEvents() != []:
            print "Closing!"
            done = True
        window.updateDisplay()
        time.sleep(1/60.)
    sdl2.ext.quit()
