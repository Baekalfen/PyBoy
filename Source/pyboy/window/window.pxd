#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#


import cython
from .genericwindow cimport GenericWindow


cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

@cython.locals(window=GenericWindow)
cpdef GenericWindow getWindow(str, unsigned int)
