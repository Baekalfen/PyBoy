#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#


cimport cython
from libc cimport time
from libc.stdint cimport int64_t, uint64_t

from pyboy.api.gameshark cimport GameShark
from pyboy.api.memory_scanner cimport MemoryScanner
from pyboy.api.screen cimport Screen
from pyboy.api.sound cimport Sound
from pyboy.api.tilemap cimport TileMap
from pyboy.core.cpu cimport CPU
from pyboy.core.mb cimport Motherboard
from pyboy.logging.logging cimport Logger
from pyboy.plugins.manager cimport PluginManager
from pyboy.utils cimport IntIOInterface, IntIOWrapper

cdef int TILES, TILES_CGB, OPCODE_BRK

cdef Logger logger

cdef double SPF

cdef class PyBoyRegisterFile:
    cdef CPU cpu

cdef class PyBoyMemoryView:
    cdef Motherboard mb

    @cython.locals(start=int,stop=int,step=int)
    cpdef (int,int,int) _fix_slice(self, slice) noexcept
    @cython.locals(start=int,stop=int,step=int)
    cdef object __getitem(self, int, int, int, int, bint, bint)
    @cython.locals(start=int,stop=int,step=int,x=int, bank=int)
    cdef int __setitem(self, int, int, int, object, int, bint, bint) except -1

cdef class PyBoy:
    cdef Motherboard mb
    cdef readonly PluginManager _plugin_manager
    cdef readonly uint64_t frame_count
    cdef readonly str gamerom
    cdef readonly bint paused

    cdef double avg_tick
    cdef double avg_emu

    cdef readonly list events
    cdef list queued_input
    cdef bint quitting
    cdef bint stopped
    cdef bint initialized
    cdef bint no_input
    cdef readonly str window_title
    cdef readonly bint title_status
    cdef readonly PyBoyMemoryView memory
    cdef readonly PyBoyRegisterFile register_file
    cdef readonly Screen screen
    cdef readonly Sound sound
    cdef readonly TileMap tilemap_background
    cdef readonly TileMap tilemap_window
    cdef readonly object game_wrapper
    cdef readonly MemoryScanner memory_scanner
    cdef readonly GameShark gameshark
    cdef readonly str cartridge_title

    cdef bint limit_emulationspeed
    cdef int emulationspeed, target_emulationspeed, save_target_emulationspeed
    cdef bint record_input
    cdef str record_input_file
    cdef list recorded_input
    cdef list external_input

    @cython.locals(t_start=int64_t, t_pre=int64_t, t_tick=int64_t, t_post=int64_t, nsecs=int64_t)
    cdef int64_t _tick(self, bint, bint) except -1 nogil
    @cython.locals(running=bint, _render=bint, _sound=bint)
    cpdef int64_t tick(self, int count=*, bint render=*, bint sound=*) except -1
    cpdef void stop(self, save=*) noexcept
    cpdef int save_state(self, object) except -1
    cpdef int load_state(self, object) except -1

    @cython.locals(state_path=str)
    cdef void _handle_events(self, list) noexcept with gil
    cpdef void _pause(self) noexcept
    cpdef void _unpause(self) noexcept
    cdef void _update_window_title(self) noexcept
    cdef void _post_tick(self) noexcept
    cdef void _post_handle_events(self) noexcept with gil

    cdef dict _hooks
    cdef object symbols_file
    cdef public dict rom_symbols
    cdef public dict rom_symbols_inverse
    cpdef bint _handle_hooks(self) noexcept
    cpdef int hook_register(self, uint16_t, uint16_t, object, object) except -1
    cpdef int hook_deregister(self, uint16_t, uint16_t) except -1

    cpdef bint _is_cpu_stuck(self) noexcept

    cpdef object get_sprite(self, int)
    cpdef list get_sprite_by_tile_identifier(self, list, on_screen=*)
    cpdef object get_tile(self, int)
