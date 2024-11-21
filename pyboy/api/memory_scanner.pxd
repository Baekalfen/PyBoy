from libc.stdint cimport uint64_t


cdef class MemoryScanner:
    cdef object pyboy
    cdef dict _memory_cache
    cdef int _memory_cache_byte_width

    cpdef list rescan_memory(self, object new_value=*, dynamic_comparison_type=*, byteorder=*)
    cpdef list scan_memory(self, object target_value=*, int start_addr=*, int end_addr=*, standard_comparison_type=*, value_type=*, int byte_width=*, byteorder=*)
    cpdef bint _check_value(self, uint64_t, uint64_t, int)noexcept
