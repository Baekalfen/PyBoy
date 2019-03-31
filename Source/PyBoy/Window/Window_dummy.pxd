# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from PyBoy.LCD cimport LCD
from PyBoy.Window.GenericWindow cimport GenericWindow
cdef (int, int) gameboyResolution
cdef (int, int, int, int) _dummy_declaration2

cdef class DummyWindow(GenericWindow):
    pass

