#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from cpython.array cimport array
from array import array

cimport SDL2 as sdl2
from pyboy.lcd cimport LCD

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
    @cython.locals(
            y=int,
            x=int,
            yy=int,
            xx=int,
            )
    cdef void copy_tile(self, uint32_t[:,:], int, (int, int), uint32_t[:,:])
    cdef void update_display(self)
    cdef inline void _update_display(self):
        # sdl2.SDL_UpdateTexture(self.sdl_texture_buffer, NULL, self.buf_p, 160*4)
        sdl2.SDL_UpdateTexture(self.sdl_texture_buffer, NULL, self.buf.data.as_voidptr, self.width*4)
        sdl2.SDL_RenderCopy(self.sdlrenderer, self.sdl_texture_buffer, NULL, NULL)
        sdl2.SDL_RenderPresent(self.sdlrenderer)

    cdef int mouse_x, mouse_y, mouse_hover_x, mouse_hover_y
    cdef int mouse(self, bint, int, int, int)
    cdef int _mouse(self, bint, int, int, int)
    cdef void mark_tile(self, int, int, int)


cdef class TileWindow(Window):
    @cython.locals(t=int, xx=int, yy=int)
    cdef void update(self, uint32_t[:,:])
    @cython.locals(t=int)
    cdef void draw_overlay(self, int, uint8_t[144][4])


cdef class TileViewWindow(Window):
    cdef int offset
    @cython.locals(tile_column=int, tile_row=int, des=(int, int), x=int, y=int, n=int, hor_limit=int, ver_limit=int)
    cdef void update(self, LCD, uint32_t[:,:])
    cdef void draw_overlay(self, int, uint8_t[144][4], int, int)


cdef class DebugWindow():
    cdef LCD lcd
    cdef void set_lcd(self, LCD)
    cdef public uint32_t[4] color_palette
    # cdef unsigned int alpha_mask
    # cdef unicode color_format
    cdef unsigned int scale
    # cdef bint enable_title

    # cdef uint32_t ticks
    # # cdef list get_events(self)
    # cdef dict window_events_down
    # cdef dict window_events_up
    # cdef array _screen_buffer
    # cdef array _tile_cache, _sprite_cache_OBP0, _sprite_cache_OBP1
    # cdef uint32_t[:,:] screen_buffer

    cdef int marked_tile
    cdef void mouse(self, bint, int, long, long)

    cdef TileViewWindow tile1
    cdef TileViewWindow tile2
    cdef Window sprite
    cdef TileWindow tile
    cdef int tile_data_width
    cdef int tile_data_height

    cdef array tile_cache
    cdef uint32_t[:,:] tile_cache0
    cdef object tile_cache_p

    cdef uint8_t[144][4] scanline_parameters

    cdef sdl2.SDL_Window *_window
    cdef sdl2.SDL_Renderer *_sdlrenderer
    cdef sdl2.SDL_Texture *_sdl_texture_buffer

    @cython.locals(view_pos=(int, int), window_pos=(int, int))
    cdef void scanline(self, int)

    cdef bint clear_cache
    cdef set tiles_changed
    @cython.locals(
            y=int,
            x=int,
            window_view_address=int,
            background_view_address=int,
            background_tile_index=int,
            window_tile_index=int,
            bx=int,
            by=int,
            wx=int,
            wy=int,
            offset=int,
            BGPkey=uint32_t,
            sprite_size=int,
            n=int,
            tile_index=int,
            attributes=int,
            x_flip=bint,
            y_flip=bint,
            sprite_priority=bint,
            sprite_cache=uint32_t[:,:],
            dy=int,
            dx=int,
            yy=int,
            xx=int,
            pixel=uint32_t,
            )
    cdef void update(self)

    @cython.locals(
        x=int,
        t=int,
        k=int,
        y=int,
        byte1=uint8_t,
        byte2=uint8_t,
        color_code=uint32_t,
        alpha=uint32_t
        )
    cdef void update_cache(self)


