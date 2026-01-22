#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import cython

cimport cython

from pyboy.logging.logging cimport Logger
from pyboy.plugins.window_openal cimport WindowOpenAL


cdef Logger logger

cdef int ROWS, COLS

cdef class WindowGLFW(WindowOpenAL):
    cdef list events
    cdef object window

    cdef void _key_callback(self, object, int, int, int, int) noexcept

    # TODO: Callbacks don't really work, when Cythonized
    cpdef void _gldraw(self) noexcept
    @cython.locals(scale=double)
    cpdef void _window_resize(self, object, int, int) noexcept
