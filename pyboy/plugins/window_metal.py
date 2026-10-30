#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys

try:
    import sdl2
except ImportError:
    sdl2 = None

from pyboy.plugins.window_sdl2 import WindowSDL2
from pyboy.plugins.base_plugin import PyBoyWindowPlugin
from pyboy.utils import PyBoyAssertException, PyBoyDependencyError


class WindowMetal(WindowSDL2):
    argv = []

    def __init__(self, pyboy, mb, pyboy_argv):
        self._metal_view = None
        self._metal_layer = None
        self._screen = None

        if pyboy_argv.get("window") == "Metal":
            if not pyboy.fast_mode:
                raise RuntimeError("The Metal window requires fast_mode=True")
            if pyboy_argv.get("sgb_border", False):
                raise RuntimeError("The Metal window does not support the SGB border")

        PyBoyWindowPlugin.__init__(self, pyboy, mb, pyboy_argv)

        if pyboy_argv.get("window") != "Metal":
            return

        try:
            WindowSDL2._initialize_video_audio(self, self._init_video)
            self._screen = pyboy.screen
            self._screen.gpu_tensor("mps")
        except Exception:
            self.stop()
            raise

    def _init_video(self, window_width, window_height, render_width, render_height):
        self._window = sdl2.SDL_CreateWindow(
            b"PyBoy - Metal",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            window_width,
            window_height,
            sdl2.SDL_WINDOW_RESIZABLE | sdl2.SDL_WINDOW_METAL,
        )
        if not self._window:
            sdl2.SDL_QuitSubSystem(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_GAMECONTROLLER)
            raise PyBoyAssertException("SDL_CreateWindow failed: %s", sdl2.SDL_GetError().decode())

        self._metal_view = sdl2.SDL_Metal_CreateView(self._window)
        if not self._metal_view:
            error = sdl2.SDL_GetError().decode()
            sdl2.SDL_DestroyWindow(self._window)
            self._window = None
            sdl2.SDL_QuitSubSystem(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_GAMECONTROLLER)
            raise PyBoyAssertException("SDL_Metal_CreateView failed: %s", error)

        self._metal_layer = sdl2.SDL_Metal_GetLayer(self._metal_view)
        if not self._metal_layer:
            error = sdl2.SDL_GetError().decode()
            sdl2.SDL_Metal_DestroyView(self._metal_view)
            sdl2.SDL_DestroyWindow(self._window)
            self._metal_view = None
            self._window = None
            sdl2.SDL_QuitSubSystem(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_GAMECONTROLLER)
            raise PyBoyAssertException("SDL_Metal_GetLayer failed: %s", error)

        sdl2.SDL_ShowWindow(self._window)

    def post_tick(self):
        layer_address = getattr(self._metal_layer, "value", self._metal_layer)
        self._screen._present_gpu_frame_metal(int(layer_address))
        self._post_audio()

    def enabled(self):
        if self.pyboy_argv.get("window") != "Metal":
            return False
        if sys.platform != "darwin":
            raise PyBoyDependencyError("The Metal window is only available on macOS")
        if (
            sdl2 is None
            or not hasattr(sdl2, "SDL_WINDOW_METAL")
            or not hasattr(sdl2, "SDL_Metal_CreateView")
            or not hasattr(sdl2, "SDL_Metal_GetLayer")
            or not hasattr(sdl2, "SDL_Metal_DestroyView")
        ):
            raise PyBoyDependencyError("The Metal window requires SDL2 with Metal support")

        try:
            import torch
        except ImportError as exc:
            raise PyBoyDependencyError(
                'Install the optional "ai-training" dependencies with `pip install pyboy[ai-training]`'
            ) from exc
        if not torch.backends.mps.is_available():
            raise PyBoyDependencyError("The Metal window requires an available PyTorch MPS device")
        return True

    def stop(self):
        if self._metal_view:
            sdl2.SDL_Metal_DestroyView(self._metal_view)
            self._metal_view = None
        WindowSDL2.stop(self)
