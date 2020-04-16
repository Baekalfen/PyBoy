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
                         glutCreateWindow, glutDisplayFunc, glutInit, glutInitDisplayMode, glutInitWindowSize,
                         glutKeyboardFunc, glutKeyboardUpFunc, glutReshapeFunc, glutSetWindowTitle, glutSpecialFunc,
                         glutSpecialUpFunc)

from .. import windowevent
from ..logger import logger
from .window_sdl2 import SDLWindow

ROWS, COLS = 144, 160


class OpenGLWindow(SDLWindow):
    def __init__(self, scale=1):
        super(self.__class__, self).__init__(scale)

    def init(self, hide_window):
        # Shift from ARGB to RGBA
        self.color_palette = [((x << 8) & 0xFFFFFFFF) | 0x000000FF for x in self.color_palette]
        self.alphamask = 0x000000FF
        self.color_format = u"RGB"
        self.buffer_dims = (144, 160)

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

        if hide_window:
            logger.warning("Hiding the window is not supported in OpenGL")

    # Cython does not cooperate with lambdas
    def _key(self, c, x, y):
        self._glkeyboard(c.decode("ascii"), x, y, False)

    def _keyUp(self, c, x, y):
        self._glkeyboard(c.decode("ascii"), x, y, True)

    def _spec(self, c, x, y):
        self._glkeyboardspecial(c, x, y, False)

    def _specUp(self, c, x, y):
        self._glkeyboardspecial(c, x, y, True)

    def dump(self, filename):
        pass

    def set_title(self, title):
        glutSetWindowTitle(title)

    def get_events(self):
        evts = self.events
        self.events = []
        return evts

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
        buf = np.asarray(self._screenbuffer)[::-1, :]
        glDrawPixels(COLS, ROWS, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8, buf)
        glFlush()

    def update_display(self, paused):
        self._gldraw()
        OpenGL.GLUT.freeglut.glutMainLoopEvent()

    def get_screen_buffer_as_ndarray(self):
        return np.frombuffer(self.get_screen_buffer(), dtype=np.uint8).reshape(144, 160, 4)[:, :, 1:]

    def get_screen_image(self):
        if not Image:
            logger.warning("Cannot generate screen image. Missing dependency \"Pillow\".")
            return None

        # Convert to RGBA for consistency with SDL2
        return Image.fromarray(np.frombuffer(self.get_screen_buffer(), dtype=np.uint8).reshape(
            self.buffer_dims+(4,))[:, :, 1:], self.color_format).convert(mode='RGBA')

    def frame_limiter(self, speed):
        pass

    def stop(self):
        pass
