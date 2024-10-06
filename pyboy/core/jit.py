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

# NOTE: print('\n'.join([f"0x{i:02X}, # {x}" for i,x in enumerate(pyboy.core.opcodes.CPU_COMMANDS) if "JR" in x]))
jr_instruction = [
    0x18, # JR r8
    0x20, # JR NZ,r8
    0x28, # JR Z,r8
    0x30, # JR NC,r8
    0x38, # JR C,r8
]
jp_instruction = [
    0xC2, # JP NZ,a16
    0xC3, # JP a16
    0xCA, # JP Z,a16
    0xD2, # JP NC,a16
    0xDA, # JP C,a16
]
boundary_instruction = [
    0xC7, # RST 00H
    0xCF, # RST 08H
    0xD7, # RST 10H
    0xDF, # RST 18H
    0xE7, # RST 20H
    0xEF, # RST 28H
    0xF7, # RST 30H
    0xFF, # RST 38H
    0xC4, # CALL NZ,a16
    0xCC, # CALL Z,a16
    0xCD, # CALL a16
    0xD4, # CALL NC,a16
    0xDC, # CALL C,a16
    0xC0, # RET NZ
    0xC8, # RET Z
    0xC9, # RET
    0xD0, # RET NC
    0xD8, # RET C
    0xD9, # RETI
    0xE9, # JP (HL)
    0x76, # HALT
    0x10, # STOP
    0xFB, # EI
    0xDB, # Breakpoint/hook
]


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
            code_text += "flag = 0\n\tt = 0\n\tv = 0\n\t_cycles0 = cpu.cycles\n\t_target = _cycles0 + cycles_target"
        else:
            code_text += f"cdef public void {func_name}(_cpu.CPU cpu, int64_t cycles_target) noexcept nogil:"
            code_text += "\n\tcdef uint8_t flag\n\tcdef int t\n\tcdef int v\n\tcdef int64_t _cycles0 = cpu.cycles\n\tcdef int64_t _target = _cycles0 + cycles_target"
            code_text += """
\tcdef uint16_t FLAGC = 4
\tcdef uint16_t FLAGH = 5
\tcdef uint16_t FLAGN = 6
\tcdef uint16_t FLAGZ = 7"""

        def emit_opcode(indent, opcode, length, pc, literal1, literal2):
            opcode_handler = opcodes_gen[opcode]
            opcode_name = opcode_handler.name.split()[0]
            preamble = f"\n\t\n\t" + "# " + opcode_handler.name + f" (PC: 0x{pc:04x})\n\t"
            if length == 2:
                v = literal1
                preamble += f"v = 0x{v:02x} # {v}\n\t"
            elif length == 3:
                v = (literal2 << 8) + literal1
                preamble += f"v = 0x{v:04x} # {v}\n\t"

            tmp_code = opcode_handler.functionhandlers[opcode_name]()._code_body()
            if "if" in tmp_code:
                # Return early on jump
                tmp_code = tmp_code.replace("else:", f"\treturn\n\telse:")
            elif "cpu.mb.setitem" in tmp_code:
                # Return early on state-altering writes
                tmp_code += f"\n\tif cpu.bail: return"
            return (preamble + tmp_code).replace("\t", indent)

        for i, (opcode, length, pc, literal1, literal2) in enumerate(code_block):
            if opcode < 0x200: # Regular opcode
                code_text += emit_opcode("\t", opcode, length, pc, literal1, literal2)
            elif opcode == 0x200: # Loop body
                loop_body_cycles, jump_to, jump_from, _block = length, pc, literal1, literal2
                # breakpoint()
                code_text += f"\n\n\twhile True: # Loop body (PC: 0x{jump_to:04X} to 0x{jump_from:04X})"
                for i, (opcode, length, pc, literal1, literal2) in enumerate(_block[:-1]):
                    code_text += emit_opcode("\t\t", opcode, length, pc, literal1, literal2)

                # Loop condition
                opcode, length, pc, literal1, literal2 = _block[-1]
                loop_condition = emit_opcode("\t\t", opcode, length, pc, literal1, literal2)
                loop_condition = loop_condition.replace(
                    "return",
                    f'if cpu.cycles + {loop_body_cycles} < _target:\n\t\t\t\t\tcpu.jit_jump=False;continue\n\t\t\t\telse:\n\t\t\t\t\tcpu.jit_jump=False;return'
                )
                loop_condition += "\n\t\tbreak"
                code_text += loop_condition
            elif opcode == 0x201: # Remainder of block
                remainder_cycles = length
                code_text += f'\n\tif cpu.cycles + {remainder_cycles} < _target: return'

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
        code_block = []
        PC = block_id >> 8
        _PC = PC
        assert PC < 0x8000
        rom_bank = block_id & 0xFF

        has_internal_jump = False
        block_max_cycles = 0
        while True:
            # for _ in range(200):
            # while block_max_cycles < 200:
            opcode = self.getitem_bank(rom_bank, PC)
            if opcode == 0xCB: # Extension code
                PC += 1
                opcode = self.getitem_bank(rom_bank, PC)
                opcode += 0x100 # Internally shifting look-up table
            opcode_length = opcodes.OPCODE_LENGTHS[opcode]
            opcode_max_cycles = opcodes.OPCODE_MAX_CYCLES[opcode]
            # if (not interrupt_master_enable) and (block_max_cycles + opcode_max_cycles > cycles_target):
            if (block_max_cycles + opcode_max_cycles > cycles_target):
                break
            block_max_cycles += opcode_max_cycles
            l1, l2 = self.getitem_bank(rom_bank, PC + 1), self.getitem_bank(rom_bank, PC + 2)
            code_block.append((opcode, opcode_length, PC, l1, l2))
            PC += opcode_length

            is_jr = opcode in jr_instruction
            is_jp = opcode in jp_instruction

            if opcode in boundary_instruction:
                break
            elif is_jr or is_jp:
                # We assume it's the ending instruction? Or is the validation at the top?
                if not has_internal_jump:
                    if is_jr:
                        jump_to = PC + ((l1 ^ 0x80) - 0x80)
                    else:
                        jump_to = ((l2 << 8) | l1)

                    if _PC <= jump_to < PC: # Detect internal jump
                        has_internal_jump = True
                    else:
                        # The jump is to somewhere else
                        break
                else:
                    # Expected jump away
                    # TODO: Just one loop?
                    break

        return code_block, block_max_cycles, has_internal_jump

    def print_block(self, code_block):
        def opcode_translate(opcode):
            if opcode == 0x200:
                return "loop block"
            else:
                return pyboy.core.opcodes.CPU_COMMANDS[opcode]

        print(
            "\n".join(
                f"0x{opcode:02X} {opcode_translate(opcode)}\tlen: {opcode_length}\tPC: {pc:04X}\tlit1: {l1:02X}\tlit2: {l2:02X}\tlit: {(l2<<8) | l1:04X}\t r8: {pc + ((l1 ^ 0x80) - 0x80):04X}"
                for opcode, opcode_length, pc, l1, l2 in code_block
            )
        )

    def check_no_overlap(self, ranges):
        if len(ranges) == 1:
            return True

        # Sort the ranges by the starting points
        ranges.sort(key=lambda x: x[0])

        # Traverse through the ranges to check for overlap
        for i in range(1, len(ranges)):
            # If the start of the current range is less than the end of the previous range, there's an overlap
            if ranges[i][0] < ranges[i - 1][1]:
                return False

        return True

    def optimize_block(self, raw_code_block, raw_block_max_cycles, has_internal_jump):
        if not has_internal_jump:
            return raw_code_block

        # _, _, PC, _, _ = raw_code_block[0]
        jumps = []
        for opcode, opcode_length, PC, l1, l2 in raw_code_block:
            is_jr = opcode in jr_instruction
            is_jp = opcode in jp_instruction
            if is_jp or is_jr:
                if is_jr:
                    jump_to = PC + ((l1 ^ 0x80) - 0x80)
                elif is_jp:
                    jump_to = ((l2 << 8) | l1)

                jumps.append((jump_to, PC)) # Sorted as (start, end)

        if not self.check_no_overlap(jumps):
            return raw_code_block

        new_block = []
        _block = []
        current_jump = jumps.pop()
        for i, (opcode, opcode_length, pc, l1, l2) in enumerate(raw_code_block):
            if current_jump and current_jump[0] <= pc < current_jump[1]:
                # Collect body
                _block.append((opcode, opcode_length, pc, l1, l2))
            elif current_jump and pc == current_jump[1]:
                # Add loop block
                _block.append((opcode, opcode_length, pc, l1, l2))
                loop_body_cycles = sum(opcodes.OPCODE_MAX_CYCLES[opcode] for opcode, _, _, _, _, in _block)
                new_block.append((0x200, loop_body_cycles, current_jump[0], current_jump[1], _block))
                _block = []
                current_jump = jumps.pop() if jumps else None

                remainder_cycles = sum(opcodes.OPCODE_MAX_CYCLES[opcode] for opcode, _, _, _, _, in raw_code_block[i:])
                new_block.append((0x201, remainder_cycles, None, None, None))
            else:
                # Add regular opcode
                new_block.append((opcode, opcode_length, pc, l1, l2))
        return new_block

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

            raw_code_block, block_max_cycles, has_internal_jump = self.collect_block(block_id, cycles_target)
            code_block = self.optimize_block(raw_code_block, block_max_cycles, has_internal_jump)

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
