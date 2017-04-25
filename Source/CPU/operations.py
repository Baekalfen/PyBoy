# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# from opcodes import Z, NZ, NC, N
import CoreDump
from flags import flagZ, flagN, flagH, flagC
from registers import SP, A  # No need to use as self.<reg>
from MathUint8 import resetBit, setBit, getBit, swap, lshift, rshift, lrotate_inC, lrotate_thruC, rrotate_inC, rrotate_thruC, getSignedInt8

from GbLogger import gblogger


def CPU_EI(self):
    # Enable interrupts. This intruction enables interrupts but not immediately. Interrupts are enabled after instruction after EI is executed
    # gblogger.info("Enabling interrupts")
    self.interruptMasterEnableLatch = True


def CPU_STOP(self):
    self.stopped = True
    coredump(Exception("STOP is not implemented yet"))


def CPU_HALT(self):
    # GPCPUman.pdf p. 19
    # The CPU will remain suspended until an interrupt occurs, at which point the interrupt
    # is serviced and then the instruction immediately following the HALT is executed.
    # If interrupts are disabled (DI) then halt doesn't suspend operation but it does cause
    # the program counter to stop counting for one instruction on the GB,GBP, and SGB as mentioned below.

    self.halted = True


def CPU_LDD(self, r0, r1):
    # Split instruction into two parts (LD (HL),A and DEC HL)
    r0.setInt(r1)
    self.executeInstruction((self.opcodes[0x2B][2], (0,), (self, None, newPC)))


def CPU_LDHL(self, r0, r1):
    # Split instruction into two parts (LD (HL),A and DEC HL)
    r0.setInt(r1)
    self.executeInstruction((self.opcodes[0x2B][2], (0,), (self, None, newPC)))


def CPU_LDI(self):
    # LD A,(HL) - INC HL
    # LD (HL),A - INC HL

    opcode = hex(0)  # The opcode is irrelevant
    operands = inst.operands
    variable = inst.variable

    # gblogger.info("(Will be split into LD (HL), A and - INC HL)")

    # Split instruction into two parts (LD (HL),A and INC HL)
    instA = Instruction(opcode,
                        opcodes.LD,
                        operands,
                        variable,
                        0,
                        0,
                        0x77)

    instB = Instruction(opcode,
                        opcodes.INC,
                        (operands[1],),
                        variable,
                        0,
                        0,
                        0x2C)

    self.executeToken(instA)
    self.executeToken(instB)


def CPU_INC8(self, r0):
    result = (r0 + 1) & 0xFF

    # gblogger.info(flagZ, result == 0)
    self.setFlag(flagZ, result == 0)
    self.setFlag(flagN, False)
    self.setFlag(flagH, (getBit(r0, 3) == 1) and (getBit(result, 3) == 0))

    return result


def CPU_INC16(self, r0):
    #Flags not affected! GBCPUman.pdf p.92
    result = (r0 + 1) & 0xFFFF
    return result


def CPU_DEC8(self, r0):
    result = (r0 - 1)

    self.setFlag(flagZ, result & 0xFF == 0)
    self.setFlag(flagN, True)
    self.setFlag(flagH, getBit(r0, 4) == 1 and getBit(result, 4) == 0)

    return result & 0xFF


def CPU_DEC16(self, r0):
    #Flags not affected! GBCPUman.pdf p.93
    result = (r0 - 1) & 0xFFFF
    return result


def CPU_ADD8(self, r0, r1):
    result = r0 + r1

    self.setFlag(flagZ, result & 0xFF == 0)
    self.setFlag(flagN, 0)
    self.setFlag(flagH, ((r0 & 0xF) + (r1 & 0xF)) > 0xF)
    self.setFlag(flagC, result > 0xFF)

    return result & 0xFF


def CPU_ADC8(self, r0, r1):
    return self.CPU_ADD8(r0 + self.testFlag(flagC), r1)


def CPU_ADD16(self, r0, r1):
    result = r0 + r1

    self.setFlag(flagN, False)
    self.setFlag(flagH, (getBit(r0, 11) == 1) and (getBit(result, 11) == 0))
    self.setFlag(flagC, result > 0xFFFF)

    return result & 0xFFFF


def CPU_SUB8(self, r0, r1):
    # result = (r0 + (self.testFlag(flagC) << 8)) - r1
    result = r0 - r1

    self.setFlag(flagC, result < 0)
    self.setFlag(flagZ, result & 0xFF == 0)
    self.setFlag(flagN, True)
    self.setFlag(flagH, ((r0 & 0xF) - (r1 & 0xF)) < 0)

    return result & 0xFF


def CPU_SBC8(self, r0, r1):
    return self.CPU_SUB8(r0 - self.testFlag(flagC), r1)
    # result = r0 - r1 - self.testFlag(flagC)

    # self.setFlag(flagC, result < 0) # Proven correct
    # self.setFlag(flagZ, result & 0xFF == 0)
    # self.setFlag(flagN, True)
    # self.setFlag(flagH, ((r0 & 0xF) - (r1 & 0xF) - self.testFlag(flagC)) < 0)

    # return result & 0xFF


def CPU_AND8(self, r0, r1):
    c = (r0 & r1) & 0xFF

    self.setFlag(flagZ, c == 0)
    self.setFlag(flagN, 0)
    self.setFlag(flagH, 1)
    self.setFlag(flagC, 0)

    return c


def CPU_XOR8(self, r0, r1):
    c = (r0 ^ r1) & 0xFF

    self.setFlag(flagZ, c == 0)
    self.setFlag(flagN, 0)
    self.setFlag(flagH, 0)
    self.setFlag(flagC, 0)

    return c


def CPU_OR8(self, r0, r1):
    c = (r0 | r1) & 0xFF

    self.setFlag(flagZ, c == 0)
    self.setFlag(flagN, 0)
    self.setFlag(flagH, 0)
    self.setFlag(flagC, 0)

    return c


def CPU_CP(self, r0, r1):
    # GBCPUman.pdf
    # Compare A with n. This is basically an A - n subtraction instruction
    # but the results are thrown away.
    # try:
    self.CPU_SUB8(r0, r1)
    # except CoreDump.CoreDump:
    #     gblogger.info("CP called SUB8 that caused CoreDump")


def CPU_RLC(self, r0):  # WARN: There are is one more in CB
    r0, carry = lrotate_inC(r0)
    self.setFlag(flagZ, r0 == 0)
    self.setFlag(flagN, False)
    self.setFlag(flagH, False)
    self.setFlag(flagC, carry)
    return r0


def CPU_RRC(self, r0):  # WARN: There are is one more in CB

    result, carry = rrotate_inC(r0)
    self.setFlag(flagZ, result == 0)
    self.setFlag(flagN, False)
    self.setFlag(flagH, False)
    self.setFlag(flagC, carry)
    return result


def CPU_RL(self, r0):  # WARN: There are is one more in CB
    result, carry = lrotate_thruC(r0, self.testFlag(flagC))

    self.setFlag(flagZ, result == 0)
    self.setFlag(flagN, False)
    self.setFlag(flagH, False)
    self.setFlag(flagC, carry)
    return result


def CPU_RR(self, r0):  # WARN: There are is one more in CB
    result, carry = rrotate_thruC(r0, self.testFlag(flagC))
    self.setFlag(flagZ, result == 0)
    self.setFlag(flagN, False)
    self.setFlag(flagH, False)
    self.setFlag(flagC, carry)
    return result


def CPU_DAA(self):
    # http://stackoverflow.com/a/29990058/3831206
    # http://forums.nesdev.com/viewtopic.php?t=9088
    a = self.reg[A]

    corr = 0
    corr |= 0x06 if self.testFlag(flagH) else 0x00
    corr |= 0x60 if self.testFlag(flagC) else 0x00

    if self.testFlag(flagN):
        a -= corr
    else:
        corr |= 0x06 if (a & 0x0F) > 0x09 else 0x00
        corr |= 0x60 if a > 0x99 else 0x00
        a += corr

    self.clearFlag(flagH)
    self.setFlag(flagC, corr & 0x60)
    a &= 0xFF
    self.setFlag(flagZ, a == 0)

    self.reg[A] = a


def CPU_POP(self):
    """This instruction first loads to the low-order portion of qq, the byte at the memory location
    corresponding to the contents of SP; then SP is incremented and the con- tents of the
    corresponding adjacent memory location are loaded to the high-order portion of qq and the SP is
    now incremented again. """

    high = self.mb[self.reg[SP]+1]
    low = self.mb[self.reg[SP]]

    self.reg[SP] += 2

    return (high << 8) + low


def CPU_PUSH(self, r0):
    """This instruction first decrements SP and loads the high-order byte of register pair qq to the
    memory address specified by the SP. The SP is decremented again and loads the low-order byte of
    qq to the memory location corresponding to this new address in the SP."""

    #FIXME: Quick hack to make interrupts during halt to work
    if self.halted:
        r0 += 1 # Byte-length of HALT

    self.mb[self.reg[SP]-1] = (r0 & 0xFF00) >> 8  # High
    self.mb[self.reg[SP]-2] = r0 & 0x00FF  # Low

    # DEC
    self.reg[SP] -= 2


def CPU_RET(self):
    return self.CPU_POP()


def CPU_DI(self):
    # "Enable interrupts. This intruction enables interrupts but not immediately.
    # Interrupts are enabled after instruction after EI is executed"
    # gblogger.info("Disabling interrupts")
    self.interruptMasterEnableLatch = False


def CPU_EXT_SLA(self, r0):
    r0, carry = lshift(r0)
    self.setFlag(flagZ, r0 == 0)
    self.setFlag(flagN, False)
    self.setFlag(flagH, False)
    self.setFlag(flagC, carry)
    return r0


def CPU_EXT_SRA(self, r0):
    MSB = r0 & 0x80
    r0, carry = rshift(r0)
    self.setFlag(flagZ, r0 == 0)
    self.setFlag(flagN, False)
    self.setFlag(flagH, False)
    self.setFlag(flagC, carry)
    return r0 + MSB


def CPU_EXT_SRL(self, r0):
    r0, carry = rshift(r0)
    self.setFlag(flagZ, r0 == 0)
    self.setFlag(flagN, False)
    self.setFlag(flagH, False)
    self.setFlag(flagC, carry)
    return r0 & 0x7F


def CPU_EXT_SWAP(self, r0):
    r0 = swap(r0)
    self.setFlag(flagZ, r0 == 0)
    self.setFlag(flagN, False)
    self.setFlag(flagH, False)
    self.setFlag(flagC, False)
    return r0


def CPU_EXT_BIT(self, r1, r0):
    # "Set if bit b of register r is 0"
    self.setFlag(flagZ, ((r0 & (1 << r1)) == 0))
    self.clearFlag(flagN)
    self.setFlag(flagH)


def CPU_EXT_RES(self, r1, r0):
    return r0 & (255 - (1 << r1))


def CPU_EXT_SET(self, r1, r0):
    return r0 | (1 << r1)


def CPU_EXT_RLC(self, r0):  # WARN: There are is one more in CB
    r0, carry = lrotate_inC(r0)
    self.setFlag(flagZ, r0 == 0)
    self.setFlag(flagN, False)
    self.setFlag(flagH, False)
    self.setFlag(flagC, carry)
    return r0


def CPU_EXT_RRC(self, r0):  # WARN: There are is one more in CB
    r0, carry = rrotate_inC(r0)
    self.setFlag(flagZ, r0 == 0)
    self.setFlag(flagN, False)
    self.setFlag(flagH, False)
    self.setFlag(flagC, carry)
    return r0


def CPU_EXT_RL(self, r0):  # WARN: There are is one more in CB
    r0, carry = lrotate_thruC(r0, 1 if self.testFlag(flagC) else 0)
    self.setFlag(flagZ, r0 == 0)
    self.setFlag(flagN, False)
    self.setFlag(flagH, False)
    self.setFlag(flagC, carry)
    return r0


def CPU_EXT_RR(self, r0):  # WARN: There are is one more in CB
    r0, carry = rrotate_thruC(r0, 1 if self.testFlag(flagC) else 0)
    self.setFlag(flagZ, r0 == 0)
    self.setFlag(flagN, False)
    self.setFlag(flagH, False)
    self.setFlag(flagC, carry)
    return r0
