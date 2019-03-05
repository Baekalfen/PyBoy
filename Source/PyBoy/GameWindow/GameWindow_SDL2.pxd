# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cimport sdl2_cython.events as sdl2_events
cimport PyBoy.MathUint8
cimport SDL2 as sdl2
cimport PyBoy.LCD

import numpy as np
cimport numpy as np

# cimport PyBoy.GameWindow.AbstractGameWindow
cdef tuple gameboyResolution
# cdef object pixels2dWithoutWarning(object)

cdef class SdlGameWindow:
    # cdef tuple makeWindowAndGetBuffer(self, int, int, int, int, char*)

    cdef list getEvents(self)
    cdef unsigned int _scale
    cdef dict windowEventsDown
    cdef dict windowEventsUp
    cdef bint debug
    cdef tuple _scaledResolution
    cdef np.uint32_t[:, :] _screenBuffer
    cdef int[:, :] scanlineParameters

    # cdef int ticks
    cdef sdl2.SDL_Window *_window
    # cdef sdl2.SDL_Renderer *_renderer
    cdef sdl2.SDL_Renderer *_sdlrenderer
    cdef sdl2.SDL_Texture *_sdlTextureBuffer

    cdef void setTitle(self, char*)
    cdef void VSync(self)
    cdef void stop(self)
    cdef void scanline(self, int, tuple, tuple)
    cdef void renderScreen(self, PyBoy.LCD.LCD)
    cdef void copySprite(self, tuple, tuple, object, object, int, bint, unsigned int, xFlip=*, yFlip=*)
    cdef void blankScreen(self)
    cdef object getScreenBuffer(self)

    cdef inline void updateDisplay(self):
        sdl2.SDL_RenderCopy(
                self._sdlrenderer,
                self._sdlTextureBuffer,
                NULL,
                NULL)
        sdl2.SDL_RenderPresent(self._sdlrenderer)

