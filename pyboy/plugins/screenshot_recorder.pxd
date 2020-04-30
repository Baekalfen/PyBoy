#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.plugins.base_plugin cimport PyBoyPlugin

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef class ScreenshotRecorder(PyBoyPlugin):
    pass
