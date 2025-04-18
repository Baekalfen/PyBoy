#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython
cimport numpy as cnp
from cpython.array cimport array
from libc.stdint cimport int64_t, uint8_t, uint16_t, uint32_t

from pyboy.core.lcd cimport LCD, Renderer, CGBRenderer
from pyboy.core.sound cimport Sound
from pyboy.core.mb cimport Motherboard
from pyboy.logging.logging cimport Logger
from pyboy.utils cimport WindowEvent


cdef Logger logger
cdef int ROWS, COLS


cdef class PyBoyPlugin:
    cdef object pyboy
    cdef Motherboard mb
    cdef Renderer renderer
    cdef bint is_cgb_renderer
    cdef CGBRenderer cgb_renderer
    cdef LCD lcd
    cdef bint cgb
    cdef dict pyboy_argv
    @cython.locals(event=WindowEvent)
    cdef list handle_events(self, list)
    cdef void post_tick(self) noexcept
    cdef str window_title(self)
    cdef void stop(self) noexcept
    cpdef object enabled(self) # object for actual Python bool and exceptions


cdef class PyBoyWindowPlugin(PyBoyPlugin):
    cdef bint sound_support
    cdef int scale
    cdef int[2] _scaledresolution
    cdef bint enable_title
    cdef Sound sound

    cdef int64_t _ftime
    cdef bint frame_limiter(self, int) noexcept
    cdef void set_title(self, str) noexcept


cdef class PyBoyGameWrapper(PyBoyPlugin):
    cdef readonly shape
    cdef bint game_has_started
    cdef object tilemap_background
    cdef object tilemap_window
    cdef bint tilemap_use_background
    cdef uint16_t sprite_offset
    cdef object mapping

    cdef bint _tile_cache_invalid
    cdef array _cached_game_area_tiles_raw
    cdef object _cached_game_area_tiles
    @cython.locals(xx=int, yy=int, width=int, height=int, SCX=int, SCY=int, _x=int, _y=int)
    cdef cnp.ndarray[cnp.uint32_t, ndim=2] _game_area_tiles(self)

    cdef bint game_area_follow_scxy
    cdef tuple game_area_section
    @cython.locals(tiles_matrix=cnp.ndarray, sprites=list, xx=int, yy=int, width=int, height=int, _x=int, _y=int)
    cpdef cnp.ndarray[cnp.uint32_t, ndim=2] game_area(self)

    cdef bint _sprite_cache_invalid
    cdef list _cached_sprites_on_screen
    cpdef list _sprites_on_screen(self)

    cdef object saved_state

    cpdef void post_tick(self) noexcept

    cpdef int start_game(self, timer_div=*) except -1
    cpdef int reset_game(self, timer_div=*) except -1
