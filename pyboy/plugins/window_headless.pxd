#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.plugins.base_plugin cimport BaseWindowPlugin

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef class HeadlessWindow(BaseWindowPlugin):
    pass
