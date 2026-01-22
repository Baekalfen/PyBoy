import numpy as np

import pyboy
from pyboy.plugins.window_openal import WindowOpenAL
from pyboy.utils import WindowEvent, PyBoyException, PyBoyDependencyError

logger = pyboy.logging.get_logger(__name__)

try:
    import glfw
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

    glfw_enabled = True
except (ImportError, AttributeError):
    glfw_enabled = False

ROWS, COLS = 144, 160


class WindowGLFW(WindowOpenAL):
    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        if not glfw.init():
            raise PyBoyException("GLFW couldn't initialize!")
        self._scaledresolution = (COLS * self.scale, ROWS * self.scale)

        # Fix scaling on macOS Retina displays. Call before 'glfw.create_window'!
        glfw.window_hint(glfw.COCOA_RETINA_FRAMEBUFFER, glfw.FALSE)

        self.window = glfw.create_window(*self._scaledresolution, "PyBoy", None, None)
        if not self.window:
            glfw.terminate()
            raise PyBoyException("GLFW couldn't open window!")
        glfw.make_context_current(self.window)
        glfw.set_key_callback(self.window, self._key_callback)
        glfw.set_window_size_callback(self.window, self._window_resize)
        self.events = []

        glPixelZoom(self.scale, self.scale)

    def set_title(self, title):
        glfw.set_window_title(self.window, title)

    def handle_events(self, events):
        events += self.events
        self.events = []
        return events

    def _key_callback(self, window, key, scancode, action, mods):
        # Map GLFW keys to PyBoy events
        if action == glfw.PRESS:
            if key == glfw.KEY_A:
                self.events.append(WindowEvent(WindowEvent.PRESS_BUTTON_A))
            elif key == glfw.KEY_S:
                self.events.append(WindowEvent(WindowEvent.PRESS_BUTTON_B))
            elif key == glfw.KEY_ESCAPE:
                self.events.append(WindowEvent(WindowEvent.QUIT))
            elif key == glfw.KEY_SPACE:
                self.events.append(WindowEvent(WindowEvent.PRESS_SPEED_UP))
            elif key == glfw.KEY_I:
                self.events.append(WindowEvent(WindowEvent.SCREEN_RECORDING_TOGGLE))
            elif key == glfw.KEY_BACKSPACE:
                self.events.append(WindowEvent(WindowEvent.PRESS_BUTTON_SELECT))
            elif key == glfw.KEY_ENTER:
                self.events.append(WindowEvent(WindowEvent.PRESS_BUTTON_START))
            elif key == glfw.KEY_UP:
                self.events.append(WindowEvent(WindowEvent.PRESS_ARROW_UP))
            elif key == glfw.KEY_DOWN:
                self.events.append(WindowEvent(WindowEvent.PRESS_ARROW_DOWN))
            elif key == glfw.KEY_LEFT:
                self.events.append(WindowEvent(WindowEvent.PRESS_ARROW_LEFT))
            elif key == glfw.KEY_RIGHT:
                self.events.append(WindowEvent(WindowEvent.PRESS_ARROW_RIGHT))
            elif key == glfw.KEY_Z:
                self.events.append(WindowEvent(WindowEvent.STATE_SAVE))
            elif key == glfw.KEY_X:
                self.events.append(WindowEvent(WindowEvent.STATE_LOAD))
            elif key == glfw.KEY_O:
                self.events.append(WindowEvent(WindowEvent.SCREENSHOT_RECORD))
        elif action == glfw.RELEASE:
            if key == glfw.KEY_A:
                self.events.append(WindowEvent(WindowEvent.RELEASE_BUTTON_A))
            elif key == glfw.KEY_S:
                self.events.append(WindowEvent(WindowEvent.RELEASE_BUTTON_B))
            elif key == glfw.KEY_P:
                self.events.append(WindowEvent(WindowEvent.PAUSE_TOGGLE))
            elif key == glfw.KEY_SPACE:
                self.events.append(WindowEvent(WindowEvent.RELEASE_SPEED_UP))
            elif key == glfw.KEY_BACKSPACE:
                self.events.append(WindowEvent(WindowEvent.RELEASE_BUTTON_SELECT))
            elif key == glfw.KEY_ENTER:
                self.events.append(WindowEvent(WindowEvent.RELEASE_BUTTON_START))
            elif key == glfw.KEY_UP:
                self.events.append(WindowEvent(WindowEvent.RELEASE_ARROW_UP))
            elif key == glfw.KEY_DOWN:
                self.events.append(WindowEvent(WindowEvent.RELEASE_ARROW_DOWN))
            elif key == glfw.KEY_LEFT:
                self.events.append(WindowEvent(WindowEvent.RELEASE_ARROW_LEFT))
            elif key == glfw.KEY_RIGHT:
                self.events.append(WindowEvent(WindowEvent.RELEASE_ARROW_RIGHT))

    def _window_resize(self, window, width, height):
        scale = max(min(height / ROWS, width / COLS), 1)
        self._scaledresolution = (round(scale * COLS), round(scale * ROWS))
        glPixelZoom(scale, scale)

    def _gldraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        buf = np.asarray(self.renderer._screenbuffer)[::-1, :]
        glDrawPixels(COLS, ROWS, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8_REV, buf)
        glFlush()
        glfw.swap_buffers(self.window)

    def enabled(self):
        if self.pyboy_argv.get("window") == "GLFW":
            if glfw_enabled:
                return True
            else:
                raise PyBoyDependencyError('Missing dependency "PyOpenGL" or "glfw"')
        return False

    def post_tick(self):
        self._gldraw()
        glfw.poll_events()
        if glfw.window_should_close(self.window):
            raise PyBoyException("Window closed")
        WindowOpenAL.post_tick(self)

    def stop(self):
        glfw.set_window_should_close(self.window, True)
        glfw.destroy_window(self.window)
        glfw.terminate()
