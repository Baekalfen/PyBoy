#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from pyboy.lcd cimport LCD
from pyboy.window.window cimport Window


cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef class DummyWindow(Window):
    pass
