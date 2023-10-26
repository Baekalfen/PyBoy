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
from pyboy.utils cimport WindowEvent


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
    cdef tuple _scaledresolution
    cdef bint enable_title
    cdef Renderer renderer

    cdef bint frame_limiter(self, int) noexcept
    cdef void set_title(self, str) noexcept
