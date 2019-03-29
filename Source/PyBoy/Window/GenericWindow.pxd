# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from PyBoy.LCD cimport LCD

cdef (int, int) gameboyResolution

cdef class GenericWindow:
    cdef (int, int) _scaledResolution
    cdef unsigned int _scale
    cdef bint enable_title

    cdef void setTitle(self, char*)
    cdef list getEvents(self)

    cdef void updateDisplay(self)
    cdef void framelimiter(self)
    cdef void stop(self)
    cdef void scanline(self, int, LCD)
    cdef void renderScreen(self, LCD)
    cdef void blankScreen(self)
    cdef object getScreenBuffer(self)

