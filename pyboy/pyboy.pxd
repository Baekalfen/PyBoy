#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#


cimport cython
from libc cimport time
from libc.stdint cimport int64_t, uint64_t

from pyboy.core.mb cimport Motherboard
from pyboy.logging.logging cimport Logger
from pyboy.plugins.manager cimport PluginManager
from pyboy.utils cimport IntIOInterface, IntIOWrapper


cdef Logger logger

cdef double SPF

cdef class PyBoy:
    cdef Motherboard mb
    cdef public PluginManager plugin_manager
    cdef public uint64_t frame_count
    cdef public str gamerom_file
    cdef readonly bint paused

    cdef double avg_pre
    cdef double avg_tick
    cdef double avg_post

    cdef list old_events
    cdef list events
    cdef bint quitting
    cdef bint stopped
    cdef bint initialized
    cdef public str window_title

    cdef bint limit_emulationspeed
    cdef int emulationspeed, target_emulationspeed, save_target_emulationspeed
    cdef object screen_recorder
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
