#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyPlugin


cdef Logger logger

cdef class ScreenRecorder(PyBoyPlugin):
    cdef bint recording_gif
    cdef bint recording_mp4
    cdef object ffmpeg_bin
    cdef object _session
