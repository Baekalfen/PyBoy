# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cimport sdl2_cython.events as sdl2_events
# cimport PyBoy.WindowEvent


from cpython.array cimport array
from array import array

from cpython.buffer cimport PyObject_GetBuffer, PyBuffer_Release, PyBUF_ANY_CONTIGUOUS, PyBUF_SIMPLE

cimport SDL2 as sdl2
from PyBoy.LCD cimport LCD
from PyBoy.Window.GenericWindow cimport GenericWindow

cdef (int, int, int, int) _dummy_declaration2

import cython
cimport cython
from libc.stdint cimport uint8_t, uint16_t, uint32_t

cdef unsigned char getColorCode(unsigned char, unsigned char, unsigned char)

cdef (int, int) gameboyResolution

cdef class SdlWindow(GenericWindow):
    # cdef tuple makeWindowAndGetBuffer(self, int, int, int, int, char*)

    cdef int ticks
    # cdef list getEvents(self)
    cdef dict windowEventsDown
    cdef dict windowEventsUp
    cdef uint8_t[:] _screenBuffer
    cdef uint8_t[:] _tileCache, _spriteCacheOBP0, _spriteCacheOBP1
    cdef uint32_t[:,:] screenBuffer
    cdef uint32_t[:,:] tileCache, spriteCacheOBP0, spriteCacheOBP1

    cdef uint8_t[144][4] scanlineParameters

    cdef sdl2.SDL_Window *_window
    cdef sdl2.SDL_Renderer *_sdlrenderer
    cdef sdl2.SDL_Texture *_sdlTextureBuffer

    # cdef void setTitle(self, char*)

    @cython.locals(now=cython.int, delay=cython.int)
    cdef void framelimiter(self, int)

    @cython.locals(viewPos=(int, int), windowPos=(int, int))
    cdef void scanline(self, int, LCD)

    @cython.locals(
            y=int,
            x=int,
            windowViewAddress=int,
            backgroundViewAddress=int,
            backgroundTileIndex=int,
            windowTileIndex=int,
            bx=int,
            by=int,
            wx=int,
            wy=int,
            offset=int,
            n=int,
            tileIndex=int,
            attributes=int,
            xFlip=bint,
            yFlip=bint,
            spritePriority=bint,
            spriteSize=int,
            yy=int,
            xx=int,
            pixel=uint32_t,
            )
    cdef void renderScreen(self, LCD)

    # Not directly override updateDisplay. Otherwise we get: "Overriding final methods is not allowed"
    cdef inline void _updateDisplay(self):
        cdef Py_buffer buffer
        PyObject_GetBuffer(self._screenBuffer, &buffer, PyBUF_SIMPLE | PyBUF_ANY_CONTIGUOUS)
        try:
            sdl2.SDL_UpdateTexture(self._sdlTextureBuffer, NULL, <void*>buffer.buf, 160*4)
        finally:
            PyBuffer_Release(&buffer)
        sdl2.SDL_RenderCopy(
                self._sdlrenderer,
                self._sdlTextureBuffer,
                NULL,
                NULL)
        sdl2.SDL_RenderPresent(self._sdlrenderer)
