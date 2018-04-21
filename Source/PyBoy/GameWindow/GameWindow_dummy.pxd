# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cimport PyBoy.GameWindow.AbstractGameWindow
cdef tuple gameboyResolution
# cdef object pixels2dWithoutWarning(object)

cdef class DummyGameWindow:
    # cdef tuple makeWindowAndGetBuffer(self, int, int, int, int, char*)

    # cdef void setTitle(self, char*)

    # TODO: sdl2_events.SDL_Event
    # cdef object[:] getEvents(self)
    cdef unsigned int _scale
    cdef dict windowEventsDown
    cdef dict windowEventsUp
    cdef bint debug
    cdef tuple _scaledResolution
    cdef object _window
    cdef object _windowSurface
    cdef object _screenBuffer # TODO: Make into NumPy array
    cdef int[:, :] scanlineParameters

    cdef object win
    cdef object renderer

    cpdef void updateDisplay(self)
    cpdef void VSync(self)
    # cdef void stop(self)
    cpdef void scanline(self, int, tuple, tuple)
    cpdef void blankScreen(self)

