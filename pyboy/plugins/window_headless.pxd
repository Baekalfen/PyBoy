#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyWindowPlugin


cdef Logger logger

cdef class WindowHeadless(PyBoyWindowPlugin):
    pass
