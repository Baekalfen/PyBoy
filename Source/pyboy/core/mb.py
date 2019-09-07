#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.logger import logger
from . import bootrom, cartridge, cpu, interaction, lcd, ram, timer

VBLANK, LCDC, TIMER, SERIAL, HIGHTOLOW = range(5)
STAT, _, _, LY, LYC = range(0xFF41, 0xFF46)


class Motherboard:
    def __init__(self, gamerom_file, bootrom_file, window, profiling=False):
        if bootrom_file is not None:
            logger.info("Boot-ROM file provided")

        if profiling:
            logger.info("Profiling enabled")

        self.window = window
        self.timer = timer.Timer()
        self.interaction = interaction.Interaction()
        self.cartridge = cartridge.Cartridge(gamerom_file)
        self.bootrom = bootrom.BootROM(bootrom_file)
        self.ram = ram.RAM(random=False)
        self.cpu = cpu.CPU(self, profiling)
        self.lcd = lcd.LCD(window.color_palette)
        self.bootrom_enabled = True
        self.serialbuffer = u''

    def getserial(self):
        b = self.serialbuffer
        self.serialbuffer = u''
        return b

    def buttonevent(self, key):
        if self.interaction.key_event(key):
            self.cpu.set_interruptflag(HIGHTOLOW)

    def stop(self, save):
        self.window.stop()
        if save:
            self.cartridge.stop()

    def save_state(self, f):
        logger.info("Saving state...")
        f.write(self.bootrom_enabled.to_bytes(1, 'little'))
        self.cpu.save_state(f)
        self.lcd.save_state(f)
        self.ram.save_state(f)
        self.cartridge.save_state(f)
        logger.info("State saved.")

    def load_state(self, f):
        logger.info("Loading state...")
        self.bootrom_enabled = ord(f.read(1))
        self.cpu.load_state(f)
        self.lcd.load_state(f)
        self.ram.load_state(f)
        self.cartridge.load_state(f)
        logger.info("State loaded.")

        self.window.clearcache = True
        self.window.update_cache(self.lcd)

    ###################################################################
    # Coordinator
    #
    def set_STAT_mode(self, mode):
        self.setitem(STAT, self.getitem(STAT) & 0b11111100) # Clearing 2 LSB
        self.setitem(STAT, self.getitem(STAT) | mode) # Apply mode to LSB

        # Mode "3" is not interruptable
        if self.cpu.test_ramregisterflag(STAT, mode + 3) and mode != 3:
            self.cpu.set_interruptflag(LCDC)

    def check_LYC(self, y):
        self.setitem(LY, y)
        if self.getitem(LYC) == y:
            self.setitem(STAT, self.getitem(STAT) | 0b100) # Sets the LYC flag
            if self.getitem(STAT) & 0b01000000:
                self.cpu.set_interruptflag(LCDC)
        else:
            self.setitem(STAT, self.getitem(STAT) & 0b11111011)

    def calculate_cycles(self, x):
        while x > 0:
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
                cycles = min(self.timer.cyclestointerrupt(), x)

                # Profiling
                if self.cpu.profiling:
                    self.cpu.hitrate[0x76] += cycles//4

            x -= cycles
            if self.timer.tick(cycles):
                self.cpu.set_interruptflag(TIMER)

    def tickframe(self):
        lcdenabled = self.lcd.LCDC.lcd_enable
        if lcdenabled:
            self.window.update_cache(self.lcd)

            # TODO: the 19, 41 and 49._ticks should correct for longer instructions
            # Iterate the 144 lines on screen
            for y in range(144):
                self.check_LYC(y)

                # Mode 2
                self.set_STAT_mode(2)
                self.calculate_cycles(80)

                # Mode 3
                self.set_STAT_mode(3)
                self.calculate_cycles(170)
                self.window.scanline(y, self.lcd)

                # Mode 0
                self.set_STAT_mode(0)
                self.calculate_cycles(206)

            self.cpu.set_interruptflag(VBLANK)
            self.window.render_screen(self.lcd)

            # Wait for next frame
            for y in range(144, 154):
                self.check_LYC(y)

                # Mode 1
                self.set_STAT_mode(1)
                self.calculate_cycles(456)
        else:
            # https://www.reddit.com/r/EmuDev/comments/6r6gf3
            # TODO: What happens if LCD gets turned on/off mid-cycle?
            self.window.blank_screen()
            self.set_STAT_mode(0)
            self.setitem(LY, 0)

            for y in range(154):
                self.calculate_cycles(456)

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
            return self.ram.internal_ram1[i-0xFF80]
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
                self.window.tiles_changed.add(i & 0xFFF0)
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
            elif i == 0xFF40:
                self.lcd.LCDC.set(value)
            elif i == 0xFF42:
                self.lcd.SCY = value
            elif i == 0xFF43:
                self.lcd.SCX = value
            elif i == 0xFF46:
                self.transfer_DMA(value)
            elif i == 0xFF47:
                self.window.clearcache |= self.lcd.BGP.set(value)
            elif i == 0xFF48:
                self.window.clearcache |= self.lcd.OBP0.set(value)
            elif i == 0xFF49:
                self.window.clearcache |= self.lcd.OBP1.set(value)
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
            self.ram.internal_ram1[i-0xFF80] = value
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
