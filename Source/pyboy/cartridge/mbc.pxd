#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from pyboy.cartridge.rtc cimport RTC
from libc.stdint cimport uint8_t, uint32_t


cdef class MBC:
    cdef unicode filename
    cdef unicode gamename
    # 256 is absoulte max. 16KB in each bank
    cdef uint8_t[256][16 * 1024] rombanks
    # 16 is absoulte max. 8KB in each bank
    cdef uint8_t[16][8 * 1024] rambanks
    cdef unsigned char carttype
    cdef bint battery
    cdef bint rtcenabled
    cdef RTC rtc
    cdef unsigned char memorymodel
    cdef bint rambankenabled
    cdef int exramcount
    cdef bint rambanksinitialized
    cdef unsigned short rambankselected
    cdef unsigned short rombankselected

    cdef void save_state(self, file)
    cdef void load_state(self, file)
    cdef void save_ram(self, file)
    cdef void load_ram(self, file)
    cdef void initrambanks(self, unsigned char)
    cdef unicode getgamename(self, list)

    cdef unsigned char getitem(self, unsigned short)
    cdef void setitem(self, unsigned short, unsigned char)


cdef class ROM(MBC):
    cdef void setitem(self, unsigned short, unsigned char)
