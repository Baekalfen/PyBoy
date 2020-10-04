#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import logging

from pyboy.utils import STATE_VERSION

from . import bootrom, cartridge, cpu, interaction, lcd, ram, sound, timer

logger = logging.getLogger(__name__)

VBLANK, LCDC, TIMER, SERIAL, HIGHTOLOW = range(5)
STAT, _, _, LY, LYC = range(0xFF41, 0xFF46)


class Motherboard:
    def __init__(
        self,
        gamerom_file,
        bootrom_file,
        color_palette,
        disable_renderer,
        sound_enabled,
        randomize=False,
        profiling=False
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
        self.lcd = lcd.LCD(randomize=randomize)
        self.renderer = lcd.Renderer(color_palette)
        self.disable_renderer = disable_renderer
        self.sound_enabled = sound_enabled
        if sound_enabled:
            self.sound = sound.Sound()
        self.bootrom_enabled = True
        self.serialbuffer = ""
        self.cycles_remaining = 0

    def getserial(self):
        b = self.serialbuffer
        self.serialbuffer = ""
        return b

    def buttonevent(self, key):
        if self.interaction.key_event(key):
            self.cpu.set_interruptflag(HIGHTOLOW)

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
        self.renderer.save_state(f)
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
        if state_version >= 6:
            self.sound.load_state(f, state_version)
        if state_version >= 2:
            self.renderer.load_state(f, state_version)
        self.ram.load_state(f, state_version)
        if state_version >= 5:
            self.timer.load_state(f, state_version)
        self.cartridge.load_state(f, state_version)
        f.flush()
        logger.debug("State loaded.")

        # TODO: Move out of MB
        self.renderer.clearcache = True
        self.renderer.render_screen(self.lcd)

    ###################################################################
    # Coordinator
    #

    # TODO: Move out of MB
    def set_STAT_mode(self, mode):
        self.setitem(STAT, self.getitem(STAT) & 0b11111100) # Clearing 2 LSB
        self.setitem(STAT, self.getitem(STAT) | mode) # Apply mode to LSB

        # Mode "3" is not interruptable
        if self.cpu.test_ramregisterflag(STAT, mode + 3) and mode != 3:
            self.cpu.set_interruptflag(LCDC)

    # TODO: Move out of MB
    def check_LYC(self, y):
        self.setitem(LY, y)
        if self.getitem(LYC) == y:
            self.setitem(STAT, self.getitem(STAT) | 0b100) # Sets the LYC flag
            if self.getitem(STAT) & 0b01000000:
                self.cpu.set_interruptflag(LCDC)
        else:
            self.setitem(STAT, self.getitem(STAT) & 0b11111011)

    def calculate_cycles(self, cycles_period):
        self.cycles_remaining += cycles_period
        while self.cycles_remaining > 0:
            cycles = self.cpu.tick()

            # TODO: Benchmark whether 'if' and 'try/except' is better
            if cycles == -1: # CPU has HALTED
                # Fast-forward to next interrupt:
                # VBLANK and LCDC are covered by just returning.
                # Timer has to be determined.
                # As we are halted, we are guaranteed, that our state
                # cannot be altered by other factors than time.
                # For HiToLo interrupt it is indistinguishable whether
                # it gets triggered mid-frame or by next frame
                # Serial is not implemented, so this isn't a concern
                cycles = min(self.timer.cyclestointerrupt(), self.cycles_remaining)

                # Profiling
                if self.cpu.profiling:
                    self.cpu.hitrate[0x76] += cycles // 4

            if self.sound_enabled:
                self.sound.clock += cycles
            self.cycles_remaining -= cycles

            if self.timer.tick(cycles):
                self.cpu.set_interruptflag(TIMER)

    def tickframe(self):
        lcdenabled = self.lcd.LCDC.lcd_enable
        if lcdenabled:
            # TODO: the 19, 41 and 49._ticks should correct for longer instructions
            # Iterate the 144 lines on screen
            for y in range(144):
                self.check_LYC(y)

                # Mode 2
                # TODO: Move out of MB
                self.set_STAT_mode(2)
                self.calculate_cycles(80)

                # Mode 3
                # TODO: Move out of MB
                self.set_STAT_mode(3)
                self.calculate_cycles(170)
                self.renderer.scanline(y, self.lcd)

                # Mode 0
                # TODO: Move out of MB
                self.set_STAT_mode(0)
                self.calculate_cycles(206)

            self.cpu.set_interruptflag(VBLANK)
            if not self.disable_renderer:
                self.renderer.render_screen(self.lcd)

            # Wait for next frame
            for y in range(144, 154):
                self.check_LYC(y)

                # Mode 1
                self.set_STAT_mode(1)
                self.calculate_cycles(456)
        else:
            # https://www.reddit.com/r/EmuDev/comments/6r6gf3
            # TODO: What happens if LCD gets turned on/off mid-cycle?
            self.renderer.blank_screen()
            # TODO: Move out of MB
            self.set_STAT_mode(0)
            self.setitem(LY, 0)

            for y in range(154):
                self.calculate_cycles(456)
        if self.sound_enabled:
            self.sound.sync()

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
            elif 0xFF10 <= i < 0xFF40:
                if self.sound_enabled:
                    return self.sound.get(i - 0xFF10)
                else:
                    return 0
            elif i == 0xFF40:
                return self.lcd.LCDC.value
            elif i == 0xFF42:
                return self.lcd.SCY
            elif i == 0xFF43:
                return self.lcd.SCX
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
            return self.ram.interrupt_register[0]
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
                self.renderer.tiles_changed.add(i & 0xFFF0)
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
                self.timer.DIV = 0
            elif i == 0xFF05:
                self.timer.TIMA = value
            elif i == 0xFF06:
                self.timer.TMA = value
            elif i == 0xFF07:
                self.timer.TAC = value & 0b111
            elif 0xFF10 <= i < 0xFF40:
                if self.sound_enabled:
                    self.sound.set(i - 0xFF10, value)
            elif i == 0xFF40:
                self.lcd.LCDC.set(value)
            elif i == 0xFF42:
                self.lcd.SCY = value
            elif i == 0xFF43:
                self.lcd.SCX = value
            elif i == 0xFF46:
                self.transfer_DMA(value)
            elif i == 0xFF47:
                # TODO: Move out of MB
                self.renderer.clearcache |= self.lcd.BGP.set(value)
            elif i == 0xFF48:
                # TODO: Move out of MB
                self.renderer.clearcache |= self.lcd.OBP0.set(value)
            elif i == 0xFF49:
                # TODO: Move out of MB
                self.renderer.clearcache |= self.lcd.OBP1.set(value)
            elif i == 0xFF4A:
                self.lcd.WY = value
            elif i == 0xFF4B:
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
            self.ram.interrupt_register[0] = value
        else:
            raise Exception("Memory access violation. Tried to write: %s" % hex(i))

    def transfer_DMA(self, src):
        # http://problemkaputt.de/pandocs.htm#lcdoamdmatransfers
        # TODO: Add timing delay of 160µs and disallow access to RAM!
        dst = 0xFE00
        offset = src * 0x100
        for n in range(0xA0):
            self.setitem(dst + n, self.getitem(n + offset))
