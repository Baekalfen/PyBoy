#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import time

from pyboy import utils
from pyboy.plugins.base_plugin import PyBoyWindowPlugin
from pyboy.utils import WindowEvent, WindowEventMouse

try:
    import sdl2
    from sdl2.ext import get_events
except ImportError:
    sdl2 = None

import pyboy

logger = pyboy.logging.get_logger(__name__)

ROWS, COLS = 144, 160

# https://wiki.libsdl.org/SDL_Scancode#Related_Enumerations
# yapf: disable
if sdl2:
    KEY_DOWN = {
        sdl2.SDLK_UP        : WindowEvent.PRESS_ARROW_UP,
        sdl2.SDLK_DOWN      : WindowEvent.PRESS_ARROW_DOWN,
        sdl2.SDLK_RIGHT     : WindowEvent.PRESS_ARROW_RIGHT,
        sdl2.SDLK_LEFT      : WindowEvent.PRESS_ARROW_LEFT,
        sdl2.SDLK_a         : WindowEvent.PRESS_BUTTON_A,
        sdl2.SDLK_s         : WindowEvent.PRESS_BUTTON_B,
        sdl2.SDLK_RETURN    : WindowEvent.PRESS_BUTTON_START,
        sdl2.SDLK_BACKSPACE : WindowEvent.PRESS_BUTTON_SELECT,
        sdl2.SDLK_SPACE     : WindowEvent.PRESS_SPEED_UP,
        sdl2.SDLK_COMMA     : WindowEvent.PRESS_REWIND_BACK,
        sdl2.SDLK_PERIOD    : WindowEvent.PRESS_REWIND_FORWARD,
        sdl2.SDLK_j         : WindowEvent.DEBUG_MEMORY_SCROLL_DOWN,
        sdl2.SDLK_k         : WindowEvent.DEBUG_MEMORY_SCROLL_UP,
        sdl2.SDLK_LSHIFT    : WindowEvent.MOD_SHIFT_ON,
        sdl2.SDLK_RSHIFT    : WindowEvent.MOD_SHIFT_ON,
    }

    KEY_UP = {
        sdl2.SDLK_UP        : WindowEvent.RELEASE_ARROW_UP,
        sdl2.SDLK_DOWN      : WindowEvent.RELEASE_ARROW_DOWN,
        sdl2.SDLK_RIGHT     : WindowEvent.RELEASE_ARROW_RIGHT,
        sdl2.SDLK_LEFT      : WindowEvent.RELEASE_ARROW_LEFT,
        sdl2.SDLK_a         : WindowEvent.RELEASE_BUTTON_A,
        sdl2.SDLK_s         : WindowEvent.RELEASE_BUTTON_B,
        sdl2.SDLK_RETURN    : WindowEvent.RELEASE_BUTTON_START,
        sdl2.SDLK_BACKSPACE : WindowEvent.RELEASE_BUTTON_SELECT,
        sdl2.SDLK_z         : WindowEvent.STATE_SAVE,
        sdl2.SDLK_x         : WindowEvent.STATE_LOAD,
        sdl2.SDLK_SPACE     : WindowEvent.RELEASE_SPEED_UP,
        sdl2.SDLK_p         : WindowEvent.PAUSE_TOGGLE,
        sdl2.SDLK_i         : WindowEvent.SCREEN_RECORDING_TOGGLE,
        sdl2.SDLK_o         : WindowEvent.SCREENSHOT_RECORD,
        sdl2.SDLK_ESCAPE    : WindowEvent.QUIT,
        sdl2.SDLK_COMMA     : WindowEvent.RELEASE_REWIND_BACK,
        sdl2.SDLK_PERIOD    : WindowEvent.RELEASE_REWIND_FORWARD,
        sdl2.SDLK_LSHIFT    : WindowEvent.MOD_SHIFT_OFF,
        sdl2.SDLK_RSHIFT    : WindowEvent.MOD_SHIFT_OFF,
        sdl2.SDLK_F11       : WindowEvent.FULL_SCREEN_TOGGLE,
    }

    CONTROLLER_DOWN = {
        sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP       : WindowEvent.PRESS_ARROW_UP,
        sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN     : WindowEvent.PRESS_ARROW_DOWN,
        sdl2.SDL_CONTROLLER_BUTTON_DPAD_RIGHT    : WindowEvent.PRESS_ARROW_RIGHT,
        sdl2.SDL_CONTROLLER_BUTTON_DPAD_LEFT     : WindowEvent.PRESS_ARROW_LEFT,
        sdl2.SDL_CONTROLLER_BUTTON_B             : WindowEvent.PRESS_BUTTON_A,
        sdl2.SDL_CONTROLLER_BUTTON_A             : WindowEvent.PRESS_BUTTON_B,
        sdl2.SDL_CONTROLLER_BUTTON_START         : WindowEvent.PRESS_BUTTON_START,
        sdl2.SDL_CONTROLLER_BUTTON_BACK          : WindowEvent.PRESS_BUTTON_SELECT,
        sdl2.SDL_CONTROLLER_BUTTON_GUIDE         : WindowEvent.PRESS_SPEED_UP,
    }

    CONTROLLER_UP = {
        sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP       : WindowEvent.RELEASE_ARROW_UP,
        sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN     : WindowEvent.RELEASE_ARROW_DOWN,
        sdl2.SDL_CONTROLLER_BUTTON_DPAD_RIGHT    : WindowEvent.RELEASE_ARROW_RIGHT,
        sdl2.SDL_CONTROLLER_BUTTON_DPAD_LEFT     : WindowEvent.RELEASE_ARROW_LEFT,
        sdl2.SDL_CONTROLLER_BUTTON_B             : WindowEvent.RELEASE_BUTTON_A,
        sdl2.SDL_CONTROLLER_BUTTON_A             : WindowEvent.RELEASE_BUTTON_B,
        sdl2.SDL_CONTROLLER_BUTTON_START         : WindowEvent.RELEASE_BUTTON_START,
        sdl2.SDL_CONTROLLER_BUTTON_BACK          : WindowEvent.RELEASE_BUTTON_SELECT,
        sdl2.SDL_CONTROLLER_BUTTON_LEFTSHOULDER  : WindowEvent.STATE_SAVE,
        sdl2.SDL_CONTROLLER_BUTTON_RIGHTSHOULDER : WindowEvent.STATE_LOAD,
        sdl2.SDL_CONTROLLER_BUTTON_GUIDE         : WindowEvent.RELEASE_SPEED_UP,
    }
else:
    KEY_DOWN = {}
    KEY_UP = {}
    CONTROLLER_DOWN = {}
    CONTROLLER_UP = {}
# yapf: enable


def sdl2_event_pump(events):
    global _sdlcontroller
    # Feed events into the loop
    for event in get_events():
        if event.type == sdl2.SDL_QUIT:
            events.append(WindowEvent(WindowEvent.QUIT))
        elif event.type == sdl2.SDL_KEYDOWN:
            events.append(WindowEvent(KEY_DOWN.get(event.key.keysym.sym, WindowEvent.PASS)))
        elif event.type == sdl2.SDL_KEYUP:
            events.append(WindowEvent(KEY_UP.get(event.key.keysym.sym, WindowEvent.PASS)))
        elif event.type == sdl2.SDL_WINDOWEVENT:
            if event.window.windowID == 1:
                if event.window.event == sdl2.SDL_WINDOWEVENT_FOCUS_LOST:
                    events.append(WindowEvent(WindowEvent.WINDOW_UNFOCUS))
                elif event.window.event == sdl2.SDL_WINDOWEVENT_FOCUS_GAINED:
                    events.append(WindowEvent(WindowEvent.WINDOW_FOCUS))
        elif event.type == sdl2.SDL_MOUSEWHEEL:
            events.append(
                WindowEventMouse(
                    WindowEvent._INTERNAL_MOUSE,
                    window_id=event.motion.windowID,
                    mouse_scroll_x=event.wheel.x,
                    mouse_scroll_y=event.wheel.y
                )
            )
        elif event.type == sdl2.SDL_MOUSEMOTION or event.type == sdl2.SDL_MOUSEBUTTONUP:
            mouse_button = -1
            if event.type == sdl2.SDL_MOUSEBUTTONUP:
                if event.button.button == sdl2.SDL_BUTTON_LEFT:
                    mouse_button = 0
                elif event.button.button == sdl2.SDL_BUTTON_RIGHT:
                    mouse_button = 1

            events.append(
                WindowEventMouse(
                    WindowEvent._INTERNAL_MOUSE,
                    window_id=event.motion.windowID,
                    mouse_x=event.motion.x,
                    mouse_y=event.motion.y,
                    mouse_button=mouse_button
                )
            )
        elif event.type == sdl2.SDL_CONTROLLERDEVICEADDED:
            _sdlcontroller = sdl2.SDL_GameControllerOpen(event.cdevice.which)
        elif event.type == sdl2.SDL_CONTROLLERDEVICEREMOVED:
            sdl2.SDL_GameControllerClose(_sdlcontroller)
        elif event.type == sdl2.SDL_CONTROLLERBUTTONDOWN:
            events.append(WindowEvent(CONTROLLER_DOWN.get(event.cbutton.button, WindowEvent.PASS)))
        elif event.type == sdl2.SDL_CONTROLLERBUTTONUP:
            events.append(WindowEvent(CONTROLLER_UP.get(event.cbutton.button, WindowEvent.PASS)))
    return events


class WindowSDL2(PyBoyWindowPlugin):
    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_GAMECONTROLLER)
        self._ftime = time.perf_counter_ns()

        self._window = sdl2.SDL_CreateWindow(
            b"PyBoy", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, self._scaledresolution[0],
            self._scaledresolution[1], sdl2.SDL_WINDOW_RESIZABLE
        )

        self._sdlrenderer = sdl2.SDL_CreateRenderer(self._window, -1, sdl2.SDL_RENDERER_ACCELERATED)
        sdl2.SDL_RenderSetLogicalSize(self._sdlrenderer, COLS, ROWS)
        self._sdltexturebuffer = sdl2.SDL_CreateTexture(
            self._sdlrenderer, sdl2.SDL_PIXELFORMAT_ABGR8888, sdl2.SDL_TEXTUREACCESS_STATIC, COLS, ROWS
        )

        sdl2.SDL_ShowWindow(self._window)
        self.fullscreen = False

    def set_title(self, title):
        sdl2.SDL_SetWindowTitle(self._window, title.encode())

    def handle_events(self, events):
        events = sdl2_event_pump(events)
        for e in events:
            if e.event == WindowEvent.FULL_SCREEN_TOGGLE:
                if self.fullscreen:
                    sdl2.SDL_SetWindowFullscreen(self._window, 0)
                else:
                    sdl2.SDL_SetWindowFullscreen(self._window, sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
                self.fullscreen ^= True
        return events

    def post_tick(self):
        sdl2.SDL_UpdateTexture(self._sdltexturebuffer, None, self.renderer._screenbuffer_ptr, COLS * 4)
        sdl2.SDL_RenderCopy(self._sdlrenderer, self._sdltexturebuffer, None, None)
        sdl2.SDL_RenderPresent(self._sdlrenderer)
        sdl2.SDL_RenderClear(self._sdlrenderer)

    def enabled(self):
        if self.pyboy_argv.get("window_type") in ("SDL2", None):
            if not sdl2:
                logger.error("Failed to import sdl2, needed for sdl2 window")
                return False # Disable, or raise exception?
            else:
                return True
        else:
            return False

    def frame_limiter(self, speed):
        self._ftime += int((1.0 / (60.0*speed)) * 1_000_000_000)
        now = time.perf_counter_ns()
        if (self._ftime > now):
            delay = (self._ftime - now) // 1_000_000
            sdl2.SDL_Delay(delay)
        else:
            self._ftime = now
        return True

    def stop(self):
        sdl2.SDL_DestroyWindow(self._window)
        for _ in range(10): # At least 2 to close
            get_events()
        sdl2.SDL_Quit()
