#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

try:
    from PIL import Image
except ImportError:
    Image = None

import numpy as np
import OpenGL.GLUT.freeglut
from OpenGL.GL import (GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8, glClear,
                       glDrawPixels, glFlush, glPixelZoom)
# from OpenGL.GLU import *
from OpenGL.GLUT import (GLUT_KEY_DOWN, GLUT_KEY_LEFT, GLUT_KEY_RIGHT, GLUT_KEY_UP, GLUT_RGBA, GLUT_SINGLE,
                         glutCreateWindow, glutDestroyWindow, glutDisplayFunc, glutGetWindow, glutInit,
                         glutInitDisplayMode, glutInitWindowSize, glutKeyboardFunc, glutKeyboardUpFunc, glutReshapeFunc,
                         glutSetWindowTitle, glutSpecialFunc, glutSpecialUpFunc)
from pyboy import windowevent
from pyboy.logger import logger
from pyboy.plugins.base_plugin import PyBoyWindowPlugin

ROWS, COLS = 144, 160


class WindowOpenGL(PyBoyWindowPlugin):
    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        self._scale = pyboy_argv.get("scale")
        logger.info("%s initialization" % self.__class__.__name__)

        self._scaledresolution = (self._scale * COLS, self._scale * ROWS)
        logger.info('Scale: x%s %s' % (self._scale, self._scaledresolution))

        if not glutInit():
            raise Exception("OpenGL couldn't initialize!")
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
        glutInitWindowSize(*self._scaledresolution)
        glutCreateWindow("PyBoy")
        glutKeyboardFunc(self._key)
        glutKeyboardUpFunc(self._keyUp)
        glutSpecialFunc(self._spec)
        glutSpecialUpFunc(self._specUp)
        self.events = []

        glPixelZoom(self._scale, self._scale)
        glutReshapeFunc(self._glreshape)
        glutDisplayFunc(self._gldraw)

    # Cython does not cooperate with lambdas
    def _key(self, c, x, y):
        self._glkeyboard(c.decode("ascii"), x, y, False)

    def _keyUp(self, c, x, y):
        self._glkeyboard(c.decode("ascii"), x, y, True)

    def _spec(self, c, x, y):
        self._glkeyboardspecial(c, x, y, False)

    def _specUp(self, c, x, y):
        self._glkeyboardspecial(c, x, y, True)

    def set_title(self, title):
        glutSetWindowTitle(title)

    def handle_events(self, events):
        events += self.events
        self.events = []
        return events

    def _glkeyboardspecial(self, c, x, y, up):
        if up:
            if c == GLUT_KEY_UP:
                self.events.append(windowevent.RELEASE_ARROW_UP)
            if c == GLUT_KEY_DOWN:
                self.events.append(windowevent.RELEASE_ARROW_DOWN)
            if c == GLUT_KEY_LEFT:
                self.events.append(windowevent.RELEASE_ARROW_LEFT)
            if c == GLUT_KEY_RIGHT:
                self.events.append(windowevent.RELEASE_ARROW_RIGHT)
        else:
            if c == GLUT_KEY_UP:
                self.events.append(windowevent.PRESS_ARROW_UP)
            if c == GLUT_KEY_DOWN:
                self.events.append(windowevent.PRESS_ARROW_DOWN)
            if c == GLUT_KEY_LEFT:
                self.events.append(windowevent.PRESS_ARROW_LEFT)
            if c == GLUT_KEY_RIGHT:
                self.events.append(windowevent.PRESS_ARROW_RIGHT)

    def _glkeyboard(self, c, x, y, up):
        if up:
            if c == 'a':
                self.events.append(windowevent.RELEASE_BUTTON_A)
            elif c == 's':
                self.events.append(windowevent.RELEASE_BUTTON_B)
            elif c == 'z':
                self.events.append(windowevent.SAVE_STATE)
            elif c == 'x':
                self.events.append(windowevent.LOAD_STATE)
            elif c == ' ':
                self.events.append(windowevent.RELEASE_SPEED_UP)
            elif c == chr(8):
                self.events.append(windowevent.RELEASE_BUTTON_SELECT)
            elif c == chr(13):
                self.events.append(windowevent.RELEASE_BUTTON_START)
        else:
            if c == 'a':
                self.events.append(windowevent.PRESS_BUTTON_A)
            elif c == 's':
                self.events.append(windowevent.PRESS_BUTTON_B)
            elif c == chr(27):
                self.events.append(windowevent.QUIT)
            elif c == 'd':
                self.events.append(windowevent.DEBUG_TOGGLE)
            elif c == ' ':
                self.events.append(windowevent.PRESS_SPEED_UP)
            elif c == 'i':
                self.events.append(windowevent.SCREEN_RECORDING_TOGGLE)
            elif c == chr(8):
                self.events.append(windowevent.PRESS_BUTTON_SELECT)
            elif c == chr(13):
                self.events.append(windowevent.PRESS_BUTTON_START)

    def _glreshape(self, width, height):
        scale = max(min(height / ROWS, width / COLS), 1)
        self._scaledresolution = (round(scale * COLS), round(scale * ROWS))
        glPixelZoom(scale, scale)
        # glutReshapeWindow(*self._scaledresolution);

    def _gldraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        buf = np.asarray(self.renderer._screenbuffer)[::-1, :]
        glDrawPixels(COLS, ROWS, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8, buf)
        glFlush()

    def enabled(self):
        return self.pyboy_argv.get('window_type') == 'OpenGL'

    def post_tick(self):
        self._gldraw()
        OpenGL.GLUT.freeglut.glutMainLoopEvent()

    def stop(self):
        glutDestroyWindow(glutGetWindow())
