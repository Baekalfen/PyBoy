#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from posix cimport dlfcn

cimport cython
from libc.stdint cimport int64_t, uint8_t, uint16_t, uint32_t, uint64_t

cimport pyboy
cimport pyboy.core.cartridge.base_mbc
cimport pyboy.core.cpu
from pyboy.logging.logging cimport Logger

from . cimport opcodes


cdef Logger logger
ctypedef int(*f_type)(pyboy.core.cpu.CPU, int64_t) noexcept nogil

cdef class JIT:
    cdef pyboy.core.cpu.CPU cpu
    cdef pyboy.core.cartridge.base_mbc.BaseMBC cartridge
    cdef dict queue
    cdef bint thread_stop
    cdef object thread_queue
    cdef object thread

    cdef f_type[0xFFFFFF] array
    cdef int[0xFFFFFF] cycles

    cdef inline int load(self, str module_name, str module_path, str file_base, list block_manifest) except -1 with gil:
        # logger.debug("JIT LOAD %d", block_id)
        cdef void* handle = dlfcn.dlopen(module_path.encode(), dlfcn.RTLD_NOW | dlfcn.RTLD_GLOBAL) # RTLD_LAZY?
        if (handle == NULL):
            return -1
        dlfcn.dlerror() # Clear error

        cdef f_type execute
        for func_name, block_id, block_max_cycles in block_manifest:
            execute = <f_type> dlfcn.dlsym(handle, func_name.encode())
            if (execute == NULL):
                print(dlfcn.dlerror())

            self.array[block_id] = execute
            self.cycles[block_id] = block_max_cycles

    cdef inline int execute(self, int block_id, int64_t cycles_target) noexcept nogil:
        # logger.debug("JIT EXECUTE %d", block_id)
        return self.array[block_id](self.cpu, cycles_target)

    cdef void stop(self) noexcept with gil

    cdef uint8_t getitem_bank(self, uint8_t, uint16_t) noexcept nogil

    cdef void _jit_clear(self) noexcept with gil
    cdef tuple get_module_name(self, str) with gil
    cdef void gen_files(self, str, str, list) noexcept with gil
    cdef void compile(self, str, str, str) noexcept with gil
    cdef object emit_code(self, object, str) with gil
    # @cython.locals(block_max_cycles=int64_t)
    # cdef bint analyze(self, int, int64_t, bint) noexcept with gil
    cdef void offload(self, int, int64_t, bint) noexcept with gil
    @cython.locals(block_id=int64_t, cycles_target=int64_t, interrupt_master_enable=bint, count=int64_t)
    cdef void process(self) noexcept with gil

cpdef void threaded_processor(JIT) noexcept with gil
