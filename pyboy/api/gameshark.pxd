import cython

from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t

from pyboy cimport utils
from pyboy.core.mb cimport Motherboard


cdef class GameShark:
    cdef Motherboard mb
    cdef object cheats_path
    cdef dict cheats
    cdef bint cheats_enabled

    cdef void _get_cheats(self, bint _is_path)
    cdef void _convert_cheat(self, str cheat_name, str gameshark_code)
    cdef void _update_codes(self, bint _is_path)

    cdef bint set_cheats_path(self, object cheats_path, bint _is_path)
    cpdef void run_cheats(self, object cheats_path, bint _is_path)