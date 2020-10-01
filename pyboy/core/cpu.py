#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import array
import logging

from . import opcodes

FLAGC, FLAGH, FLAGN, FLAGZ = range(4, 8)
INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW = [1 << x for x in range(5)]

logger = logging.getLogger(__name__)


class CPU:
    def set_bc(self, x):
        self.B = x >> 8
        self.C = x & 0x00FF

    def set_de(self, x):
        self.D = x >> 8
        self.E = x & 0x00FF

    def f_c(self):
        return (self.F & (1 << FLAGC)) != 0

    def f_h(self):
        return (self.F & (1 << FLAGH)) != 0

    def f_n(self):
        return (self.F & (1 << FLAGN)) != 0

    def f_z(self):
        return (self.F & (1 << FLAGZ)) != 0

    def f_nc(self):
        return (self.F & (1 << FLAGC)) == 0

    def f_nz(self):
        return (self.F & (1 << FLAGZ)) == 0

    def __init__(self, mb, profiling=False):
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

        # Profiling
        self.profiling = profiling
        if profiling:
            self.hitrate = array.array("L", [0] * 512)

    def save_state(self, f):
        for n in [self.A, self.F, self.B, self.C, self.D, self.E]:
            f.write(n & 0xFF)

        for n in [self.HL, self.SP, self.PC]:
            f.write_16bit(n)

        f.write(self.interrupt_master_enable)
        f.write(self.halted)
        f.write(self.stopped)
        f.write(self.interrupts_enabled_register)

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
        logger.debug("State loaded: " + self.dump_state())

    def dump_state(self):
        return (
            f"A:{self.A:02x}, F:{self.F:02x}, B:{self.B:02x}, C:{self.C:02x}, D:{self.D:02x}, E:{self.E:02x}, "
            f"HL:{self.HL:02x}, SP:{self.SP:02x}, PC:{self.PC:02x}, "
            f"Opcode:{self.mb.getitem(self.PC):02x}, "
            f"Opcode+1:{self.mb.getitem((self.PC+1) & 0xFFFF):02x}, "
            f"Opcode+2:{self.mb.getitem((self.PC+2) & 0xFFFF):02x}, "
            f"IME:{self.interrupt_master_enable}, halted:{self.halted}, "
            f"interrupt_queued:{self.interrupt_queued} "
            f"stopped:{self.stopped}"
        )

    def set_interruptflag(self, flag):
        self.interrupts_flag_register |= flag

    def tick(self):
        if self.check_interrupts():
            self.halted = False
            # TODO: We return with the cycles it took to handle the interrupt
            return 0

        if self.halted and self.interrupt_queued:
            # GBCPUman.pdf page 20
            # WARNING: The instruction immediately following the HALT instruction is "skipped" when interrupts are
            # disabled (DI) on the GB,GBP, and SGB.
            self.halted = False
            self.PC += 1
            self.PC &= 0xFFFF
        elif self.halted:
            return 4 # TODO: Number of cycles for a HALT in effect?

        old_pc = self.PC
        cycles = self.fetch_and_execute(self.PC)
        if not self.halted and old_pc == self.PC:
            raise Exception("CPU is stuck: " + self.dump_state())
        self.interrupt_queued = False
        return cycles

    def check_interrupts(self):
        if self.interrupt_queued:
            # Interrupt already queued. This happens only when using a debugger.
            return False

        if (self.interrupts_flag_register & 0b11111) & (self.interrupts_enabled_register & 0b11111):
            if self.handle_interrupt(INTR_VBLANK, 0x0040):
                self.interrupt_queued = True
            elif self.handle_interrupt(INTR_LCDC, 0x0048):
                self.interrupt_queued = True
            elif self.handle_interrupt(INTR_TIMER, 0x0050):
                self.interrupt_queued = True
            elif self.handle_interrupt(INTR_SERIAL, 0x0058):
                self.interrupt_queued = True
            elif self.handle_interrupt(INTR_HIGHTOLOW, 0x0060):
                self.interrupt_queued = True
            else:
                logger.error("No interrupt triggered, but it should!")
                self.interrupt_queued = False
            return True
        else:
            self.interrupt_queued = False
        return False

    def handle_interrupt(self, flag, addr):
        if (self.interrupts_enabled_register & flag) and (self.interrupts_flag_register & flag):
            # Clear interrupt flag
            if self.halted:
                self.PC += 1 # Escape HALT on return
                self.PC &= 0xFFFF

            # Handle interrupt vectors
            if self.interrupt_master_enable:
                self.interrupts_flag_register ^= flag # Remove flag
                self.mb.setitem((self.SP - 1) & 0xFFFF, self.PC >> 8) # High
                self.mb.setitem((self.SP - 2) & 0xFFFF, self.PC & 0xFF) # Low
                self.SP -= 2
                self.SP &= 0xFFFF

                self.PC = addr
                self.interrupt_master_enable = False

            return True
        return False

    def fetch_and_execute(self, pc):
        opcode = self.mb.getitem(pc)
        if opcode == 0xCB: # Extension code
            pc += 1
            opcode = self.mb.getitem(pc)
            opcode += 0x100 # Internally shifting look-up table

        # Profiling
        if self.profiling:
            self.hitrate[opcode] += 1

        return opcodes.execute_opcode(self, opcode)
