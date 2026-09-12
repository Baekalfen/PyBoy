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
        GL_UNSIGNED_BYTE,
        GL_UNSIGNED_INT_8_8_8_8_REV,
        glClear,
        glDrawPixels,
        glFlush,
        glPixelZoom,
        glWindowPos2f,
    )

    glfw_enabled = True
except (ImportError, AttributeError):
    glfw_enabled = False

ROWS, COLS = 144, 160


class WindowGLFW(WindowOpenAL):
    argv = [
        ("--sgb-border", {"action": "store_true", "help": "Enable SGB border rendering (requires SDL2 or GLFW window)"})
    ]

    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)
        self._windowed_position = None
        self._windowed_size = None

        self.sgb_border_enabled = pyboy_argv.get("sgb_border", False)

        if not self.enabled():
            return

        if not glfw.init():
            raise PyBoyException("GLFW couldn't initialize!")

        # Determine window dimensions based on SGB border enabled state
        if self.sgb_border_enabled:
            # SGB mode: 256x224 screen dimensions
            window_width = 256 * self.scale
            window_height = 224 * self.scale
            self._scaledresolution = (window_width, window_height)
        else:
            # Normal GB mode: 160x144
            window_width = COLS * self.scale
            window_height = ROWS * self.scale
            self._scaledresolution = (window_width, window_height)

        # Fix scaling on macOS Retina displays. Call before 'glfw.create_window'!
        glfw.window_hint(glfw.COCOA_RETINA_FRAMEBUFFER, glfw.FALSE)

        self.window = glfw.create_window(*self._scaledresolution, "PyBoy", None, None)
        if not self.window:
            glfw.terminate()
            raise PyBoyException("GLFW couldn't open window!")
        glfw.make_context_current(self.window)
        glfw.swap_interval(0)
        glfw.set_key_callback(self.window, self._key_callback)
        glfw.set_window_size_callback(self.window, self._window_resize)
        self.events = []

        self._window_resize(self.window, *self._scaledresolution)

    def set_title(self, title):
        glfw.set_window_title(self.window, title)

    def handle_events(self, events):
        events += self.events
        self.events = []

        for event in events:
            if event != WindowEvent.FULL_SCREEN_TOGGLE:
                continue

            if self.fullscreen:
                x, y = self._windowed_position
                width, height = self._windowed_size
                glfw.set_window_monitor(self.window, None, x, y, width, height, glfw.DONT_CARE)
                self.fullscreen = False
            else:
                self._windowed_position = glfw.get_window_pos(self.window)
                self._windowed_size = glfw.get_window_size(self.window)
                monitor = glfw.get_primary_monitor()
                mode = glfw.get_video_mode(monitor)
                glfw.set_window_monitor(
                    self.window, monitor, 0, 0, mode.size.width, mode.size.height, mode.refresh_rate
                )
                self.fullscreen = True

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
            elif key == glfw.KEY_U:
                self.events.append(WindowEvent(WindowEvent.SCREEN_RECORDING_TOGGLE_MP4))
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
            elif key == glfw.KEY_COMMA:
                self.events.append(WindowEvent(WindowEvent.PRESS_REWIND_BACK))
            elif key == glfw.KEY_PERIOD:
                self.events.append(WindowEvent(WindowEvent.PRESS_REWIND_FORWARD))
            elif key == glfw.KEY_J:
                self.events.append(WindowEvent(WindowEvent.DEBUG_MEMORY_SCROLL_DOWN))
            elif key == glfw.KEY_K:
                self.events.append(WindowEvent(WindowEvent.DEBUG_MEMORY_SCROLL_UP))
            elif key in (glfw.KEY_LEFT_SHIFT, glfw.KEY_RIGHT_SHIFT):
                self.events.append(WindowEvent(WindowEvent.MOD_SHIFT_ON))
        elif action == glfw.RELEASE:
            if key == glfw.KEY_A:
                self.events.append(WindowEvent(WindowEvent.RELEASE_BUTTON_A))
            elif key == glfw.KEY_S:
                self.events.append(WindowEvent(WindowEvent.RELEASE_BUTTON_B))
            elif key == glfw.KEY_P:
                self.events.append(WindowEvent(WindowEvent.PAUSE_TOGGLE))
            elif key == glfw.KEY_C:
                self.events.append(WindowEvent(WindowEvent.CYCLE_PALETTE))
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
            elif key == glfw.KEY_COMMA:
                self.events.append(WindowEvent(WindowEvent.RELEASE_REWIND_BACK))
            elif key == glfw.KEY_PERIOD:
                self.events.append(WindowEvent(WindowEvent.RELEASE_REWIND_FORWARD))
            elif key == glfw.KEY_F11:
                self.events.append(WindowEvent(WindowEvent.FULL_SCREEN_TOGGLE))
            elif key in (glfw.KEY_LEFT_SHIFT, glfw.KEY_RIGHT_SHIFT):
                self.events.append(WindowEvent(WindowEvent.MOD_SHIFT_OFF))

    def _window_resize(self, window, width, height):
        if self.sgb_border_enabled:
            # SGB mode: 256x224 base dimensions
            scale = max(min(height / 224, width / 256), 1)
            self._scaledresolution = (round(scale * 256), round(scale * 224))
        else:
            # Normal GB mode: 160x144
            scale = max(min(height / ROWS, width / COLS), 1)
            self._scaledresolution = (round(scale * COLS), round(scale * ROWS))
        glPixelZoom(scale, scale)
        glWindowPos2f((width - COLS * scale) / 2, (height - ROWS * scale) / 2)

    def _gldraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Use direct access to Cython attributes - when compiled, we have direct access to self.mb and self.renderer
        if self.sgb_border_enabled and self.mb.sgb.enabled and self.renderer:
            try:
                frame = self.mb.sgb_border.get_composited_frame(self.renderer._screenbuffer_raw)
                if frame and len(frame) > 0:
                    buf = np.asarray(frame, dtype=np.uint8).reshape(224, 256, 4)
                    glDrawPixels(256, 224, GL_RGBA, GL_UNSIGNED_BYTE, buf[::-1, :, :])
                else:
                    buf = np.asarray(self.renderer._screenbuffer)[::-1, :]
                    glDrawPixels(COLS, ROWS, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8_REV, buf)
            except Exception as e:
                logger.debug(f"Error rendering SGB border: {e}")
                buf = np.asarray(self.renderer._screenbuffer)[::-1, :]
                glDrawPixels(COLS, ROWS, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8_REV, buf)
        else:
            # Normal GB rendering (160x144)
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
