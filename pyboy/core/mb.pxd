#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from posix cimport dlfcn

from libc.stdint cimport int64_t, uint8_t, uint16_t, uint32_t, uint64_t

import cython

cimport pyboy.core.bootrom
cimport pyboy.core.cartridge.base_mbc
cimport pyboy.core.cpu
cimport pyboy.core.interaction
cimport pyboy.core.lcd
cimport pyboy.core.ram
cimport pyboy.core.sound
cimport pyboy.core.timer
# cimport pyboy.core.opcodes
from pyboy.logging.logging cimport Logger
from pyboy.utils cimport IntIOInterface, WindowEvent

from . cimport opcodes


cdef Logger logger

cdef int64_t MAX_CYCLES
cdef uint16_t STAT, LY, LYC
cdef short VBLANK, LCDC, TIMER, SERIAL, HIGHTOLOW
cdef int INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW
cdef int STATE_VERSION

ctypedef int(*f_type)(pyboy.core.cpu.CPU, int64_t) noexcept nogil

cdef class Motherboard:
    cdef pyboy.core.interaction.Interaction interaction
    cdef pyboy.core.bootrom.BootROM bootrom
    cdef pyboy.core.ram.RAM ram
    cdef pyboy.core.lcd.LCD lcd
    cdef pyboy.core.cpu.CPU cpu
    cdef pyboy.core.timer.Timer timer
    cdef pyboy.core.sound.Sound sound
    cdef pyboy.core.cartridge.base_mbc.BaseMBC cartridge
    cdef bint bootrom_enabled
    cdef char[1024] serialbuffer
    cdef uint16_t serialbuffer_count

    # CGB
    cdef HDMA hdma
    cdef uint8_t key1
    cdef bint double_speed
    cdef readonly bint cgb, cartridge_cgb

    cdef dict breakpoints
    cdef bint breakpoint_singlestep
    cdef bint breakpoint_singlestep_latch
    cdef int64_t breakpoint_waiting
    cdef int64_t breakpoint_add(self, int64_t, int64_t) except -1 with gil
    cdef int64_t breakpoint_remove(self, int64_t, int64_t) except -1 with gil
    cdef inline tuple[int64_t, int64_t, int64_t] breakpoint_reached(self) noexcept with gil
    cdef inline void breakpoint_reinject(self) noexcept nogil

    cdef f_type[0xFFFFFF] jit_array
    cdef int[0xFFFFFF] jit_cycles

    cdef inline int jit_load(self, str module_name, str module_path, str file_base, int block_id, int block_max_cycles) except -1 with gil:
        # logger.debug("JIT LOAD %d", block_id)
        cdef void* handle = dlfcn.dlopen(module_path.encode(), dlfcn.RTLD_NOW | dlfcn.RTLD_GLOBAL) # RTLD_LAZY?
        if (handle == NULL):
            return -1
        dlfcn.dlerror() # Clear error

        cdef f_type execute = <f_type> dlfcn.dlsym(handle, b"execute")
        if (execute == NULL):
            print(dlfcn.dlerror())

        self.jit_array[block_id] = execute
        self.jit_cycles[block_id] = block_max_cycles
        # execute(self.cpu)

    cdef inline int jit_execute(self, int block_id, int64_t cycles_target) noexcept nogil:
        # logger.debug("JIT EXECUTE %d", block_id)
        return self.jit_array[block_id](self.cpu, cycles_target)

    cdef bint jit_enabled
    cdef tuple jit_get_module_name(self, str) with gil
    cdef void jit_gen_files(self, str, str) noexcept with gil
    cdef void jit_compile(self, str, str, str) noexcept with gil
    cdef object jit_emit_code(self, object) with gil
    cdef bint jit_analyze(self, int, int64_t, bint) noexcept with gil
    @cython.locals(block_id=int64_t)
    cdef int64_t jit(self, int64_t) noexcept nogil
    cdef inline int cpu_pending_interrupt(self) noexcept nogil

    cdef void buttonevent(self, WindowEvent) noexcept
    cdef void stop(self, bint) noexcept
    @cython.locals(cycles=int64_t, cycles_target=int64_t, mode0_cycles=int64_t, breakpoint_index=int64_t)
    cdef bint tick(self) noexcept nogil

    cdef void switch_speed(self) noexcept nogil

    cdef uint8_t getitem(self, uint16_t) noexcept nogil
    cdef void setitem(self, uint16_t, uint8_t) noexcept nogil
    cdef uint8_t getitem_io_ports(self, uint16_t) noexcept nogil
    cdef void setitem_io_ports(self, uint16_t, uint8_t) noexcept nogil

    @cython.locals(offset=cython.int, dst=cython.int, n=cython.int)
    cdef void transfer_DMA(self, uint8_t) noexcept nogil
    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface) except -1

cdef class HDMA:
    cdef uint8_t hdma1
    cdef uint8_t hdma2
    cdef uint8_t hdma3
    cdef uint8_t hdma4
    cdef uint8_t hdma5
    cdef uint8_t _hdma5

    cdef bint transfer_active
    cdef uint16_t curr_src
    cdef uint16_t curr_dst

    cdef void set_hdma5(self, uint8_t, Motherboard) noexcept nogil
    cdef int64_t tick(self, Motherboard) noexcept nogil

    cdef int save_state(self, IntIOInterface) except -1
    cdef int load_state(self, IntIOInterface, int) except -1
