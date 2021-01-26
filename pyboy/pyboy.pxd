#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from libc cimport time
cimport cython
from libc.stdint cimport uint64_t
from pyboy.core.mb cimport Motherboard
from pyboy.utils cimport IntIOWrapper, IntIOInterface
from pyboy.plugins.manager cimport PluginManager


cdef float SPF

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
    cdef public str window_title

    cdef bint limit_emulationspeed
    cdef int emulationspeed, target_emulationspeed, save_target_emulationspeed
    cdef object screen_recorder
    cdef bint record_input
    cdef bint disable_input
    cdef str record_input_file
    cdef list recorded_input
    cdef list external_input

    @cython.locals(done=cython.bint, event=int, t_start=float, t_cpu=float, t_emu=float, secs=float)
    cpdef bint tick(self)
    cpdef void stop(self, save=*)
