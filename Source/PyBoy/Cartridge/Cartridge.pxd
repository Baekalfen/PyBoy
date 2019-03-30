# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from . cimport GenericMBC
# from .GenericMBC cimport ROM_only
# from . cimport MBC1
# from . cimport MBC2
# from . cimport MBC3
# from . cimport MBC5
# from . cimport RTC

cimport numpy as np
import numpy as np
# cimport numpy as np
# cimport PyBoy.Global

# cdef GenericMBC Cartridge(unicode)
cdef public GenericMBC.GenericMBC Cartridge(char*)
cdef bint validateCheckSum(unsigned char[:,:])
cdef unsigned char[:, :] loadROMfile(char*)

cdef dict cartridgeTable
cdef dict ExRAMTable


