# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# from RTC cimport RTC
cimport numpy as np

cdef class GenericMBC:
    cdef char* filename
    cdef char* gameName
    cdef unsigned char[:,:] ROMBanks
    cdef unsigned char[:,:] RAMBanks
    cdef unsigned char cartType
    cdef bint battery
    cdef bint rtcEnabled
    cdef object rtc
    cdef unsigned char memoryModel
    cdef bint RAMBankEnabled
    cdef bint RAMBanksInitialized
    cdef unsigned short RAMBankSelected
    cdef unsigned short ROMBankSelected

    cdef void saveRAM(self, filename=*)
    cdef void loadRAM(self, filename=*)
    cdef void initRAMBanks(self, unsigned char)
    cdef char* getGameName(self, unsigned char[:, :])

cdef class ROM_only(GenericMBC):
    pass

