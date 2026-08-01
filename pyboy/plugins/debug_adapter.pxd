#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.logging.logging cimport Logger
from pyboy.plugins.base_plugin cimport PyBoyPlugin

cdef Logger logger

cdef class DebugAdapter(PyBoyPlugin):
    cdef object reader
    cdef object writer
    cdef object _seq
    cdef object _seq_lock
    cdef object _breakpoint_refs
    cdef object _instruction_breakpoint_refs
    cdef object _source_breakpoint_refs
    cdef object _stop_on_entry
    cdef object _source_map
    cdef object _resume
    cdef object _pending_action
    cdef object _hooks
    cdef object _hook_original_bytes
    cdef object _stopped_lock
    cdef object is_stopped
    cdef object _configured
    cdef object _entry_paused
    cdef object _protocol_thread
