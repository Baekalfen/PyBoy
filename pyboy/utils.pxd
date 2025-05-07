#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython
from libc.stdint cimport int64_t, uint8_t, uint16_t, uint32_t, uint64_t
from libc.math cimport ceil
from libc.stdlib cimport free as _free, malloc as _malloc

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

cdef inline uint64_t double_to_uint64_ceil(double val) noexcept nogil:
    return <uint64_t> ceil(val)

cdef inline uint8_t[:] malloc(size_t n) noexcept:
    return <uint8_t[:n]> _malloc(n)

cdef inline void free(uint8_t[:] pointer) noexcept:
    _free(<void *> &pointer[0])

##############################################################
# Window Events

cdef class WindowEvent:
    cdef readonly int __event

cdef class WindowEventMouse(WindowEvent):
    cdef readonly int window_id
    cdef readonly int mouse_x
    cdef readonly int mouse_y
    cdef readonly int mouse_scroll_x
    cdef readonly int mouse_scroll_y
    cdef readonly int mouse_button


##############################################################
# Memory Scanning
#

cpdef uint64_t dec_to_bcd(uint64_t,int byte_width=*,byteorder=*) noexcept
@cython.locals(decimal_value=uint64_t, multiplier=uint64_t)
cpdef uint64_t bcd_to_dec(uint64_t,int byte_width=*,byteorder=*) noexcept
