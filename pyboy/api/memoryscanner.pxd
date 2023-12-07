from libc.stdint cimport uint64_t


cdef class MemoryScanner:
    cdef object pyboy
    cdef dict _memory_cache
    cdef int _memory_cache_byte_width

    cpdef list rescan_memory(self, dynamic_comparison_type=*,uint64_t new_value=*)
    cpdef uint64_t read_memory(self, int, int byte_width=*, value_type=*, endian_type=*) noexcept
    cpdef list scan_memory(self, int, int, uint64_t, standard_comparison_type=*, value_type=*,int byte_width=*,endian_type=*) noexcept
    cpdef bint _check_value(self, uint64_t, uint64_t, int)noexcept
