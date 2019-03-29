# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

import cython
from GenericWindow cimport GenericWindow

cdef (int, int) _dummy_declaration

@cython.locals(window=GenericWindow)
cpdef GenericWindow getWindow(str, unsigned int)

