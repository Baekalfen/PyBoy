#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.plugins.window_sdl2 cimport WindowSDL2


cdef class WindowMetal(WindowSDL2):
    cdef object _metal_view
    cdef object _metal_layer
    cdef object _screen
    cpdef void post_tick(self) except *
