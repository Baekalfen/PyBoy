# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from PyBoy.Cartridge.RTC cimport RTC
import cython
cimport numpy as np

cdef class GenericMBC:
    cdef unicode filename
    cdef unicode gameName
    # 256 is absoulte max. 16KB in each bank
    cdef unsigned char[256][16 * 1024] ROMBanks
    # 16 is absoulte max. 8KB in each bank
    cdef unsigned char[16][8 * 1024] RAMBanks
    cdef unsigned char cartType
    cdef bint battery
    cdef bint rtcEnabled
    cdef RTC rtc
    cdef unsigned char memoryModel
    cdef bint RAMBankEnabled
    cdef int exRAMCount
    cdef bint RAMBanksInitialized
    cdef unsigned short RAMBankSelected
    cdef unsigned short ROMBankSelected

    cdef void saveState(self, file)
    cdef void loadState(self, file)
    cdef void saveRAM(self, file)
    cdef void loadRAM(self, file)
    cdef void initRAMBanks(self, unsigned char)
    cdef unicode getGameName(self, unsigned char[:, :])

    cdef unsigned char getitem(self, unsigned short)
    cdef void setitem(self, unsigned short, unsigned char)

cdef class ROM_only(GenericMBC):
    cdef void setitem(self, unsigned short, unsigned char)

