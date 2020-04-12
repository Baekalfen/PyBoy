#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython

from libc.stdint cimport uint8_t, int64_t

##############################################################
# Buffer classes

cdef class IntIOInterface:
    cdef int64_t write(self, uint8_t)
    cdef uint8_t read(self)
    cdef void seek(self, int64_t)
    cdef void flush(self)
    cdef int read_16bit(self)


cdef class IntIOWrapper(IntIOInterface):
    cdef object buffer

##############################################################
# Misc

cpdef uint8_t color_code(uint8_t, uint8_t, uint8_t)

##############################################################
# Window Events
# Temporarily placed here to not be exposed on public API

cdef class WindowEvent:
    cdef public int event

cdef class WindowEventMouse(WindowEvent):
    cdef public int window_id
    cdef public int mouse_x
    cdef public int mouse_y
    cdef public int mouse_button
