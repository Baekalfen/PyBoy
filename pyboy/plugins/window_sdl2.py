#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from array import array
import time
from ctypes import POINTER, c_ubyte, c_void_p, cast

from pyboy.plugins.base_plugin import PyBoyWindowPlugin
from pyboy.utils import WindowEvent, WindowEventMouse, cython_compiled, PyBoyAssertException

try:
    import sdl2
    from sdl2.ext import get_events
except ImportError:
    sdl2 = None

import pyboy
from pyboy.utils import PyBoyDependencyError

logger = pyboy.logging.get_logger(__name__)

ROWS, COLS = 144, 160

SOUND_DESYNC_THRESHOLD = 4
SOUND_PREBUFFER_THRESHOLD = 2

# https://wiki.libsdl.org/SDL_Scancode#Related_Enumerations
# fmt: off
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
# fmt: on


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
                    mouse_scroll_y=event.wheel.y,
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
                    mouse_button=mouse_button,
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

        if sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_GAMECONTROLLER) < 0:
            raise PyBoyAssertException("SDL_InitSubSystem video failed: %s", sdl2.SDL_GetError().decode())

        self._window = sdl2.SDL_CreateWindow(
            b"PyBoy",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            self._scaledresolution[0],
            self._scaledresolution[1],
            sdl2.SDL_WINDOW_RESIZABLE,
        )

        self._sdlrenderer = sdl2.SDL_CreateRenderer(self._window, -1, sdl2.SDL_RENDERER_ACCELERATED)
        sdl2.SDL_RenderSetLogicalSize(self._sdlrenderer, COLS, ROWS)
        self._sdltexturebuffer = sdl2.SDL_CreateTexture(
            self._sdlrenderer, sdl2.SDL_PIXELFORMAT_ABGR8888, sdl2.SDL_TEXTUREACCESS_STATIC, COLS, ROWS
        )

        sdl2.SDL_ShowWindow(self._window)
        self.fullscreen = False
        self.sound_paused = True

        # Helps Cython access mb.sound
        self.init_audio(mb)

    def init_audio(self, mb):
        if mb.sound.emulate:
            if sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_AUDIO) >= 0:
                # NOTE: We have to keep spec variables alive to avoid segfault
                self.spec_want = sdl2.SDL_AudioSpec(self.mb.sound.sample_rate, sdl2.AUDIO_S8, 2, 128)
                self.spec_have = sdl2.SDL_AudioSpec(0, 0, 0, 0)
                self.sound_device = sdl2.SDL_OpenAudioDevice(None, 0, self.spec_want, self.spec_have, 0)

                if self.sound_device > 1:
                    assert self.spec_have.freq == self.mb.sound.sample_rate
                    assert self.spec_have.format == sdl2.AUDIO_S8
                    assert self.spec_have.channels == 2
                    self.sound_support = True

                    self.mixingbuffer = array(self.sound.buffer_format, [0] * self.sound.audiobuffer_length)
                    if cython_compiled:
                        audiobuffer, _ = self.sound.audiobuffer.base.buffer_info()
                        mixingbuffer, _ = self.mixingbuffer.base.buffer_info()
                    else:
                        audiobuffer, _ = self.sound.audiobuffer.buffer_info()
                        mixingbuffer, _ = self.mixingbuffer.buffer_info()
                    self.audiobuffer_p = cast(c_void_p(audiobuffer), POINTER(c_ubyte))
                    self.mixingbuffer_p = cast(c_void_p(mixingbuffer), POINTER(c_ubyte))

                    sdl2.SDL_PauseAudioDevice(self.sound_device, 0)
                    self.sound_paused = False
                else:
                    self.sound_support = False
                    logger.warning("SDL_OpenAudioDevice failed: %s", sdl2.SDL_GetError().decode())
            else:
                self.sound_support = False
                logger.warning("SDL_InitSubSystem audio failed: %s", sdl2.SDL_GetError().decode())
        else:
            self.sound_support = False

    def set_title(self, title):
        if self.sound_support and self.pyboy.title_status:
            queued_bytes = sdl2.SDL_GetQueuedAudioSize(self.sound_device)
            title += f" Sound: {queued_bytes}B"
        sdl2.SDL_SetWindowTitle(self._window, title.encode())

    def handle_events(self, events):
        events = sdl2_event_pump(events)
        for e in events:
            if e == WindowEvent.FULL_SCREEN_TOGGLE:
                if self.fullscreen:
                    sdl2.SDL_SetWindowFullscreen(self._window, 0)
                else:
                    sdl2.SDL_SetWindowFullscreen(self._window, sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
                self.fullscreen ^= True
        return events

    def frame_limiter(self, speed):
        if self.sound_support and speed == 1:
            queued_bytes = sdl2.SDL_GetQueuedAudioSize(self.sound_device)
            frames_buffered = queued_bytes / (self.sound.samples_per_frame * 2.0)
            if frames_buffered > 2:
                # logger.debug("%d %f %f", queued_bytes, frames_buffered, (frames_buffered-float(2)) * (1./60.))
                # Sleep for the excees of the 2 frames of buffer we have
                time.sleep(min(1 / 60.0, (frames_buffered - float(2)) * (1.0 / 60.0)))
            return True
        else:
            return PyBoyWindowPlugin.frame_limiter(self, speed)

    def post_tick(self):
        sdl2.SDL_UpdateTexture(self._sdltexturebuffer, None, self.renderer._screenbuffer_ptr, COLS * 4)
        sdl2.SDL_RenderCopy(self._sdlrenderer, self._sdltexturebuffer, None, None)
        sdl2.SDL_RenderPresent(self._sdlrenderer)
        sdl2.SDL_RenderClear(self._sdlrenderer)

        if self.sound_support and not self.sound_paused:
            queued_bytes = sdl2.SDL_GetQueuedAudioSize(self.sound_device)

            # NOTE: Fixes audio after running more than 1x realtime
            if queued_bytes > 2 * self.mb.sound.samples_per_frame * (
                SOUND_PREBUFFER_THRESHOLD + SOUND_DESYNC_THRESHOLD
            ):
                logger.debug(
                    "Sound device buffer drifting above threshold (%s frames), resetting buffer", SOUND_DESYNC_THRESHOLD
                )
                sdl2.SDL_ClearQueuedAudio(self.sound_device)

            length = min(self.sound.audiobuffer_head, self.sound.audiobuffer_length)
            # TODO: Maybe combine the zero and mixing steps
            for i in range(length):
                self.mixingbuffer[i] = 0
            sdl2.SDL_MixAudioFormat(
                self.mixingbuffer_p, self.audiobuffer_p, sdl2.AUDIO_S8, length, self.mb.sound.volume * 128 // 100
            )

            sdl2.SDL_QueueAudio(self.sound_device, self.mixingbuffer_p, length)

    def paused(self, pause):
        self.sound_paused = pause
        if self.sound_paused:
            sdl2.SDL_PauseAudioDevice(self.sound_device, 1)
        else:
            sdl2.SDL_PauseAudioDevice(self.sound_device, 0)

    def enabled(self):
        if self.pyboy_argv.get("window") in ("SDL2", None):
            if not sdl2:
                raise PyBoyDependencyError("Failed to import sdl2, needed for sdl2 window")
            else:
                return True
        else:
            return False

    def stop(self):
        if self.enabled():
            if self.sound_support:
                sdl2.SDL_CloseAudioDevice(self.sound_device)

            sdl2.SDL_DestroyWindow(self._window)
            for _ in range(3):  # At least 2 to close
                get_events()
                time.sleep(0.1)
            sdl2.SDL_QuitSubSystem(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_GAMECONTROLLER)
