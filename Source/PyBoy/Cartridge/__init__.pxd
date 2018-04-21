# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# cimport GenericMBC
from PyBoy.Cartridge.GenericMBC cimport GenericMBC
# cimport RTC
from PyBoy.Cartridge.GenericMBC cimport ROM_only
from PyBoy.Cartridge.MBC1 cimport MBC1
from PyBoy.Cartridge.MBC2 cimport MBC2
from PyBoy.Cartridge.MBC3 cimport MBC3
from PyBoy.Cartridge.MBC5 cimport MBC5

import numpy as np
# cimport numpy as np
# cimport PyBoy.Global

# cdef GenericMBC Cartridge(unicode)
cdef GenericMBC Cartridge(char*)
cdef bint validateCheckSum(unsigned char[:,:])
cdef unsigned char[:, :] loadROMfile(char*)

cdef dict cartridgeTable
cdef dict ExRAMTable
