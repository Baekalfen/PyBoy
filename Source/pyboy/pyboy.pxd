#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


from libc cimport time
cimport cython
from libc.stdint cimport uint64_t
from pyboy.core.mb cimport Motherboard
from pyboy.rewind cimport IntIOWrapper, IntIOInterface, FixedAllocBuffers
from pyboy.window.base_window cimport BaseWindow

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef float SPF
cdef bint argv_debug
cdef bint argv_profiling
cdef bint argv_loadstate

cdef class PyBoy:
    cdef unicode gamerom_file
    cdef Motherboard mb
    cdef BaseWindow window

    cdef double avg_emu
    cdef double avg_cpu
    cdef unsigned int counter
    cdef bint paused
    cdef bint autopause
    cdef bint limit_emulationspeed
    cdef int emulationspeed, target_emulationspeed
    cdef object screen_recorder
    cdef uint64_t frame_count
    cdef bint profiling
    cdef bint record_input
    cdef bint disable_input
    cdef unicode record_input_file
    cdef list recorded_input
    cdef list external_input
    cdef FixedAllocBuffers rewind_buffer
    cdef bint enable_rewind
    cdef float rewind_speed

    @cython.locals(done=cython.bint, event=int, t_start=float, t_cpu=float, t_emu=float, secs=float)
    cpdef bint tick(self)
    cpdef void stop(self, save=*, _replay_state_file=*)
    cdef void update_window_title(self)
