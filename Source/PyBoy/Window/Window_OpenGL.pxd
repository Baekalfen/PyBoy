# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cimport sdl2_cython.events as sdl2_events
# cimport PyBoy.WindowEvent


cimport SDL2 as sdl2
from PyBoy.LCD cimport LCD
from .Window_SDL2 cimport SdlWindow

cdef (int, int, int, int) _dummy_declaration2

import cython
cimport cython
from libc.stdint cimport uint8_t, uint16_t, uint32_t

cdef (int, int) gameboyResolution

cdef class OpenGLWindow(SdlWindow):
    cdef list events
