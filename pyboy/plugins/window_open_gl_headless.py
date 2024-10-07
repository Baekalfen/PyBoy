#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import time

import numpy as np

import pyboy
from pyboy import utils
from pyboy.plugins.base_plugin import PyBoyWindowPlugin
from pyboy.utils import WindowEvent

logger = pyboy.logging.get_logger(__name__)

try:
    from OpenGL.GL import (GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8_REV, glClear,
                           glDrawPixels, glFlush, glPixelZoom)
    opengl_enabled = True
except (ImportError, AttributeError):
    opengl_enabled = False

ROWS, COLS = 144, 160


class WindowOpenGLHeadless(PyBoyWindowPlugin):
    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        self.events = []

        self._ftime = time.perf_counter_ns()

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
        pass

    def handle_events(self, events):
        events += self.events
        self.events = []
        return events

    def _glkeyboardspecial(self, c, x, y, up):
        # Keybindings should be handled by your own code
        # EG: pyboy.events.append(WindowEvent.PRESS_ARROW_UP)
        pass

    def _glkeyboard(self, c, x, y, up):
        # Keybindings should be handled by your own code
        # EG: pyboy.events.append(WindowEvent.PRESS_ARROW_UP)
        pass

    def _glreshape(self, width, height):
        scale = max(min(height / ROWS, width / COLS), 1)
        self._scaledresolution = (round(scale * COLS), round(scale * ROWS))
        glPixelZoom(scale, scale)

    def _gldraw(self):
        buf = np.asarray(self.renderer._screenbuffer)[::-1, :]
        glDrawPixels(COLS, ROWS, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8_REV, buf)
        glFlush()

    def frame_limiter(self, speed):
        self._ftime += int((1.0 / (60.0*speed)) * 1_000_000_000)
        now = time.perf_counter_ns()
        if (self._ftime > now):
            delay = (self._ftime - now) // 1_000_000
            time.sleep(delay / 1000)
        else:
            self._ftime = now
        return True

    def enabled(self):
        if self.pyboy_argv.get("window") == "OpenGLHeadless":
            if opengl_enabled:
                return True
            else:
                logger.error("Missing depencency \"PyOpenGL\". OpenGL window disabled")
        return False

    def post_tick(self):
        self._gldraw()

    def stop(self):
        pass

