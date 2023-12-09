#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#


cimport cython
from libc cimport time
from libc.stdint cimport int64_t, uint64_t

from pyboy.api.screen cimport Screen
from pyboy.api.tilemap cimport TileMap
from pyboy.core.mb cimport Motherboard
from pyboy.logging.logging cimport Logger
from pyboy.plugins.manager cimport PluginManager
from pyboy.utils cimport IntIOInterface, IntIOWrapper


cdef Logger logger

cdef double SPF

cdef class PyBoyMemoryView:
    cdef Motherboard mb

    @cython.locals(start=int,stop=int,step=int)
    cpdef (int,int,int) _fix_slice(self, slice)
    @cython.locals(start=int,stop=int,step=int)
    cdef object __getitem(self, int, int, int, int, bint, bint)
    @cython.locals(start=int,stop=int,step=int,x=int, bank=int)
    cdef int __setitem(self, int, int, int, object, int, bint, bint) except -1

cdef class PyBoy:
    cdef Motherboard mb
    cdef public PluginManager plugin_manager
    cdef readonly uint64_t frame_count
    cdef readonly str gamerom_file
    cdef readonly bint paused

    cdef double avg_pre
    cdef double avg_tick
    cdef double avg_post

    cdef list old_events
    cdef list events
    cdef list queued_input
    cdef bint quitting
    cdef bint stopped
    cdef bint initialized
    cdef readonly str window_title
    cdef readonly PyBoyMemoryView memory
    cdef readonly Screen screen
    cdef readonly TileMap tilemap_background
    cdef readonly TileMap tilemap_window

    cdef bint limit_emulationspeed
    cdef int emulationspeed, target_emulationspeed, save_target_emulationspeed
    cdef bint record_input
    cdef bint disable_input
    cdef str record_input_file
    cdef list recorded_input
    cdef list external_input

    @cython.locals(t_start=int64_t, t_pre=int64_t, t_tick=int64_t, t_post=int64_t, nsecs=int64_t)
    cpdef bint _tick(self, bint) noexcept
    @cython.locals(running=bint)
    cpdef bint tick(self, count=*, render=*) noexcept
    cpdef void stop(self, save=*) noexcept

    @cython.locals(state_path=str)
    cdef void _handle_events(self, list) noexcept
    cpdef void _pause(self) noexcept
    cpdef void _unpause(self) noexcept
    cdef void _update_window_title(self) noexcept
    cdef void _post_tick(self) noexcept

    cdef dict _hooks
    cpdef bint _handle_hooks(self)
    cpdef int hook_register(self, uint16_t, uint16_t, object, object) except -1
    cpdef int hook_deregister(self, uint16_t, uint16_t) except -1

    cpdef bint _is_cpu_stuck(self)
    cdef void __rendering(self, int) noexcept

    cpdef object get_sprite(self, int) noexcept
    cpdef list get_sprite_by_tile_identifier(self, list, on_screen=*) noexcept
    cpdef object get_tile(self, int) noexcept
