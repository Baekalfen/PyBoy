#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cimport pyboy.plugins.autopause
cimport pyboy.plugins.base_plugin
# cimport pyboy.plugins.debug
# cimport pyboy.plugins.disable_input
# cimport pyboy.plugins.record_replay
cimport pyboy.plugins.rewind
# cimport pyboy.plugins.screenrecorder
cimport pyboy.plugins.window_dummy
cimport pyboy.plugins.window_headless
cimport pyboy.plugins.window_opengl
cimport pyboy.plugins.window_sdl2
from pyboy.plugins.base_plugin cimport PyBoyPlugin

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef class PluginManager(PyBoyPlugin):
    cdef list handle_events(self, list)
    cdef void post_tick(self)
    cdef void _post_tick_windows(self)
    cdef void frame_limiter(self, int)
    cdef str window_title(self)
    cdef void stop(self)
