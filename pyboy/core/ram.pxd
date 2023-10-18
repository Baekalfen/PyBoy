#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t
from pyboy.utils cimport IntIOInterface


cdef class RAM:
    cdef void save_state(self, IntIOInterface) noexcept
    cdef void load_state(self, IntIOInterface, int) noexcept

    cdef uint8_t[:] internal_ram0 # Dynamic size for DMG/CGB
    cdef uint8_t[0x60] non_io_internal_ram0
    cdef uint8_t[0x4C] io_ports
    cdef uint8_t[0x7F] internal_ram1
    cdef uint8_t[0x34] non_io_internal_ram1
    cdef bint cgb
