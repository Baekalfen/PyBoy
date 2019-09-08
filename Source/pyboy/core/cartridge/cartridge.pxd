#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .base_mbc cimport BaseMBC


cdef BaseMBC Cartridge(unicode)
cdef bint validate_checksum(unsigned char[:,:])
cdef unsigned char[:, :] load_romfile(unicode)

cdef dict CARTRIDGE_TABLE
cdef dict EXTERNAL_RAM_TABLE
