#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import numpy as np

import pyboy
from pyboy.plugins.base_plugin import PyBoyWindowPlugin
from pyboy.utils import WindowEvent, PyBoyException, PyBoyDependencyError

logger = pyboy.logging.get_logger(__name__)

# isort: skip_file
try:
    import OpenGL.GLUT.freeglut
    from OpenGL.GL import (
        GL_COLOR_BUFFER_BIT,
        GL_DEPTH_BUFFER_BIT,
        GL_RGBA,
        GL_UNSIGNED_INT_8_8_8_8_REV,
        glClear,
        glDrawPixels,
        glFlush,
        glPixelZoom,
    )
    from OpenGL.GLUT import (
        GLUT_KEY_DOWN,
        GLUT_KEY_LEFT,
        GLUT_KEY_RIGHT,
        GLUT_KEY_UP,
        GLUT_RGBA,
        GLUT_SINGLE,
        glutCreateWindow,
        glutDestroyWindow,
        glutDisplayFunc,
        glutGetWindow,
        glutInit,
        glutInitDisplayMode,
        glutInitWindowSize,
        glutKeyboardFunc,
        glutKeyboardUpFunc,
        glutReshapeFunc,
        glutSetWindowTitle,
        glutSpecialFunc,
        glutSpecialUpFunc,
    )

    opengl_enabled = True
except (ImportError, AttributeError):
    opengl_enabled = False

ROWS, COLS = 144, 160


class WindowOpenGL(PyBoyWindowPlugin):
    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        if not glutInit():
            raise PyBoyException("OpenGL couldn't initialize!")
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
        glutInitWindowSize(*self._scaledresolution)
        glutCreateWindow("PyBoy")
        glutKeyboardFunc(self._key)
        glutKeyboardUpFunc(self._keyUp)
        glutSpecialFunc(self._spec)
        glutSpecialUpFunc(self._specUp)
        self.events = []

        glPixelZoom(self.scale, self.scale)
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
                self.events.append(WindowEvent(WindowEvent.RELEASE_ARROW_UP))
            if c == GLUT_KEY_DOWN:
                self.events.append(WindowEvent(WindowEvent.RELEASE_ARROW_DOWN))
            if c == GLUT_KEY_LEFT:
                self.events.append(WindowEvent(WindowEvent.RELEASE_ARROW_LEFT))
            if c == GLUT_KEY_RIGHT:
                self.events.append(WindowEvent(WindowEvent.RELEASE_ARROW_RIGHT))
        else:
            if c == GLUT_KEY_UP:
                self.events.append(WindowEvent(WindowEvent.PRESS_ARROW_UP))
            if c == GLUT_KEY_DOWN:
                self.events.append(WindowEvent(WindowEvent.PRESS_ARROW_DOWN))
            if c == GLUT_KEY_LEFT:
                self.events.append(WindowEvent(WindowEvent.PRESS_ARROW_LEFT))
            if c == GLUT_KEY_RIGHT:
                self.events.append(WindowEvent(WindowEvent.PRESS_ARROW_RIGHT))

    def _glkeyboard(self, c, x, y, up):
        if up:
            if c == "a":
                self.events.append(WindowEvent(WindowEvent.RELEASE_BUTTON_A))
            elif c == "s":
                self.events.append(WindowEvent(WindowEvent.RELEASE_BUTTON_B))
            elif c == "z":
                self.events.append(WindowEvent(WindowEvent.STATE_SAVE))
            elif c == "x":
                self.events.append(WindowEvent(WindowEvent.STATE_LOAD))
            elif c == " ":
                self.events.append(WindowEvent(WindowEvent.RELEASE_SPEED_UP))
            elif c == chr(8):
                self.events.append(WindowEvent(WindowEvent.RELEASE_BUTTON_SELECT))
            elif c == chr(13):
                self.events.append(WindowEvent(WindowEvent.RELEASE_BUTTON_START))
            elif c == "o":
                self.events.append(WindowEvent(WindowEvent.SCREENSHOT_RECORD))
        else:
            if c == "a":
                self.events.append(WindowEvent(WindowEvent.PRESS_BUTTON_A))
            elif c == "s":
                self.events.append(WindowEvent(WindowEvent.PRESS_BUTTON_B))
            elif c == chr(27):
                self.events.append(WindowEvent(WindowEvent.QUIT))
            elif c == " ":
                self.events.append(WindowEvent(WindowEvent.PRESS_SPEED_UP))
            elif c == "i":
                self.events.append(WindowEvent(WindowEvent.SCREEN_RECORDING_TOGGLE))
            elif c == chr(8):
                self.events.append(WindowEvent(WindowEvent.PRESS_BUTTON_SELECT))
            elif c == chr(13):
                self.events.append(WindowEvent(WindowEvent.PRESS_BUTTON_START))

    def _glreshape(self, width, height):
        scale = max(min(height / ROWS, width / COLS), 1)
        self._scaledresolution = (round(scale * COLS), round(scale * ROWS))
        glPixelZoom(scale, scale)
        # glutReshapeWindow(*self._scaledresolution);

    def _gldraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        buf = np.asarray(self.renderer._screenbuffer)[::-1, :]
        glDrawPixels(COLS, ROWS, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8_REV, buf)
        glFlush()

    def enabled(self):
        if self.pyboy_argv.get("window") == "OpenGL":
            if opengl_enabled:
                if bool(OpenGL.GLUT.freeglut.glutMainLoopEvent):
                    return True
                else:
                    raise PyBoyException('Failed to load "PyOpenGL"')
            else:
                raise PyBoyDependencyError('Missing depencency "PyOpenGL"')
        return False

    def post_tick(self):
        self._gldraw()
        OpenGL.GLUT.freeglut.glutMainLoopEvent()

    def stop(self):
        glutDestroyWindow(glutGetWindow())
        for _ in range(10):  # At least 2 to close
            OpenGL.GLUT.freeglut.glutMainLoopEvent()
