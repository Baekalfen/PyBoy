#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import cython

from cpython.array cimport array
from libc.stdint cimport uint8_t, uint16_t, uint32_t

from pyboy.logging.logging cimport Logger

from .base_mbc cimport BaseMBC


cdef Logger logger

@cython.locals(carttype=uint8_t, cart_name=basestring, cart_line=basestring)
cpdef BaseMBC load_cartridge(str)
cdef bint validate_checksum(uint8_t[:,:]) noexcept

@cython.locals(romdata=array, banksize=int)
cdef uint8_t[:, :] load_romfile(str) noexcept

cdef dict CARTRIDGE_TABLE
cdef dict EXTERNAL_RAM_TABLE
