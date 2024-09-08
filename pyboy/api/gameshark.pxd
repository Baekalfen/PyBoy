import cython

from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t

from pyboy cimport utils
from pyboy.core.mb cimport Motherboard


cdef class GameShark:
    cdef Motherboard mb
    cdef dict cheats

    cpdef void load_from_file(self, str path)
    cdef void _convert_cheat(self, str cheat_name, str gameshark_code)
    cpdef void add_cheat(self, str cheat_name, str gameshark_code)
    cpdef void remove_cheat(self, str cheat_name)
    cpdef void clear(self)
    cdef void tick(self)
