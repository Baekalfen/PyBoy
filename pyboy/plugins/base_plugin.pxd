#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from pyboy.core.lcd cimport Renderer

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2
cdef int ROWS, COLS

cdef class PyBoyPlugin:

    cdef list handle_events(self, list)
    cdef void post_tick(self)
    cdef str window_title(self)
    cdef void stop(self)
    cdef bint enabled(self)


cdef class BaseWindowPlugin(PyBoyPlugin):
    cdef int _scale
    cdef tuple _scaledresolution
    cdef bint enable_title
    cdef Renderer renderer

    cdef bint frame_limiter(self, int)
    cdef void set_title(self, str)
