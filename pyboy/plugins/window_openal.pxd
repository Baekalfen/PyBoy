#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import cython

cimport cython

from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyWindowPlugin
from pyboy.core.mb cimport Motherboard

cdef Logger logger

cdef class WindowOpenAL(PyBoyWindowPlugin):
    cdef object sound_device, sound_context
    cdef void init_audio(self, Motherboard) noexcept
    cdef object source, buffers, buffers_free
    cdef object audiobuffer_p