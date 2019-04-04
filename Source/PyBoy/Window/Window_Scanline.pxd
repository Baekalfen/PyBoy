# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


cimport cython

from libc.stdint cimport uint8_t, uint16_t, uint32_t

cimport SDL2 as sdl2
from PyBoy.LCD cimport LCD
from PyBoy.Window.GenericWindow cimport GenericWindow


cdef (int, int) gameboyResolution
cdef uint32_t[4] palette
cdef dict windowEventsDown
cdef dict windowEventsUp


cdef class ScanlineWindow(GenericWindow):


    cdef sdl2.SDL_Window* _window
    cdef sdl2.SDL_Renderer* _sdlrenderer
    cdef sdl2.SDL_Texture* _screenbuf

    cdef uint32_t[160] _linebuf
    cdef sdl2.SDL_Rect _linerect

    cdef uint32_t ticks
    cdef int scale

    @cython.profile(False)
    @cython.locals(now=uint32_t, delay=int)
    cdef void framelimiter(self, int)

    @cython.locals(
        bOffset=int,
        wOffset=int,
        bx=int,
        by=int,
        wx=int,
        wy=int,
        bdy=int,
        wdy=int,
        tile_select=bint,
        window_enabled_and_y=bint,
        bgp=uint32_t[4],
        obp0 = uint32_t[4],
        obp1 = uint32_t[4],
        tile=int,
        x=int,
        dx=int,
        byte0=uint8_t,
        byte1=uint8_t,
        pixel=int,
        nsprites=int,
        n=int,
        sy=int,  # These maybe should be uint8_t, since they're
        sx=int,  # getting unpacked from an array of bytes, but then
        sf=int,  # the operations would have to be overflow safe.
        dy=int,
        )
    cdef void scanline(self, int, LCD)

    cdef inline void _scanlineCopy(self):
        sdl2.SDL_UpdateTexture(self._screenbuf,
                               &self._linerect,
                               &self._linebuf,
                               160)

    cdef inline void _renderCopy(self):
        sdl2.SDL_RenderCopy(
                self._sdlrenderer,
                self._screenbuf,
                NULL,
                NULL)

    cdef inline void _renderPresent(self):
        sdl2.SDL_RenderPresent(self._sdlrenderer)
