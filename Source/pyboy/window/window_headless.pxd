#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from pyboy.lcd cimport LCD
from .window_sdl2 cimport SdlWindow

import cython
cimport cython

from libc.stdint cimport uint8_t, uint16_t, uint32_t


cdef (int, int, int, int) _dummy_declaration2

cdef (int, int) gameboyResolution

cdef class HeadlessWindow(SdlWindow):
    cdef LCD lcd
    pass
