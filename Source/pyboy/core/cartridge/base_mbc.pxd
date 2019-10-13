#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.core.cartridge.rtc cimport RTC
from libc.stdint cimport uint8_t, uint32_t

cdef class BaseMBC:
    cdef unicode filename
    cdef unicode gamename
    cdef uint8_t[:, :] rombanks
    # 16 is absoulte max. 8KB in each bank
    cdef uint8_t[16][8 * 1024] rambanks
    cdef unsigned char carttype
    cdef bint battery
    cdef bint rtc_enabled
    cdef RTC rtc
    cdef unsigned char memorymodel
    cdef bint rambank_enabled
    cdef int external_ram_count
    cdef bint rambank_initialized
    cdef unsigned short rambank_selected
    cdef unsigned short rombank_selected

    cdef void save_state(self, file)
    cdef void load_state(self, file)
    cdef void save_ram(self, file)
    cdef void load_ram(self, file)
    cdef void init_rambanks(self, unsigned char)
    cdef unicode getgamename(self, uint8_t[:,:])

    cdef unsigned char getitem(self, unsigned short)
    cdef void setitem(self, unsigned short, unsigned char)


cdef class ROMOnly(BaseMBC):
    cdef void setitem(self, unsigned short, unsigned char)
