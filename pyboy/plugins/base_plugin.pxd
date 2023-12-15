#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython
from cpython.array cimport array
from libc.stdint cimport uint8_t, uint16_t, uint32_t

from pyboy.botsupport.tilemap cimport TileMap
from pyboy.core.lcd cimport Renderer
from pyboy.core.mb cimport Motherboard
from pyboy.logging.logging cimport Logger
from pyboy.utils cimport WindowEvent


cdef Logger logger

cdef int ROWS, COLS


cdef class PyBoyPlugin:
    cdef object pyboy
    cdef Motherboard mb
    cdef bint cgb
    cdef dict pyboy_argv
    @cython.locals(event=WindowEvent)
    cdef list handle_events(self, list) noexcept
    cdef void post_tick(self) noexcept
    cdef str window_title(self) noexcept
    cdef void stop(self) noexcept
    cpdef bint enabled(self) noexcept


cdef class PyBoyWindowPlugin(PyBoyPlugin):

    cdef int scale
    cdef int[2] _scaledresolution
    cdef bint enable_title
    cdef Renderer renderer

    cdef bint frame_limiter(self, int) noexcept
    cdef void set_title(self, str) noexcept


cdef class PyBoyGameWrapper(PyBoyPlugin):
    cdef public shape
    cdef bint game_has_started
    cdef TileMap tilemap_background
    cdef TileMap tilemap_window
    cdef bint tilemap_use_background
    cdef uint16_t sprite_offset

    cdef bint _tile_cache_invalid
    cdef array _cached_game_area_tiles_raw
    cdef uint32_t[:, :] _cached_game_area_tiles
    @cython.locals(xx=int, yy=int, width=int, height=int, SCX=int, SCY=int, _x=int, _y=int)
    cdef uint32_t[:, :] _game_area_tiles(self) noexcept

    cdef bint game_area_wrap_around
    cdef tuple game_area_section
    @cython.locals(tiles_matrix=uint32_t[:, :], sprites=list, xx=int, yy=int, width=int, height=int, _x=int, _y=int)
    cpdef uint32_t[:, :] game_area(self) noexcept

    cdef bint _sprite_cache_invalid
    cdef list _cached_sprites_on_screen
    cpdef list _sprites_on_screen(self) noexcept

    cdef object saved_state

    cpdef void post_tick(self) noexcept

    cpdef void start_game(self, timer_div=*) noexcept
    cpdef void reset_game(self, timer_div=*) noexcept
