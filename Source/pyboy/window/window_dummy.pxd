#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.lcd cimport LCD
from pyboy.window.base_window cimport BaseWindow


cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef class DummyWindow(BaseWindow):
    pass
