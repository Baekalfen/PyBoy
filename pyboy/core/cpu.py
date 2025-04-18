#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import pyboy

from . import opcodes
from pyboy.utils import INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW

FLAGC, FLAGH, FLAGN, FLAGZ = range(4, 8)


logger = pyboy.logging.get_logger(__name__)


class CPU:
    def __init__(self, mb):
        self.A = 0
        self.F = 0
        self.B = 0
        self.C = 0
        self.D = 0
        self.E = 0
        self.HL = 0
        self.SP = 0
        self.PC = 0

        self.interrupts_flag_register = 0
        self.interrupts_enabled_register = 0
        self.interrupt_master_enable = False
        self.interrupt_queued = False

        self.mb = mb

        self.halted = False
        self.stopped = False
        self.is_stuck = False
        self.cycles = 0

    def save_state(self, f):
        for n in [self.A, self.F, self.B, self.C, self.D, self.E]:
            f.write(n & 0xFF)

        for n in [self.HL, self.SP, self.PC]:
            f.write_16bit(n)

        f.write(self.interrupt_master_enable)
        f.write(self.halted)
        f.write(self.stopped)
        f.write(self.interrupts_enabled_register)
        f.write(self.interrupt_queued)
        f.write(self.interrupts_flag_register)
        f.write_64bit(self.cycles)

    def load_state(self, f, state_version):
        self.A, self.F, self.B, self.C, self.D, self.E = [f.read() for _ in range(6)]
        self.HL = f.read_16bit()
        self.SP = f.read_16bit()
        self.PC = f.read_16bit()

        self.interrupt_master_enable = f.read()
        self.halted = f.read()
        self.stopped = f.read()
        if state_version >= 5:
            # Interrupt register moved from RAM to CPU
            self.interrupts_enabled_register = f.read()
        if state_version >= 8:
            self.interrupt_queued = f.read()
            self.interrupts_flag_register = f.read()
        if state_version >= 12:
            self.cycles = f.read_64bit()
        logger.debug("State loaded: %s", self.dump_state(""))

    def dump_state(self, sym_label):
        opcode_data = [
            self.mb.getitem(self.mb.cpu.PC + n) for n in range(3)
        ]  # Max 3 length, then we don't need to backtrack

        opcode = opcode_data[0]
        opcode_length = opcodes.OPCODE_LENGTHS[opcode]
        opcode_str = f"Opcode: [{opcodes.CPU_COMMANDS[opcode]}]"
        if opcode == 0xCB:
            opcode_str += f" {opcodes.CPU_COMMANDS[opcode_data[1]+0x100]}"
        else:
            opcode_str += " " + " ".join(f"{d:02X}" for d in opcode_data[1:opcode_length])

        return (
            "\n"
            f"A: {self.mb.cpu.A:02X}, F: {self.mb.cpu.F:02X}, B: {self.mb.cpu.B:02X}, "
            f"C: {self.mb.cpu.C:02X}, D: {self.mb.cpu.D:02X}, E: {self.mb.cpu.E:02X}, "
            f"HL: {self.mb.cpu.HL:04X}, SP: {self.mb.cpu.SP:04X}, PC: {self.mb.cpu.PC:04X} ({sym_label})\n"
            f"{opcode_str} "
            f"Interrupts - IME: {self.mb.cpu.interrupt_master_enable}, "
            f"IE: {self.mb.cpu.interrupts_enabled_register:08b}, "
            f"IF: {self.mb.cpu.interrupts_flag_register:08b}\n"
            f"LCD Intr.: {self.mb.lcd._cycles_to_interrupt}, LY:{self.mb.lcd.LY}, LYC:{self.mb.lcd.LYC}\n"
            f"Timer Intr.: {self.mb.timer._cycles_to_interrupt}\n"
            f"Sound: PCM12:{self.mb.sound.pcm12():02X}, PCM34:{self.mb.sound.pcm34():02X}\n"
            f"Sound CH1: \n"
            f"sound_period: {self.mb.sound.sweepchannel.sound_period}\n"
            f"length_enable: {self.mb.sound.sweepchannel.length_enable}\n"
            f"enable: {self.mb.sound.sweepchannel.enable}\n"
            f"lengthtimer: {self.mb.sound.sweepchannel.lengthtimer}\n"
            f"envelopetimer: {self.mb.sound.sweepchannel.envelopetimer}\n"
            f"periodtimer: {self.mb.sound.sweepchannel.periodtimer}\n"
            f"period: {self.mb.sound.sweepchannel.period}\n"
            f"waveframe: {self.mb.sound.sweepchannel.waveframe}\n"
            f"volume: {self.mb.sound.sweepchannel.volume}\n"
            f"halted:{self.halted}, "
            f"interrupt_queued:{self.interrupt_queued}, "
            f"stopped:{self.stopped}\n"
            f"cycles:{self.cycles}\n"
        )

    def set_interruptflag(self, flag):
        self.interrupts_flag_register |= flag

    def tick(self, cycles_target):
        _cycles0 = self.cycles
        _target = _cycles0 + cycles_target

        if self.check_interrupts():
            self.halted = False
            # TODO: Cycles it took to handle the interrupt

        if self.halted and self.interrupt_queued:
            # GBCPUman.pdf page 20
            # WARNING: The instruction immediately following the HALT instruction is "skipped" when interrupts are
            # disabled (DI) on the GB,GBP, and SGB.
            self.halted = False
            self.PC += 1
            self.PC &= 0xFFFF
        elif self.halted:
            self.cycles += cycles_target  # TODO: Number of cycles for a HALT in effect?
        self.interrupt_queued = False

        self.bail = False
        while self.cycles < _target:
            # TODO: cpu-stuck check for blargg tests?
            self.fetch_and_execute()
            if self.bail:  # Possible cycles-target changes
                break

    def check_interrupts(self):
        if self.interrupt_queued:
            # Interrupt already queued. This happens only when using a debugger.
            return False

        raised_and_enabled = (self.interrupts_flag_register & 0b11111) & (self.interrupts_enabled_register & 0b11111)
        if raised_and_enabled:
            # Clear interrupt flag
            if self.halted:
                self.PC += 1  # Escape HALT on return
                self.PC &= 0xFFFF

            if self.interrupt_master_enable:
                if raised_and_enabled & INTR_VBLANK:
                    self.handle_interrupt(INTR_VBLANK, 0x0040)
                elif raised_and_enabled & INTR_LCDC:
                    self.handle_interrupt(INTR_LCDC, 0x0048)
                elif raised_and_enabled & INTR_TIMER:
                    self.handle_interrupt(INTR_TIMER, 0x0050)
                elif raised_and_enabled & INTR_SERIAL:
                    self.handle_interrupt(INTR_SERIAL, 0x0058)
                elif raised_and_enabled & INTR_HIGHTOLOW:
                    self.handle_interrupt(INTR_HIGHTOLOW, 0x0060)
            self.interrupt_queued = True
            return True
        else:
            self.interrupt_queued = False
        return False

    def handle_interrupt(self, flag, addr):
        self.interrupts_flag_register ^= flag  # Remove flag
        self.mb.setitem((self.SP - 1) & 0xFFFF, self.PC >> 8)  # High
        self.mb.setitem((self.SP - 2) & 0xFFFF, self.PC & 0xFF)  # Low
        self.SP -= 2
        self.SP &= 0xFFFF

        self.PC = addr
        self.interrupt_master_enable = False

    def fetch_and_execute(self):
        opcode = self.mb.getitem(self.PC)
        if opcode == 0xCB:  # Extension code
            opcode = self.mb.getitem(self.PC + 1)
            opcode += 0x100  # Internally shifting look-up table

        return opcodes.execute_opcode(self, opcode)
