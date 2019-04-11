#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from pyboy.lcd cimport LCD
from pyboy.window.genericwindow cimport GenericWindow


cdef (int, int) _dummy_declaration

cdef class DummyWindow(GenericWindow):
    pass
