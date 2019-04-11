#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from .mbc cimport MBC


cdef public MBC Cartridge(unicode)
cdef bint validatechecksum(unsigned char[:,:])
cdef unsigned char[:, :] loadromfile(unicode)

cdef dict CARTRIDGETABLE
cdef dict EXRAMTABLE
