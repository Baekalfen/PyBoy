# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

cimport GenericMBC
cimport ROM_only
cimport MBC1
cimport MBC2
cimport MBC3
cimport MBC5
cimport RTC

cimport numpy as np
import numpy as np
# cimport numpy as np
# cimport PyBoy.Global

# cdef GenericMBC Cartridge(unicode)
cdef GenericMBC Cartridge(char*)
cdef bint validateCheckSum(unsigned char[:,:])
cdef unsigned char[:, :] loadROMfile(char*)

cdef dict cartridgeTable
cdef dict ExRAMTable


