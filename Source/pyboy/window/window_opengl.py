#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GLUT.freeglut

from .. import windowevent
from .window_sdl2 import SdlWindow


gameboyResolution = (160, 144)


class OpenGLWindow(SdlWindow):
    def __init__(self, scale=1):
        super(self.__class__, self).__init__(scale)

    def init(self):
        self.colorPalette = [((x << 8) & 0xFFFFFFFF) | 0x000000FF for x in self.colorPalette] # Shifting from ARGB to RGBA
        self.alphaMask = 0x000000FF
        self.colorFormat = u"RGB"

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
                self.events.append(windowevent.ReleaseArrowUp)
            if c == GLUT_KEY_DOWN:
                self.events.append(windowevent.ReleaseArrowDown)
            if c == GLUT_KEY_LEFT:
                self.events.append(windowevent.ReleaseArrowLeft)
            if c == GLUT_KEY_RIGHT:
                self.events.append(windowevent.ReleaseArrowRight)
        else:
            if c == GLUT_KEY_UP:
                self.events.append(windowevent.PressArrowUp)
            if c == GLUT_KEY_DOWN:
                self.events.append(windowevent.PressArrowDown)
            if c == GLUT_KEY_LEFT:
                self.events.append(windowevent.PressArrowLeft)
            if c == GLUT_KEY_RIGHT:
                self.events.append(windowevent.PressArrowRight)

    def glKeyboard(self, c, x, y, up):
        if up:
            if c == 'a':
                self.events.append(windowevent.ReleaseButtonA)
            elif c == 's':
                self.events.append(windowevent.ReleaseButtonB)
            elif c == 'z':
                self.events.append(windowevent.SaveState)
            elif c == 'x':
                self.events.append(windowevent.LoadState)
            elif c == ' ':
                self.events.append(windowevent.ReleaseSpeedUp)
            elif c == chr(8):
                self.events.append(windowevent.ReleaseButtonSelect)
            elif c == chr(13):
                self.events.append(windowevent.ReleaseButtonStart)
        else:
            if c == 'a':
                self.events.append(windowevent.PressButtonA)
            elif c == 's':
                self.events.append(windowevent.PressButtonB)
            elif c == chr(27):
                self.events.append(windowevent.Quit)
            elif c == 'd':
                self.events.append(windowevent.DebugToggle)
            elif c == ' ':
                self.events.append(windowevent.PressSpeedUp)
            elif c == 'i':
                self.events.append(windowevent.ScreenRecordingToggle)
            elif c == chr(8):
                self.events.append(windowevent.PressButtonSelect)
            elif c == chr(13):
                self.events.append(windowevent.PressButtonStart)


    def glReshape(self, width, height):
        scale = max(min(float(height)/gameboyResolution[1], float(width)/gameboyResolution[0]), 1)
        self._scaledResolution = tuple([int(x * scale) for x in gameboyResolution])
        glPixelZoom(scale,scale)
        # glutReshapeWindow(*self._scaledResolution);

    def glDraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        buf = np.asarray(self.screenBuffer)[::-1,:]
        w,h = gameboyResolution
        glDrawPixels(w,h, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8, buf)
        glFlush()

    def updateDisplay(self):
        self.glDraw()
        OpenGL.GLUT.freeglut.glutMainLoopEvent()

    def getScreenBuffer(self):
        frame = np.asarray(self.screenBuffer).view(np.uint8).reshape(160,144,4)[:,:,1:]
        return np.ascontiguousarray(frame)

    def framelimiter(self, speed):
        pass

    def stop(self):
        pass
