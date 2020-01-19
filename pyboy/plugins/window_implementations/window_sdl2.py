#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sdl2
import sdl2.ext
from pyboy import windowevent

from .base_window import BaseWindow

ROWS, COLS = 144, 160

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False

# https://wiki.libsdl.org/SDL_Scancode#Related_Enumerations
KEY_DOWN = {
    sdl2.SDLK_UP        : windowevent.PRESS_ARROW_UP,
    sdl2.SDLK_DOWN      : windowevent.PRESS_ARROW_DOWN,
    sdl2.SDLK_RIGHT     : windowevent.PRESS_ARROW_RIGHT,
    sdl2.SDLK_LEFT      : windowevent.PRESS_ARROW_LEFT,
    sdl2.SDLK_a         : windowevent.PRESS_BUTTON_A,
    sdl2.SDLK_s         : windowevent.PRESS_BUTTON_B,
    sdl2.SDLK_RETURN    : windowevent.PRESS_BUTTON_START,
    sdl2.SDLK_BACKSPACE : windowevent.PRESS_BUTTON_SELECT,
    sdl2.SDLK_SPACE     : windowevent.PRESS_SPEED_UP,
    sdl2.SDLK_COMMA     : windowevent.PRESS_REWIND_BACK,
    sdl2.SDLK_PERIOD    : windowevent.PRESS_REWIND_FORWARD,
}

KEY_UP = {
    sdl2.SDLK_UP        : windowevent.RELEASE_ARROW_UP,
    sdl2.SDLK_DOWN      : windowevent.RELEASE_ARROW_DOWN,
    sdl2.SDLK_RIGHT     : windowevent.RELEASE_ARROW_RIGHT,
    sdl2.SDLK_LEFT      : windowevent.RELEASE_ARROW_LEFT,
    sdl2.SDLK_a         : windowevent.RELEASE_BUTTON_A,
    sdl2.SDLK_s         : windowevent.RELEASE_BUTTON_B,
    sdl2.SDLK_RETURN    : windowevent.RELEASE_BUTTON_START,
    sdl2.SDLK_BACKSPACE : windowevent.RELEASE_BUTTON_SELECT,
    sdl2.SDLK_z         : windowevent.SAVE_STATE,
    sdl2.SDLK_x         : windowevent.LOAD_STATE,
    sdl2.SDLK_SPACE     : windowevent.RELEASE_SPEED_UP,
    sdl2.SDLK_p         : windowevent.PAUSE_TOGGLE,
    sdl2.SDLK_i         : windowevent.SCREEN_RECORDING_TOGGLE,
    sdl2.SDLK_ESCAPE    : windowevent.QUIT,
    sdl2.SDLK_d         : windowevent.DEBUG_TOGGLE,
    sdl2.SDLK_COMMA     : windowevent.RELEASE_REWIND_BACK,
    sdl2.SDLK_PERIOD    : windowevent.RELEASE_REWIND_FORWARD,
}


class SDLWindow(BaseWindow):
    color_format = u"ABGR"

    def __init__(self, renderer, scale, color_palette, hide_window):
        BaseWindow.__init__(self, renderer, scale, color_palette, hide_window)

        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        self._ticks = sdl2.SDL_GetTicks()

        self._window = sdl2.SDL_CreateWindow(
            b"PyBoy",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            self._scaledresolution[0],
            self._scaledresolution[1],
            sdl2.SDL_WINDOW_RESIZABLE)

        self._sdlrenderer = sdl2.SDL_CreateRenderer(self._window, -1, sdl2.SDL_RENDERER_ACCELERATED)

        self._sdltexturebuffer = sdl2.SDL_CreateTexture(
            self._sdlrenderer, sdl2.SDL_PIXELFORMAT_RGBA32,
            sdl2.SDL_TEXTUREACCESS_STATIC, COLS, ROWS)

        self.blank_screen()

        if hide_window:
            sdl2.SDL_HideWindow(self._window)
        else:
            sdl2.SDL_ShowWindow(self._window)

    def set_title(self, title):
        sdl2.SDL_SetWindowTitle(self._window, title.encode())

    def handle_events(self, events):
        # Feed events into the loop
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                events.append(windowevent.QUIT)
            elif event.type == sdl2.SDL_KEYDOWN:
                events.append(KEY_DOWN.get(event.key.keysym.sym, windowevent.PASS))
            elif event.type == sdl2.SDL_KEYUP:
                events.append(KEY_UP.get(event.key.keysym.sym, windowevent.PASS))
            elif event.type == sdl2.SDL_WINDOWEVENT:
                if event.window.windowID == 1:
                    if event.window.event == sdl2.SDL_WINDOWEVENT_FOCUS_LOST:
                        events.append(windowevent.WINDOW_UNFOCUS)
                    elif event.window.event == sdl2.SDL_WINDOWEVENT_FOCUS_GAINED:
                        events.append(windowevent.WINDOW_FOCUS)

        return events

    def update_display(self, paused):
        if not paused:
            self._update_display()

    def frame_limiter(self, speed):
        now = sdl2.SDL_GetTicks()
        delay = int(1000.0/(60.0*speed) - (now-self._ticks))
        sdl2.SDL_Delay(delay if delay > 0 else 0)
        self._ticks = sdl2.SDL_GetTicks()

    def stop(self):
        sdl2.SDL_DestroyWindow(self._window)
        sdl2.SDL_Quit()



# Unfortunately CPython/PyPy code has to be hidden in an exec call to
# prevent Cython from trying to parse it. This block provides the
# functions that are otherwise implemented as inlined cdefs in the pxd
if not cythonmode:
    exec("""
def _update_display(self):
    sdl2.SDL_UpdateTexture(self._sdltexturebuffer, None, self.renderer._screenbuffer_ptr, COLS*4)
    sdl2.SDL_RenderCopy(self._sdlrenderer, self._sdltexturebuffer, None, None)
    sdl2.SDL_RenderPresent(self._sdlrenderer)
    sdl2.SDL_RenderClear(self._sdlrenderer)

SDLWindow._update_display = _update_display
""", globals(), locals())
