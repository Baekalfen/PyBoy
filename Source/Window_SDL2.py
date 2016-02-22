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

        self._screenBuffer = sdl2.ext.pixels2d(self._windowSurface)
        self._screenBuffer.fill(0x00558822)
        self._window.show()

        # Only used for VSYNC
        self.win = sdl2.SDL_CreateWindow("", 0,0,0,0, 0) # Hack doesn't work, if hidden # sdl2.SDL_WINDOW_HIDDEN)
        self.renderer = sdl2.SDL_CreateRenderer(self.win, -1, sdl2.SDL_RENDERER_PRESENTVSYNC)

        if __debug__:
            tiles = 384
            self.tileDataWidth = 16*8 # Change the 16 to whatever wide you want the tile window
            self.tileDataHeight = ((tiles*8) / self.tileDataWidth)*8

            # Tile Data
            sdl2.ext.Window.DEFAULTPOS = (0, 0)
            self.tileDataWindow = sdl2.ext.Window("Tile Data", size=(self.tileDataWidth, self.tileDataHeight))
            self.tileDataWindowSurface = self.tileDataWindow.get_surface()
            self.tileDataBuffer = sdl2.ext.pixels2d(self.tileDataWindowSurface)
            self.tileDataWindow.show()

            self.tileView1Width = 0x100
            self.tileView1Height = 0x100        
            
            self.tileView2Width = 0x100
            self.tileView2Height = 0x100

            # # Background View 1
            sdl2.ext.Window.DEFAULTPOS = (self.tileDataWidth, 0)
            self.tileView1Window = sdl2.ext.Window("Tile View 1", size=(self.tileView1Width, self.tileView1Height))
            self.tileView1WindowSurface = self.tileView1Window.get_surface()
            self.tileView1Buffer = sdl2.ext.pixels2d(self.tileView1WindowSurface)
            self.tileView1Window.show()

            # # Background View 2
            sdl2.ext.Window.DEFAULTPOS = (self.tileDataWidth + self.tileView1Width, 0)
            self.tileView2Window = sdl2.ext.Window("Tile View 2", size=(self.tileView2Width, self.tileView2Height))
            self.tileView2WindowSurface = self.tileView2Window.get_surface()
            self.tileView2Buffer = sdl2.ext.pixels2d(self.tileView2WindowSurface)
            self.tileView2Window.show()


    def dump(self,filename):
        sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle._windowSurface,filename+".bmp")
        if __debug__:
            sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle.tileDataWindowSurface,filename+"tileData.bmp")
            sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle.tileView2WindowSurface,filename+"tileView1.bmp")
            sdl2.surface.SDL_SaveBMP(CoreDump.windowHandle.tileView1WindowSurface,filename+"tileView2.bmp")

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
                elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    events.append(WindowEvent.Quit)
                elif event.key.keysym.sym == sdl2.SDLK_d:
                    events.append(WindowEvent.DebugNext)
                elif event.key.keysym.sym == sdl2.SDLK_SPACE:
                    events.append(WindowEvent.PressSpeedUp)
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
                elif event.key.keysym.sym == sdl2.SDLK_z:
                    events.append(WindowEvent.SaveState)
                elif event.key.keysym.sym == sdl2.SDLK_x:
                    events.append(WindowEvent.LoadState)
                elif event.key.keysym.sym == sdl2.SDLK_SPACE:
                    events.append(WindowEvent.ReleaseSpeedUp)

        return events

    def updateDisplay(self):
        # print "Updating Display"
        self._window.refresh()
        if __debug__:
            self.tileDataWindow.refresh()
            self.tileView1Window.refresh()
            self.tileView2Window.refresh()
        # self.VSync()

    def VSync(self):
        sdl2.SDL_RenderPresent(self.renderer)

    def stop(self):
        # self._window.stop()
        sdl2.ext.quit()

