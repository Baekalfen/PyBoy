#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import cython
cimport cython
from libc.stdint cimport uint8_t, uint16_t, uint32_t
from pyboy.plugins.base_plugin cimport PyBoyWindowPlugin



cdef int ROWS, COLS

cdef class WindowOpenGL(PyBoyWindowPlugin):
    cdef list events

    cdef void _glkeyboard(self, str, int, int, bint)
    cdef void _glkeyboardspecial(self, char, int, int, bint)

    # TODO: Callbacks don't really work, when Cythonized
    cpdef void _gldraw(self)
    @cython.locals(scale=float)
    cpdef void _glreshape(self, int, int)
