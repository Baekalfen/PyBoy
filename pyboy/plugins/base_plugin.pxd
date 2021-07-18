#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from cpython.array cimport array
from libc.stdint cimport uint8_t, uint32_t
cimport cython
from pyboy.botsupport.tilemap cimport TileMap
from pyboy.core.mb cimport Motherboard
from pyboy.core.lcd cimport Renderer
from pyboy.utils cimport WindowEvent

cdef int ROWS, COLS


cdef class PyBoyPlugin:
    cdef object pyboy
    cdef Motherboard mb
    cdef dict pyboy_argv
    @cython.locals(event=WindowEvent)
    cdef list handle_events(self, list)
    cdef void post_tick(self)
    cdef str window_title(self)
    cdef void stop(self)
    cpdef bint enabled(self)


cdef class PyBoyWindowPlugin(PyBoyPlugin):

    cdef int scale
    cdef tuple _scaledresolution
    cdef bint enable_title
    cdef Renderer renderer

    cdef bint frame_limiter(self, int)
    cdef void set_title(self, str)


cdef class PyBoyGameWrapper(PyBoyPlugin):
    cdef public shape
    cdef bint game_has_started
    cdef TileMap tilemap_background

    cdef bint _tile_cache_invalid
    cdef array _cached_game_area_tiles_raw
    cdef uint32_t[:, :] _cached_game_area_tiles
    @cython.locals(xx=int, yy=int, width=int, height=int, SCX=int, SCY=int, _x=int, _y=int)
    cdef uint32_t[:, :] _game_area_tiles(self)

    cdef bint game_area_wrap_around
    cdef tuple game_area_section
    @cython.locals(tiles_matrix=uint32_t[:, :], sprites=list, xx=int, yy=int, width=int, height=int, _x=int, _y=int)
    cpdef uint32_t[:, :] game_area(self)

    cdef bint _sprite_cache_invalid
    cdef list _cached_sprites_on_screen
    cpdef list _sprites_on_screen(self)

    cdef object saved_state

    cpdef void post_tick(self)

    cpdef void start_game(self, timer_div=*)
    cpdef void reset_game(self, timer_div=*)
