#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.plugins.base_plugin cimport PyBoyWindowPlugin
cimport pyboy.utils

import cython
cimport cython
from libc.stdint cimport int64_t, uint8_t, uint16_t, int16_t, uint32_t


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
