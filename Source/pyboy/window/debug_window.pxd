#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from cpython.array cimport array
from array import array

cimport sdl2
from pyboy.core.lcd cimport LCD
from .window_sdl2 cimport SDLWindow

cdef (int, int, int, int) _dummy_declaration2

import cython
cimport cython
from libc.stdint cimport uint8_t, uint16_t, uint32_t

cdef unsigned char get_color_code(unsigned char, unsigned char, unsigned char)

cdef int TILES, COLOR, MASK
cdef (int, int) GAMEBOY_RESOLUTION


cdef tuple make_buffer(int, int)

cdef class Window():
    cdef LCD lcd
    cdef int width
    cdef int height
    cdef int scale
    cdef sdl2.SDL_Window *window

    cdef array buf
    cdef uint32_t[:,:] buf0
    cdef object buf_p

    cdef sdl2.SDL_Renderer *sdlrenderer
    cdef sdl2.SDL_Texture *sdl_texture_buffer

    cdef void reset_hover(self)

    cdef void stop(self)
    @cython.locals(y=int, x=int, yy=int, xx=int)
    cdef void copy_tile(self, uint32_t[:,:], int, (int, int), uint32_t[:,:])

    cdef void update_display(self, bint)
    cdef inline void _update_display(self):
        sdl2.SDL_UpdateTexture(self.sdl_texture_buffer, NULL, self.buf.data.as_voidptr, self.width*4)
        sdl2.SDL_RenderCopy(self.sdlrenderer, self.sdl_texture_buffer, NULL, NULL)
        sdl2.SDL_RenderPresent(self.sdlrenderer)

    cdef int mouse_x, mouse_y, mouse_hover_x, mouse_hover_y
    cdef int mouse(self, bint, int, int, int)
    cdef int _mouse(self, bint, int, int, int)
    @cython.locals(tw=int, th=int, xx=int, yy=int)
    cdef void mark_tile(self, int, int, int, height=*, width=*)


cdef class SpriteWindow(Window):
    @cython.locals(n=int, t=int, xx=int, yy=int)
    cdef void update(self, uint32_t[:,:], int, uint8_t[144][4])
    @cython.locals(t=int)
    cdef void draw_overlay(self, int, uint8_t[144][4])


cdef class TileWindow(Window):
    @cython.locals(t=int, xx=int, yy=int)
    cdef void update(self, uint32_t[:,:], int, uint8_t[144][4])
    @cython.locals(t=int)
    cdef void draw_overlay(self, int, uint8_t[144][4])


cdef class TileViewWindow(Window):
    cdef int offset
    @cython.locals(tile_column=int, tile_row=int, des=(int, int), x=int, y=int, n=int, hor_limit=int, ver_limit=int)
    cdef void update(self, uint32_t[:,:], int, uint8_t[144][4], int, int)
    cdef void draw_overlay(self, int, uint8_t[144][4], int, int)


cdef class DebugWindow(SDLWindow):
    cdef LCD lcd
    cdef void set_lcd(self, LCD)
    cdef unsigned int scale

    cdef int marked_tile
    cdef void mouse(self, bint, int, long, long)

    cdef bint tile1_update
    cdef bint tile2_update
    cdef bint sprite_update
    cdef bint tile_update

    cdef TileViewWindow tile1
    cdef TileViewWindow tile2
    cdef SpriteWindow sprite
    cdef TileWindow tile
    cdef int tile_data_width
    cdef int tile_data_height

    @cython.locals(view_pos=(int, int), window_pos=(int, int))
    cdef void scanline(self, int, LCD)

