#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import hashlib
import importlib
import os
from distutils.command.build_ext import build_ext
from distutils.core import Distribution, Extension
from importlib.machinery import ExtensionFileLoader

from Cython.Build import cythonize

from pyboy import utils
from pyboy.core.opcodes_gen import opcodes as opcodes_gen
from pyboy.utils import STATE_VERSION

from . import bootrom, cartridge, cpu, interaction, lcd, opcodes, ram, sound, timer

INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW = [1 << x for x in range(5)]
OPCODE_BRK = 0xDB

import pyboy

logger = pyboy.logging.get_logger(__name__)


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

        self.breakpoints_list = [] #[(0, 0x150), (0, 0x0040), (0, 0x0048), (0, 0x0050)]
        self.breakpoint_singlestep = False
        self.breakpoint_singlestep_latch = False
        self.breakpoint_waiting = -1

        self.jit_enabled = jit_enabled
        self._cycles = 0

    def __cinit__(self):
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

        self.breakpoints_list.append((bank, addr, opcode))
        return len(self.breakpoints_list) - 1

    def breakpoint_find(self, bank, addr):
        for i, (_bank, _addr, _) in enumerate(self.breakpoints_list):
            if _bank == bank and _addr == addr:
                return i
        return -1

    def breakpoint_remove(self, index):
        logger.debug(f"Breakpoint remove: {index}")
        if not 0 <= index < len(self.breakpoints_list):
            logger.error("Cannot remove breakpoint: Index out of bounds %d/%d", index, len(self.breakpoints_list))
            # return (None, None, None)
        bank, addr, opcode = self.breakpoints_list.pop(index)
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
        #     return (None, None, None)
        # return (bank, addr, opcode)

    def breakpoint_reached(self):
        for i, (bank, pc, _) in enumerate(self.breakpoints_list):
            if self.cpu.PC == pc and (
                (pc < 0x4000 and bank == 0 and not self.bootrom_enabled) or \
                (0x4000 <= pc < 0x8000 and self.cartridge.rombank_selected == bank) or \
                (0xA000 <= pc < 0xC000 and self.cartridge.rambank_selected == bank) or \
                (0xC000 <= pc <= 0xFFFF and bank == -1) or \
                (pc < 0x100 and bank == -1 and self.bootrom_enabled)
            ):
                # Breakpoint hit
                # bank, addr, opcode = self.breakpoint_remove(i)
                bank, addr, opcode = self.breakpoints_list[i]
                logger.debug(f"Breakpoint reached: {bank:02x}:{addr:04x} {opcode:02x}")
                self.breakpoint_waiting = (bank & 0xFF) << 24 | (addr & 0xFFFF) << 8 | (opcode & 0xFF)
                logger.debug(f"Breakpoint waiting: {self.breakpoint_waiting:08x}")
                return i
        logger.debug("Invalid breakpoint reached: %04x", self.cpu.PC)
        return -1

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

    def jit_compile(self, code_text):
        # https://github.com/cython/cython/blob/4e0eee43210d6b7822859f3001202910888644af/Cython/Build/Inline.py#L141
        m = hashlib.sha1()
        m.update(code_text.encode())
        _hash = m.digest().hex()

        module_name = "jit_" + _hash
        module_path = module_name + ".cpython-311-darwin.so" #os.path.splitext(jit_file)[0] + '.so'

        if not os.path.exists(module_path):
            # logger.info("Compiling JIT block: %s", module_path)
            file_base = os.path.splitext(self.cartridge.filename)[0].replace(".", "_") + "_jit_" + _hash # Generate name
            jit_file = file_base + ".pyx"
            with open(jit_file, "w") as f:
                f.write(code_text)

            jit_file_pxd = file_base + ".pxd"
            with open(jit_file_pxd, "w") as f:
                f.write("from pyboy.core cimport cpu as _cpu\ncdef public int execute(void* __cpu) noexcept with gil")

            cythonize_files = [
                Extension(
                    module_name, #src.split(".")[0].replace(os.sep, "."),
                    [jit_file],
                    extra_compile_args=["-O3"],
                    # include_dirs=[np.get_include()],
                )
            ]
            build_extension = self._get_build_extension()
            build_extension.extensions = cythonize(
                [*cythonize_files],
                nthreads=1,
                annotate=False,
                gdb_debug=False,
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

        return module_path

    # def jit_load(self, module_path):
    #     # spec = importlib.util.spec_from_file_location(module_name, loader=ExtensionFileLoader(module_name, module_path))
    #     # module = importlib.util.module_from_spec(spec)
    #     # spec.loader.exec_module(module)
    #     self.jit_load(module_path)
    #     # self.test_func = module.execute

    #     # module.execute(self.cpu)
    #     # code = CodeBlock(module.execute)
    #     # return code

    def jit_emit_code(self, code_block):
        preamble = """
cimport pyboy

from libc.stdint cimport uint8_t, uint16_t, int16_t, uint32_t
cimport cython
from pyboy.core cimport cpu as _cpu

cdef uint8_t FLAGC = 4
cdef uint8_t FLAGH = 5
cdef uint8_t FLAGN = 6
cdef uint8_t FLAGZ = 7

"""
        code_text = preamble + "cdef public int execute(void* __cpu) noexcept with gil:\n\tcdef uint8_t flag\n\tcdef int t\n\tcdef uint16_t tr\n\tcdef int v\n\tcdef int cycles = 0\n\tcdef _cpu.CPU cpu = <_cpu.CPU> __cpu"
        for opcode, length, literal1, literal2 in code_block:
            opcode_handler = opcodes_gen[opcode]
            opcode_name = opcode_handler.name.split()[0]
            code_text += "\n\t" + "# " + opcode_handler.name + "\n\t"
            if length == 2:
                v = literal1
                code_text += "v = " + str(v) + "\n\t"
            elif length == 3:
                v = (literal2 << 8) + literal1
                code_text += "v = " + str(v) + "\n\t"

            tmp_code = opcode_handler.functionhandlers[opcode_name]()._code_body()
            tmp_code = tmp_code.replace("return", "cycles +=")
            if "tr = " in tmp_code:
                # if "(" in opcode_handler.name.split(',')[0]: #"setitem" in tmp_code:
                # breakpoint()
                # Return early on state-altering writes
                tmp_code += "\n\tif tr: return cycles"
            code_text += tmp_code
            # TODO: Shouldn't this work?
            # code_text += "\n\tcpu.mb.timer.tick(cycles)\n\tcpu.mb.lcd.tick(cycles)\n\tcycles = 0"

        code_text += "\n\treturn cycles"
        # opcodes[7].functionhandlers[opcodes[7].name.split()[0]]().branch_op
        # if .getitem in code, commit timer.tick(cycles); cycles = 0
        return code_text

    def jit_analyze(self, block_id):
        boundary_instruction = [
            # JR
            0x20,
            0x30,

            # JR
            0x18,
            0x28,
            0x38,

            # RET
            0xC0,
            0xD0,

            # JP
            0xC2,
            0xD2,

            # JP
            0xC3,

            # CALL
            0xC4,
            0xD4,

            # RST
            0xC7,
            0xD7,
            0xE7,
            0xF7,

            # RET
            0xC8,
            0xD8,
            0xC9, # RET
            0xD9, # RETI
            0xE9, # JP

            # JP
            0xCA,
            0xDA,

            # CALL
            0xCC,
            0xDC,

            # CALL
            0xCD,

            # RST
            0xCF,
            0xDF,
            0xEF,
            0xFF,
            0x76, # HALT
            0x10, # STOP
            0xF0, # LDH A,(a8) Used often for VBLANK check
        ]
        code_block = []
        pc = self.cpu.PC
        block_max_cycles = 0
        while True:
            opcode = self.getitem(pc)
            if opcode == 0xCB: # Extension code
                pc += 1
                opcode = self.getitem(pc)
                opcode += 0x100 # Internally shifting look-up table
            opcode_length = opcodes.OPCODE_LENGTHS[opcode]
            opcode_max_cycles = opcodes.OPCODE_MAX_CYCLES[opcode]
            block_max_cycles += opcode_max_cycles
            code_block.append((opcode, opcode_length, self.getitem(pc + 1), self.getitem(pc + 2)))
            pc += opcode_length
            if opcode in boundary_instruction:
                break

        if len(code_block) < 10:
            return -1

        code_text = self.jit_emit_code(code_block)
        module_path = self.jit_compile(code_text)
        self.jit_load(module_path, block_id, block_max_cycles)
        # code = CodeBlock(block_id)
        # code.cycles = block_max_cycles
        # return block_id
        return 0

    def jit(self, max_cycles):
        if self.bootrom_enabled:
            block_id = (self.cpu.PC << 8) | 0xFF
        else:
            block_id = (self.cpu.PC << 8) | self.cartridge.rombank_selected

        block_max_cycles = self.jit_cycles[block_id]
        if block_max_cycles == 0 and self.jit_analyze(block_id):
            self.jit_cycles[block_id] = -1 # Don't retry

        if block_max_cycles <= 0 or block_max_cycles > max_cycles:
            return 0

        return self.jit_execute(block_id)

        # if code.eligible:
        #     # if  <= cycles:
        #     return self.jit_execute(block_id, code.cycles)
        # logger.debug("Executing JIT block: PC=%x, code.cycles=%s, cycles=%d", self.cpu.PC, code.cycles, cycles)
        # cycles = code.body(self.cpu)
        # logger.debug(
        #     "After block: PC=%x, jit_jump=%d, actual cycles=%d", self.cpu.PC, self.cpu.jit_jump, cycles
        # )
        # return cycles
        # else:
        #     logger.debug("Too narrow to execute JIT block %s, %d", code.cycles, cycles)
        return 0

    def processing_frame(self):
        b = (not self.lcd.frame_done)
        self.lcd.frame_done = False # Clear vblank flag for next iteration
        return b

    def tick(self):
        # Threading by 'LD_21(cpu, v, cycles_left, cycles_acc)'
        # cpu.HL = v
        # cpu.PC += 3
        # cpu.PC &= 0xFFFF
        # if (cycles_left < 12):
        #     return cpu.next_opcode(cpu, cycles_left, cycles_acc + 12)
        # else:
        #     return 12

        while self.processing_frame():
            # if self.cpu.PC > 0x70:
            #     self.cpu.dump_state()
            # Inject special opcode instead? ~~Long immediate as identifier~~
            # Special opcode cannot be more than 1 byte, to avoid jumps to sub-parts of the jit block
            # Compile in other thread, acquire memory lock between frames
            # logger.debug("sdf %d, %d, %d, %d", self.jit_enabled, self.cpu.jit_jump, not self.cpu.pending_interrupt(), self.cpu.PC < 0x8000)
            if self.cgb and self.hdma.transfer_active and self.lcd._STAT._mode & 0b11 == 0:
                self.cpu.jit_jump = False
                cycles = self.hdma.tick(self)
            elif self.jit_enabled and self.cpu.jit_jump and not self.cpu.pending_interrupt(
            ) and self.cpu.PC < 0x8000: # and self.jit_cycles[block_id] >= 0:
                self.cpu.jit_jump = False
                mode0_cycles = 1 << 32
                if self.cgb and self.hdma.transfer_active:
                    mode0_cycles = self.lcd.cycles_to_mode0()

                max_cycles = max(
                    0,
                    min(
                        self.lcd.cycles_to_interrupt(),
                        self.timer.cycles_to_interrupt(),
                        # self.serial.cycles_to_interrupt(),
                        mode0_cycles
                    ) #- 24 # TODO: Avoid overshooting?
                )

                # logger.debug("max cycles %d", max_cycles)
                if max_cycles > 0:
                    cycles = self.jit(max_cycles)
                    if cycles == 0:
                        self.cpu.jit_jump = False
                        cycles = self.cpu.tick()
                else:
                    self.cpu.jit_jump = False
                    cycles = self.cpu.tick()
            else:
                # TODO: Run while-loop for max_cycles here. We clearly don't need to return to tick before.
                self.cpu.jit_jump = False
                cycles = self.cpu.tick()

            if self.cpu.halted:
                # Fast-forward to next interrupt:
                # As we are halted, we are guaranteed, that our state
                # cannot be altered by other factors than time.
                # For HiToLo interrupt it is indistinguishable whether
                # it gets triggered mid-frame or by next frame
                # Serial is not implemented, so this isn't a concern

                # Help Cython with types
                mode0_cycles = 1 << 32
                if self.cgb and self.hdma.transfer_active:
                    mode0_cycles = self.lcd.cycles_to_mode0()

                cycles = max(
                    0,
                    min(
                        self.lcd.cycles_to_interrupt(),
                        self.timer.cycles_to_interrupt(),
                        # self.serial.cycles_to_interrupt(),
                        mode0_cycles
                    )
                )

            #TODO: Support General Purpose DMA
            # https://gbdev.io/pandocs/CGB_Registers.html#bit-7--0---general-purpose-dma

            # TODO: Unify interface
            sclock = self.sound.clock
            if self.cgb and self.double_speed:
                self.sound.clock = sclock + cycles//2
            else:
                self.sound.clock = sclock + cycles

            if self.timer.tick(cycles):
                self.cpu.set_interruptflag(INTR_TIMER)

            lcd_interrupt = self.lcd.tick(cycles)
            if lcd_interrupt:
                self.cpu.set_interruptflag(lcd_interrupt)

            self._cycles += cycles

            if self.breakpoint_singlestep:
                break

        # TODO: Move SDL2 sync to plugin
        self.sound.sync()

        return self.breakpoint_singlestep

    ###################################################################
    # MemoryManager
    #
    def getitem(self, i):
        if 0x0000 <= i < 0x4000: # 16kB ROM bank #0
            if self.bootrom_enabled and (i <= 0xFF or (self.cgb and 0x200 <= i < 0x900)):
                return self.bootrom.getitem(i)
            else:
                return self.cartridge.getitem(i)
        elif 0x4000 <= i < 0x8000: # 16kB switchable ROM bank
            return self.cartridge.getitem(i)
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
                bank = self.getitem(0xFF70)
                bank &= 0b111
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
            return 1
        elif 0x4000 <= i < 0x8000: # 16kB switchable ROM bank
            # Doesn't change the data. This is for MBC commands
            self.cartridge.setitem(i, value)
            return 1
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
            return 2
        elif 0xFF4C <= i < 0xFF80: # Empty but unusable for I/O
            if self.bootrom_enabled and i == 0xFF50 and (value == 0x1 or value == 0x11):
                logger.debug("Bootrom disabled!")
                self.bootrom_enabled = False
                for n in range(0xFFFFFF):
                    self.jit_cycles[n] = 0
            # CGB registers
            elif self.cgb and i == 0xFF4D:
                self.key1 = value
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
            return 3
        elif 0xFF80 <= i < 0xFFFF: # Internal RAM
            self.ram.internal_ram1[i - 0xFF80] = value
        elif i == 0xFFFF: # Interrupt Enable Register
            self.cpu.interrupts_enabled_register = value
            return 4
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
