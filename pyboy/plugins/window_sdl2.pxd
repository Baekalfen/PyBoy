#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport pyboy.utils
from pyboy.plugins.base_plugin cimport PyBoyWindowPlugin
from pyboy.core.mb cimport Motherboard
import cython

cimport cython
from libc.stdint cimport int8_t, int64_t

from pyboy.logging.logging cimport Logger


cdef Logger logger

cdef int ROWS, COLS

cdef object _sdlcontroller

cpdef list sdl2_event_pump(list)


cdef class WindowSDL2(PyBoyWindowPlugin):

    cdef dict _key_down
    cdef dict _key_up
    cdef bint fullscreen
    cdef bint sound_paused

    cdef object _window
    cdef object _sdlrenderer
    cdef object _sdltexturebuffer

    cdef int64_t sound_device
    cdef object audiobuffer_p
    cdef int8_t[:] mixingbuffer
    cdef object mixingbuffer_p
    cdef object spec_want, spec_have

    cdef void init_audio(self, Motherboard) noexcept

    @cython.locals(queued_bytes=int, frames_buffered=cython.double)
    cdef bint frame_limiter(self, int) noexcept

    @cython.locals(queued_bytes=int)
    cpdef void post_tick(self) noexcept
