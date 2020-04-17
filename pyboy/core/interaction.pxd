#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.utils cimport WindowEvent
from libc.stdint cimport uint8_t

cdef uint8_t P10, P11, P12, P13, P14, P15
cdef uint8_t reset_bit(uint8_t, uint8_t)
cdef uint8_t set_bit(uint8_t, uint8_t)


cdef class Interaction:
    cdef uint8_t directional, standard
    cdef bint key_event(self, WindowEvent)
    cdef uint8_t pull(self, uint8_t)
