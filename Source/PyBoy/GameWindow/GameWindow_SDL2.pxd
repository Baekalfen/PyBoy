# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cimport sdl2_cython.events as sdl2_events
# cimport PyBoy.WindowEvent


cimport SDL2 as sdl2
cimport PyBoy.LCD

import numpy as np
cimport numpy as np
import cython
cimport cython

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
    cdef (int, int) _scaledResolution
    cdef np.uint32_t[:, :] _screenBuffer
    cdef int[144][4] scanlineParameters

    cdef sdl2.SDL_Window *_window
    cdef sdl2.SDL_Renderer *_sdlrenderer
    cdef sdl2.SDL_Texture *_sdlTextureBuffer

    cdef void setTitle(self, char*)
    cdef void VSync(self)
    cdef void stop(self)
    cdef void scanline(self, int, (int, int), (int, int))
    @cython.locals(
            y=ushort,
            x=ushort,
            windowViewAddress=ushort,
            backgroundViewAddress=ushort,
            backgroundTileIndex=int,
            windowTileIndex=int,
            xx=int,
            yy=int,
            wx=int,
            wy=int,
            offset=int,
            n=uchar,
            fromXY=(int, int),
            toXY=(int, int),
            tileIndex=uchar,
            attributes=uchar,
            xFlip=bint,
            yFlip=bint,
            spritePriority=bint,
            # spriteCache=np.uint32_t[384 * 8][8],
            spriteSize=uchar,
            colorPalette=(int, int, int, int))
    cdef void renderScreen(self, PyBoy.LCD.LCD)

    @cython.locals(
            x1=ushort,
            y1=ushort,
            x2=ushort,
            y2=ushort,
            y=ushort,
            x=ushort,
            yy=ushort,
            xx=ushort,
            pixel=int,
            )
    cdef void copySprite(self, PyBoy.LCD.LCD, bint, (int, int), (int, int), int, bint, unsigned int, bint, bint)
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

