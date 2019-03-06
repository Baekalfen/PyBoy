# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# from RTC cimport RTC
import cython
cimport numpy as np

cdef class GenericMBC:
    cdef unicode filename
    cdef unicode gameName
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
    cdef unicode getGameName(self, unsigned char[:, :])

cdef class ROM_only(GenericMBC):
    @cython.locals(address=cython.ushort, value=cython.uchar)
    cdef void set(self, unsigned short, unsigned char)

