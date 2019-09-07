#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cdef unsigned char P10, P11, P12, P13, P14, P15
cdef unsigned char reset_bit(unsigned char, unsigned char)
cdef unsigned char set_bit(unsigned char, unsigned char)


cdef class Interaction:
    cdef unsigned char directional, standard
    cdef bint key_event(self, int)
    cdef unsigned char pull(self, unsigned char)
