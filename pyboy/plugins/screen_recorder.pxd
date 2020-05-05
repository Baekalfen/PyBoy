#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.plugins.base_plugin cimport PyBoyPlugin


cdef class ScreenRecorder(PyBoyPlugin):
    cdef bint recording
    cdef frames

