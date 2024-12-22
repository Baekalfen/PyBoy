#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t, int64_t

from pyboy.logging.logging cimport Logger


cdef Logger logger

cdef class GameShark:
    cdef object memory
    cdef dict cheats
    cdef bint enabled

    cdef int64_t _get_value(self, int, int) except -1
    cdef int64_t _set_value(self, int, int, int) except -1
    cdef tuple _convert_cheat(self, str code)
    cpdef int64_t add(self, str code) except -1
    cpdef int64_t remove(self, str code, bint restore_value=*) except -1
    cpdef int64_t clear_all(self, bint restore_value=*) except -1
    cdef int64_t tick(self) except -1 with gil
