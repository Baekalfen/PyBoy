# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cimport sdl2_cython.events as sdl2_events
# cimport PyBoy.WindowEvent

cdef enum WindowEvent:
    Quit, PressArrowUp, PressArrowDown, PressArrowRight, PressArrowLeft, PressButtonA, PressButtonB, PressButtonSelect, PressButtonStart, ReleaseArrowUp, ReleaseArrowDown, ReleaseArrowRight, ReleaseArrowLeft, ReleaseButtonA, ReleaseButtonB, ReleaseButtonSelect, ReleaseButtonStart, DebugToggle, PressSpeedUp, ReleaseSpeedUp, SaveState, LoadState, Pass


cimport PyBoy.MathUint8
cimport SDL2 as sdl2
cimport PyBoy.LCD

import numpy as np
cimport numpy as np
import cython

# cimport PyBoy.GameWindow.AbstractGameWindow
# TODO: ctuple? https://cython.readthedocs.io/en/latest/src/userguide/language_basics.html
cdef tuple gameboyResolution
cdef unsigned int alphaMask
# cdef object pixels2dWithoutWarning(object)

cdef class SdlGameWindow:
    # cdef tuple makeWindowAndGetBuffer(self, int, int, int, int, char*)

    cdef int ticks
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
    @cython.locals(y=cython.ushort, x=cython.ushort, windowViewAddress=cython.ushort, backgroundViewAddress=cython.ushort,backgroundTileIndex=cython.int, windowTileIndex=cython.int, xx=cython.int, yy=cython.int, wx=cython.int, wy=cython.int, offset=cython.int, n=cython.uchar)
    cdef void renderScreen(self, PyBoy.LCD.LCD)
    cdef void copySprite(self, tuple, tuple, object, object, int, bint, unsigned int, xFlip=*, yFlip=*)
    cdef void blankScreen(self)
    cdef object getScreenBuffer(self)

    cdef inline void updateDisplay(self):
        sdl2.SDL_UpdateTexture(self._sdlTextureBuffer, NULL, &self._screenBuffer[0,0], self._screenBuffer.strides[0])
        sdl2.SDL_RenderCopy(
                self._sdlrenderer,
                self._sdlTextureBuffer,
                NULL,
                NULL)
        sdl2.SDL_RenderPresent(self._sdlrenderer)

