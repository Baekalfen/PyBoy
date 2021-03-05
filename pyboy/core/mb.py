#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import logging

from pyboy.core.opcodes import CPU_COMMANDS
from pyboy.utils import STATE_VERSION

from . import bootrom, cartridge, cpu, interaction, lcd, ram, sound, timer

INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW = [1 << x for x in range(5)]

logger = logging.getLogger(__name__)


class Motherboard:
    def __init__(
        self,
        gamerom_file,
        bootrom_file,
        color_palette,
        disable_renderer,
        sound_enabled,
        randomize=False,
        profiling=False,
    ):
        if bootrom_file is not None:
            logger.info("Boot-ROM file provided")

        if profiling:
            logger.info("Profiling enabled")

        self.timer = timer.Timer()
        self.interaction = interaction.Interaction()
        self.cartridge = cartridge.load_cartridge(gamerom_file)
        self.bootrom = bootrom.BootROM(bootrom_file)
        self.ram = ram.RAM(randomize=randomize)
        self.cpu = cpu.CPU(self, profiling)
        self.lcd = lcd.LCD(disable_renderer, color_palette, randomize=randomize)
        self.sound_enabled = sound_enabled
        if sound_enabled:
            self.sound = sound.Sound()
        self.bootrom_enabled = True
        self.serialbuffer = ""

        self.breakpoints_enabled = False # breakpoints_enabled
        self.breakpoints_list = [] #[(0, 0x150), (0, 0x0040), (0, 0x0048), (0, 0x0050)]
        self.breakpoint_latch = 0

    def add_breakpoint(self, bank, addr):
        self.breakpoints_enabled = True
        self.breakpoints_list.append((bank, addr))

    def remove_breakpoint(self, index):
        self.breakpoints_list.pop(index)
        if self.breakpoints == []:
            self.breakpoints_enabled = False

    def getserial(self):
        b = self.serialbuffer
        self.serialbuffer = ""
        return b

    def buttonevent(self, key):
        if self.interaction.key_event(key):
            self.cpu.set_interruptflag(INTR_HIGHTOLOW)

    def stop(self, save):
        if self.sound_enabled:
            self.sound.stop()
        if save:
            self.cartridge.stop()

    def save_state(self, f):
        logger.debug("Saving state...")
        f.write(STATE_VERSION)
        f.write(self.bootrom_enabled)
        self.cpu.save_state(f)
        self.lcd.save_state(f)
        if self.sound_enabled:
            self.sound.save_state(f)
        else:
            pass
        self.lcd.renderer.save_state(f)
        self.ram.save_state(f)
        self.timer.save_state(f)
        self.cartridge.save_state(f)
        f.flush()
        logger.debug("State saved.")

    def load_state(self, f):
        logger.debug("Loading state...")
        state_version = f.read()
        if state_version >= 2:
            logger.debug(f"State version: {state_version}")
            # From version 2 and above, this is the version number
            self.bootrom_enabled = f.read()
        else:
            logger.debug(f"State version: 0-1")
            # HACK: The byte wasn't a state version, but the bootrom flag
            self.bootrom_enabled = state_version
        self.cpu.load_state(f, state_version)
        self.lcd.load_state(f, state_version)
        if state_version >= 6 and self.sound_enabled:
            self.sound.load_state(f, state_version)
        self.lcd.renderer.load_state(f, state_version)
        self.lcd.renderer.update_cache(self.lcd)
        self.ram.load_state(f, state_version)
        if state_version < 5:
            # Interrupt register moved from RAM to CPU
            self.cpu.interrupts_enabled_register = f.read()
        if state_version >= 5:
            self.timer.load_state(f, state_version)
        self.cartridge.load_state(f, state_version)
        f.flush()
        logger.debug("State loaded.")

    ###################################################################
    # Coordinator
    #

    def breakpoint_reached(self):
        if self.breakpoint_latch > 0:
            self.breakpoint_latch -= 1
            return True

        for bank, pc in self.breakpoints_list:
            if self.cpu.PC == pc and (
                (pc < 0x4000 and bank == 0 and not self.bootrom_enabled) or \
                (0x4000 <= pc < 0x8000 and self.cartridge.rombank_selected == bank) or \
                (0xA000 <= pc < 0xC000 and self.cartridge.rambank_selected == bank) or \
                (0xC000 <= pc <= 0xFFFF and bank == -1) or \
                (pc < 0x100 and bank == -1 and self.bootrom_enabled)
            ):
                # Breakpoint hit
                return True
        return False

    def tick(self):
        # print("MB TICK")
        while self.lcd.processing_frame():
            cycles = self.cpu.tick()

            if self.cpu.halted:
                # Fast-forward to next interrupt:
                # As we are halted, we are guaranteed, that our state
                # cannot be altered by other factors than time.
                # For HiToLo interrupt it is indistinguishable whether
                # it gets triggered mid-frame or by next frame
                # Serial is not implemented, so this isn't a concern
                cycles = min(
                    self.lcd.cyclestointerrupt(),
                    self.timer.cyclestointerrupt(),
                    # self.serial.cyclestointerrupt(),
                )

                # Profiling
                self.cpu.add_opcode_hit(0x76, cycles // 4)

            # TODO: Unify interface
            if self.sound_enabled:
                self.sound.clock += cycles

            if self.timer.tick(cycles):
                self.cpu.set_interruptflag(INTR_TIMER)

            lcd_interrupt = self.lcd.tick(cycles)
            if lcd_interrupt:
                self.cpu.set_interruptflag(lcd_interrupt)

            # Escape halt. This happens when pressing 'return' in the debugger. It will make us skip breaking on halt
            # for every cycle, but do break on the next instruction -- even in an interrupt.
            escape_halt = self.cpu.halted and self.breakpoint_latch == 1
            if self.breakpoints_enabled and (not escape_halt) and self.breakpoint_reached():
                return True

        # TODO: Move SDL2 sync to plugin
        if self.sound_enabled:
            self.sound.sync()

        return False

    ###################################################################
    # MemoryManager
    #
    def getitem(self, i):
        if 0x0000 <= i < 0x4000: # 16kB ROM bank #0
            if i <= 0xFF and self.bootrom_enabled:
                return self.bootrom.getitem(i)
            else:
                return self.cartridge.getitem(i)
        elif 0x4000 <= i < 0x8000: # 16kB switchable ROM bank
            return self.cartridge.getitem(i)
        elif 0x8000 <= i < 0xA000: # 8kB Video RAM
            return self.lcd.VRAM[i - 0x8000]
        elif 0xA000 <= i < 0xC000: # 8kB switchable RAM bank
            return self.cartridge.getitem(i)
        elif 0xC000 <= i < 0xE000: # 8kB Internal RAM
            return self.ram.internal_ram0[i - 0xC000]
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
                if self.sound_enabled:
                    return self.sound.get(i - 0xFF10)
                else:
                    return 0
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
                return self.lcd.BGP.value
            elif i == 0xFF48:
                return self.lcd.OBP0.value
            elif i == 0xFF49:
                return self.lcd.OBP1.value
            elif i == 0xFF4A:
                return self.lcd.WY
            elif i == 0xFF4B:
                return self.lcd.WX
            else:
                return self.ram.io_ports[i - 0xFF00]
        elif 0xFF4C <= i < 0xFF80: # Empty but unusable for I/O
            return self.ram.non_io_internal_ram1[i - 0xFF4C]
        elif 0xFF80 <= i < 0xFFFF: # Internal RAM
            return self.ram.internal_ram1[i - 0xFF80]
        elif i == 0xFFFF: # Interrupt Enable Register
            return self.cpu.interrupts_enabled_register
        else:
            raise IndexError("Memory access violation. Tried to read: %s" % hex(i))

    def setitem(self, i, value):
        assert 0 <= value < 0x100, "Memory write error! Can't write %s to %s" % (hex(value), hex(i))

        if 0x0000 <= i < 0x4000: # 16kB ROM bank #0
            # Doesn't change the data. This is for MBC commands
            self.cartridge.setitem(i, value)
        elif 0x4000 <= i < 0x8000: # 16kB switchable ROM bank
            # Doesn't change the data. This is for MBC commands
            self.cartridge.setitem(i, value)
        elif 0x8000 <= i < 0xA000: # 8kB Video RAM
            self.lcd.VRAM[i - 0x8000] = value
            if i < 0x9800: # Is within tile data -- not tile maps
                # Mask out the byte of the tile
                self.lcd.renderer.tiles_changed.add(i & 0xFFF0)
        elif 0xA000 <= i < 0xC000: # 8kB switchable RAM bank
            self.cartridge.setitem(i, value)
        elif 0xC000 <= i < 0xE000: # 8kB Internal RAM
            self.ram.internal_ram0[i - 0xC000] = value
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
                self.serialbuffer += chr(value)
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
                if self.sound_enabled:
                    self.sound.set(i - 0xFF10, value)
            elif i == 0xFF40:
                self.lcd.set_lcdc(value)
            elif i == 0xFF41:
                self.lcd.set_stat(value)
            elif i == 0xFF42:
                # print(f"SCY: {value}")
                self.lcd.SCY = value
            elif i == 0xFF43:
                # print(f"SCX: {value}")
                self.lcd.SCX = value
            elif i == 0xFF44:
                self.lcd.LY = value
            elif i == 0xFF45:
                # print(f"LYC: {value}")
                self.lcd.LYC = value
            elif i == 0xFF46:
                self.transfer_DMA(value)
            elif i == 0xFF47:
                # TODO: Move out of MB
                self.lcd.renderer.clearcache = self.lcd.renderer.clearcache | self.lcd.BGP.set(value)
            elif i == 0xFF48:
                # TODO: Move out of MB
                self.lcd.renderer.clearcache = self.lcd.renderer.clearcache | self.lcd.OBP0.set(value)
            elif i == 0xFF49:
                # TODO: Move out of MB
                self.lcd.renderer.clearcache = self.lcd.renderer.clearcache | self.lcd.OBP1.set(value)
            elif i == 0xFF4A:
                # print(f"WY: {value}")
                self.lcd.WY = value
            elif i == 0xFF4B:
                # print(f"WX: {value}")
                self.lcd.WX = value
            else:
                self.ram.io_ports[i - 0xFF00] = value
        elif 0xFF4C <= i < 0xFF80: # Empty but unusable for I/O
            if self.bootrom_enabled and i == 0xFF50 and value == 1:
                self.bootrom_enabled = False
            self.ram.non_io_internal_ram1[i - 0xFF4C] = value
        elif 0xFF80 <= i < 0xFFFF: # Internal RAM
            self.ram.internal_ram1[i - 0xFF80] = value
        elif i == 0xFFFF: # Interrupt Enable Register
            self.cpu.interrupts_enabled_register = value
        else:
            raise Exception("Memory access violation. Tried to write: %s" % hex(i))

    def transfer_DMA(self, src):
        # http://problemkaputt.de/pandocs.htm#lcdoamdmatransfers
        # TODO: Add timing delay of 160µs and disallow access to RAM!
        dst = 0xFE00
        offset = src * 0x100
        for n in range(0xA0):
            self.setitem(dst + n, self.getitem(n + offset))
