#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport pyboy.utils
from pyboy.plugins.base_plugin cimport PyBoyWindowPlugin

import cython

cimport cython
from libc.stdint cimport int16_t, int64_t, uint8_t, uint16_t, uint32_t

from pyboy.logging.logging cimport Logger


cdef Logger logger

cdef int ROWS, COLS

cdef object _sdlcontroller

cpdef list sdl2_event_pump(list) noexcept


cdef class WindowSDL2(PyBoyWindowPlugin):

    cdef int64_t _ftime
    cdef dict _key_down
    cdef dict _key_up
    cdef bint fullscreen

    cdef object _window
    cdef object _sdlrenderer
    cdef object _sdltexturebuffer

    @cython.locals(now=int64_t, delay=int64_t)
    cdef bint frame_limiter(self, int) noexcept
