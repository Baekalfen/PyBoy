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
        sound_emulated,
        cgb,
        randomize=False,
    ):
        if bootrom_file is not None:
            logger.info("Boot-ROM file provided")

        self.cartridge = cartridge.load_cartridge(gamerom_file)
        if cgb is None:
            cgb = self.cartridge.cgb
            logger.debug(f'Cartridge type auto-detected to {"CGB" if cgb else "DMG"}')

        self.timer = timer.Timer()
        self.interaction = interaction.Interaction()
        self.bootrom = bootrom.BootROM(bootrom_file, cgb)
        self.ram = ram.RAM(cgb, randomize=randomize)
        self.cpu = cpu.CPU(self)

        if cgb:
            self.lcd = lcd.CGBLCD(
                cgb,
                self.cartridge.cgb,
                disable_renderer,
                color_palette,
                randomize=randomize,
            )
        else:
            self.lcd = lcd.LCD(
                cgb,
                self.cartridge.cgb,
                disable_renderer,
                color_palette,
                randomize=randomize,
            )

        # QUIRK: Force emulation of sound (muted)
        sound_emulated |= self.cartridge.gamename == "ZELDA DIN"
        self.sound = sound.Sound(sound_enabled, sound_emulated)

        self.key1 = 0
        self.double_speed = False
        self.cgb = cgb

        if self.cgb:
            self.hdma = HDMA()

        # self.disable_renderer = disable_renderer

        self.bootrom_enabled = True
        self.serialbuffer = ""

        self.breakpoints_enabled = False # breakpoints_enabled
        self.breakpoints_list = [] #[(0, 0x150), (0, 0x0040), (0, 0x0048), (0, 0x0050)]
        self.breakpoint_latch = 0

    def switch_speed(self):
        bit0 = self.key1 & 0b1
        if bit0 == 1:
            self.double_speed = not self.double_speed
            self.lcd.double_speed = self.double_speed
            self.key1 ^= 0b10000001

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
            logger.debug(f"State version: {state_version}")
            # From version 2 and above, this is the version number
            self.bootrom_enabled = f.read()
        else:
            logger.debug(f"State version: 0-1")
            # HACK: The byte wasn't a state version, but the bootrom flag
            self.bootrom_enabled = state_version
        if state_version >= 8:
            self.key1 = f.read()
            self.double_speed = f.read()
            _cgb = f.read()
            if self.cgb != _cgb:
                logger.critical(f"Loading state which is not CGB, but PyBoy is loaded in CGB mode!")
                return
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
        while self.lcd.processing_frame():
            if self.cgb and self.hdma.transfer_active and self.lcd._STAT._mode & 0b11 == 0:
                cycles = self.hdma.tick(self)
            else:
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

                cycles = min(
                    self.lcd.cycles_to_interrupt(),
                    self.timer.cycles_to_interrupt(),
                    # self.serial.cycles_to_interrupt(),
                    mode0_cycles
                )

            #TODO: Support General Purpose DMA
            # https://gbdev.io/pandocs/CGB_Registers.html#bit-7--0---general-purpose-dma

            # TODO: Unify interface
            if self.cgb and self.double_speed:
                self.sound.clock += cycles // 2
            else:
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
        self.sound.sync()

        return False

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
                # logger.error("HDMA1 is not readable")
                return 0x00 # Not readable
            elif self.cgb and i == 0xFF52:
                # logger.error("HDMA2 is not readable")
                return 0x00 # Not readable
            elif self.cgb and i == 0xFF53:
                # logger.error("HDMA3 is not readable")
                return 0x00 # Not readable
            elif self.cgb and i == 0xFF54:
                # logger.error("HDMA4 is not readable")
                return 0x00 # Not readable
            elif self.cgb and i == 0xFF55:
                return self.hdma.hdma5 & 0xFF
            return self.ram.non_io_internal_ram1[i - 0xFF4C]
        elif 0xFF80 <= i < 0xFFFF: # Internal RAM
            return self.ram.internal_ram1[i - 0xFF80]
        elif i == 0xFFFF: # Interrupt Enable Register
            return self.cpu.interrupts_enabled_register
        # else:
        #     raise IndexError("Memory access violation. Tried to read: %s" % hex(i))

    def setitem(self, i, value):
        # assert 0 <= value < 0x100, "Memory write error! Can't write %s to %s" % (hex(value), hex(i))

        if 0x0000 <= i < 0x4000: # 16kB ROM bank #0
            # Doesn't change the data. This is for MBC commands
            self.cartridge.setitem(i, value)
        elif 0x4000 <= i < 0x8000: # 16kB switchable ROM bank
            # Doesn't change the data. This is for MBC commands
            self.cartridge.setitem(i, value)
        elif 0x8000 <= i < 0xA000: # 8kB Video RAM
            if not self.cgb or self.lcd.vbk.active_bank == 0:
                self.lcd.VRAM0[i - 0x8000] = value
                if i < 0x9800: # Is within tile data -- not tile maps
                    # Mask out the byte of the tile
                    self.lcd.renderer.invalidate_tile(((i & 0xFFF0) - 0x8000) // 16, 0)
                    # self.lcd.renderer.tiles_changed0.add(i & 0xFFF0)
            else:
                self.lcd.VRAM1[i - 0x8000] = value
                if i < 0x9800: # Is within tile data -- not tile maps
                    # Mask out the byte of the tile
                    self.lcd.renderer.invalidate_tile(((i & 0xFFF0) - 0x8000) // 16, 1)
                    # self.lcd.renderer.tiles_changed1.add(i & 0xFFF0)
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
        elif 0xFF4C <= i < 0xFF80: # Empty but unusable for I/O
            if self.bootrom_enabled and i == 0xFF50 and (value == 0x1 or value == 0x11):
                # logger.debug("Bootrom disabled!")
                self.bootrom_enabled = False
            # CGB registers
            elif self.cgb and i == 0xFF4D:
                self.key1 = value
            elif self.cgb and i == 0xFF4F:
                self.lcd.vbk.set(value)
            elif self.cgb and i == 0xFF51:
                # if 0x7F < value < 0xA0:
                #     value = 0
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
        elif 0xFF80 <= i < 0xFFFF: # Internal RAM
            self.ram.internal_ram1[i - 0xFF80] = value
        elif i == 0xFFFF: # Interrupt Enable Register
            self.cpu.interrupts_enabled_register = value
        # else:
        #     raise Exception("Memory access violation. Tried to write: %s" % hex(i))

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
                # self.curr_dst += bytes_to_transfer
                # self.curr_src += bytes_to_transfer

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
