#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython
from pyboy.plugins.base_plugin cimport PyBoyPlugin, PyBoyWindowPlugin



cdef class PluginManager:
    cdef object pyboy

    cdef list enabled_plugins
    cdef list enabled_window_plugins
    cdef list enabled_debug_plugins
    cdef list enabled_gamewrappers

    cdef dict plugin_mapping
    cpdef list list_plugins(self)
    cpdef PyBoyPlugin get_plugin(self, str)

    cdef list handle_events(self, list)
    cdef void post_tick(self)
    cdef void _post_tick_windows(self)
    cdef void frame_limiter(self, int)
    cdef str window_title(self)
    cdef void stop(self)
    cdef void _set_title(self)
    cdef void handle_breakpoint(self)
