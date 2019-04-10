#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from pyboy.lcd cimport LCD
from pyboy.window.genericwindow cimport GenericWindow


cdef (int, int) gameboyResolution
cdef (int, int, int, int) _dummy_declaration2

cdef class DummyWindow(GenericWindow):
    pass
