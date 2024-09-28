#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import hashlib
import importlib
import os
import queue
import sysconfig
import threading
import time
from distutils.command.build_ext import build_ext
from distutils.core import Distribution, Extension
from importlib.machinery import ExtensionFileLoader

from Cython.Build import cythonize
from Cython.Compiler.Nodes import CFuncDefNode


# HACK: Disable this check to allow usage of CPU outside of GIL
def patched_validate_type_visibility(self, type, pos, env):
    pass


CFuncDefNode._validate_type_visibility = patched_validate_type_visibility

import pyboy
from pyboy import utils
from pyboy.core.opcodes_gen import opcodes as opcodes_gen

from . import opcodes

logger = pyboy.logging.get_logger(__name__)

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False

EXT_SUFFIX = sysconfig.get_config_var("EXT_SUFFIX")
JIT_EXTENSION = ".pyx" if cythonmode else ".py"

if not cythonmode:
    JIT_PREAMBLE = "FLAGC, FLAGH, FLAGN, FLAGZ = range(4, 8)\n\n"
else:
    JIT_PREAMBLE = """
from libc.stdint cimport uint8_t, uint16_t, int16_t, uint32_t, int64_t
from pyboy.core cimport cpu as _cpu

"""


def threaded_processor(jit):
    while not jit.thread_stop:
        while not jit.thread_queue.empty():
            message = jit.thread_queue.get()
            block_id, cycles_target, interrupt_master_enable = message

            if jit.queue.get(block_id) is None:
                jit.queue[block_id] = []
            jit.queue[block_id].append((cycles_target, interrupt_master_enable))
        logger.critical("PROCESSING!")
        jit.process()
        time.sleep(0.1)


class JIT:
    def __init__(self, cpu, cartridge):
        self.cpu = cpu
        self.cartridge = cartridge
        self._jit_clear()
        self.init_load()

        self.thread_queue = queue.Queue()
        self.thread = threading.Thread(target=threaded_processor, args=(self, ))
        self.thread_stop = False
        self.thread.start()

    def stop(self):
        self.thread_stop = True

    def _jit_clear(self):
        self.queue = {}
        for n in range(0xFFFFFF):
            self.cycles[n] = 0

    # TODO: Taken from https://github.com/cython/cython/blob/4e0eee43210d6b7822859f3001202910888644af/Cython/Build/Inline.py#L95
    def _get_build_extension(self):
        dist = Distribution()
        # Ensure the build respects distutils configuration by parsing
        # the configuration files
        config_files = dist.find_config_files()
        dist.parse_config_files(config_files)
        build_extension = build_ext(dist)
        build_extension.finalize_options()
        return build_extension

    def get_module_name(self, code_text):
        m = hashlib.sha1()
        m.update(code_text.encode())
        _hash = m.digest().hex()

        module_name = "jit_" + _hash
        module_path = module_name + EXT_SUFFIX #os.path.splitext(jit_file)[0] + '.so'

        # logger.debug("%s %s", self.cartridge.filename, _hash)
        file_base = os.path.splitext(self.cartridge.filename)[0].replace(".", "_") + "_jit_" + _hash # Generate name
        return module_name, file_base, module_path

    def gen_files(self, code_text, file_base, block_manifest):
        # https://github.com/cython/cython/blob/4e0eee43210d6b7822859f3001202910888644af/Cython/Build/Inline.py#L141

        if not os.path.exists(file_base + JIT_EXTENSION):
            # logger.info("Compiling JIT block: %s", module_path)
            with open(file_base + JIT_EXTENSION, "w") as f:
                f.write(code_text)

            if cythonmode:
                jit_file_pxd = file_base + ".pxd"
                with open(jit_file_pxd, "w") as f:
                    f.write("from pyboy.core cimport cpu as _cpu\nfrom libc.stdint cimport int64_t\n\n")
                    for func_name, _, _ in block_manifest:
                        f.write(f"cdef public int {func_name}(_cpu.CPU __cpu, int64_t cycles_target) noexcept nogil\n")

    def compile(self, module_name, file_base, module_path):
        cythonize_files = [
            Extension(
                module_name,
                [file_base + JIT_EXTENSION],
                extra_compile_args=["-O3", "-march=native", "-mtune=native"],
            )
        ]
        build_extension = self._get_build_extension()
        build_extension.extensions = cythonize(
            [*cythonize_files],
            nthreads=1,
            annotate=False,
            gdb_debug=True,
            language_level=3,
            compiler_directives={
                "boundscheck": False,
                "cdivision": True,
                "cdivision_warnings": False,
                "infer_types": True,
                "initializedcheck": False,
                "nonecheck": False,
                "overflowcheck": False,
                # "profile" : True,
                "wraparound": False,
                "legacy_implicit_noexcept": True,
            },
        )
        build_extension.inplace = True
        # build_extension.build_temp = "./"# os.path.dirname(jit_file)
        build_extension.run()

    def emit_code(self, code_block, func_name):
        # TODO: Detect loops
        # TODO: memory address (eliminate bail, know if it's a RAM or ROM write, interpolate specific memory pointer and bypass getitem)
        # TODO: Easy to detect high RAM LDH
        # TODO: Detect memcpy loop and replace. We don't need to LD A, (HL+) and then LD (DE), A. For each byte. This means to allow relative jumps within the block
        # TODO: Invalidate JIT block on breakpoint

        code_text = ""
        if not cythonmode:
            code_text += f"def {func_name}(cpu, cycles_target):\n\t"
            code_text += "flag = 0\n\tt = 0\n\ttr = 0\n\tv = 0"
        else:
            code_text += f"cdef public void {func_name}(_cpu.CPU cpu, int64_t cycles_target) noexcept nogil:"
            code_text += "\n\tcdef uint8_t flag\n\tcdef int t\n\tcdef int v"
            code_text += """
\tcdef uint16_t FLAGC = 4
\tcdef uint16_t FLAGH = 5
\tcdef uint16_t FLAGN = 6
\tcdef uint16_t FLAGZ = 7"""

        for i, (opcode, length, pc, literal1, literal2) in enumerate(code_block):
            opcode_handler = opcodes_gen[opcode]
            opcode_name = opcode_handler.name.split()[0]
            code_text += "\n\t\n\t" + "# " + opcode_handler.name + f" (PC: 0x{pc:04x})\n\t"
            if length == 2:
                v = literal1
                code_text += f"v = 0x{v:02x} # {v}\n\t"
            elif length == 3:
                v = (literal2 << 8) + literal1
                code_text += f"v = 0x{v:04x} # {v}\n\t"

            tmp_code = opcode_handler.functionhandlers[opcode_name]()._code_body()
            if "if" in tmp_code:
                # Return early on jump
                tmp_code = tmp_code.replace("else:", "\treturn\n\telse:")
            elif "cpu.mb.setitem" in tmp_code:
                # Return early on state-altering writes
                tmp_code += "\n\tif cpu.bail: return"
            code_text += tmp_code

        code_text += "\n\treturn\n\n"
        # opcodes[7].functionhandlers[opcodes[7].name.split()[0]]().branch_op
        # if .getitem in code, commit timer.tick(cycles); cycles = 0
        return code_text

    def getitem_bank(self, bank, i):
        if 0x0000 <= i < 0x4000: # 16kB ROM bank #0
            return self.cartridge.rombanks[0, i] # TODO: Actually self.cartridge.rombank_selected_low
        elif 0x4000 <= i < 0x8000: # 16kB switchable ROM bank
            return self.cartridge.rombanks[bank, i - 0x4000]

    def collect_block(self, block_id, cycles_target):
        boundary_instruction = [
            0x18, # JR r8

            # RET
            0xC0,
            0xD0,
            0xC3, # JP a16

            # RST
            0xC7,
            0xD7,
            0xE7,
            0xF7,
            0xC9, # RET
            0xD9, # RETI
            0xE9, # JP (HL)
            0xCD, # CALL a16

            # RST
            0xCF,
            0xDF,
            0xEF,
            0xFF,
            0x76, # HALT
            0x10, # STOP
            0xFB, # EI
            0xDB, # Breakpoint/hook
        ]
        code_block = []
        pc = block_id >> 8
        assert pc < 0x8000
        rom_bank = block_id & 0xFF

        block_max_cycles = 0
        while True:
            # for _ in range(200):
            # while block_max_cycles < 200:
            opcode = self.getitem_bank(rom_bank, pc)
            if opcode == 0xCB: # Extension code
                pc += 1
                opcode = self.getitem_bank(rom_bank, pc)
                opcode += 0x100 # Internally shifting look-up table
            opcode_length = opcodes.OPCODE_LENGTHS[opcode]
            opcode_max_cycles = opcodes.OPCODE_MAX_CYCLES[opcode]
            # if (not interrupt_master_enable) and (block_max_cycles + opcode_max_cycles > cycles_target):
            if (block_max_cycles + opcode_max_cycles > cycles_target):
                break
            block_max_cycles += opcode_max_cycles
            code_block.append(
                (opcode, opcode_length, pc, self.getitem_bank(rom_bank, pc + 1), self.getitem_bank(rom_bank, pc + 2))
            )
            pc += opcode_length
            if opcode in boundary_instruction:
                break

        return code_block, block_max_cycles

    def invalidate(self, bank, address):
        # Invalidate any JIT block that crosses this bank and adress.
        # Used when adding breakpoints and hooks
        pass

    def offload(self, block_id, cycles_target, interrupt_master_enable):
        if cycles_target < 200:
            return

        self.thread_queue.put((block_id, cycles_target, interrupt_master_enable))

    def init_load(self):
        # breakpoint()
        logger.critical("initload")
        for module_path in os.listdir():
            # logger.critical("file: %s", module_path)
            if module_path.startswith("jit_") and module_path.endswith(EXT_SUFFIX):
                # logger.critical("match")
                module_name = module_path.split(".")[0]
                file_base = os.path.splitext(self.cartridge.filename)[0].replace(".", "_") + "_" + module_name

                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if getattr(module, "cartridge") == self.cartridge.gamename:
                    block_manifest = getattr(module, "block_manifest")
                    no_blocks = len(block_manifest)
                    logger.critical("Loading %d precompiled blocks from %s", no_blocks, file_base)
                    self.load(module_name, module_path, file_base, block_manifest)
                del spec, module

    def process(self):
        # TODO: Send cycles_target and which interrupt to jit_analyze. Track interrupt enable and flags on JIT block?
        # Interrupts are likely to hit the same rythm -- sync on halt, do hblank, do vblank, etc.
        # JIT interrupt routines and just straight to them?
        # Predict which interrupt and inline interrupt vector?

        priority_list = []
        for k, v in self.queue.items():
            priority_list.append((k, len(v))) # block_id, number of hits

        block_manifest = []
        code_text = JIT_PREAMBLE
        # Pick the 10 most frequent

        no_blocks = 0
        for block_id, count in sorted(priority_list, key=lambda x: x[1], reverse=True):
            # if no_blocks >= 500:
            #     break
            # TODO: Currently just picking the first entry!
            cycles_target, interrupt_master_enable = self.queue[block_id][0]

            # logger.critical("analyze: %x, %d, %d", block_id, cycles_target, interrupt_master_enable)

            code_block, block_max_cycles = self.collect_block(block_id, cycles_target)

            if block_max_cycles < 100:
                self.cycles[block_id] = -1 # Don't retry
                continue

            no_blocks += 1

            # if len(code_block) < 25:
            #     continue

            func_name = f"block_{block_id:08x}"

            # logger.debug("Code block size: %d, block cycles: %d", len(code_block), block_max_cycles)
            code_text += self.emit_code(code_block, func_name)

            block_manifest.append((func_name, block_id, block_max_cycles))

        if no_blocks < 20:
            temp_queue = {}
            for _, block_id, _ in block_manifest:
                temp_queue[block_id] = self.queue[block_id]
            self.queue = temp_queue # Clear all unwanted blocks and wait for more blocks to come in
            return
        else:
            self.queue = {} # Throw the rest away to not grow the list indefinitely. Maybe there's a better way.

        logger.critical("processing: %d blocks", no_blocks)

        code_text = "block_manifest = " + str(
            block_manifest
        ) + "\n" + f"cartridge = '{self.cartridge.gamename}'\n\n" + code_text

        module_name, file_base, module_path = self.get_module_name(code_text)
        self.gen_files(code_text, file_base, block_manifest)
        if cythonmode:
            self.compile(module_name, file_base, module_path)
        # logger.debug("Loading: %s %x %d", file_base, block_id, block_max_cycles)
        self.load(module_name, module_path, file_base, block_manifest)


# Unfortunately CPython/PyPy code has to be hidden in an exec call to
# prevent Cython from trying to parse it. This block provides the
# functions that are otherwise implemented as inlined cdefs in the pxd
if not cythonmode:
    exec(
        """
def _load(self, module_name, module_path, file_base, block_manifest):
    # spec = importlib.util.spec_from_file_location(module_name, loader=ExtensionFileLoader(module_name, file_base + JIT_EXTENSION))
    spec = importlib.util.spec_from_file_location(module_name, file_base + JIT_EXTENSION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for func_name, block_id, block_max_cycles in block_manifest:
        self.array[block_id] = getattr(module, func_name)
        self.cycles[block_id] = block_max_cycles

def _jit_clear(self):
    self.queue = {}
    self.cycles = [0] * 0xFFFFFF
    self.array = [None] * 0xFFFFFF

def _execute(self, block_id, cycles_target):
    return self.array[block_id](self.cpu, cycles_target)

JIT.load = _load
JIT._jit_clear = _jit_clear
JIT.execute = _execute
""", globals(), locals()
    )
