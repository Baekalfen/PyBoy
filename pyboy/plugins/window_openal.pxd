#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import cython

cimport cython

from libc.stdint cimport uint64_t

from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyWindowPlugin
from pyboy.core.mb cimport Motherboard

cdef Logger logger

cdef class WindowOpenAL(PyBoyWindowPlugin):
    cdef object sound_device, sound_context
    cdef void init_audio(self, Motherboard) noexcept
    cdef object source, buffers, buffers_free
    cdef object audiobuffer_p
    cdef uint64_t bytes_buffered

    @cython.locals(frames_buffered=cython.double)
    cdef cython.double _get_sound_frames_buffered(self) noexcept