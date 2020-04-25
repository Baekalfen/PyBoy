#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.utils cimport IntIOInterface
from pyboy.core.cartridge.rtc cimport RTC
from libc.stdint cimport uint8_t, uint16_t, uint32_t

cdef class BaseMBC:
    cdef str filename
    cdef str gamename
    cdef uint8_t[:, :] rombanks
    # 16 is absoulte max. 8KB in each bank
    cdef uint8_t[16][8 * 1024] rambanks
    cdef uint8_t carttype
    cdef bint battery
    cdef bint rtc_enabled
    cdef RTC rtc
    cdef uint8_t memorymodel
    cdef bint rambank_enabled
    cdef int external_ram_count
    cdef int external_rom_count
    cdef bint rambank_initialized
    cdef uint16_t rambank_selected
    cdef uint16_t rombank_selected

    cdef void save_state(self, IntIOInterface)
    cdef void load_state(self, IntIOInterface, int)
    cdef void save_ram(self, IntIOInterface)
    cdef void load_ram(self, IntIOInterface)
    cdef void init_rambanks(self, uint8_t)
    cdef str getgamename(self, uint8_t[:,:])

    cdef uint8_t getitem(self, uint16_t)
    cdef void setitem(self, uint16_t, uint8_t)
    cdef void overrideitem(self, int, uint16_t, uint8_t)


cdef class ROMOnly(BaseMBC):
    cdef void setitem(self, uint16_t, uint8_t)
