# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

import cython

from PyBoy.LCD cimport LCD

cdef (int, int) gameboyResolution

cdef class GenericWindow:
    cdef (int, int) _scaledResolution
    cdef unsigned int _scale
    cdef bint enable_title

    cdef (int, int, int, int) colorPalette

    cdef void setTitle(self, char*)
    cdef list getEvents(self)

    cdef void updateDisplay(self)
    cdef void framelimiter(self)
    cdef void stop(self)
    cdef void scanline(self, int, LCD)
    cdef void renderScreen(self, LCD)
    cdef void blankScreen(self)
    cdef object getScreenBuffer(self)

    cdef bint clearCache
    cdef set tiles_changed
    @cython.locals(
            x=cython.ushort,
            y=cython.ushort,
            t=cython.int,
            k=cython.int,
            pixelOnLine=cython.int,
            colorCode=cython.int,
            alpha=cython.int,
            )
    cdef void updateCache(self, LCD)
