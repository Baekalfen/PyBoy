#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from . cimport sdl2
from pyboy.plugins.base_plugin cimport PyBoyWindowPlugin
cimport pyboy.utils

import cython
cimport cython
from libc.stdint cimport uint8_t, uint16_t, int16_t, uint32_t


cdef int ROWS, COLS

cdef sdl2.SDL_GameController *_sdlcontroller = NULL

cpdef list sdl2_event_pump(list)


cdef class WindowSDL2(PyBoyWindowPlugin):

    cdef float _ftime
    cdef dict _key_down
    cdef dict _key_up

    cdef sdl2.SDL_Window *_window
    cdef sdl2.SDL_Renderer *_sdlrenderer
    cdef sdl2.SDL_Texture *_sdltexturebuffer

    @cython.locals(now=float, delay=cython.int)
    cdef bint frame_limiter(self, int)

    cdef inline void _update_display(self):
        sdl2.SDL_UpdateTexture(self._sdltexturebuffer, NULL, self.renderer._screenbuffer_raw.data.as_voidptr, 160*4)
        sdl2.SDL_RenderCopy(self._sdlrenderer, self._sdltexturebuffer, NULL, NULL)
        sdl2.SDL_RenderPresent(self._sdlrenderer)
