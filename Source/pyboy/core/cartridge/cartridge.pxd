#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .base_mbc cimport BaseMBC

from cpython.array cimport array
from array import array

import cython
from libc.stdint cimport uint8_t, uint16_t, uint32_t


cdef BaseMBC Cartridge(unicode)
cdef bint validate_checksum(uint8_t[:,:])

@cython.locals(romdata=array, banksize=int)
cdef uint8_t[:, :] load_romfile(unicode)

cdef dict CARTRIDGE_TABLE
cdef dict EXTERNAL_RAM_TABLE
