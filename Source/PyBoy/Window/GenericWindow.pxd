# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from PyBoy.LCD cimport LCD

cdef (int, int) _dummy_declaration

cdef class GenericWindow:
    cdef void setTitle(self, char*)

    # TODO: sdl2_events.SDL_Event
    cdef list getEvents(self)

    cdef void updateDisplay(self)
    cdef void framelimiter(self)
    cdef void stop(self)
    cdef void scanline(self, int, LCD)
    cdef void renderScreen(self, LCD)
    cdef void blankScreen(self)
    cdef object getScreenBuffer(self)

