#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

import cython
from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t
from pyboy.utils cimport IntIOInterface

from pyboy.core.lcd cimport LCD


cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef int ROWS, COLS


cdef class BaseWindow:
    cdef (int, int) _scaledresolution
    cdef uint64_t _scale
    cdef bint enable_title
    cdef void init(self, bint)

    cdef uint32_t[4] color_palette
    cdef uint64_t alphamask
    cdef (int, int) buffer_dims

    cdef void set_title(self, str)
    cdef list get_events(self)

    cdef void save_state(self, IntIOInterface)
    cdef void load_state(self, IntIOInterface, int)
    cdef void disable_title(self)
    cdef void update_display(self, bint)
    cdef bint frame_limiter(self, int)
    cdef void stop(self)
    cdef void scanline(self, int, LCD)
    cdef void render_screen(self, LCD)
    cdef void blank_screen(self)
    cdef bytes get_screen_buffer(self)
    cdef object get_screen_buffer_as_ndarray(self)

    cdef bint clearcache
    cdef set tiles_changed
    cdef void update_cache(self, LCD)

    cdef void set_lcd(self, LCD)
