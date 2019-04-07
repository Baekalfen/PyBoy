#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sdl2
import ctypes
from .Window_SDL2 import SdlWindow

class SdlWindowCPython(SdlWindow):
    def __init__(self, scale=1):
        super(self.__class__, self).__init__(scale)

    def _updateDisplay(self):
        sdl2.SDL_UpdateTexture(self._sdlTextureBuffer, None, self._screenBuffer.ctypes.data_as(ctypes.c_void_p), self._screenBuffer.strides[0])
        sdl2.SDL_RenderCopy(self._sdlrenderer, self._sdlTextureBuffer, None, None)
        sdl2.SDL_RenderPresent(self._sdlrenderer)


