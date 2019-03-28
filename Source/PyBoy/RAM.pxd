# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


# cpdef unsigned int VIDEO_RAM, INTERNAL_RAM_0, OBJECT_ATTRIBUTE_MEMORY, NON_IO_INTERNAL_RAM0, IO_PORTS, NON_IO_INTERNAL_RAM1, INTERNAL_RAM_1, INTERRUPT_ENABLE_REGISTER
import numpy as np
cimport numpy as np
# cimport PyBoy.Global

# cdef int VIDEO_RAM, INTERNAL_RAM_0, OBJECT_ATTRIBUTE_MEMORY, NON_IO_INTERNAL_RAM0, IO_PORTS, NON_IO_INTERNAL_RAM1, INTERNAL_RAM_1, INTERRUPT_ENABLE_REGISTER

# cdef public int INTERNAL_RAM_0 = 8 * 1024  # 8KB
# cdef public int NON_IO_INTERNAL_RAM0 = 0x60
# cdef public int IO_PORTS = 0x4C
# cdef public int NON_IO_INTERNAL_RAM1 = 0x34
# cdef public int INTERNAL_RAM_1 = 0x7F
# cdef public int INTERRUPT_ENABLE_REGISTER = 1


ctypedef unsigned char DTYPE_t

cdef class RAM:
    cdef void saveState(self, file)
    cdef void loadState(self, file)
    cdef public DTYPE_t[8*1024] internalRAM0
    cdef public DTYPE_t[0x60] nonIOInternalRAM0
    cdef public DTYPE_t[0x4C] IOPorts
    cdef public DTYPE_t[0x7F] internalRAM1
    cdef public DTYPE_t[0x34] nonIOInternalRAM1
    cdef public DTYPE_t[0x01] interruptRegister
