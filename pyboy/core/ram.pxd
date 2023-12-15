#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport cython
from libc.stdint cimport uint8_t

from pyboy.logging.logging cimport Logger
from pyboy.utils cimport IntIOInterface


cdef Logger logger

cdef class RAM:
    @cython.locals(n=int)
    cdef void save_state(self, IntIOInterface) noexcept
    @cython.locals(n=int)
    cdef void load_state(self, IntIOInterface, int) noexcept

    cdef uint8_t[:] internal_ram0 # Dynamic size for DMG/CGB
    cdef uint8_t[0x60] non_io_internal_ram0
    cdef uint8_t[0x4C] io_ports
    cdef uint8_t[0x7F] internal_ram1
    cdef uint8_t[0x34] non_io_internal_ram1
    cdef bint cgb
