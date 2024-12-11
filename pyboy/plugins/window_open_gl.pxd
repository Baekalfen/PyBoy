#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import cython

cimport cython
from libc.stdint cimport int64_t, uint8_t, uint16_t, uint32_t

from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyWindowPlugin


cdef Logger logger

cdef int ROWS, COLS

cdef class WindowOpenGL(PyBoyWindowPlugin):
    cdef list events

    cdef void _glkeyboard(self, str, int, int, bint) noexcept
    cdef void _glkeyboardspecial(self, char, int, int, bint) noexcept

    # TODO: Callbacks don't really work, when Cythonized
    cpdef void _gldraw(self) noexcept
    @cython.locals(scale=double)
    cpdef void _glreshape(self, int, int) noexcept
