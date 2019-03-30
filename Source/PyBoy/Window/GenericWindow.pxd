# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

import cython

from libc.stdint cimport uint32_t
from PyBoy.LCD cimport LCD

cdef (int, int) gameboyResolution

cdef class GenericWindow:
    cdef (int, int) _scaledResolution
    cdef unsigned int _scale
    cdef bint enable_title
    cdef void init(self)

    cdef public uint32_t[4] colorPalette
    cdef unsigned int alphaMask

    cdef void setTitle(self, unicode)
    cdef list getEvents(self)

    cdef void disableTitle(self)
    cdef void updateDisplay(self)
    cdef void framelimiter(self, int)
    cdef void stop(self)
    cdef void scanline(self, int, LCD)
    cdef void renderScreen(self, LCD)
    cdef void blankScreen(self)
    cdef object getScreenBuffer(self)

    cdef bint clearCache
    cdef set tiles_changed
    cdef void updateCache(self, LCD)
