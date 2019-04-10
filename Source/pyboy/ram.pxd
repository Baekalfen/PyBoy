#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t

cdef class RAM:
    cdef void saveState(self, file)
    cdef void loadState(self, file)
    cdef public uint8_t[8*1024] internalRAM0
    cdef public uint8_t[0x60] nonIOInternalRAM0
    cdef public uint8_t[0x4C] IOPorts
    cdef public uint8_t[0x7F] internalRAM1
    cdef public uint8_t[0x34] nonIOInternalRAM1
    cdef public uint8_t[0x01] interruptRegister
