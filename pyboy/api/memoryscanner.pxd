from libc.stdint cimport int64_t, uint8_t, uint16_t, uint32_t, uint64_t

cdef class MemoryScanner:
    cdef object pyboy

    cpdef uint64_t read_memory(self, int, int byte_width=*, value_type=*, endian_type=*) noexcept
    cpdef list scan_memory(self, int, int, uint64_t, compare_type=*, value_type=*,int byte_width=*,endian_type=*) noexcept
    cpdef bint _check_value(self, uint64_t, uint64_t, int)noexcept