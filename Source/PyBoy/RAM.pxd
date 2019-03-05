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


ctypedef np.uint8_t DTYPE_t

cpdef DTYPE_t[:] allocateRAM(unsigned short, rand=*)

cdef class RAM:
    cdef public DTYPE_t[:] internalRAM0
    cdef public DTYPE_t[:] nonIOInternalRAM0
    cdef public DTYPE_t[:] IOPorts
    cdef public DTYPE_t[:] internalRAM1
    cdef public DTYPE_t[:] nonIOInternalRAM1
    cdef public DTYPE_t[:] interruptRegister
