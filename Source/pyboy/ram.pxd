#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from libc.stdint cimport uint8_t

cdef class RAM:
    cdef void save_state(self, file)
    cdef void load_state(self, file)
    cdef public uint8_t[8*1024] internal_ram0
    cdef public uint8_t[0x60] non_io_internal_ram0
    cdef public uint8_t[0x4C] io_ports
    cdef public uint8_t[0x7F] internal_ram1
    cdef public uint8_t[0x34] non_io_internal_ram1
    cdef public uint8_t[0x01] interrupt_register
