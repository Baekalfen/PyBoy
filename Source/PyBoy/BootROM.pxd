# -*- encoding: utf-8 -*-
#
# Authors: Mads Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import numpy as np
cimport numpy as np
# cimport PyBoy.Global

ctypedef np.uint8_t DTYPE_t

cdef class BootROM:
    cdef public DTYPE_t[:] bootROM
    # cdef np.ndarray[DTYPE_t, ndim=256] _bootROM

