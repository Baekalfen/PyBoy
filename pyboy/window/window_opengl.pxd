#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport sdl2
from pyboy.core.lcd cimport LCD
from .window_sdl2 cimport SDLWindow

import cython
cimport cython
from libc.stdint cimport uint8_t, uint16_t, uint32_t


cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef int ROWS, COLS

cdef class OpenGLWindow(SDLWindow):
    cdef list events

    cdef void _glkeyboard(self, str, int, int, bint)
    cdef void _glkeyboardspecial(self, char, int, int, bint)

    # TODO: Callbacks don't really work, when Cythonized
    cpdef void _gldraw(self)
    @cython.locals(scale=float)
    cpdef void _glreshape(self, int, int)
