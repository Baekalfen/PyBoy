#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t

from pyboy.logging.logging cimport Logger
from pyboy.utils cimport IntIOInterface, WindowEvent


cdef Logger logger

cdef uint8_t P10, P11, P12, P13, P14, P15
cdef uint8_t reset_bit(uint8_t, uint8_t) noexcept
cdef uint8_t set_bit(uint8_t, uint8_t) noexcept


cdef class Interaction:
    cdef uint8_t directional, standard
    cdef bint key_event(self, WindowEvent) noexcept
    cdef uint8_t pull(self, uint8_t) noexcept nogil
    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1
