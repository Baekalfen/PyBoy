#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pyboy
from pyboy.utils import (
    STATE_VERSION,
    PyBoyException,
    PyBoyOutOfBoundsException,
    INTR_TIMER,
    INTR_SERIAL,
    INTR_HIGHTOLOW,
    OPCODE_BRK,
    MAX_CYCLES,
)

from . import bootrom, cartridge, cpu, interaction, lcd, ram, serial, sound, timer

logger = pyboy.logging.get_logger(__name__)


class Motherboard:
    def __init__(
        self,
        gamerom,
        bootrom_file,
        color_palette,
        cgb_color_palette,
        sound_volume,
        sound_emulated,
        sound_sample_rate,
        cgb,
        randomize=False,
    ):
        if bootrom_file is not None:
            logger.info("Boot-ROM file provided")

        self.cartridge = cartridge.load_cartridge(gamerom)
        logger.debug("Cartridge started:\n%s", str(self.cartridge))

        self.bootrom = bootrom.BootROM(bootrom_file, self.cartridge.cgb)
        if self.bootrom.cgb:
            logger.debug("Boot ROM type auto-detected to %s", ("CGB" if self.bootrom.cgb else "DMG"))
            cgb = cgb or True

        if cgb is None:
            cgb = self.cartridge.cgb
            logger.debug("Cartridge type auto-detected to %s", ("CGB" if self.cartridge.cgb else "DMG"))

        self.timer = timer.Timer()
        self.serial = serial.Serial()
        self.interaction = interaction.Interaction()
        self.ram = ram.RAM(cgb, randomize=randomize)
        self.cpu = cpu.CPU(self)

        if cgb:
            self.lcd = lcd.CGBLCD(
                cgb,
                self.cartridge.cgb or self.bootrom.cgb,
                color_palette,
                cgb_color_palette,
                randomize=randomize,
            )
        else:
            self.lcd = lcd.LCD(
                cgb,
                self.cartridge.cgb or self.bootrom.cgb,
                color_palette,
                cgb_color_palette,
                randomize=randomize,
            )

        # breakpoint()
        self.sound = sound.Sound(sound_volume, sound_emulated, sound_sample_rate, cgb)

        self.key1 = 0
        self.double_speed = False
        self.cgb = cgb
        self.cartridge_cgb = self.cartridge.cgb

        if self.cgb:
            self.hdma = HDMA()
        else:
            self.hdma = None

        self.bootrom_enabled = True
        self.serialbuffer = [0] * 1024
        self.serialbuffer_count = 0

        self.breakpoints = {}  # {(0, 0x150): (0x100) (0, 0x0040): 0x200, (0, 0x0048): 0x300, (0, 0x0050): 0x44}
        self.breakpoint_singlestep = False
        self.breakpoint_singlestep_latch = False
        self.breakpoint_waiting = -1

    def switch_speed(self):
        bit0 = self.key1 & 0b1
        if bit0 == 1:
            self.double_speed = not self.double_speed
            self.lcd.tick(self.cpu.cycles)
            self.lcd.speed_shift = 1 if self.double_speed else 0
            self.sound.tick(self.cpu.cycles)
            self.sound.speed_shift = 1 if self.double_speed else 0
            logger.debug("CGB double speed is now: %d", self.double_speed)
            self.key1 ^= 0b10000001

    def breakpoint_add(self, bank, addr):
        # Replace instruction at address with OPCODE_BRK and save original opcode
        # for later reinsertion and when breakpoint is deleted.
        if addr < 0x100 and bank == -1:
            opcode = self.bootrom.bootrom[addr]
            self.bootrom.bootrom[addr] = OPCODE_BRK
        elif addr < 0x4000:
            if self.cartridge.external_rom_count < bank:
                raise PyBoyOutOfBoundsException(
                    f"ROM bank out of bounds. Asked for {bank}, max is {self.cartridge.external_rom_count}"
                )
            opcode = self.cartridge.rombanks[bank, addr]
            self.cartridge.rombanks[bank, addr] = OPCODE_BRK
        elif 0x4000 <= addr < 0x8000:
            if self.cartridge.external_rom_count < bank:
                raise PyBoyOutOfBoundsException(
                    f"ROM bank out of bounds. Asked for {bank}, max is {self.cartridge.external_rom_count}"
                )
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
                raise PyBoyOutOfBoundsException(
                    f"RAM bank out of bounds. Asked for {bank}, max is {self.cartridge.external_ram_count}"
                )
            opcode = self.cartridge.rambanks[bank, addr - 0xA000]
            self.cartridge.rambanks[bank, addr - 0xA000] = OPCODE_BRK
        elif 0xC000 <= addr <= 0xE000:
            opcode = self.ram.internal_ram0[addr - 0xC000]
            self.ram.internal_ram0[addr - 0xC000] = OPCODE_BRK
        else:
            raise PyBoyOutOfBoundsException(
                "Unsupported breakpoint address. If this a mistake, reach out to the developers"
            )

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
                raise PyBoyException("Unsupported breakpoint address. If this a mistake, reach out to the developers")
        else:
            raise PyBoyException("Breakpoint not found. If this a mistake, reach out to the developers")

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
            return  # skip
        bank = (self.breakpoint_waiting >> 24) & 0xFF
        # TODO: Improve signedness
        if bank == 0xFF:
            bank = -1
        addr = (self.breakpoint_waiting >> 8) & 0xFFFF
        logger.debug("Breakpoint reinjecting: %02x:%02x", bank, addr)
        self.breakpoint_add(bank, addr)
        self.breakpoint_waiting = -1

    def getserial(self):
        b = "".join([chr(x) for x in self.serialbuffer[: self.serialbuffer_count]])
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
        self.serial.save_state(f)
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

        if state_version < STATE_VERSION:
            logger.warning("Loading state from an older version of PyBoy. This might cause compatibility issues.")
        elif state_version > STATE_VERSION:
            raise PyBoyException("Cannot load state from a newer version of PyBoy")

        if state_version >= 8:
            self.key1 = f.read()
            self.double_speed = f.read()
            _cgb = f.read()
            if self.cgb and not _cgb:
                raise PyBoyException("Loading state which *is not* CGB-mode, but PyBoy *is* in CGB mode!")
            if not self.cgb and _cgb:
                raise PyBoyException("Loading state which *is* CGB-mode, but PyBoy *is not* in CGB mode!")

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
        if state_version >= 15:
            self.serial.load_state(f, state_version)
        f.flush()
        logger.debug("State loaded.")

    ###################################################################
    # Coordinator
    #

    def tick(self):
        while not self.lcd.frame_done:
            if self.cgb and self.hdma.transfer_active and self.lcd._STAT._mode & 0b11 == 0:
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
                        # https://gbdev.io/pandocs/STAT.html
                        # STAT (_cycles_to_interrupt) vs. VBLANK interrupt (_cycles_to_interrupt) vs. end frame (_cycles_to_frame)
                        self.lcd._cycles_to_interrupt,  # TODO: Be more agreesive. Only if actual interrupt enabled.
                        self.lcd._cycles_to_frame,
                        self.sound._cycles_to_interrupt,
                        self.serial._cycles_to_interrupt,
                        mode0_cycles,
                    ),
                )
                if self.breakpoint_singlestep:
                    cycles_target = 4
                self.cpu.tick(cycles_target)

            # TODO: Support General Purpose DMA
            # https://gbdev.io/pandocs/CGB_Registers.html#bit-7--0---general-purpose-dma

            self.sound.tick(self.cpu.cycles)

            if self.serial.tick(self.cpu.cycles):
                self.cpu.set_interruptflag(INTR_SERIAL)

            if self.timer.tick(self.cpu.cycles):
                self.cpu.set_interruptflag(INTR_TIMER)

            if lcd_interrupt := self.lcd.tick(self.cpu.cycles):
                self.cpu.set_interruptflag(lcd_interrupt)

            if self.breakpoint_singlestep:
                break

        return self.breakpoint_singlestep

    ###################################################################
    # MemoryManager
    #
    def getitem(self, i):
        if 0x0000 <= i < 0x4000:  # 16kB ROM bank #0
            if self.bootrom_enabled and (i <= 0xFF or (self.bootrom.cgb and 0x200 <= i < 0x900)):
                return self.bootrom.getitem(i)
            else:
                return self.cartridge.rombanks[self.cartridge.rombank_selected_low, i]
        elif 0x4000 <= i < 0x8000:  # 16kB switchable ROM bank
            return self.cartridge.rombanks[self.cartridge.rombank_selected, i - 0x4000]
        elif 0x8000 <= i < 0xA000:  # 8kB Video RAM
            if not self.cgb or self.lcd.vbk.active_bank == 0:
                return self.lcd.VRAM0[i - 0x8000]
            else:
                return self.lcd.VRAM1[i - 0x8000]
        elif 0xA000 <= i < 0xC000:  # 8kB switchable RAM bank
            return self.cartridge.getitem(i)
        elif 0xC000 <= i < 0xE000:  # 8kB Internal RAM
            bank_offset = 0
            if self.cgb and 0xD000 <= i:
                # Find which bank to read from at FF70
                bank = self.ram.non_io_internal_ram1[0xFF70 - 0xFF4C] & 0b111
                if bank == 0x0:
                    bank = 0x01
                bank_offset = (bank - 1) * 0x1000
            return self.ram.internal_ram0[i - 0xC000 + bank_offset]
        elif 0xE000 <= i < 0xFE00:  # Echo of 8kB Internal RAM
            # Redirect to internal RAM
            return self.getitem(i - 0x2000)
        elif 0xFE00 <= i < 0xFEA0:  # Sprite Attribute Memory (OAM)
            return self.lcd.OAM[i - 0xFE00]
        elif 0xFEA0 <= i < 0xFF00:  # Empty but unusable for I/O
            return self.ram.non_io_internal_ram0[i - 0xFEA0]
        elif 0xFF00 <= i < 0xFF4C:  # I/O ports
            if 0xFF01 <= i <= 0xFF02:
                if self.serial.tick(self.cpu.cycles):
                    self.cpu.set_interruptflag(INTR_SERIAL)
                if i == 0xFF01:
                    return self.serial.SB
                elif i == 0xFF02:
                    return self.serial.SC
            elif 0xFF04 <= i <= 0xFF07:
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
                self.sound.tick(self.cpu.cycles)
                return self.sound.get(i - 0xFF10)
            elif 0xFF40 <= i <= 0xFF4B:
                if lcd_interrupt := self.lcd.tick(self.cpu.cycles):
                    self.cpu.set_interruptflag(lcd_interrupt)

                if i == 0xFF40:
                    return self.lcd._LCDC.value
                elif i == 0xFF41:
                    return self.lcd._STAT.value
                elif i == 0xFF42:
                    return self.lcd.SCY
                elif i == 0xFF43:
                    return self.lcd.SCX
                elif i == 0xFF44:
                    return self.lcd.LY
                elif i == 0xFF45:
                    return self.lcd.LYC
                elif i == 0xFF46:
                    return 0x00  # DMA
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
        elif 0xFF4C <= i < 0xFF80:  # Empty but unusable for I/O
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
                return 0x00  # Not readable
            elif self.cgb and i == 0xFF52:
                # logger.debug("HDMA2 is not readable")
                return 0x00  # Not readable
            elif self.cgb and i == 0xFF53:
                # logger.debug("HDMA3 is not readable")
                return 0x00  # Not readable
            elif self.cgb and i == 0xFF54:
                # logger.debug("HDMA4 is not readable")
                return 0x00  # Not readable
            elif self.cgb and i == 0xFF55:
                return self.hdma.hdma5 & 0xFF
            elif self.cgb and i == 0xFF76:
                self.sound.tick(self.cpu.cycles)
                return self.sound.pcm12()
            elif self.cgb and i == 0xFF77:
                self.sound.tick(self.cpu.cycles)
                return self.sound.pcm34()
            return self.ram.non_io_internal_ram1[i - 0xFF4C]
        elif 0xFF80 <= i < 0xFFFF:  # Internal RAM
            return self.ram.internal_ram1[i - 0xFF80]
        elif i == 0xFFFF:  # Interrupt Enable Register
            return self.cpu.interrupts_enabled_register
        # else:
        #     logger.critical("Memory access violation. Tried to read: %0.4x", i)

    def setitem(self, i, value):
        if 0x0000 <= i < 0x4000:  # 16kB ROM bank #0
            # Doesn't change the data. This is for MBC commands
            self.cartridge.setitem(i, value)
            self.cpu.bail = True
        elif 0x4000 <= i < 0x8000:  # 16kB switchable ROM bank
            # Doesn't change the data. This is for MBC commands
            self.cartridge.setitem(i, value)
            self.cpu.bail = True
        elif 0x8000 <= i < 0xA000:  # 8kB Video RAM
            if not self.cgb or self.lcd.vbk.active_bank == 0:
                self.lcd.VRAM0[i - 0x8000] = value
                if i < 0x9800:  # Is within tile data -- not tile maps
                    # Mask out the byte of the tile
                    self.lcd.renderer.invalidate_tile(((i & 0xFFF0) - 0x8000) // 16, 0)
            else:
                self.lcd.VRAM1[i - 0x8000] = value
                if i < 0x9800:  # Is within tile data -- not tile maps
                    # Mask out the byte of the tile
                    self.lcd.renderer.invalidate_tile(((i & 0xFFF0) - 0x8000) // 16, 1)
        elif 0xA000 <= i < 0xC000:  # 8kB switchable RAM bank
            self.cartridge.setitem(i, value)
        elif 0xC000 <= i < 0xE000:  # 8kB Internal RAM
            bank_offset = 0
            if self.cgb and 0xD000 <= i:
                # Find which bank to read from at FF70
                bank = self.getitem(0xFF70)
                bank &= 0b111
                if bank == 0x0:
                    bank = 0x01
                bank_offset = (bank - 1) * 0x1000
            self.ram.internal_ram0[i - 0xC000 + bank_offset] = value
        elif 0xE000 <= i < 0xFE00:  # Echo of 8kB Internal RAM
            self.setitem(i - 0x2000, value)  # Redirect to internal RAM
        elif 0xFE00 <= i < 0xFEA0:  # Sprite Attribute Memory (OAM)
            self.lcd.OAM[i - 0xFE00] = value
        elif 0xFEA0 <= i < 0xFF00:  # Empty but unusable for I/O
            self.ram.non_io_internal_ram0[i - 0xFEA0] = value
        elif 0xFF00 <= i < 0xFF4C:  # I/O ports
            if i == 0xFF00:
                self.ram.io_ports[i - 0xFF00] = self.interaction.pull(value)
            elif 0xFF01 <= i <= 0xFF02:
                if self.serial.tick(self.cpu.cycles):
                    self.cpu.set_interruptflag(INTR_SERIAL)
                if i == 0xFF01:
                    self.serialbuffer[self.serialbuffer_count] = value
                    self.serialbuffer_count += 1
                    self.serialbuffer_count &= 0x3FF
                    self.serial.set_SB(value)
                elif i == 0xFF02:
                    self.serial.set_SC(value)
            elif 0xFF04 <= i <= 0xFF07:
                if self.timer.tick(self.cpu.cycles):
                    self.cpu.set_interruptflag(INTR_TIMER)

                if i == 0xFF04:
                    # Pan docs:
                    # “DIV-APU” ... is increased every time DIV’s bit 4 (5 in double-speed mode) goes from 1 to 0 ...
                    # the counter can be made to increase faster by writing to DIV while its relevant bit is set (which
                    # clears DIV, and triggers the falling edge).
                    if self.timer.DIV & (0b1_0000 << self.sound.speed_shift):
                        self.sound.tick(self.cpu.cycles)  # Process outstanding cycles
                        # TODO: Force a falling edge tick
                        self.sound.reset_apu_div()

                    self.timer.reset()
                elif i == 0xFF05:
                    self.timer.TIMA = value
                elif i == 0xFF06:
                    self.timer.TMA = value
                elif i == 0xFF07:
                    self.timer.TAC = value & 0b111  # TODO: Move logic to Timer class
            elif i == 0xFF0F:
                self.cpu.interrupts_flag_register = value
            elif 0xFF10 <= i < 0xFF40:
                self.sound.tick(self.cpu.cycles)
                self.sound.set(i - 0xFF10, value)
            elif 0xFF40 <= i <= 0xFF4B:
                if lcd_interrupt := self.lcd.tick(self.cpu.cycles):
                    self.cpu.set_interruptflag(lcd_interrupt)

                if i == 0xFF40:
                    self.lcd.set_lcdc(value)
                elif i == 0xFF41:
                    self.lcd._STAT.set(value)
                elif i == 0xFF42:
                    self.lcd.SCY = value
                elif i == 0xFF43:
                    self.lcd.SCX = value
                elif i == 0xFF44:
                    # LCDC Read-only
                    return
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
        elif 0xFF4C <= i < 0xFF80:  # Empty but unusable for I/O
            if self.bootrom_enabled and i == 0xFF50 and (value == 0x1 or value == 0x11):
                logger.debug("Bootrom disabled!")
                self.bootrom_enabled = False
                self.cpu.bail = True
            # CGB registers
            elif self.cgb and i == 0xFF4D:
                self.key1 = value
                self.cpu.bail = True
            elif self.cgb and i == 0xFF4F:
                self.lcd.vbk.set(value)
            elif self.cgb and i == 0xFF51:
                self.hdma.hdma1 = value
            elif self.cgb and i == 0xFF52:
                self.hdma.hdma2 = value  # & 0xF0
            elif self.cgb and i == 0xFF53:
                self.hdma.hdma3 = value  # & 0x1F
            elif self.cgb and i == 0xFF54:
                self.hdma.hdma4 = value  # & 0xF0
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
        elif 0xFF80 <= i < 0xFFFF:  # Internal RAM
            self.ram.internal_ram1[i - 0xFF80] = value
        elif i == 0xFFFF:  # Interrupt Enable Register
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
                self.hdma5 = 0xFF  # (value & 0x7F) | 0x80 #0xFF
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

        return 206  # TODO: adjust for double speed
