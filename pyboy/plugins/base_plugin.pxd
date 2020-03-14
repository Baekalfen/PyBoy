#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
cimport cython
from pyboy.core.mb cimport Motherboard
from pyboy.core.lcd cimport Renderer
from pyboy.utils cimport WindowEvent

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2
cdef int ROWS, COLS


cdef class PyBoyPlugin:
    cdef object pyboy
    cdef Motherboard mb
    cdef dict pyboy_argv
    @cython.locals(event=WindowEvent)
    cdef list handle_events(self, list)
    cdef void post_tick(self)
    cdef str window_title(self)
    cdef void stop(self)
    cpdef bint enabled(self)


cdef class PyBoyWindowPlugin(PyBoyPlugin):

    cdef int scale
    cdef tuple _scaledresolution
    cdef bint enable_title
    cdef Renderer renderer

    cdef bint frame_limiter(self, int)
    cdef void set_title(self, str)

cdef class PyBoyGameWrapper(PyBoyPlugin):
    pass

