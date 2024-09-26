#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import array
import hashlib
import heapq
import importlib
import os
import sysconfig
from distutils.command.build_ext import build_ext
from distutils.core import Distribution, Extension
from importlib.machinery import ExtensionFileLoader

from Cython.Build import cythonize
from Cython.Compiler.Nodes import CFuncDefNode


# HACK: Disable this check to allow usage of CPU outside of GIL
def patched_validate_type_visibility(self, type, pos, env):
    pass


CFuncDefNode._validate_type_visibility = patched_validate_type_visibility

from pyboy import utils
from pyboy.core.opcodes_gen import opcodes as opcodes_gen
from pyboy.utils import STATE_VERSION

from . import bootrom, cartridge, cpu, interaction, lcd, opcodes, ram, sound, timer

INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW = [1 << x for x in range(5)]
OPCODE_BRK = 0xDB

import pyboy

logger = pyboy.logging.get_logger(__name__)

MAX_CYCLES = 1 << 16

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False

EXT_SUFFIX = sysconfig.get_config_var("EXT_SUFFIX")
JIT_EXTENSION = ".pyx" if cythonmode else ".py"
JIT_PREAMBLE = """
cimport pyboy

from libc.stdint cimport uint8_t, uint16_t, int16_t, uint32_t, int64_t
cimport cython
from pyboy.core cimport cpu as _cpu

"""


class Motherboard:
    def __init__(
        self,
        gamerom,
        bootrom_file,
        color_palette,
        cgb_color_palette,
        sound_enabled,
        sound_emulated,
        cgb,
        jit_enabled,
        randomize=False,
    ):
        if bootrom_file is not None:
            logger.info("Boot-ROM file provided")

        self.cartridge = cartridge.load_cartridge(gamerom)
        logger.debug("Cartridge started:\n%s", str(self.cartridge))
        if cgb is None:
            cgb = self.cartridge.cgb
            logger.debug("Cartridge type auto-detected to %s", ("CGB" if cgb else "DMG"))

        self.timer = timer.Timer()
        self.interaction = interaction.Interaction()
        self.bootrom = bootrom.BootROM(bootrom_file, cgb)
        self.ram = ram.RAM(cgb, randomize=randomize)
        self.cpu = cpu.CPU(self)

        if cgb:
            self.lcd = lcd.CGBLCD(
                cgb,
                self.cartridge.cgb,
                color_palette,
                cgb_color_palette,
                randomize=randomize,
            )
        else:
            self.lcd = lcd.LCD(
                cgb,
                self.cartridge.cgb,
                color_palette,
                cgb_color_palette,
                randomize=randomize,
            )

        # QUIRK: Force emulation of sound (muted)
        sound_emulated |= self.cartridge.gamename == "ZELDA DIN"
        self.sound = sound.Sound(sound_enabled, sound_emulated)

        self.key1 = 0
        self.double_speed = False
        self.cgb = cgb
        self.cartridge_cgb = self.cartridge.cgb

        if self.cgb:
            self.hdma = HDMA()

        self.bootrom_enabled = True
        self.serialbuffer = [0] * 1024
        self.serialbuffer_count = 0

        self.breakpoints = {} #{(0, 0x150): (0x100) (0, 0x0040): 0x200, (0, 0x0048): 0x300, (0, 0x0050): 0x44}
        self.breakpoint_singlestep = False
        self.breakpoint_singlestep_latch = False
        self.breakpoint_waiting = -1

        self.jit_enabled = jit_enabled
        self._jit_clear()

    def _jit_clear(self):
        self.jit_queue = {}
        for n in range(0xFFFFFF):
            self.jit_cycles[n] = 0

    def switch_speed(self):
        bit0 = self.key1 & 0b1
        if bit0 == 1:
            self.double_speed = not self.double_speed
            self.lcd.double_speed = self.double_speed
            self.key1 ^= 0b10000001

    def breakpoint_add(self, bank, addr):
        # Replace instruction at address with OPCODE_BRK and save original opcode
        # for later reinsertion and when breakpoint is deleted.
        if addr < 0x100 and bank == -1:
            opcode = self.bootrom.bootrom[addr]
            self.bootrom.bootrom[addr] = OPCODE_BRK
        elif addr < 0x4000:
            if self.cartridge.external_rom_count < bank:
                raise Exception(f"ROM bank out of bounds. Asked for {bank}, max is {self.cartridge.external_rom_count}")
            opcode = self.cartridge.rombanks[bank, addr]
            self.cartridge.rombanks[bank, addr] = OPCODE_BRK
        elif 0x4000 <= addr < 0x8000:
            if self.cartridge.external_rom_count < bank:
                raise Exception(f"ROM bank out of bounds. Asked for {bank}, max is {self.cartridge.external_rom_count}")
            opcode = self.cartridge.rombanks[bank, addr - 0x4000]
            self.cartridge.rombanks[bank, addr - 0x4000] = OPCODE_BRK
        elif 0x8000 <= addr < 0xA000:
            if bank == 0:
                opcode = self.lcd.VRAM0[addr - 0x8000]
                self.lcd.VRAM0[addr - 0x8000] = OPCODE_BRK
            else:
                opcode = self.lcd.VRAM1[addr - 0x8000]
                self.lcd.VRAM1[addr - 0x8000] = OPCODE_BRK
        elif 0xA000 <= addr < 0xC000:
            if self.cartridge.external_ram_count < bank:
                raise Exception(f"RAM bank out of bounds. Asked for {bank}, max is {self.cartridge.external_ram_count}")
            opcode = self.cartridge.rambanks[bank, addr - 0xA000]
            self.cartridge.rambanks[bank, addr - 0xA000] = OPCODE_BRK
        elif 0xC000 <= addr <= 0xE000:
            opcode = self.ram.internal_ram0[addr - 0xC000]
            self.ram.internal_ram0[addr - 0xC000] = OPCODE_BRK
        else:
            raise Exception("Unsupported breakpoint address. If this a mistake, reach out to the developers")

        self.breakpoints[(bank, addr)] = opcode

    def breakpoint_find(self, bank, addr):
        opcode = self.breakpoints.get((bank, addr))
        if opcode is not None:
            return (bank, addr, opcode)
        return tuple()

    def breakpoint_remove(self, bank, addr):
        logger.debug(f"Breakpoint remove: ({bank}, {addr})")
        opcode = self.breakpoints.pop((bank, addr), None)
        if opcode is not None:
            logger.debug(f"Breakpoint remove: {bank:02x}:{addr:04x} {opcode:02x}")

            # Restore opcode
            if addr < 0x100 and bank == -1:
                self.bootrom.bootrom[addr] = opcode
            elif addr < 0x4000:
                self.cartridge.rombanks[bank, addr] = opcode
            elif 0x4000 <= addr < 0x8000:
                self.cartridge.rombanks[bank, addr - 0x4000] = opcode
            elif 0x8000 <= addr < 0xA000:
                if bank == 0:
                    self.lcd.VRAM0[addr - 0x8000] = opcode
                else:
                    self.lcd.VRAM1[addr - 0x8000] = opcode
            elif 0xA000 <= addr < 0xC000:
                self.cartridge.rambanks[bank, addr - 0xA000] = opcode
            elif 0xC000 <= addr <= 0xE000:
                self.ram.internal_ram0[addr - 0xC000] = opcode
            else:
                logger.error("Unsupported breakpoint address. If this a mistake, reach out to the developers")
        else:
            logger.error("Breakpoint not found. If this a mistake, reach out to the developers")

    def breakpoint_reached(self):
        pc = self.cpu.PC
        bank = None
        if pc < 0x100 and self.bootrom_enabled:
            bank = -1
        elif pc < 0x4000:
            bank = 0
        elif 0x4000 <= pc < 0x8000:
            bank = self.cartridge.rombank_selected
        elif 0xA000 <= pc < 0xC000:
            bank = self.cartridge.rambank_selected
        elif 0xC000 <= pc <= 0xFFFF:
            bank = 0
        opcode = self.breakpoints.get((bank, pc))
        if opcode is not None:
            # Breakpoint hit
            addr = pc
            logger.debug("Breakpoint reached: %02x:%04x %02x", bank, addr, opcode)
            self.breakpoint_waiting = (bank & 0xFF) << 24 | (addr & 0xFFFF) << 8 | (opcode & 0xFF)
            logger.debug("Breakpoint waiting: %08x", self.breakpoint_waiting)
            return (bank, addr, opcode)
        logger.debug("Invalid breakpoint reached: %04x", self.cpu.PC)
        return (-1, -1, -1)

    def breakpoint_reinject(self):
        if self.breakpoint_waiting < 0:
            return # skip
        bank = (self.breakpoint_waiting >> 24) & 0xFF
        # TODO: Improve signedness
        if bank == 0xFF:
            bank = -1
        addr = (self.breakpoint_waiting >> 8) & 0xFFFF
        logger.debug("Breakpoint reinjecting: %02x:%02x", bank, addr)
        self.breakpoint_add(bank, addr)
        self.breakpoint_waiting = -1

    def getserial(self):
        b = "".join([chr(x) for x in self.serialbuffer[:self.serialbuffer_count]])
        self.serialbuffer_count = 0
        return b

    def buttonevent(self, key):
        if self.interaction.key_event(key):
            self.cpu.set_interruptflag(INTR_HIGHTOLOW)

    def stop(self, save):
        self.sound.stop()
        if save:
            self.cartridge.stop()

    def save_state(self, f):
        logger.debug("Saving state...")
        f.write(STATE_VERSION)
        f.write(self.bootrom_enabled)
        f.write(self.key1)
        f.write(self.double_speed)
        f.write(self.cgb)
        if self.cgb:
            self.hdma.save_state(f)
        self.cpu.save_state(f)
        self.lcd.save_state(f)
        self.sound.save_state(f)
        self.lcd.renderer.save_state(f)
        self.ram.save_state(f)
        self.timer.save_state(f)
        self.cartridge.save_state(f)
        self.interaction.save_state(f)
        f.flush()
        logger.debug("State saved.")

    def load_state(self, f):
        logger.debug("Loading state...")
        state_version = f.read()
        if state_version >= 2:
            logger.debug("State version: %d", state_version)
            # From version 2 and above, this is the version number
            self.bootrom_enabled = f.read()
        else:
            logger.debug("State version: 0-1")
            # HACK: The byte wasn't a state version, but the bootrom flag
            self.bootrom_enabled = state_version
        if state_version >= 8:
            self.key1 = f.read()
            self.double_speed = f.read()
            _cgb = f.read()
            if self.cgb != _cgb:
                raise Exception("Loading state which is not CGB, but PyBoy is loaded in CGB mode!")
            self.cgb = _cgb
            if self.cgb:
                self.hdma.load_state(f, state_version)
        self.cpu.load_state(f, state_version)
        self.lcd.load_state(f, state_version)
        if state_version >= 8:
            self.sound.load_state(f, state_version)
        self.lcd.renderer.load_state(f, state_version)
        self.lcd.renderer.clear_cache()
        self.ram.load_state(f, state_version)
        if state_version < 5:
            # Interrupt register moved from RAM to CPU
            self.cpu.interrupts_enabled_register = f.read()
        if state_version >= 5:
            self.timer.load_state(f, state_version)
        self.cartridge.load_state(f, state_version)
        self.interaction.load_state(f, state_version)
        f.flush()
        logger.debug("State loaded.")

    ###################################################################
    # Coordinator
    #

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

    def jit_get_module_name(self, code_text):
        m = hashlib.sha1()
        m.update(code_text.encode())
        _hash = m.digest().hex()

        module_name = "jit_" + _hash
        module_path = module_name + EXT_SUFFIX #os.path.splitext(jit_file)[0] + '.so'

        # logger.debug("%s %s", self.cartridge.filename, _hash)
        file_base = os.path.splitext(self.cartridge.filename)[0].replace(".", "_") + "_jit_" + _hash # Generate name
        return module_name, file_base, module_path

    def jit_gen_files(self, code_text, file_base):
        # https://github.com/cython/cython/blob/4e0eee43210d6b7822859f3001202910888644af/Cython/Build/Inline.py#L141

        if not os.path.exists(file_base + JIT_EXTENSION):
            # logger.info("Compiling JIT block: %s", module_path)
            with open(file_base + JIT_EXTENSION, "w") as f:
                f.write(code_text)

            if cythonmode:
                jit_file_pxd = file_base + ".pxd"
                with open(jit_file_pxd, "w") as f:
                    f.write("from pyboy.core cimport cpu as _cpu\n")
                    f.write("cdef public int execute(_cpu.CPU __cpu, int64_t cycles_target) noexcept nogil")

    def jit_compile(self, module_name, file_base, module_path):
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
        # else:
        #     logger.info("JIT block already compiled: %s", module_path)

    def jit_emit_code(self, code_block):
        code_text = ""
        if not cythonmode:
            code_text += "FLAGC, FLAGH, FLAGN, FLAGZ = range(4, 8)\n\n"
            code_text += "def execute(cpu, cycles_target):\n\t"
            code_text += "flag = 0\n\tt = 0\n\ttr = 0\n\tv = 0"
        else:
            code_text += JIT_PREAMBLE
            code_text += "cdef public void execute(_cpu.CPU cpu, int64_t cycles_target) noexcept nogil:"
            code_text += "\n\tcdef uint8_t flag\n\tcdef int t\n\tcdef uint16_t tr\n\tcdef int v"
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

        code_text += "\n\treturn"
        # opcodes[7].functionhandlers[opcodes[7].name.split()[0]]().branch_op
        # if .getitem in code, commit timer.tick(cycles); cycles = 0
        return code_text

    def getitem_bank(self, bank, i):
        if 0x0000 <= i < 0x4000: # 16kB ROM bank #0
            if bank == 0xFF and (i <= 0xFF or (self.cgb and 0x200 <= i < 0x900)):
                return self.bootrom.getitem(i)
            else:
                return self.cartridge.rombanks[0, i] # TODO: Actually self.cartridge.rombank_selected_low
        elif 0x4000 <= i < 0x8000: # 16kB switchable ROM bank
            return self.cartridge.rombanks[bank, i - 0x4000]

    def jit_analyze(self, block_id, cycles_target, interrupt_master_enable):
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

        if block_max_cycles < 100:
            return False
        # if len(code_block) < 25:
        #     return False

        logger.debug("Code block size: %d, block cycles: %d", len(code_block), block_max_cycles)

        code_text = self.jit_emit_code(code_block)
        module_name, file_base, module_path = self.jit_get_module_name(code_text)
        self.jit_gen_files(code_text, file_base)
        if cythonmode:
            self.jit_compile(module_name, file_base, module_path)
        logger.debug("Loading: %s %x %d", file_base, block_id, block_max_cycles)
        self.jit_load(module_name, module_path, file_base, block_id, block_max_cycles)

        return True

    def jit_offload(self, block_id, cycles_target, interrupt_master_enable):
        if cycles_target < 200:
            return

        if self.jit_queue.get(block_id) is None:
            self.jit_queue[block_id] = []
        self.jit_queue[block_id].append((cycles_target, interrupt_master_enable))

    def jit_process(self):
        # TODO: Send cycles_target and which interrupt to jit_analyze. Track interrupt enable and flags on JIT block?
        # Interrupts are likely to hit the same rythm -- sync on halt, do hblank, do vblank, etc.
        # JIT interrupt routines and just straight to them?
        # Predict which interrupt and inline interrupt vector?

        priority_list = []
        for k, v in self.jit_queue.items():
            priority_list.append((k, len(v))) # block_id, number of hits

        # Pick the 10 most frequent
        for block_id, count in sorted(priority_list, key=lambda x: x[1], reverse=True)[:10]:
            cycles_target, interrupt_master_enable = self.jit_queue[block_id][
                0] # TODO: Currently just picking the first entry!
            logger.critical("analyze: %x, %d, %d", block_id, cycles_target, interrupt_master_enable)
            if not self.jit_analyze(block_id, cycles_target, interrupt_master_enable):
                self.jit_cycles[block_id] = -1 # Don't retry

        self.jit_queue = {} # Throw the rest away to not grow the list indefinitely. Maybe there's a better way.

    def processing_frame(self):
        b = (not self.lcd.frame_done)
        self.lcd.frame_done = False # Clear vblank flag for next iteration
        return b

    def cpu_pending_interrupt(self):
        return self.cpu.interrupt_queued or (self.cpu.interrupts_flag_register &
                                             0b11111) & (self.cpu.interrupts_enabled_register & 0b11111)

    def tick(self):
        while self.processing_frame():
            if self.cgb and self.hdma.transfer_active and self.lcd._STAT._mode & 0b11 == 0:
                self.cpu.jit_jump = False
                self.cpu.cycles = self.cpu.cycles + self.hdma.tick(self)
            else:
                # Fast-forward to next interrupt:
                # As we are halted, we are guaranteed, that our state
                # cannot be altered by other factors than time.
                # For HiToLo interrupt it is indistinguishable whether
                # it gets triggered mid-frame or by next frame
                # Serial is not implemented, so this isn't a concern

                mode0_cycles = MAX_CYCLES
                if self.cgb and self.hdma.transfer_active:
                    mode0_cycles = self.lcd.cycles_to_mode0()

                cycles_target = max(
                    4,
                    min(
                        self.timer._cycles_to_interrupt,
                        self.lcd._cycles_to_interrupt, # TODO: Be more agreesive. Only if actual interrupt enabled.
                        self.lcd._cycles_to_frame,
                        self.sound._cycles_to_interrupt, # TODO: Not implemented
                        # self.serial.cycles_to_interrupt(),
                        mode0_cycles
                    )
                )

                # Inject special opcode instead? ~~Long immediate as identifier~~
                # Special opcode cannot be more than 1 byte, to avoid jumps to sub-parts of the jit block
                # Compile in other thread, acquire memory lock between frames
                if self.jit_enabled and self.cpu.PC < 0x8000 and not self.bootrom_enabled:
                    block_id = (self.cpu.PC << 8)
                    block_id |= self.cartridge.rombank_selected

                    block_max_cycles = self.jit.cycles[block_id]

                    # Hot path
                    if 0 < block_max_cycles and not self.cpu_pending_interrupt():
                        self.jit.execute(block_id, cycles_target)
                    else:
                        if self.cpu.jit_jump and block_max_cycles == 0:
                            self.jit.offload(block_id, cycles_target, self.cpu.interrupt_master_enable)

                        self.cpu.jit_jump = False
                        self.cpu.tick(cycles_target)
                else:
                    self.cpu.jit_jump = False
                    self.cpu.tick(cycles_target)

            #TODO: Support General Purpose DMA
            # https://gbdev.io/pandocs/CGB_Registers.html#bit-7--0---general-purpose-dma

            self.sound.tick(self.cpu.cycles, self.double_speed)

            if self.timer.tick(self.cpu.cycles):
                self.cpu.set_interruptflag(INTR_TIMER)

            lcd_interrupt = self.lcd.tick(self.cpu.cycles)
            if lcd_interrupt:
                self.cpu.set_interruptflag(lcd_interrupt)

            if self.breakpoint_singlestep:
                break

        # TODO: Move SDL2 sync to plugin
        self.sound.sync()

        self.jit_process()

        return self.breakpoint_singlestep

    ###################################################################
    # MemoryManager
    #
    def getitem(self, i):
        if 0x0000 <= i < 0x4000: # 16kB ROM bank #0
            if self.bootrom_enabled and (i <= 0xFF or (self.cgb and 0x200 <= i < 0x900)):
                return self.bootrom.getitem(i)
            else:
                return self.cartridge.rombanks[self.cartridge.rombank_selected_low, i]
        elif 0x4000 <= i < 0x8000: # 16kB switchable ROM bank
            return self.cartridge.rombanks[self.cartridge.rombank_selected, i - 0x4000]
        elif 0x8000 <= i < 0xA000: # 8kB Video RAM
            if not self.cgb or self.lcd.vbk.active_bank == 0:
                return self.lcd.VRAM0[i - 0x8000]
            else:
                return self.lcd.VRAM1[i - 0x8000]
        elif 0xA000 <= i < 0xC000: # 8kB switchable RAM bank
            return self.cartridge.getitem(i)
        elif 0xC000 <= i < 0xE000: # 8kB Internal RAM
            bank_offset = 0
            if self.cgb and 0xD000 <= i:
                # Find which bank to read from at FF70
                bank = self.ram.non_io_internal_ram1[0xFF70 - 0xFF4C] & 0b111
                if bank == 0x0:
                    bank = 0x01
                bank_offset = (bank-1) * 0x1000
            return self.ram.internal_ram0[i - 0xC000 + bank_offset]
        elif 0xE000 <= i < 0xFE00: # Echo of 8kB Internal RAM
            # Redirect to internal RAM
            return self.getitem(i - 0x2000)
        elif 0xFE00 <= i < 0xFEA0: # Sprite Attribute Memory (OAM)
            return self.lcd.OAM[i - 0xFE00]
        elif 0xFEA0 <= i < 0xFF00: # Empty but unusable for I/O
            return self.ram.non_io_internal_ram0[i - 0xFEA0]
        elif 0xFF00 <= i < 0xFF4C: # I/O ports
            # NOTE: A bit ad-hoc, but interrupts can occur right between writes
            if self.timer.tick(self.cpu.cycles):
                self.cpu.set_interruptflag(INTR_TIMER)

            if i == 0xFF04:
                return self.timer.DIV
            elif i == 0xFF05:
                return self.timer.TIMA
            elif i == 0xFF06:
                return self.timer.TMA
            elif i == 0xFF07:
                return self.timer.TAC
            elif i == 0xFF0F:
                return self.cpu.interrupts_flag_register
            elif 0xFF10 <= i < 0xFF40:
                self.sound.tick(self.cpu.cycles, self.double_speed)
                return self.sound.get(i - 0xFF10)
            elif i == 0xFF40:
                return self.lcd.get_lcdc()
            elif i == 0xFF41:
                return self.lcd.get_stat()
            elif i == 0xFF42:
                return self.lcd.SCY
            elif i == 0xFF43:
                return self.lcd.SCX
            elif i == 0xFF44:
                return self.lcd.LY
            elif i == 0xFF45:
                return self.lcd.LYC
            elif i == 0xFF46:
                return 0x00 # DMA
            elif i == 0xFF47:
                return self.lcd.BGP.get()
            elif i == 0xFF48:
                return self.lcd.OBP0.get()
            elif i == 0xFF49:
                return self.lcd.OBP1.get()
            elif i == 0xFF4A:
                return self.lcd.WY
            elif i == 0xFF4B:
                return self.lcd.WX
            else:
                return self.ram.io_ports[i - 0xFF00]
        elif 0xFF4C <= i < 0xFF80: # Empty but unusable for I/O
            # CGB registers
            if self.cgb and i == 0xFF4D:
                return self.key1
            elif self.cgb and i == 0xFF4F:
                return self.lcd.vbk.get()
            elif self.cgb and i == 0xFF68:
                return self.lcd.bcps.get() | 0x40
            elif self.cgb and i == 0xFF69:
                return self.lcd.bcpd.get()
            elif self.cgb and i == 0xFF6A:
                return self.lcd.ocps.get() | 0x40
            elif self.cgb and i == 0xFF6B:
                return self.lcd.ocpd.get()
            elif self.cgb and i == 0xFF51:
                # logger.debug("HDMA1 is not readable")
                return 0x00 # Not readable
            elif self.cgb and i == 0xFF52:
                # logger.debug("HDMA2 is not readable")
                return 0x00 # Not readable
            elif self.cgb and i == 0xFF53:
                # logger.debug("HDMA3 is not readable")
                return 0x00 # Not readable
            elif self.cgb and i == 0xFF54:
                # logger.debug("HDMA4 is not readable")
                return 0x00 # Not readable
            elif self.cgb and i == 0xFF55:
                return self.hdma.hdma5 & 0xFF
            return self.ram.non_io_internal_ram1[i - 0xFF4C]
        elif 0xFF80 <= i < 0xFFFF: # Internal RAM
            return self.ram.internal_ram1[i - 0xFF80]
        elif i == 0xFFFF: # Interrupt Enable Register
            return self.cpu.interrupts_enabled_register
        # else:
        #     logger.critical("Memory access violation. Tried to read: %0.4x", i)

    def setitem(self, i, value):
        if 0x0000 <= i < 0x4000: # 16kB ROM bank #0
            # Doesn't change the data. This is for MBC commands
            self.cartridge.setitem(i, value)
            self.cpu.bail = True # TODO: This is not something to bail for in non-jit mode
        elif 0x4000 <= i < 0x8000: # 16kB switchable ROM bank
            # Doesn't change the data. This is for MBC commands
            self.cartridge.setitem(i, value)
            self.cpu.bail = True # TODO: This is not something to bail for in non-jit mode
        elif 0x8000 <= i < 0xA000: # 8kB Video RAM
            if not self.cgb or self.lcd.vbk.active_bank == 0:
                self.lcd.VRAM0[i - 0x8000] = value
                if i < 0x9800: # Is within tile data -- not tile maps
                    # Mask out the byte of the tile
                    self.lcd.renderer.invalidate_tile(((i & 0xFFF0) - 0x8000) // 16, 0)
            else:
                self.lcd.VRAM1[i - 0x8000] = value
                if i < 0x9800: # Is within tile data -- not tile maps
                    # Mask out the byte of the tile
                    self.lcd.renderer.invalidate_tile(((i & 0xFFF0) - 0x8000) // 16, 1)
        elif 0xA000 <= i < 0xC000: # 8kB switchable RAM bank
            self.cartridge.setitem(i, value)
        elif 0xC000 <= i < 0xE000: # 8kB Internal RAM
            bank_offset = 0
            if self.cgb and 0xD000 <= i:
                # Find which bank to read from at FF70
                bank = self.getitem(0xFF70)
                bank &= 0b111
                if bank == 0x0:
                    bank = 0x01
                bank_offset = (bank-1) * 0x1000
            self.ram.internal_ram0[i - 0xC000 + bank_offset] = value
        elif 0xE000 <= i < 0xFE00: # Echo of 8kB Internal RAM
            self.setitem(i - 0x2000, value) # Redirect to internal RAM
        elif 0xFE00 <= i < 0xFEA0: # Sprite Attribute Memory (OAM)
            self.lcd.OAM[i - 0xFE00] = value
        elif 0xFEA0 <= i < 0xFF00: # Empty but unusable for I/O
            self.ram.non_io_internal_ram0[i - 0xFEA0] = value
        elif 0xFF00 <= i < 0xFF4C: # I/O ports
            # NOTE: A bit ad-hoc, but interrupts can occur right between writes
            if self.timer.tick(self.cpu.cycles):
                self.cpu.set_interruptflag(INTR_TIMER)

            if i == 0xFF00:
                self.ram.io_ports[i - 0xFF00] = self.interaction.pull(value)
            elif i == 0xFF01:
                self.serialbuffer[self.serialbuffer_count] = value
                self.serialbuffer_count += 1
                self.serialbuffer_count &= 0x3FF
                self.ram.io_ports[i - 0xFF00] = value
            elif i == 0xFF04:
                self.timer.reset()
            elif i == 0xFF05:
                self.timer.TIMA = value
            elif i == 0xFF06:
                self.timer.TMA = value
            elif i == 0xFF07:
                self.timer.TAC = value & 0b111 # TODO: Move logic to Timer class
            elif i == 0xFF0F:
                self.cpu.interrupts_flag_register = value
            elif 0xFF10 <= i < 0xFF40:
                self.sound.tick(self.cpu.cycles, self.double_speed)
                self.sound.set(i - 0xFF10, value)
            elif i == 0xFF40:
                self.lcd.set_lcdc(value)
            elif i == 0xFF41:
                self.lcd.set_stat(value)
            elif i == 0xFF42:
                self.lcd.SCY = value
            elif i == 0xFF43:
                self.lcd.SCX = value
            elif i == 0xFF44:
                self.lcd.LY = value
            elif i == 0xFF45:
                self.lcd.LYC = value
            elif i == 0xFF46:
                self.transfer_DMA(value)
            elif i == 0xFF47:
                if self.lcd.BGP.set(value):
                    # TODO: Move out of MB
                    self.lcd.renderer.clear_tilecache0()
            elif i == 0xFF48:
                if self.lcd.OBP0.set(value):
                    # TODO: Move out of MB
                    self.lcd.renderer.clear_spritecache0()
            elif i == 0xFF49:
                if self.lcd.OBP1.set(value):
                    # TODO: Move out of MB
                    self.lcd.renderer.clear_spritecache1()
            elif i == 0xFF4A:
                self.lcd.WY = value
            elif i == 0xFF4B:
                self.lcd.WX = value
            else:
                self.ram.io_ports[i - 0xFF00] = value
            self.cpu.bail = True
        elif 0xFF4C <= i < 0xFF80: # Empty but unusable for I/O
            if self.bootrom_enabled and i == 0xFF50 and (value == 0x1 or value == 0x11):
                logger.debug("Bootrom disabled!")
                self.bootrom_enabled = False
                self.cpu.bail = True
                if self.jit_enabled:
                    self.jit._jit_clear()
            # CGB registers
            elif self.cgb and i == 0xFF4D:
                self.key1 = value
                self.cpu.bail = True
            elif self.cgb and i == 0xFF4F:
                self.lcd.vbk.set(value)
            elif self.cgb and i == 0xFF51:
                self.hdma.hdma1 = value
            elif self.cgb and i == 0xFF52:
                self.hdma.hdma2 = value # & 0xF0
            elif self.cgb and i == 0xFF53:
                self.hdma.hdma3 = value # & 0x1F
            elif self.cgb and i == 0xFF54:
                self.hdma.hdma4 = value # & 0xF0
            elif self.cgb and i == 0xFF55:
                self.hdma.set_hdma5(value, self)
                self.cpu.bail = True
            elif self.cgb and i == 0xFF68:
                self.lcd.bcps.set(value)
            elif self.cgb and i == 0xFF69:
                self.lcd.bcpd.set(value)
                self.lcd.renderer.clear_tilecache0()
                self.lcd.renderer.clear_tilecache1()
            elif self.cgb and i == 0xFF6A:
                self.lcd.ocps.set(value)
            elif self.cgb and i == 0xFF6B:
                self.lcd.ocpd.set(value)
                self.lcd.renderer.clear_spritecache0()
                self.lcd.renderer.clear_spritecache1()
            else:
                self.ram.non_io_internal_ram1[i - 0xFF4C] = value
        elif 0xFF80 <= i < 0xFFFF: # Internal RAM
            self.ram.internal_ram1[i - 0xFF80] = value
        elif i == 0xFFFF: # Interrupt Enable Register
            self.cpu.interrupts_enabled_register = value
            self.cpu.bail = True
        # else:
        #     logger.critical("Memory access violation. Tried to write: 0x%0.2x to 0x%0.4x", value, i)

    def transfer_DMA(self, src):
        # http://problemkaputt.de/pandocs.htm#lcdoamdmatransfers
        # TODO: Add timing delay of 160µs and disallow access to RAM!
        dst = 0xFE00
        offset = src * 0x100
        for n in range(0xA0):
            self.setitem(dst + n, self.getitem(n + offset))


class HDMA:
    def __init__(self):
        self.hdma1 = 0
        self.hdma2 = 0
        self.hdma3 = 0
        self.hdma4 = 0
        self.hdma5 = 0xFF

        self.transfer_active = False
        self.curr_src = 0
        self.curr_dst = 0

    def save_state(self, f):
        f.write(self.hdma1)
        f.write(self.hdma2)
        f.write(self.hdma3)
        f.write(self.hdma4)
        f.write(self.hdma5)
        f.write(self.transfer_active)
        f.write_16bit(self.curr_src)
        f.write_16bit(self.curr_dst)

    def load_state(self, f, state_version):
        self.hdma1 = f.read()
        self.hdma2 = f.read()
        self.hdma3 = f.read()
        self.hdma4 = f.read()
        self.hdma5 = f.read()
        if STATE_VERSION <= 8:
            # NOTE: Deprecated read to self._hdma5
            f.read()
        self.transfer_active = f.read()
        self.curr_src = f.read_16bit()
        self.curr_dst = f.read_16bit()

    def set_hdma5(self, value, mb):
        if self.transfer_active:
            bit7 = value & 0x80
            if bit7 == 0:
                # terminate active transfer
                self.transfer_active = False
                self.hdma5 = (self.hdma5 & 0x7F) | 0x80
            else:
                self.hdma5 = value & 0x7F
        else:
            self.hdma5 = value & 0xFF
            bytes_to_transfer = ((value & 0x7F) * 16) + 16
            src = (self.hdma1 << 8) | (self.hdma2 & 0xF0)
            dst = ((self.hdma3 & 0x1F) << 8) | (self.hdma4 & 0xF0)
            dst |= 0x8000

            transfer_type = value >> 7
            if transfer_type == 0:
                # General purpose DMA transfer
                for i in range(bytes_to_transfer):
                    mb.setitem((dst + i) & 0xFFFF, mb.getitem((src + i) & 0xFFFF))

                # Number of blocks of 16-bytes transfered. Set 7th bit for "completed".
                self.hdma5 = 0xFF #(value & 0x7F) | 0x80 #0xFF
                self.hdma4 = 0xFF
                self.hdma3 = 0xFF
                self.hdma2 = 0xFF
                self.hdma1 = 0xFF
                # TODO: Progress cpu cycles!
                # https://gist.github.com/drhelius/3394856
                # cpu is halted during dma transfer
            else:
                # Hblank DMA transfer
                # set 7th bit to 0
                self.hdma5 = self.hdma5 & 0x7F
                self.transfer_active = True
                self.curr_dst = dst
                self.curr_src = src

    def tick(self, mb):
        # HBLANK HDMA routine
        src = self.curr_src & 0xFFF0
        dst = (self.curr_dst & 0x1FF0) | 0x8000

        for i in range(0x10):
            mb.setitem(dst + i, mb.getitem(src + i))

        self.curr_dst += 0x10
        self.curr_src += 0x10

        if self.curr_dst == 0xA000:
            self.curr_dst = 0x8000

        if self.curr_src == 0x8000:
            self.curr_src = 0xA000

        self.hdma1 = (self.curr_src & 0xFF00) >> 8
        self.hdma2 = self.curr_src & 0x00FF

        self.hdma3 = (self.curr_dst & 0xFF00) >> 8
        self.hdma4 = self.curr_dst & 0x00FF

        if self.hdma5 == 0:
            self.transfer_active = False
            self.hdma5 = 0xFF
        else:
            self.hdma5 -= 1

        return 206 # TODO: adjust for double speed


# Unfortunately CPython/PyPy code has to be hidden in an exec call to
# prevent Cython from trying to parse it. This block provides the
# functions that are otherwise implemented as inlined cdefs in the pxd
if not cythonmode:
    exec(
        """
def _jit_load(self, module_name, module_path, file_base, block_id, block_max_cycles):
    # spec = importlib.util.spec_from_file_location(module_name, loader=ExtensionFileLoader(module_name, file_base + JIT_EXTENSION))
    spec = importlib.util.spec_from_file_location(module_name, file_base + JIT_EXTENSION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    self.jit_array[block_id] = module.execute
    self.jit_cycles[block_id] = block_max_cycles

def _jit_clear(self):
    self.jit_queue = {}
    self.jit_cycles = [0] * 0xFFFFFF
    self.jit_array = [None] * 0xFFFFFF

def _jit_execute(self, block_id, cycles_target):
    return self.jit_array[block_id](self.cpu, cycles_target)

Motherboard.jit_load = _jit_load
Motherboard._jit_clear = _jit_clear
Motherboard.jit_execute = _jit_execute
""", globals(), locals()
    )
