#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

import cython
from libc.stdint cimport uint32_t

from pyboy.lcd cimport LCD


cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef int ROWS, COLS


cdef class BaseWindow:
    cdef (int, int) _scaledresolution
    cdef unsigned int _scale
    cdef bint enable_title
    cdef void init(self)

    cdef public uint32_t[4] color_palette
    cdef unsigned int alphamask
    cdef unicode color_format

    cdef void set_title(self, unicode)
    cdef list get_events(self)

    cdef void disable_title(self)
    cdef void update_display(self)
    cdef void frame_limiter(self, int)
    cdef void stop(self)
    cdef void scanline(self, int, LCD)
    cdef void render_screen(self, LCD)
    cdef void blank_screen(self)
    cdef object getscreenbuffer(self)

    cdef bint clearcache
    cdef set tiles_changed
    cdef void update_cache(self, LCD)

