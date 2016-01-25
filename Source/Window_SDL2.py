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
        self._windowSurface_temp = self._window.get_surface()


        self._windowSurface = sdl2.ext.subsurface(self._windowSurface_temp,(0,0)+scaledResolution)
        self._windowSurfaceBuffer = sdl2.ext.pixels2d(self._windowSurface)
        self._screenBuffer = numpy.ndarray(gameboyResolution,dtype='int32')
        self._screenBuffer.fill(0x00558822)
        self._window.show()
        self.fonts = {}

        self.tileDataWidth = 0x100
        self.tileDataHeight = 0x60
        self.tileDataBuffer = numpy.ndarray((self.tileDataWidth,self.tileDataHeight),dtype='int32')

        self.tileView1Width = 0x100
        self.tileView1Height = 0x100        
        self.tileView1Buffer = numpy.ndarray((self.tileView1Width,self.tileView1Height),dtype='int32')
        
        self.tileView2Width = 0x100
        self.tileView2Height = 0x100
        self.tileView2Buffer = numpy.ndarray((self.tileView2Width,self.tileView2Height),dtype='int32')

        if __debug__:
            # Tile Data
            sdl2.ext.Window.DEFAULTPOS = (0, 0)
            self.tileDataWindow = sdl2.ext.Window("Tile Data", size=(self.tileDataWidth, self.tileDataHeight))
            self.tileDataWindowSurface = self.tileDataWindow.get_surface()
            self.tileDataWindowSurfaceBuffer = sdl2.ext.pixels2d(self.tileDataWindowSurface)
            self.tileDataWindow.show()

            # Background View 1
            sdl2.ext.Window.DEFAULTPOS = (self.tileDataWidth, 0)
            self.tileView1Window = sdl2.ext.Window("Tile View 1", size=(self.tileView1Width, self.tileView1Height))
            self.tileView1WindowSurface = self.tileView1Window.get_surface()
            self.tileView1WindowSurfaceBuffer = sdl2.ext.pixels2d(self.tileView1WindowSurface)
            self.tileView1Window.show()

            # Background View 2
            sdl2.ext.Window.DEFAULTPOS = (self.tileDataWidth + self.tileView1Width, 0)
            self.tileView2Window = sdl2.ext.Window("Tile View 2", size=(self.tileView2Width, self.tileView2Height))
            self.tileView2WindowSurface = self.tileView2Window.get_surface()
            self.tileView2WindowSurfaceBuffer = sdl2.ext.pixels2d(self.tileView2WindowSurface)
            self.tileView2Window.show()

    def dump(self,filename, tiles=False):
        sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle._windowSurface_temp,filename+".bmp")
        if tiles:
            sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle.tileDataWindowSurface,filename+"tileData.bmp")
            sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle.tileView1WindowSurface,filename+"tileView1.bmp")
            sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle.tileView2WindowSurface,filename+"tileView2.bmp")

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
            self.tileView1Window.refresh()
            self.tileView2Window.refresh()
        self._window.refresh()

    def blitBuffer(self,b1,b2,scale=1):
        assert isinstance(scale, int), "Scale has to be int!"
        assert b1.shape[0]*scale == b2.shape[0], "Can't blit buffers of different size!"
        assert b1.shape[1]*scale == b2.shape[1], "Can't blit buffers of different size!"

        if scale == 1:
            # assert b1.shape == b2.shape, "Can't blit buffers of different size!"
            b1[:] = b2[:]
        else:
            for x in xrange(b1.shape[0]):
                for y in xrange(b1.shape[1]):
                    for sx in xrange(scale):
                        for sy in xrange(scale):
                            b1[(x*scale)+sx,(y*scale)+sy] = b2[x,y]

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
