#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.plugins.window_sdl2 cimport WindowSDL2


cdef class WindowMetal(WindowSDL2):
    cdef object _metal_view
    cdef object _metal_layer
    cdef object _screen
    cdef object _gpu_window_error
    cpdef void post_tick(self) noexcept
    cpdef void raise_pending_error(self) except *
