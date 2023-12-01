#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython
from libc.stdint cimport int64_t, uint8_t, uint16_t, uint32_t, uint64_t
from cpython cimport bool

##############################################################
# Buffer classes

cdef class IntIOInterface:
    cpdef int64_t write(self, uint8_t) except -1
    cpdef int64_t write_16bit(self, uint16_t) except -1
    cpdef int64_t write_32bit(self, uint32_t) except -1
    cpdef int64_t write_64bit(self, uint64_t) except -1
    cpdef uint8_t read(self) except? -1
    cpdef uint16_t read_16bit(self) except? -1
    cpdef uint32_t read_32bit(self) except? -1

    @cython.locals(a=uint64_t, b=uint64_t, c=uint64_t,d=uint64_t,e=uint64_t,f=uint64_t,g=uint64_t,h=uint64_t,ret=uint64_t, ret2=uint64_t, ret1=uint64_t)
    cpdef uint64_t read_64bit(self) except? -1
    cpdef int seek(self, int64_t) except -1
    cpdef int flush(self) except -1
    cpdef int64_t tell(self) except -1


cdef class IntIOWrapper(IntIOInterface):
    cdef object buffer

##############################################################
# Misc

cdef uint8_t color_code(uint8_t, uint8_t, uint8_t) noexcept

##############################################################
# Window Events
# Temporarily placed here to not be exposed on public API

cdef class WindowEvent:
    cdef readonly int event

cdef class WindowEventMouse(WindowEvent):
    cdef public int window_id
    cdef public int mouse_x
    cdef public int mouse_y
    cdef public int mouse_scroll_x
    cdef public int mouse_scroll_y
    cdef public int mouse_button


##############################################################
# Memory Scanning
#
cdef class MemoryScanner:
    cdef object pyboy

    cpdef int _dec_to_bcd(self, int) noexcept
    cpdef int _bcd_to_dec(self, int) noexcept
    cpdef list scan_memory(self, int, int, int, compare_type=*, value_type=*) noexcept
    cpdef bool _check_value(self, int, int, int)noexcept
