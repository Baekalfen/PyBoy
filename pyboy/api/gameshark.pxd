#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t

from pyboy.logging.logging cimport Logger


cdef Logger logger

cdef class GameShark:
    cdef object memory
    cdef dict cheats
    cdef bint enabled

    cdef uint8_t _get_value(self, int, int) noexcept
    cdef void _set_value(self, int, int, int) noexcept
    cdef tuple _convert_cheat(self, str code)
    cpdef void add(self, str code) noexcept
    cpdef void remove(self, str code, bint restore_value=*) noexcept
    cpdef void clear_all(self, bint restore_value=*) noexcept
    cdef void tick(self) noexcept with gil
