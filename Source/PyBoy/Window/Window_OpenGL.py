#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GLUT.freeglut

from .. import WindowEvent
from .Window_SDL2 import SdlWindow
from ..Logger import logger

gameboyResolution = (160, 144)

class OpenGLWindow(SdlWindow):
    def __init__(self, scale=1):
        super(self.__class__, self).__init__(scale)

    def init(self):
        self.colorPalette = [x << 8 for x in self.colorPalette] # (0xFFFFFF00,0x99999900,0x55555500,0x00000000)
        self.alphaMask = 0x0000007F

        glutInit()
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
        glutInitWindowSize(*self._scaledResolution)
        glutCreateWindow("PyBoy")
        glutKeyboardFunc(self._key)
        glutKeyboardUpFunc(self._keyUp)
        glutSpecialFunc(self._spec)
        glutSpecialUpFunc(self._specUp)
        self.events = []

        glPixelZoom(self._scale,self._scale)
        glutReshapeFunc(self.glReshape)
        glutDisplayFunc(self.glDraw)

    # Cython does not cooperate with Lambdas
    def _key(self, c, x, y):
        self.glKeyboard(c.decode("ascii"), x, y, False)
    def _keyUp(self, c, x, y):
        self.glKeyboard(c.decode("ascii"), x, y, True)
    def _spec(self, c, x, y):
        self.glKeyboardSpecial(c, x, y, False)
    def _specUp(self, c, x, y):
        self.glKeyboardSpecial(c, x, y, True)

    def dump(self,filename):
        pass

    def setTitle(self,title):
        glutSetWindowTitle(title)

    def getEvents(self):
        evts = self.events
        self.events = []
        return evts

    def glKeyboardSpecial(self, c, x, y, up):
        if up:
            if c == GLUT_KEY_UP:
                self.events.append(WindowEvent.ReleaseArrowUp)
            if c == GLUT_KEY_DOWN:
                self.events.append(WindowEvent.ReleaseArrowDown)
            if c == GLUT_KEY_LEFT:
                self.events.append(WindowEvent.ReleaseArrowLeft)
            if c == GLUT_KEY_RIGHT:
                self.events.append(WindowEvent.ReleaseArrowRight)
        else:
            if c == GLUT_KEY_UP:
                self.events.append(WindowEvent.PressArrowUp)
            if c == GLUT_KEY_DOWN:
                self.events.append(WindowEvent.PressArrowDown)
            if c == GLUT_KEY_LEFT:
                self.events.append(WindowEvent.PressArrowLeft)
            if c == GLUT_KEY_RIGHT:
                self.events.append(WindowEvent.PressArrowRight)

    def glKeyboard(self, c, x, y, up):
        if up:
            if c == 'a':
                self.events.append(WindowEvent.ReleaseButtonA)
            elif c == 's':
                self.events.append(WindowEvent.ReleaseButtonB)
            elif c == 'z':
                self.events.append(WindowEvent.SaveState)
            elif c == 'x':
                self.events.append(WindowEvent.LoadState)
            elif c == ' ':
                self.events.append(WindowEvent.ReleaseSpeedUp)
            elif c == chr(8):
                self.events.append(WindowEvent.ReleaseButtonSelect)
            elif c == chr(13):
                self.events.append(WindowEvent.ReleaseButtonStart)
        else:
            if c == 'a':
                self.events.append(WindowEvent.PressButtonA)
            elif c == 's':
                self.events.append(WindowEvent.PressButtonB)
            elif c == chr(27):
                self.events.append(WindowEvent.Quit)
            elif c == 'd':
                self.events.append(WindowEvent.DebugToggle)
            elif c == ' ':
                self.events.append(WindowEvent.PressSpeedUp)
            elif c == 'i':
                self.events.append(WindowEvent.ScreenRecordingToggle)
            elif c == chr(8):
                self.events.append(WindowEvent.PressButtonSelect)
            elif c == chr(13):
                self.events.append(WindowEvent.PressButtonStart)


    def glReshape(self, width, height):
        scale = max(min(float(height)/gameboyResolution[1], float(width)/gameboyResolution[0]), 1)
        self._scaledResolution = tuple([int(x * scale) for x in gameboyResolution])
        glPixelZoom(scale,scale)
        # glutReshapeWindow(*self._scaledResolution);

    def glDraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        buf = np.asarray(self._screenBuffer)[::-1,:]
        w,h = gameboyResolution
        glDrawPixels(w,h, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8, buf)
        glFlush()

    def updateDisplay(self):
        self.glDraw()
        OpenGL.GLUT.freeglut.glutMainLoopEvent()

    def framelimiter(self, speed):
        pass

    def stop(self):
        pass

