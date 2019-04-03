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


# cdef unsigned char bytes2bits(unsigned char, unsigned char, unsigned char)

cdef (int, int) gameboyResolution

cdef class ScanlineWindow():

    cdef dict windowEventsDown
    cdef dict windowEventsUp
    cdef uint32_t[4] palette

    cdef sdl2.SDL_Window* _window
    # cdef object _renderer
    cdef sdl2.SDL_Renderer* _sdlrenderer
    cdef sdl2.SDL_Texture* _screenbuf
    cdef uint32_t[144] _linebuf
    cdef uint32_t* _linebuf_p
    cdef sdl2.SDL_Rect _linerect
    cdef uint32_t ticks

    # @cython.profile(False)
    # @cython.locals(now=cython.uint32_t)
    # cdef void framelimiter(self, int)

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
        tile=int,
        x=int,
        dx=int,
        byte0=uint8_t,
        byte1=uint8_t,
        pixel=uint32_t,
        nsprites=int,
        n=int,
        sy=int,  # These maybe should be uint8_t, since they're
        sx=int,  # getting unpacked from an array of bytes, but then
        sf=int,  # the operations would have to be overflow safe.
        dy=int,
        )
    cdef void scanline(self, int, LCD)

    cdef inline void renderScreen(self, LCD):
        sdl2.SDL_RenderCopy(
                self._sdlrenderer,
                self._screenbuf,
                NULL,
                NULL)
        sdl2.SDL_RenderPresent(self._sdlrenderer)
