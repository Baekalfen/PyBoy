# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cimport PyBoy.GameWindow.AbstractGameWindow
from PyBoy.LCD cimport LCD
cdef (int, int) gameboyResolution

cdef class DummyGameWindow:
    cdef list getEvents(self)
    cdef void setTitle(self, char*)
    cdef void updateDisplay(self)
    cdef void framelimiter(self)
    cdef void stop(self)
    cdef void scanline(self, int, LCD)
    cdef void blankScreen(self)

