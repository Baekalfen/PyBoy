# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

cdef class AbstractGameWindow:
    cdef void setTitle(self, char*)

    # TODO: sdl2_events.SDL_Event
    cdef object[:] getEvents(self)

    cdef void updateDisplay(self)
    cdef void VSync(self)
    cdef void stop(self)
    cdef void scanline(self, int, tuple, tuple)
    cdef void renderScreen(self, object)
    cdef void copySprite(self, tuple, tuple, object, object, int, bint, unsigned int, xFlip=*, yFlip=*)
    cdef void blankScreen(self)
    cdef object getScreenBuffer(self)

