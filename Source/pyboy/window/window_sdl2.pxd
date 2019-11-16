#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from cpython.array cimport array
from array import array

cimport sdl2
from pyboy.core.lcd cimport LCD
from pyboy.window.base_window cimport BaseWindow

import cython
cimport cython
from libc.stdint cimport uint8_t, uint16_t, int16_t, uint32_t


cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef unsigned char getcolorcode(unsigned char, unsigned char, unsigned char)

cdef int ROWS, COLS


cdef class SDLWindow(BaseWindow):

    cdef uint32_t _ticks
    cdef dict _key_down
    cdef dict _key_up
    cdef array _screenbuffer_raw
    cdef array _tilecache_raw, _spritecache0_raw, _spritecache1_raw
    cdef uint32_t[:,:] _screenbuffer
    cdef uint32_t[:,:] _tilecache, _spritecache0, _spritecache1

    cdef uint8_t[144][4] _scanlineparameters

    cdef sdl2.SDL_Window *_window
    cdef sdl2.SDL_Renderer *_sdlrenderer
    cdef sdl2.SDL_Texture *_sdltexturebuffer

    @cython.locals(now=uint32_t, delay=cython.int)
    cdef void frame_limiter(self, int)

    @cython.locals(viewpos=(int, int), windowpos=(int, int))
    cdef void scanline(self, int, LCD)

    # cdef void set_lcd(self, LCD)

    @cython.locals(
        y=int,
        x=int,
        wmap=int,
        background_offset=int,
        bt=int,
        wt=int,
        bx=int,
        by=int,
        wx=int,
        wy=int,
        offset=int,
        bgpkey=uint32_t,
        spriteheight=int,
        n=int,
        tileindex=int,
        attributes=int,
        xflip=bint,
        yflip=bint,
        spritepriority=bint,
        spritecache=uint32_t[:,:],
        dy=int,
        dx=int,
        yy=int,
        xx=int,
        pixel=uint32_t,
    )
    cdef void render_screen(self, LCD)

    @cython.locals(
        x=int,
        t=int,
        k=int,
        y=int,
        byte1=uint8_t,
        byte2=uint8_t,
        colorcode=uint32_t,
        alpha=uint32_t
        )
    cdef void update_cache(self, LCD)

    cdef inline void _update_display(self):
        sdl2.SDL_UpdateTexture(self._sdltexturebuffer, NULL, self._screenbuffer_raw.data.as_voidptr, 160*4)
        sdl2.SDL_RenderCopy(self._sdlrenderer, self._sdltexturebuffer, NULL, NULL)
        sdl2.SDL_RenderPresent(self._sdlrenderer)
