#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import array

from . import opcodes


FLAGC, FLAGH, FLAGN, FLAGZ = range(4, 8)
VBLANK, LCDC, TIMER, SERIAL, HIGHTOLOW = range(5)
IF_ADDRESS = 0xFF0F
IE_ADDRESS = 0xFFFF


class CPU():
    def setBC(self, x):
        assert x <= 0xFFFF, "%0.4x" % x
        self.B = x >> 8
        self.C = x & 0x00FF

    def setDE(self, x):
        assert x <= 0xFFFF, "%0.4x" % x
        self.D = x >> 8
        self.E = x & 0x00FF

    # CPU Flags
    def test_flag(self, flag):
        return (self.F & (1 << flag)) != 0

    def set_flag(self, flag, value=True):
        self.F = (self.F & (0xFF - (1 << flag)))
        if value:
            self.F = (self.F + (1 << flag))

    def clear_flag(self, flag):
        self.F = (self.F & (0xFF - (1 << flag)))

    # Interrupt flags
    def set_interruptflag(self, flag):
        self.motherboard.setitem(IF_ADDRESS, self.motherboard.getitem(IF_ADDRESS) | (1 << flag))

    def test_ramregisterflag(self, address, flag):
        v = self.motherboard.getitem(address)
        return (v & (1 << flag))

    def set_ramregisterflag(self, address, flag, value=True):
        self.clear_ramregisterflag(address, flag)
        # self.motherboard.setitem(address, (self.motherboard.getitem(address) & (0xFF - (1 << flag))))
        # if value:
        self.motherboard.setitem(address, (self.motherboard.getitem(address) + (value << flag)))

    def clear_ramregisterflag(self, address, flag):
        self.motherboard.setitem(address, (self.motherboard.getitem(address) & (0xFF - (1 << flag))))

    def test_ramregisterflag_enabled(self, address, flag):
        v = self.motherboard.getitem(address)
        return (v & (1 << flag))

    def test_interrupt(self, if_v, ie_v, flag):
        intr_flag_enabled = (ie_v & (1 << flag))
        intr_flag = (if_v & (1 << flag))

        if intr_flag_enabled and intr_flag:

            # Clear interrupt flag
            self.motherboard.setitem(0xFF0F, self.motherboard.getitem(0xFF0F) & (0xFF - (1 << flag)))

            self.interruptmasterenable = False
            if self.halted:
                self.PC += 1  # Escape HALT on return

            self.motherboard.setitem(self.SP-1, self.PC >> 8) # High
            self.motherboard.setitem(self.SP-2, self.PC & 0xFF) # Low
            self.SP -= 2

            return True
        return False

    def checkforinterrupts(self):
        # GPCPUman.pdf p. 40 about priorities
        # If an interrupt occours, the PC is pushed to the stack.
        # It is up to the interrupt routine to return it.
        if not self.interruptmasterenable:
            return False

        # 0xFF0F (IF_address) - Bit 0-4 Requested interrupts
        if_v = self.motherboard.getitem(IF_ADDRESS)
        # 0xFFFF (IE_address) - Bit 0-4 Enabling interrupt vectors
        ie_v = self.motherboard.getitem(IE_ADDRESS)

        # Better to make a long check, than run through 5 if statements
        if ((if_v & 0b11111) & (ie_v & 0b11111)) != 0:
            if self.test_interrupt(if_v, ie_v, VBLANK):
                self.PC = 0x0040
                return True
            elif self.test_interrupt(if_v, ie_v, LCDC):
                self.PC = 0x0048
                return True
            elif self.test_interrupt(if_v, ie_v, TIMER):
                self.PC = 0x0050
                return True
            elif self.test_interrupt(if_v, ie_v, SERIAL):
                self.PC = 0x0058
                return True
            elif self.test_interrupt(if_v, ie_v, HIGHTOLOW):
                self.PC = 0x0060
                return True
        return False

    def fC(self):
        return (self.F & (1 << FLAGC)) != 0

    def fH(self):
        return (self.F & (1 << FLAGH)) != 0

    def fN(self):
        return (self.F & (1 << FLAGN)) != 0

    def fZ(self):
        return (self.F & (1 << FLAGZ)) != 0

    def fNC(self):
        return (self.F & (1 << FLAGC)) == 0

    def fNZ(self):
        return (self.F & (1 << FLAGZ)) == 0

    def __init__(self, motherboard, profiling=False):
        self.A = 0
        self.F = 0
        self.B = 0
        self.C = 0
        self.D = 0
        self.E = 0
        self.HL = 0
        self.SP = 0
        self.PC = 0

        self.motherboard = motherboard

        self.interruptmasterenable = False

        self.breakAllow = True
        self.breakOn = False
        self.breakNext = 0

        self.halted = False
        self.stopped = False

        # Profiling
        self.profiling = profiling
        if profiling:
            self.hitrate = array.array('L', [0] * 512)

    def save_state(self, f):
        for n in [self.A, self.F, self.B, self.C, self.D, self.E]:
            f.write((n & 0xFF).to_bytes(1, 'little'))

        for n in [self.HL, self.SP, self.PC]:
            f.write((n & 0xFF).to_bytes(1, 'little'))
            f.write(((n & 0xFF00) >> 8).to_bytes(1, 'little'))

        f.write(self.interruptmasterenable.to_bytes(1, 'little'))
        f.write(self.halted.to_bytes(1, 'little'))
        f.write(self.stopped.to_bytes(1, 'little'))

    def load_state(self, f):
        self.A, self.F, self.B, self.C, self.D, self.E = [ord(f.read(1)) for _ in range(6)]
        self.HL, self.SP, self.PC = [ord(f.read(1)) | (ord(f.read(1)) << 8) for _ in range(3)]

        self.interruptmasterenable = ord(f.read(1))
        self.halted = ord(f.read(1))
        self.stopped = ord(f.read(1))

    def fetch_and_execute(self, pc):
        opcode = self.motherboard.getitem(pc)
        if opcode == 0xCB:  # Extension code
            pc += 1
            opcode = self.motherboard.getitem(pc)
            opcode += 0x100  # Internally shifting look-up table

        # Profiling
        if self.profiling:
            self.hitrate[opcode] += 1

        return opcodes.execute_opcode(self, opcode)

    def tick(self):
        # "The interrupt will be acknowledged during opcode fetch
        # period of each instruction."
        did_interrupt = self.checkforinterrupts()

        if self.halted and did_interrupt:
            # GBCPUman.pdf page 20
            # WARNING: The instruction immediately following the HALT
            # instruction is "skipped" when interrupts are disabled
            # (DI) on the GB,GBP, and SGB.
            self.halted = False
        elif self.halted:
            return -1

        return self.fetch_and_execute(self.PC)
