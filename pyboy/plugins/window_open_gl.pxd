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

cdef class WindowOpenGL(WindowOpenAL):
    cdef list events

    cdef void _glkeyboard(self, str, int, int, bint) noexcept
    cdef void _glkeyboardspecial(self, char, int, int, bint) noexcept

    # TODO: Callbacks don't really work, when Cythonized
    cpdef void _gldraw(self) noexcept
    @cython.locals(scale=double)
    cpdef void _glreshape(self, int, int) noexcept
