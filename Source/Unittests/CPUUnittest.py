#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# python CPUUnittest.py Test_CPU.test_additionRegisterPointer

from MB import Motherboard
from CPU.opcodes import *
from CPU import *
import unittest

mb = Motherboard(None, "ROMs/POKEMON BLUE.gb", None, None)


def clearFlag():
    mb.cpu.clearFlag(flagZ)
    mb.cpu.clearFlag(flagN)
    mb.cpu.clearFlag(flagH)
    mb.cpu.clearFlag(flagC)


def setFlag():
    mb.cpu.setFlag(flagZ)
    mb.cpu.setFlag(flagN)
    mb.cpu.setFlag(flagH)
    mb.cpu.setFlag(flagC)


def testFlags(self, zero, sub, half, carry, debugMsg=None):
    if debugMsg:
        self.assertEqual(zero, mb.cpu.testFlag(flagZ), debugMsg)
        self.assertEqual(sub, mb.cpu.testFlag(flagN), debugMsg)
        self.assertEqual(half, mb.cpu.testFlag(flagH), debugMsg)
        self.assertEqual(carry, mb.cpu.testFlag(flagC), debugMsg)
    else:
        self.assertEqual(zero, mb.cpu.testFlag(flagZ))
        self.assertEqual(sub, mb.cpu.testFlag(flagN))
        self.assertEqual(half, mb.cpu.testFlag(flagH))
        self.assertEqual(carry, mb.cpu.testFlag(flagC))


def clearRegisters():
    mb.cpu.reg[A] = 0
    mb.cpu.reg[F] = 0
    mb.cpu.reg[B] = 0
    mb.cpu.reg[C] = 0
    mb.cpu.reg[D] = 0
    mb.cpu.reg[E] = 0
    mb.cpu.reg[H] = 0
    mb.cpu.reg[L] = 0
    mb.cpu.reg[SP] = 0
    mb.cpu.reg[PC] = 0


def clearStack100():
    for n in range(0xFFFF, 0xFF9B, -1):
        mb[n] = 0x00


def registerName(n):
    return ["B", "C", "D", "E", "H", "L", "None", "A"][n % 8]


def offsetToRegister(n):
    n = n % 8
    if n == 0x6:
        return mb[0xCB01]
    else:
        return mb.cpu.reg[[B, C, D, E, H, L, None, A][n]]


def setAllRegTo(v):
    for n in range(8):
        # A, F, B, C, D, E, H, L
        if n == 1:  # Skip F
            continue
        else:
            mb.cpu.reg[n] = v


def printAllRegisters():
    for r, v in zip([A, B, C, D, E, H, L], ["A", "B", "C", "D", "E", "H", "L"]):
        print v, mb.cpu.reg[r]


def getInstruction(self, operation, value, newPC):
    # #OPTIMIZE: Can this be improved?
    if operation[0] == 1:
        return (
            operation[2],
            operation[1],
            (self, newPC)
        )
    elif operation[0] == 2:
        # Possible 8bit immediate
        return (
            operation[2],
            operation[1],
            (self, value, newPC)
        )
    elif operation[0] == 3:
        # Possible 16bit immediate
        # Flips order of values due to big-endian
        return (
            operation[2],
            operation[1],
            (self, value, newPC)
        )
    else:
        raise Exception("Unexpected opcode length: %s" % operation[0])


class Test_CPU(unittest.TestCase):
    def test_opcode00(self):  # NOP
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x00], None, 0x032)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x032)

        testFlags(self, False, False, False, False)

        setFlag()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x00], None, 0x032)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x032)

        testFlags(self, True, True, True, True)

    def test_opcode01(self):  # LD BC, d16
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x01], 0x1052, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getBC(), 0x1052)
        testFlags(self, False, False, False, False)

        setFlag()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x01], 0x0052, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getBC(), 0x052)
        testFlags(self, True, True, True, True)

    def test_opcode02(self):  # LD (BC), A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setBC(0xC000)
        mb.cpu.reg[A] = 0x0002
        inst = getInstruction(mb.cpu, opcodes.opcodes[0x02], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[mb.cpu.getBC()], 0x0002)
        testFlags(self, False, False, False, False)

        setFlag()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x02], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[mb.cpu.getBC()], 0x0002)
        testFlags(self, True, True, True, True)

    def test_opcode03(self):  # INC 16-bit BC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setBC(0x0010)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x03], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getBC(), 0x0011)

        testFlags(self, False, False, False, False)

        setFlag()
        mb.cpu.setBC(0x0010)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x03], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getBC(), 0x0011)

        testFlags(self, True, True, True, True)

    def test_opcode04(self):  # INC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[B] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x04], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x11)

        testFlags(self, False, False, False, False)

        setFlag()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x04], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x12)

        # Carry must be True, since all flags were forced high. INC does not change carry
        testFlags(self, False, False, False, True)

        clearFlag()
        mb.cpu.reg[B] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x04], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x00)

        testFlags(self, True, False, True, False)

        clearFlag()
        mb.cpu.reg[B] = 0x0F

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x04], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x10)

        testFlags(self, False, False, True, False)

    def test_opcode05(self):  # DEC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[B] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x05], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x0f)

        testFlags(self, False, True, True, False)

        mb.cpu.reg[B] = 0x1f

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x05], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x1e)

        testFlags(self, False, True, False, False)

        mb.cpu.reg[B] = 0x01

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x05], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x00)

        testFlags(self, True, True, False, False)

    def test_opcode06(self):  # LD B, d8
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[B] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x06], 0x03, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x03)

        testFlags(self, False, False, False, False)

        setFlag()
        mb.cpu.reg[B] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x06], 0x03, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x03)

        testFlags(self, True, True, True, True)

    def test_opcode07(self):  # RLC A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x01

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x07], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x02)

        testFlags(self, False, False, False, False)

        setFlag()
        mb.cpu.reg[A] = 0x01

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x07], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x02)

        testFlags(self, False, False, False, False)

        setFlag()
        mb.cpu.reg[A] = 0xff

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x07], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0xff)

        testFlags(self, False, False, False, True)

    def test_opcode08(self):  # LD (v), s.SP
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[SP] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x08], 0xCB01, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb[0xCB01], mb.cpu.reg[SP])

    def test_opcode09(self):  # ADD BC to HL
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setBC(0x01)
        mb.cpu.setHL(0x02)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x09], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0x03)

        testFlags(self, False, False, False, False)

        clearRegisters()
        setFlag()

        mb.cpu.setBC(0x01)
        mb.cpu.setHL(0x02)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x09], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0x03)

        testFlags(self, True, False, False, False)

        clearRegisters()
        setFlag()

        mb.cpu.setBC(0x2)
        mb.cpu.setHL(0xFFFF)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x09], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0x01)

        testFlags(self, True, False, True, True)

    def test_opcode0A(self):  # LD A,(BC)
        clearRegisters()
        clearFlag()
        clearStack100()
        mb[0xcb01] = 0xF1
        mb.cpu.setBC(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x0A], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0xF1)

    def test_opcode0B(self):  # LD A, (BC)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setBC(0xF1)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x0B], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getBC(), 0xF0)

        testFlags(self, False, False, False, False)

        setFlag()

        mb.cpu.setBC(0xF2)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x0B], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getBC(), 0xF1)

        testFlags(self, True, True, True, True)

    def test_opcode0C(self):  # INC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[C] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x0C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x11)

        testFlags(self, False, False, False, False)

        setFlag()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x0C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x12)

        # Carry must be True, since all flags were forced high. INC does not change carry
        testFlags(self, False, False, False, True)

        clearFlag()
        mb.cpu.reg[C] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x0C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x00)

        testFlags(self, True, False, True, False)

        clearFlag()
        mb.cpu.reg[C] = 0x0F

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x0C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x10)

        testFlags(self, False, False, True, False)

    def test_opcode0D(self):  # DEC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[C] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x0D], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x0f)

        testFlags(self, False, True, True, False)

        mb.cpu.reg[C] = 0x1f

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x0D], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x1e)

        testFlags(self, False, True, False, False)

        mb.cpu.reg[C] = 0x01

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x0D], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x00)

        testFlags(self, True, True, False, False)

    def test_opcode0E(self):  # LD C, v
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x0E], 0x10, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x10)

    def test_opcode0F(self):  # RRC A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x0F], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x08)

        testFlags(self, False, False, False, False)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x01

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x0F], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x80)

        testFlags(self, False, False, False, True)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x0F], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x00)

        testFlags(self, True, False, False, False)

    def test_opcode11(self):  # LD DE, d16
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x11], 0x08, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getDE(), 0x08)

    def test_opcode12(self):  # LD(DE), A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x10
        mb.cpu.setDE(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x12], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[mb.cpu.getDE()], 0x10)

    def test_opcode13(self):  # INC DE
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setDE(0x01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x13], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getDE(), 0x02)

    def test_opcode14(self):  # INC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[D] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x14], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x11)

        testFlags(self, False, False, False, False)

        setFlag()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x14], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x12)

        # Carry must be True, since all flags were forced high. INC does not change carry
        testFlags(self, False, False, False, True)

        clearFlag()
        mb.cpu.reg[D] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x14], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x00)

        testFlags(self, True, False, True, False)

        clearFlag()
        mb.cpu.reg[D] = 0x0F

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x14], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x10)

        testFlags(self, False, False, True, False)

    def test_opcode15(self):  # DEC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[D] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x15], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x0f)

        testFlags(self, False, True, True, False)

        mb.cpu.reg[D] = 0x1f

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x15], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x1e)

        testFlags(self, False, True, False, False)

        mb.cpu.reg[D] = 0x01

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x15], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x00)

        testFlags(self, True, True, False, False)

    def test_opcode16(self):  # LD D,v
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x16], 0x05, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x05)

    def test_opcode17(self):  # RL A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x17], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x20)

        testFlags(self, False, False, False, False)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x9c

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x17], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x38)

        testFlags(self, False, False, False, True)

    def test_opcode18(self):  # JR r8
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[PC] = 0x10

        #TODO: Check if PC is not 0x0000 at start

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x18], 0x10, mb.cpu.reg[PC]+2)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x22)

    def test_opcode19(self):  # ADD HL, DE
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setDE(0x01)
        mb.cpu.setHL(0x02)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x19], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0x03)

        testFlags(self, False, False, False, False)

        clearRegisters()
        setFlag()

        mb.cpu.setDE(0x01)
        mb.cpu.setHL(0x02)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x19], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0x03)

        testFlags(self, True, False, False, False)

        clearRegisters()
        setFlag()

        mb.cpu.setDE(0x2)
        mb.cpu.setHL(0xFFFF)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x19], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0x01)

        testFlags(self, True, False, True, True)

    def test_opcode1A(self):  # LD A, DE
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xcb01] = 0x10
        mb.cpu.setDE(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x1A], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x10)

    def test_opcode1B(self):  # DEC DE
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setDE(0xF1)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x1B], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getDE(), 0xF0)

        testFlags(self, False, False, False, False)

        setFlag()

        mb.cpu.setDE(0xF2)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x1B], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getDE(), 0xF1)

        testFlags(self, True, True, True, True)

    def test_opcode1C(self):  # INC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[E] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x1C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x11)

        testFlags(self, False, False, False, False)

        setFlag()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x1C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x12)

        # Carry must be True, since all flags were forced high. INC does not change carry
        testFlags(self, False, False, False, True)

        clearFlag()
        mb.cpu.reg[E] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x1C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x00)

        testFlags(self, True, False, True, False)

        clearFlag()
        mb.cpu.reg[E] = 0x0F

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x1C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x10)

        testFlags(self, False, False, True, False)

    def test_opcode1D(self):  # DEC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[E] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x1D], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x0f)

        testFlags(self, False, True, True, False)

        mb.cpu.reg[E] = 0x1f

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x1D], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x1e)

        testFlags(self, False, True, False, False)

        mb.cpu.reg[E] = 0x01

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x1D], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x00)

        testFlags(self, True, True, False, False)

    def test_opcode1F(self):  # RR A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x1F], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x8)

        testFlags(self, False, False, False, False)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x01

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x1F], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x0)

        testFlags(self, True, False, False, True)

    def test_opcode20(self):  # JR NZ,r8
        # Negativ jump: -5
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[PC] = 0x0A

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x20], 0xFB, mb.cpu.reg[PC]+2)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x07)

        # Positive jump: +5
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[PC] = 0x0A

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x20], 0x05, mb.cpu.reg[PC]+2)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x11)

        # Don't jump
        clearRegisters()
        clearFlag()
        clearStack100()
        mb.cpu.setFlag(flagZ)

        mb.cpu.reg[PC] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x20], 0xFB, mb.cpu.reg[PC]+2)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x12)

    def test_opcode21(self):  # LD HL,d16
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x21], 0xFFFF, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0xFFFF)

        testFlags(self, False, False, False, False)

    def test_opcode22(self):  # LDI (HL),A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x22], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[mb.cpu.getHL()-1], 0x10)

    def test_opcode23(self):  # INC HL
        # Check increment
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setHL(0x01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x23], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0x02)

        # Check overflow
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setHL(0xFFFF)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x23], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0x00)

    def test_opcode24(self):  # INC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[H] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x24], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x11)

        testFlags(self, False, False, False, False)

        setFlag()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x24], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x12)

        # Carry must be True, since all flags were forced high. INC does not change carry
        testFlags(self, False, False, False, True)

        clearFlag()
        mb.cpu.reg[H] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x24], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x00)

        testFlags(self, True, False, True, False)

        clearFlag()
        mb.cpu.reg[H] = 0x0F

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x24], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x10)

        testFlags(self, False, False, True, False)

    def test_opcode25(self):  # DEC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[H] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x25], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x0f)

        testFlags(self, False, True, True, False)

        mb.cpu.reg[H] = 0x1f

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x25], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x1e)

        testFlags(self, False, True, False, False)

        mb.cpu.reg[H] = 0x01

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x25], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x00)

        testFlags(self, True, True, False, False)

    def test_opcode26(self):  # LD H,v
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x26], 0x05, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x05)

    def test_opcode27(self):  # DAA
        """
        (Example from Z80 reference manual page 184)
        # BCD format

        25 (BCD) = 0010 0101
                    (1)  (5)

        # Preformated BCD numbers

        15(BCD) = 0001 0101
        27(BCD) = 0010 0111

        # Regular addition or subtract

          0001 0101
        + 0010 0111
        = 0011 1100 = 0x3C

        # BCD correction (must be adjusted)

          0011 1100
        + 0000 0110 (BCD correction)
        = 0100 0010 = 42 (BCD)
           (4) (2)
        """

        ### Addition test

        # Simulate the conditions after an addition
        mb.cpu.reg[A] = 0x27 # Interpreted as decimal 27
        mb.cpu.reg[B] = 0x15 # Interpreted as decimal 15
        additionResult = 0x42 # Interpreted as decimal after DAA

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x80], None, 0x0000) # ADD A,B
        mb.cpu.executeInstruction(inst)

        # Do BCD correction
        inst = getInstruction(mb.cpu, opcodes.opcodes[0x27], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x42)

        ### Subtraction test

        clearFlag()
        clearRegisters()

        # Simulate the conditions after a subtraction
        mb.cpu.reg[A] = 0x27 # Interpreted as decimal 27
        mb.cpu.reg[B] = 0x15 # Interpreted as decimal 15
        subtractResult = 0x12 # Interpreted as decimal after DAA

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x90], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        # Do BCD correction
        inst = getInstruction(mb.cpu, opcodes.opcodes[0x27], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x12)

    def test_opcode28(self):  # JR Z, r8
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[PC] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x28], 0x10, mb.cpu.reg[PC]+2)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x12)

        mb.cpu.reg[PC] = 0x10

        mb.cpu.setFlag(flagZ)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x28], 0x10, mb.cpu.reg[PC]+2)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x22)

    def test_opcode29(self):  # ADD HL, HL
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setHL(0x02)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x29], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0x04)

        testFlags(self, False, False, False, False)

        clearRegisters()
        setFlag()

        mb.cpu.setHL(0x00)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x29], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0x00)

        testFlags(self, True, False, False, False)

    def test_opcode2A(self):  # LDI A, (HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xcb01] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x2A], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[mb.cpu.getHL()-1], 0x10)

    def test_opcode2B(self):  # DEC HL
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setHL(0x01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x2B], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0x00)

    def test_opcode2C(self):  # INC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[L] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x2C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x11)

        testFlags(self, False, False, False, False)

        setFlag()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x2C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x12)

        # Carry must be True, since all flags were forced high. INC does not change carry
        testFlags(self, False, False, False, True)

        clearFlag()
        mb.cpu.reg[L] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x2C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x00)

        testFlags(self, True, False, True, False)

        clearFlag()
        mb.cpu.reg[L] = 0x0F

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x2C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x10)

        testFlags(self, False, False, True, False)

    def test_opcode2D(self):  # DEC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[L] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x2D], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x0f)

        testFlags(self, False, True, True, False)

        mb.cpu.reg[L] = 0x1f

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x2D], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x1e)

        testFlags(self, False, True, False, False)

        mb.cpu.reg[L] = 0x01

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x2D], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x00)

        testFlags(self, True, True, False, False)

    def test_opcode2E(self):  # LD L,v
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x2E], 0x05, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x05)

    def test_opcode2F(self):  # CPL
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x02
        inst = getInstruction(mb.cpu, opcodes.opcodes[0x2F], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0xfd)

        testFlags(self, False, False, False, False)

    def test_opcode30(self):  # JR NC, r8
        # Negativ jump: -5
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[PC] = 0x0A

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x30], 0xFB, mb.cpu.reg[PC]+2)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x07)

        # Positive jump: +5
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[PC] = 0x0A

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x30], 0x05, mb.cpu.reg[PC]+2)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x11)

        # Don't jump
        clearRegisters()
        clearFlag()
        clearStack100()
        mb.cpu.setFlag(flagC)

        mb.cpu.reg[PC] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x30], 0xFB, mb.cpu.reg[PC]+2)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x12)

    def test_opcode31(self):  # LD SP, d16
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x31], 0xFFFF, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFF)

        testFlags(self, False, False, False, False)

    def test_opcode32(self):  # LD (HL-), A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x32], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[0xcb01], 0x10)
        self.assertEqual(mb.cpu.getHL(),0xcb00)

    def test_opcode33(self):  # INC 16 SP
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[SP] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x33], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[SP], 0x11)

        testFlags(self, False, False, False, False)

        setFlag()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x33], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[SP], 0x12)

        testFlags(self, True, True, True, True)

        clearFlag()
        mb.cpu.reg[SP] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x33], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[SP], 0x100)

        testFlags(self, False, False, False, False)

        clearFlag()
        mb.cpu.reg[SP] = 0x0F

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x33], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[SP], 0x10)

        testFlags(self, False, False, False, False)

    def test_opcode34(self):  # INC (HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xcb01] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x34], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[0xcb01], 0x11)

    def test_opcode35(self):  # DEC (HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xcb01] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x35], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[0xcb01], 0x0F)

    def test_opcode36(self):  # LD (HL), d8
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xcb01] = 0x00
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x36], 0x10, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[0xcb01], 0x10)

    def test_opcode37(self):  # SCF
        clearRegisters()
        clearFlag()
        clearStack100()
        testFlags(self, False, False, False, False)
        inst = getInstruction(mb.cpu, opcodes.opcodes[0x37], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        testFlags(self, False, False, False, True)

        clearRegisters()
        setFlag()
        testFlags(self, True, True, True, True)
        inst = getInstruction(mb.cpu, opcodes.opcodes[0x37], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        testFlags(self, True, False, False, True)

    def test_opcode38(self):  # JR C,r8
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[PC] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x38], 0x10, mb.cpu.reg[PC]+2)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x12)

        mb.cpu.reg[PC] = 0x10

        mb.cpu.setFlag(flagC)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x38], 0x10, mb.cpu.reg[PC]+2)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x22)

    def test_opcode39(self):  # ADD HL, SP
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setHL(0x02)
        mb.cpu.reg[SP] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x39], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0x12)

        testFlags(self, False, False, False, False)

        clearRegisters()
        setFlag()

        mb.cpu.setHL(0x00)
        mb.cpu.reg[SP] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x39], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0x10)

        testFlags(self, True, False, False, False)

    def test_opcode3A(self):  # LDD A,(HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xcb01] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3A], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x10)
        self.assertEqual(mb.cpu.getHL(), 0xcb00)

    def test_opcode3B(self):  # DEC 16 SP
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[SP] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3B], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[SP], 0x0F)

        testFlags(self, False, False, False, False)

        setFlag()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3B], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[SP], 0x0E)

        testFlags(self, True, True, True, True)

        clearFlag()
        mb.cpu.reg[SP] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3B], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[SP], 0xFE)

        testFlags(self, False, False, False, False)

    def test_opcode3C(self):  # INC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x11)

        testFlags(self, False, False, False, False)

        setFlag()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x12)

        # Carry must be True, since all flags were forced high. INC does not change carry
        testFlags(self, False, False, False, True)

        clearFlag()
        mb.cpu.reg[A] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x00)

        testFlags(self, True, False, True, False)

        clearFlag()
        mb.cpu.reg[A] = 0x0F

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3C], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x10)

        testFlags(self, False, False, True, False)

    def test_opcode3D(self):  # DEC
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3D], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x0f)

        testFlags(self, False, True, True, False)

        mb.cpu.reg[A] = 0x1f

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3D], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x1e)

        testFlags(self, False, True, False, False)

        mb.cpu.reg[A] = 0x01

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3D], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x00)

        testFlags(self, True, True, False, False)

    def test_opcode3E(self):  # LD A, d8
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3E], 0x10, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x10)

    def test_opcode3F(self):  # CCF
        # Z is not affected.
        # N is reset
        # H, previous carry is copied.
        # C inverted

        clearRegisters()
        clearFlag()
        clearStack100()

        testFlags(self, False, False, False, False)
        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3F], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        testFlags(self, False, False, False, True)

        clearRegisters()
        setFlag()

        testFlags(self, True, True, True, True)
        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3F], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        testFlags(self, True, False, True, False)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setFlag(flagC)

        testFlags(self, False, False, False, True)
        inst = getInstruction(mb.cpu, opcodes.opcodes[0x3F], None, 0x0000)
        mb.cpu.executeInstruction(inst)
        testFlags(self, False, False, True, False)

    def test_opcode40(self):  # LD B,B
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[B] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x40], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x05)

    def test_opcode41(self):  # LD B,C
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[C] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x41], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x05)

    def test_opcode42(self):  # LD B,D
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[D] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x42], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x05)

    def test_opcode43(self):  # LD B,E
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[E] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x43], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x05)

    def test_opcode44(self):  # LD B,H
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[H] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x44], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x05)

    def test_opcode45(self):  # LD B,L
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[L] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x45], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x05)

    def test_opcode46(self):  # LD B,(HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xcb01] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x46], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x10)

    def test_opcode47(self):  # LD B,A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x47], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[B], 0x05)

    def test_opcode48(self):  # LD C,B
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[B] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x48], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x05)

    def test_opcode49(self):  # LD C,C
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[C] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x49], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x05)

    def test_opcode4A(self):  # LD C,D
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[D] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x4A], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x05)

    def test_opcode4B(self):  # LD C,E
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[E] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x4B], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x05)

    def test_opcode4C(self):  # LD C,H
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[H] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x4C], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x05)

    def test_opcode4D(self):  # LD C,L
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[L] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x4D], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x05)

    def test_opcode4E(self):  # LD C,(HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xcb01] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x4E], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x10)

    def test_opcode4F(self):  # LD C,A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x4F], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[C], 0x05)

    def test_opcode50(self):  # LD D,B
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[B] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x50], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x05)

    def test_opcode51(self):  # LD D,C
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[C] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x51], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x05)

    def test_opcode52(self):  # LD D,D
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[D] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x52], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x05)

    def test_opcode53(self):  # LD D,E
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[E] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x53], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x05)

    def test_opcode54(self):  # LD D,H
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[H] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x54], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x05)

    def test_opcode55(self):  # LD D,L
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[L] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x55], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x05)

    def test_opcode56(self):  # LD D,(HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xcb01] = 0x05
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x56], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x05)

    def test_opcode57(self):  # LD D,A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x57], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[D], 0x05)

    def test_opcode58(self):  # LD E,B
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[B] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x58], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x05)

    def test_opcode59(self):  # LD E,C
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[C] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x59], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x05)

    def test_opcode5A(self):  # LD E,D
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[D] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x5A], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x05)

    def test_opcode5B(self):  # LD E,E
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[E] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x5B], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x05)

    def test_opcode5C(self):  # LD E,H
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[H] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x5C], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x05)

    def test_opcode5D(self):  # LD E,L
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[L] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x5D], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x05)

    def test_opcode5E(self):  # LD E,(HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xcb01] = 0x05
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x5E], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x05)

    def test_opcode5F(self):  # LD E,A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x5F], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[E], 0x05)

    def test_opcode60(self):  # LD H,B
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[B] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x60], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x05)

    def test_opcode61(self):  # LD H,C
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[C] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x61], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x05)

    def test_opcode62(self):  # LD H,D
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[D] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x62], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x05)

    def test_opcode63(self):  # LD H,E
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[E] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x63], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x05)

    def test_opcode64(self):  # LD H,H
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[H] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x64], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x05)

    def test_opcode65(self):  # LD H,L
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[L] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x65], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x05)

    def test_opcode66(self):  # LD H,(s.HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0x05
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x66], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x05)

    def test_opcode67(self):  # LD H,A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x67], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[H], 0x05)

    def test_opcode68(self):  # LD L,B
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[B] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x68], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x05)

    def test_opcode69(self):  # LD L,C
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[C] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x69], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x05)

    def test_opcode6A(self):  # LD L,D
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[D] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x6A], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x05)

    def test_opcode6B(self):  # LD L,E
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[E] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x6B], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x05)

    def test_opcode6C(self):  # LD L,H
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[H] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x6C], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x05)

    def test_opcode6D(self):  # LD L,L
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[L] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x6D], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x05)

    def test_opcode6E(self):  # LD L,(s.H)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0x05
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x6E], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x05)

    def test_opcode6F(self):  # LD L,A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x6F], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[L], 0x05)

    def test_opcode70(self):  # LD (HL),B
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[B] = 0x05
        mb[0xcb01] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x70], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[0xcb01], 0x05)

    def test_opcode71(self):  # LD (HL),C
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[C] = 0x05
        mb[0xcb01] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x71], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[0xcb01], 0x05)

    def test_opcode72(self):  # LD (HL),D
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[D] = 0x05
        mb[0xcb01] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x72], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[0xcb01], 0x05)

    def test_opcode73(self):  # LD (HL),E
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[E] = 0x05
        mb[0xcb01] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x73], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[0xcb01], 0x05)

    def test_opcode74(self):  # LD (HL),H
        clearRegisters()
        clearFlag()
        clearStack100()

        # mb.cpu.reg[H] = 0x05
        mb[0xcb01] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x74], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[0xcb01], 0xcb)

    def test_opcode75(self):  # LD (HL),L
        clearRegisters()
        clearFlag()
        clearStack100()

        # mb.cpu.reg[L] = 0x05
        mb[0xcb01] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x75], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[0xcb01], 0x01)

    def test_opcode76(self):  # HALT
        clearRegisters()
        clearFlag()
        clearStack100()
        mb.bootROMEnabled = False

        entryPoint = 0xC000

        mb.cartridge.ROMBanks[0][0x50] = 0x00 # NOP
        mb.cartridge.ROMBanks[0][0x51] = 0xD9 # RETI
        mb[entryPoint] = 0x76
        for n in range(10):
            mb[entryPoint+1+n] = 0x00

        ## FIRST TEST -- Simple HALT, interrupt

        mb.cpu.interruptMasterEnable = True
        mb[0xFFFF] = 0x00 # Disable all interrupt vectors
        mb.cpu.reg[SP] = 0xD000
        mb.cpu.reg[PC] = entryPoint

        for n in range(2**16):  # Make sure we don't go anywhere
            mb.cpu.tick()
            self.assertEqual(mb.cpu.reg[PC], entryPoint)

        # Request timer interrupt, while interrupt disabled
        mb[0xFF0F] = 0b00100

        for n in range(2**16): # Make sure we don't go anywhere
            mb.cpu.tick()
            self.assertEqual(mb.cpu.reg[PC], entryPoint)

        # Enable timer interrupt
        mb[0xFFFF] = 0b00100

        self.assertEqual(mb.cpu.reg[PC], entryPoint)
        mb.cpu.tick() # Interrupt triggers
        self.assertEqual(mb.cpu.reg[PC], 0x51) # Check the PC ends up at interrupt vector for timer
        self.assertEqual(mb.cpu.interruptMasterEnable, False)

        # Returning
        print hex(mb[0x50]), hex(mb[0x51]), hex(mb.cpu.reg[SP]), hex(mb[mb.cpu.reg[SP]] + (mb[mb.cpu.reg[SP]+1]<<8))
        mb.cpu.tick() # Interrupt triggers
        self.assertEqual(mb.cpu.reg[PC], entryPoint+1) # Check the PC ends up at interrupt vector for timer
        self.assertEqual(mb.cpu.interruptMasterEnable, True)

        ## SECOND TEST -- Multiple interrupts priority

        mb.cpu.interruptMasterEnable = True
        mb[0xFFFF] = 0x00 # Disable all interrupt vectors
        mb.cartridge.ROMBanks[0][0x40] = 0x00 # NOP
        mb.cpu.reg[SP] = 0xD000
        mb.cpu.reg[PC] = entryPoint

        for n in range(2**16):  # Make sure we don't go anywhere
            mb.cpu.tick()
            self.assertEqual(mb.cpu.reg[PC], entryPoint)

        # Request timer and VBlank interrupt, while interrupt disabled
        mb[0xFF0F] = 0b00101

        for n in range(2**16): # Make sure we don't go anywhere
            mb.cpu.tick()
            self.assertEqual(mb.cpu.reg[PC], entryPoint)

        # Enable timer and VBlank interrupt
        mb[0xFFFF] = 0b00101

        self.assertEqual(mb.cpu.reg[PC], entryPoint)
        mb.cpu.tick() # Interrupt triggers
        self.assertEqual(mb.cpu.reg[PC], 0x41) # Check the PC ends up at interrupt vector for timer
        self.assertEqual(mb.cpu.interruptMasterEnable, False)



    def test_opcode77(self):  # LD (HL),A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x05
        mb[0xcb01] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x77], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[0xcb01], 0x05)

    def test_opcode78(self):  # LD A,B
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[B] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x78], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x05)

    def test_opcode79(self):  # LD A,C
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[C] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x79], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x05)

    def test_opcode7A(self):  # LD A,D
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[D] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x7A], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x05)

    def test_opcode7B(self):  # LD A,E
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[E] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x7B], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x05)

    def test_opcode7C(self):  # LD A,H
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[H] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x7C], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x05)

    def test_opcode7D(self):  # LD A,L
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[L] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x7D], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x05)

    def test_opcode7E(self):  # LD A,(HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xcb01] = 0x10
        mb.cpu.setHL(0xcb01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x7E], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[0xcb01], 0x10)

    def test_opcode7F(self):  # LD A,A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x7F], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x05)

    def batchTestALU(self, opcode, resultReg, result, resultFlags, operands, tests, pc=0, sp=0, flagOps=(clearFlag, setFlag)):

        for postfix, reg in tests:
            for flagOp in flagOps:
                clearRegisters()
                flagOp()

                mb.cpu.reg[resultReg] = operands[0]
                mb.cpu.reg[reg] = operands[1]
                mb.cpu.reg[SP] = sp

                inst = getInstruction(mb.cpu, opcodes.opcodes[opcode + postfix], None, pc)
                mb.cpu.executeInstruction(inst)

                errorMsg = "Error in: " + hex(opcode + postfix)
                testFlags(self,*resultFlags, debugMsg = errorMsg)

                self.assertEqual(mb.cpu.reg[resultReg], result, hex(mb.cpu.reg[resultReg]) + " " + hex(result) + " " + errorMsg)

    def test_opcode80(self):  # ADD A (Z 0 H C)
        self.batchTestALU(0x80,A,0x6, (False,False,False,False),(0x3,0x3), ((0,B),(1,C),(2,D),(3,E),(4,H),(5,L),(7,A)))
        self.batchTestALU(0x80,A,0x11, (False,False,True,True),(0x88,0x89), ((0,B),(1,C),(2,D),(3,E),(4,H),(5,L)))
        self.batchTestALU(0x80,A,0x10, (False,False,True,True),(0x88,0x88), ((7,A),))

        for flagOp in (clearFlag, setFlag):
            clearRegisters()
            flagOp()

            mb.cpu.reg[A] = 0x3
            mb.cpu.setHL(0xCB01)
            mb[0xCB01] = 0x3

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x86], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, False, False, False, False)
            self.assertEqual(mb.cpu.reg[A], 0x6)

    def test_opcode88(self):  # ADC A (Z 0 H C)

        self.batchTestALU(0x88,A,0x6, (False,False,False,False),(0x3,0x3), ((0,B),(1,C),(2,D),(3,E),(4,H),(5,L),(7,A)), flagOps=(clearFlag,))
        self.batchTestALU(0x88,A,0x11, (False,False,True,True),(0x88,0x89), ((0,B),(1,C),(2,D),(3,E),(4,H),(5,L)), flagOps=(clearFlag,))
        self.batchTestALU(0x88,A,0x10, (False,False,True,True),(0x88,0x88), ((7,A),), flagOps=(clearFlag,))

        self.batchTestALU(0x88,A,0x7, (False,False,False,False),(0x3,0x3), ((0,B),(1,C),(2,D),(3,E),(4,H),(5,L),(7,A)), flagOps=(setFlag,))
        self.batchTestALU(0x88,A,0x12, (False,False,True,True),(0x88,0x89), ((0,B),(1,C),(2,D),(3,E),(4,H),(5,L)), flagOps=(setFlag,))
        self.batchTestALU(0x88,A,0x11, (False,False,True,True),(0x88,0x88), ((7,A),), flagOps=(setFlag,))

        for flagOp in (clearFlag, setFlag):
            ######
            # Test without carry
            clearRegisters()
            flagOp()

            mb.cpu.clearFlag(flagC)
            mb.cpu.reg[A] = 0x3
            mb.cpu.setHL(0xCB01)
            mb[0xCB01] = 0x3

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x8E], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, False, False, False, False)
            self.assertEqual(mb.cpu.reg[A], 0x6)

            ######
            # Test with carry
            mb.cpu.setFlag(flagC)
            mb.cpu.reg[A] = 0x3
            mb.cpu.setHL(0xCB01)
            mb[0xCB01] = 0x3

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x8E], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, False, False, False, False)
            self.assertEqual(mb.cpu.reg[A], 0x7)

    def test_opcode90(self):  # SUB B
        self.batchTestALU(0x90, A, 0x12, (False, True, False, False), (0b00100111, 0b00010101), ((0, B), (1, C), (2, D), (3, E), (4, H), (5, L)))

        self.batchTestALU(0x90, A, 0b00, (True, True, False, False), (0b11, 0b11), ((0, B), (1, C), (2, D), (3, E), (4, H), (5, L)))
        self.batchTestALU(0x90, A, 0x88, (False, True, False, False), (0x88, 0x00), ((0, B), (1, C), (2, D), (3, E), (4, H), (5, L)))
        self.batchTestALU(0x90, A, 0x00, (True, True, False, False), (0x88, 0x88), ((7, A), ))
        self.batchTestALU(0x90, A, 0x00, (True, True, False, False), (0x00, 0x00), ((7, A), ))

        for flagOp in (clearFlag, setFlag):
            clearRegisters()
            flagOp()

            mb.cpu.reg[A] = 0x3
            mb.cpu.setHL(0xCB01)
            mb[0xCB01] = 0x3

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x96], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, True, True, False, False)
            self.assertEqual(mb.cpu.reg[A], 0x0)
            self.assertEqual(mb[0xCB01], 0x3)

    def test_opcode98(self):  # SBC A,B
        ###########
        # Flags cleared, exactly same test as 0x90

        carryTests = [
            (0x98, A, 0x00, (True, True, False, False), (0b11, 0b11), ((0, B), (1, C), (2, D), (3, E), (4, H), (5, L))),
            (0x98, A, 0x88, (False, True, False, False), (0x88, 0x00), ((0, B), (1, C), (2, D), (3, E), (4, H), (5, L))),
            (0x98, A, 0x00, (True, True, False, False), (0x88, 0x88), ((7, A),)),
            (0x98, A, 0x00, (True, True, False, False), (0x00, 0x00), ((7, A),))
        ]

        for n in carryTests:
            opcode, resultReg, result, resultFlags, operands, tests = n
            for postfix, reg in tests:
                clearRegisters()
                clearFlag()

                mb.cpu.reg[resultReg] = operands[0]
                mb.cpu.reg[reg] = operands[1]

                inst = getInstruction(mb.cpu, opcodes.opcodes[opcode + postfix], None, 0x0000)
                mb.cpu.executeInstruction(inst)

                testFlags(self, *resultFlags)
                self.assertEqual(mb.cpu.reg[resultReg], result, hex(mb.cpu.reg[resultReg]) + " = " + hex(result))

        ###########
        # Flags set
        carryTests = [
            (0x98, A, 0x87, (False, True, False, False), (0x88, 0x00), ((0, B), (1, C), (2, D), (3, E), (4, H), (5, L))),
            (0x98, A, 0x0F, (False, True, True, False), (0x11, 0x1), ((0, B), (1, C), (2, D), (3, E), (4, H), (5, L))),
            # Commented for undefined behaviour
            #(0x98, A, 0xEE, (False, True, True, False), (0xFE, 0x1), ((7, A),))
            #(0x98, A, 0xFF, (False, True, False, False), (0x00, 0x00), ((7, A),))
        ]

        for (opcode, resultReg, result, resultFlags, operands, tests) in carryTests:
            for postfix, reg in tests:
                clearRegisters()
                setFlag()

                mb.cpu.reg[resultReg] = operands[0]
                mb.cpu.reg[reg] = operands[1]

                inst = getInstruction(mb.cpu, opcodes.opcodes[opcode + postfix], None, 0x0000)
                mb.cpu.executeInstruction(inst)

                self.assertEqual(mb.cpu.reg[resultReg], result, hex(mb.cpu.reg[resultReg]) + " = " + hex(result))
                testFlags(self, *resultFlags)

    def test_opcodeA0(self):  # AND B

        self.batchTestALU(0xA0,A,0b11, (False,False,True,False),(0b11, 0b11), ((0,B),(1,C),(2,D),(3,E),(4,H),(5,L),(7,A)))
        self.batchTestALU(0xA0,A,0x00, (True,False,True,False),(0x88, 0x00), ((0,B),(1,C),(2,D),(3,E),(4,H),(5,L)))
        self.batchTestALU(0xA0,A,0x88, (False,False,True,False),(0x88, 0x88), ((7,A),))
        self.batchTestALU(0xA0,A,0x00, (True,False,True,False),(0x00, 0x00), ((7,A),))

        for flagOp in (clearFlag, setFlag):
            clearRegisters()
            flagOp()

            mb.cpu.reg[A] = 0x3
            mb.cpu.setHL(0xCB01)
            mb[0xCB01] = 0x3

            inst = getInstruction(mb.cpu, opcodes.opcodes[0xA6], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, False, False, True, False)
            self.assertEqual(mb.cpu.reg[A], 0x3)

    def test_opcodeA8(self):  # XOR B

        self.batchTestALU(0xA8,A,0b00, (True,False,False,False),(0b11, 0b11), ((0,B),(1,C),(2,D),(3,E),(4,H),(5,L),(7,A)))
        self.batchTestALU(0xA8,A,0x88, (False,False,False,False),(0x88, 0x00), ((0,B),(1,C),(2,D),(3,E),(4,H),(5,L)))
        self.batchTestALU(0xA8,A,0x00, (True,False,False,False),(0x88, 0x88), ((7,A),))
        self.batchTestALU(0xA8,A,0x00, (True,False,False,False),(0x00, 0x00), ((7,A),))

        for flagOp in (clearFlag, setFlag):
            clearRegisters()
            flagOp()

            mb.cpu.reg[A] = 0x3
            mb.cpu.setHL(0xCB01)
            mb[0xCB01] = 0x3

            inst = getInstruction(mb.cpu, opcodes.opcodes[0xAE], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, True, False, False, False)
            self.assertEqual(mb.cpu.reg[A], 0x0)

    def test_opcodeB0(self):  # OR B

        self.batchTestALU(0xB0,A,0b11, (False,False,False,False),(0b11, 0b11), ((0,B),(1,C),(2,D),(3,E),(4,H),(5,L),(7,A)))
        self.batchTestALU(0xB0,A,0x88, (False,False,False,False),(0x88, 0x00), ((0,B),(1,C),(2,D),(3,E),(4,H),(5,L)))
        self.batchTestALU(0xB0,A,0x88, (False,False,False,False),(0x88, 0x88), ((7,A),))
        self.batchTestALU(0xB0,A,0x00, (True,False,False,False),(0x00, 0x00), ((7,A),))

        for flagOp in (clearFlag, setFlag):
            clearRegisters()
            flagOp()

            mb.cpu.reg[A] = 0x3
            mb.cpu.setHL(0xCB01)
            mb[0xCB01] = 0x3

            inst = getInstruction(mb.cpu, opcodes.opcodes[0xB6], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, False, False, False, False)
            self.assertEqual(mb.cpu.reg[A], 0x3)

    def test_opcodeB8(self):  # CP B
        self.batchTestALU(0xB8, A, 0b11, (True, True, False, False), (0b11, 0b11), ((0, B), (1, C), (2, D), (3, E), (4, H), (5, L), (7, A)))
        self.batchTestALU(0xB8, A, 0x88, (False, True, False, False), (0x88, 0x00), ((0, B), (1, C), (2, D), (3, E), (4, H), (5, L)))
        self.batchTestALU(0xB8, A, 0x88, (True, True, False, False), (0x88, 0x88), ((7, A),))
        self.batchTestALU(0xB8, A, 0x00, (True, True, False, False), (0x00, 0x00), ((7, A),))

        for flagOp in (clearFlag, setFlag):
            clearRegisters()
            flagOp()

            mb.cpu.reg[A] = 0x3
            mb.cpu.setHL(0xCB01)
            mb[0xCB01] = 0x3

            inst = getInstruction(mb.cpu, opcodes.opcodes[0xBE], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, True, True, False, False)
            self.assertEqual(mb.cpu.reg[A], 0x3)
            self.assertEqual(mb[0xCB01], 0x3)

        for flagOp in (clearFlag, setFlag):
            clearRegisters()
            flagOp()

            mb.cpu.reg[A] = 0x00
            mb.cpu.reg[E] = 0x01

            inst = getInstruction(mb.cpu, opcodes.opcodes[0xBB], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, True, True, False, False)
            self.assertEqual(mb.cpu.reg[A], 0x00)
            self.assertEqual(mb.cpu.reg[E], 0x01)

    def test_opcodeC0(self):  # RET NZ
        clearRegisters()
        clearFlag()
        clearStack100()

        # Setup
        mb.cpu.reg[SP] = 0xFFFE
        mb.cpu.reg[PC] = 0x15

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCD], 0xcb02, mb.cpu.reg[PC]+3)  # CALL
        mb.cpu.executeInstruction(inst)

        # Do RET
        mb.cpu.reg[PC] = 0x10
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC9], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x15+3)

        # Do jump
        mb.cpu.setFlag(flagZ)
        mb.cpu.reg[PC] = 0x10
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC0], 0x00, 0x0011)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x11)

        # Don't jump
        mb.cpu.clearFlag(flagZ)
        mb.cpu.reg[PC] = 0x15
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCD], 0xcb02, mb.cpu.reg[PC]+3)  # CALL
        mb.cpu.executeInstruction(inst)

        mb.cpu.reg[PC] = 0x00
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC0], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x15+3)

    def test_opcodeC8(self):  # RET Z
        clearRegisters()
        clearFlag()
        clearStack100()

        # Setup
        mb.cpu.reg[SP] = 0xFFFE
        mb.cpu.reg[PC] = 0x15

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCD], 0xcb02, mb.cpu.reg[PC]+3)  # CALL
        mb.cpu.executeInstruction(inst)

        # Do RET
        mb.cpu.reg[PC] = 0x10
        mb.cpu.setFlag(flagZ)
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC9], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x15+3)

        # Don't jump
        mb.cpu.clearFlag(flagZ)
        mb.cpu.reg[PC] = 0x10
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC8], 0x00, 0x0011)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x11)

        # Do jump
        mb.cpu.setFlag(flagZ)
        mb.cpu.reg[PC] = 0x15
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCD], 0xcb02, mb.cpu.reg[PC]+3)  # CALL
        mb.cpu.executeInstruction(inst)

        mb.cpu.reg[PC] = 0x00
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC8], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x15+3)

    def test_opcodeC2(self):  # JP NZ,v
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC2], 0x0231, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0231)

        mb.cpu.setFlag(flagZ)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC2], 0x0233, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0231)

    def test_opcodeC3(self):  # JP NZ, a16
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC3], 0x0231, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0231)

    def test_opcodeC4(self):  # CALL NZ,v
        # Don't jump
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setFlag(flagZ)

        mb.cpu.reg[PC] = 0x1512
        mb.cpu.reg[SP] = 0xFFFE

        mb[0xFFFE] = 0x00
        mb[0xFFFD] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC4], 0xFE21, 0x1512+3)  # CALL
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x1512+3)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFE)
        self.assertEqual(mb[0xFFFE], 0x00)
        self.assertEqual(mb[0xFFFD], 0x00)

        # Do jump
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[PC] = 0x1512
        mb.cpu.reg[SP] = 0xFFFE

        mb[0xFFFD] = 0x00
        mb[0xFFFC] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC4], 0xFE21, 0x1512+3)  # CALL
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0xFE21)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFC)
        self.assertEqual(mb[0xFFFD], 0x15)
        self.assertEqual(mb[0xFFFC], 0x15)

    def test_opcodeC5(self):  # PUSH BC ...and... POP BC (opcode C1)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setBC(0x00FF)
        mb.cpu.reg[SP] = 0xFFFE

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC5], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        mb.cpu.setBC(0x0010)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC1], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.getBC(), 0x00FF)

    def test_opcodeC6(self):  # ADD A,d8
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC6], 0x01, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x06)
        testFlags(self, False, False, False, False)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setFlag(flagC)

        mb.cpu.reg[A] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC6], 0x01, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x06)
        testFlags(self, False, False, False, False)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC6], 0x01, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x00)
        testFlags(self, True, False, True, True)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC6], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x00)
        testFlags(self, True, False, False, False)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setFlag(flagN)

        mb.cpu.reg[A] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC6], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x00)
        testFlags(self, True, False, False, False)

    def test_opcodeC7(self):  # RST 0
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setBC(0x00FF)
        mb.cpu.reg[SP] = 0xFFFE
        mb.cpu.reg[PC] = 0xbb02
        mb[0xFFFD] = 0x00
        mb[0xFFFE] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC7], 0x00, 0xCB01)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0000)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFE-2)
        self.assertEqual(mb[0xFFFD], 0xCB)
        self.assertEqual(mb[0xFFFC], 0x01)

    def test_opcodeC9(self):  # RET
        clearRegisters()
        clearFlag()
        clearStack100()

        # Unconditional RET
        mb.cpu.reg[SP] = 0xFFFE
        mb.cpu.reg[PC] = 0x15

        #TODO: Check end PC. Maybe it should be plus the opcode length
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCD], 0xcb02, mb.cpu.reg[PC])  # CALL
        mb.cpu.executeInstruction(inst)

        mb.cpu.reg[PC] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC9], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x15)

    def test_opcodeCA(self):  # JP Z,v
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCA], 0x0231, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0000)

        mb.cpu.setFlag(flagZ)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCA], 0x0233, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0233)

    def test_opcodeCC(self):  # CALL Z,v
        # Don't jump
        clearRegisters()
        clearFlag()
        clearStack100()


        mb.cpu.reg[PC] = 0x1512
        mb.cpu.reg[SP] = 0xFFFE

        mb[0xFFFE] = 0x00
        mb[0xFFFD] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCC], 0xFE21, 0x1512+3)  # CALL
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x1512+3)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFE)
        self.assertEqual(mb[0xFFFE], 0x00)
        self.assertEqual(mb[0xFFFD], 0x00)

        # Do jump
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setFlag(flagZ)

        mb.cpu.reg[PC] = 0x1512
        mb.cpu.reg[SP] = 0xFFFE

        mb[0xFFFE] = 0x00
        mb[0xFFFD] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCC], 0xFE21, 0x1512+3)  # CALL
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0xFE21)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFC)
        self.assertEqual(mb[0xFFFD], 0x15)
        self.assertEqual(mb[0xFFFC], 0x15)

    def test_opcodeCE(self):  # ADC A, d8
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCE], 0x10, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x20)
        testFlags(self, False, False, False, False)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setFlag(flagC)
        mb.cpu.reg[A] = 0xFE

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCE], 0x1, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x00)
        testFlags(self, True, False, True, True)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setFlag(flagN)
        mb.cpu.reg[A] = 0xF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCE], 0x1, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x10)
        testFlags(self, False, False, True, False)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setFlag(flagN)
        mb.cpu.reg[A] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCE], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x00)
        testFlags(self, True, False, False, False)

    def test_opcodeCF(self):  # RST 8
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setBC(0x00FF)
        mb.cpu.reg[SP] = 0xFFFE
        mb.cpu.reg[PC] = 0xbb02
        mb[0xFFFD] = 0x00
        mb[0xFFFE] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCF], 0x00, 0xCB01)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0008)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFE-2)
        self.assertEqual(mb[0xFFFD], 0xCB)
        self.assertEqual(mb[0xFFFC], 0x01)

    def test_opcodeCD(self):  # CALL v
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[PC] = 0x1512
        mb.cpu.reg[SP] = 0xFFFE

        mb[0xFFFE] = 0x00
        mb[0xFFFD] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCD], 0xFE21, 0x4376)  # CALL
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0xFE21)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFC)
        self.assertEqual(mb[0xFFFD], 0x43)
        self.assertEqual(mb[0xFFFC], 0x76)

    def test_opcodeD0(self):  # RET NC
        clearRegisters()
        clearFlag()
        clearStack100()

        # Setup
        mb.cpu.reg[SP] = 0xFFFE
        mb.cpu.reg[PC] = 0x15

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCD], 0xcb02, mb.cpu.reg[PC]+3)  # CALL
        mb.cpu.executeInstruction(inst)

        # Do RET
        mb.cpu.reg[PC] = 0x10
        mb.cpu.clearFlag(flagC)
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC9], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x15+3)

        # Do jump
        mb.cpu.setFlag(flagC)
        mb.cpu.reg[PC] = 0x10
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD0], 0x00, 0x0011)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x11)

        # Don't jump
        mb.cpu.clearFlag(flagC)
        mb.cpu.reg[PC] = 0x15
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCD], 0xcb02, mb.cpu.reg[PC]+3)  # CALL
        mb.cpu.executeInstruction(inst)

        mb.cpu.reg[PC] = 0x00
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD0], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x15+3)

    def test_opcodeD2(self):  # JP NC,v
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD2], 0x0231, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0231)

        mb.cpu.setFlag(flagC)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD2], 0x0233, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0231)

    def test_opcodeD5(self):  # PUS H DE ...and... POP DE (opcode D1)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setDE(0x00FF)
        mb.cpu.reg[SP] = 0xFFFE

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD5], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        mb.cpu.setDE(0x0010)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD1], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.getDE(), 0x00FF)

    def test_opcodeD4(self):  # CALL NC,v
        # Don't jump
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setFlag(flagC)

        mb.cpu.reg[PC] = 0x1512
        mb.cpu.reg[SP] = 0xFFFE

        mb[0xFFFE] = 0x00
        mb[0xFFFD] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD4], 0xFE21, 0x1512+3)  # CALL
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x1512+3)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFE)
        self.assertEqual(mb[0xFFFE], 0x00)
        self.assertEqual(mb[0xFFFD], 0x00)

        # Do jump
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[PC] = 0x1512
        mb.cpu.reg[SP] = 0xFFFE

        mb[0xFFFE] = 0x00
        mb[0xFFFD] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD4], 0xFE21, 0x1512+3)  # CALL
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0xFE21)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFC)
        self.assertEqual(mb[0xFFFD], 0x15)
        self.assertEqual(mb[0xFFFC], 0x15)

    def test_opcodeD6(self):  # SUB A, d8
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD6], 0x01, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x04)
        testFlags(self, False, True, False, False)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD6], 0x01, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0xF)
        testFlags(self, False, True, True, False)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setFlag(flagC)

        mb.cpu.reg[A] = 0x1

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD6], 0xFF, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x2)
        testFlags(self, False, True, False, True)

    def test_opcodeD7(self):  # RST 10
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setBC(0x00FF)
        mb.cpu.reg[SP] = 0xFFFE
        mb.cpu.reg[PC] = 0xbb02
        mb[0xFFFD] = 0x00
        mb[0xFFFE] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD7], 0x00, 0xCB01)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0010)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFE-2)
        self.assertEqual(mb[0xFFFD], 0xCB)
        self.assertEqual(mb[0xFFFC], 0x01)

    def test_opcodeD8(self):  # RET C
        clearRegisters()
        clearFlag()
        clearStack100()

        # Setup
        mb.cpu.reg[SP] = 0xFFFE
        mb.cpu.reg[PC] = 0x15

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCD], 0xcb02, mb.cpu.reg[PC]+3)  # CALL
        mb.cpu.executeInstruction(inst)

        # Do RET
        mb.cpu.reg[PC] = 0x10
        mb.cpu.setFlag(flagC)
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xC9], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x15+3)

        # Do jump
        mb.cpu.clearFlag(flagC)
        mb.cpu.reg[PC] = 0x10
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD8], 0x00, 0x0011)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[PC], 0x11)

        # Don't jump
        mb.cpu.setFlag(flagC)
        mb.cpu.reg[PC] = 0x15
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xCD], 0xcb02, mb.cpu.reg[PC]+3)  # CALL
        mb.cpu.executeInstruction(inst)

        mb.cpu.reg[PC] = 0x00
        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD8], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x15+3)

    def test_opcodeD9(self):  # RETI
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[SP] = 0xFFFE-2

        mb[0xFFFC] = 0x01
        mb[0xFFFD] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xD9], 0x0000, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0501)

        self.assertEqual(mb.cpu.interruptMasterEnableLatch, True)
        self.assertEqual(mb.cpu.interruptMasterEnable, True)

    def test_opcodeDA(self):  # JP C,v
        clearRegisters()
        clearFlag()
        clearStack100()

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xDA], 0x0231, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0000)

        mb.cpu.setFlag(flagC)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xDA], 0x0233, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0233)

    def test_opcodeDC(self):  # CALL C,v
        # Don't jump
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[PC] = 0x1512
        mb.cpu.reg[SP] = 0xFFFE

        mb[0xFFFE] = 0x00
        mb[0xFFFD] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xDC], 0xFE21, 0x1512+3)  # CALL
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x1512+3)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFE)
        self.assertEqual(mb[0xFFFE], 0x00)
        self.assertEqual(mb[0xFFFD], 0x00)

        # Do jump
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setFlag(flagC)

        mb.cpu.reg[PC] = 0x1512
        mb.cpu.reg[SP] = 0xFFFE

        mb[0xFFFE] = 0x00
        mb[0xFFFD] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xDC], 0xFE21, 0x1512+3)  # CALL
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0xFE21)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFC)
        self.assertEqual(mb[0xFFFD], 0x15)
        self.assertEqual(mb[0xFFFC], 0x15)

    def test_opcodeDE(self):  # SBC A, d8
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xDE], 0x10, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x0)
        testFlags(self, True, True, True, False)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setFlag(flagC)
        mb.cpu.reg[A] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xDE], 0x1, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0xFD)
        testFlags(self, False, True, False, False)

    def test_opcodeDF(self):  # RST 18
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setBC(0x00FF)
        mb.cpu.reg[SP] = 0xFFFE
        mb.cpu.reg[PC] = 0xbb02
        mb[0xFFFD] = 0x00
        mb[0xFFFE] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xDF], 0x00, 0xCB01)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0018)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFE-2)
        self.assertEqual(mb[0xFFFD], 0xCB)
        self.assertEqual(mb[0xFFFC], 0x01)

    def test_opcodeE0(self):  # LD (v), A
        # First address
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x19
        mb[0xFF01] = 0x00

        self.assertEqual(mb.cpu.reg[A], 0x19)
        self.assertEqual(mb[0xFF01], 0x00)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE0], 0x01, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x19)
        self.assertEqual(mb[0xFF01], 0x19)

        # Second address
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x45
        mb[0xFFDE] = 0x00

        self.assertEqual(mb.cpu.reg[A], 0x45)
        self.assertEqual(mb[0xFFDE], 0x00)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE0], 0xDE, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x45)
        self.assertEqual(mb[0xFFDE], 0x45)

    def test_opcodeE2(self):  # LDH(s.C),A
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x10
        mb.cpu.reg[C] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE2], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb[0xFF05], 0x10)

    def test_opcodeE5(self):  # PUSH HL ...and... POP HL (opcode E1)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setHL(0x00FF)
        mb.cpu.reg[SP] = 0xFFFE

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE5], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        mb.cpu.setHL(0x0010)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE1], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.getHL(), 0x00FF)

    def test_opcodeE6(self):  # AND A, d8
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0b00100101

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE6], 0b11010111, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, True, False)
        self.assertEqual(mb.cpu.reg[A], 0b00000101)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0b00100101

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE6], 0b0, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, True, False, True, False)
        self.assertEqual(mb.cpu.reg[A], 0b0)

        clearRegisters()
        setFlag()

        mb.cpu.reg[A] = 0b00100101

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE6], 0b0, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, True, False, True, False)
        self.assertEqual(mb.cpu.reg[A], 0b0)

    def test_opcodeE7(self):  # RST 20
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setBC(0x00FF)
        mb.cpu.reg[SP] = 0xFFFE
        mb.cpu.reg[PC] = 0xbb02
        mb[0xFFFD] = 0x00
        mb[0xFFFE] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE7], 0x00, 0xCB01)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0020)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFE-2)
        self.assertEqual(mb[0xFFFC], 0x01)
        self.assertEqual(mb[0xFFFD], 0xCB)

    def test_opcodeE8(self):  # ADC A, B
        clearRegisters()  # test simpel addition
        clearFlag()

        mb.cpu.reg[SP] = 0x0010

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE8], 0b00000001, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[SP], 0x0011)
        testFlags(self, False, False, False, False)

        clearRegisters()  # Test two's complement
        clearFlag()

        mb.cpu.reg[SP] = 10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE8], 0b11110110, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[SP], 0x0000)
        testFlags(self, False, False, False, False)

        clearRegisters()  # Carry (Side effect: Half carry)
        clearFlag()

        mb.cpu.reg[SP] = 0xFF81

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE8], 0b01111111, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[SP], 0x0000)
        testFlags(self, False, False, True, True)

        clearRegisters()  # Half carry
        clearFlag()

        mb.cpu.reg[SP] = 0x0FFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE8], 0x1, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[SP], 0x1000)
        testFlags(self, False, False, True, False)

        clearRegisters()  # Test two's complement with sub-zero result
        clearFlag()

        mb.cpu.reg[SP] = 10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE8], 0b11110101, 0x0000)
        mb.cpu.executeInstruction(inst)

        # 10 - 11 will cause underflow and make SP=0xFFFF
        self.assertEqual(mb.cpu.reg[SP], 0xFFFF)
        testFlags(self, False, False, False, False)

    def test_opcodeE9(self):  # JP(s.getHL())
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0xCAAA
        mb.cpu.setHL(0xCB01)
        mb.cpu.reg[PC] = 0xABCD

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xE9], 0x0000, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertNotEqual(mb.cpu.reg[PC], 0xCAAA)
        self.assertEqual(mb.cpu.reg[PC], 0xCB01)

    def test_opcodeEA(self):  # LD (v), A
        # self.assertEqual(False,True)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x19
        mb[0x9910] = 0x00

        self.assertEqual(mb.cpu.reg[A], 0x19)
        self.assertEqual(mb[0x9910], 0x00)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xEA], 0x9910, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x19)
        self.assertEqual(mb[0x9910], 0x19)

    def test_opcodeEE(self):  # XOR A, d8
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0b00100101

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xEE], 0b11010111, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)
        self.assertEqual(mb.cpu.reg[A], 0b11110010)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0b00100101

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xEE], 0b0, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)
        self.assertEqual(mb.cpu.reg[A], 0b00100101)

        clearRegisters()
        setFlag()

        mb.cpu.reg[A] = 0b00100101

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xEE], 0b0, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)
        self.assertEqual(mb.cpu.reg[A], 0b00100101)

        clearRegisters()
        setFlag()

        mb.cpu.reg[A] = 0b0

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xEE], 0b0, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, True, False, False, False)
        self.assertEqual(mb.cpu.reg[A], 0b0)

    def test_opcodeEF(self):  # RST 28
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setBC(0x00FF)
        mb.cpu.reg[SP] = 0xFFFE
        mb.cpu.reg[PC] = 0xbb02
        mb[0xFFFD] = 0x00
        mb[0xFFFE] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xEF], 0x00, 0xCB01)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0028)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFE-2)
        self.assertEqual(mb[0xFFFC], 0x01)
        self.assertEqual(mb[0xFFFD], 0xCB)

    def test_opcodeF0(self):  # LD (v), A
        # First address
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x00
        mb[0xFF01] = 0x35

        self.assertEqual(mb.cpu.reg[A], 0x00)
        self.assertEqual(mb[0xFF01], 0x35)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF0], 0x01, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x35)
        self.assertEqual(mb[0xFF01], 0x35)

        # Second address
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x00
        mb[0xFFDE] = 0x37

        self.assertEqual(mb.cpu.reg[A], 0x00)
        self.assertEqual(mb[0xFFDE], 0x37)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF0], 0xDE, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x37)
        self.assertEqual(mb[0xFFDE], 0x37)

    def test_opcodeF3(self):  # DI
        # Disabling already disabled
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.interruptMasterEnable = False
        mb.cpu.interruptMasterEnableLatch = False

        self.assertEqual(mb.cpu.interruptMasterEnableLatch, False)
        self.assertEqual(mb.cpu.interruptMasterEnable, False)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF3], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.interruptMasterEnableLatch, False)
        self.assertEqual(mb.cpu.interruptMasterEnable, False)

        # NOP
        inst = getInstruction(mb.cpu, opcodes.opcodes[0x00], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.interruptMasterEnableLatch, False)
        self.assertEqual(mb.cpu.interruptMasterEnable, False)

        # Disabling when enabled
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.interruptMasterEnable = True
        mb.cpu.interruptMasterEnableLatch = True

        self.assertEqual(mb.cpu.interruptMasterEnableLatch, True)
        self.assertEqual(mb.cpu.interruptMasterEnable, True)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF3], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.interruptMasterEnableLatch, False)
        self.assertEqual(mb.cpu.interruptMasterEnable, True)

        # NOP
        inst = getInstruction(mb.cpu, opcodes.opcodes[0x00], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.interruptMasterEnableLatch, False)
        self.assertEqual(mb.cpu.interruptMasterEnable, False)

    def test_opcodeF5(self):  # PUSH AF ...and... POP AF (opcode F1)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setAF(0x00FF)
        mb.cpu.reg[SP] = 0xFFFE

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF5], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        mb.cpu.setAF(0x0010)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF1], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.getAF(), 0x00FF)

    def test_opcodeF6(self):  # OR A, d8
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0b00100101

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF6], 0b11010111, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)
        self.assertEqual(mb.cpu.reg[A], 0b11110111)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0b00100101

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF6], 0b0, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)
        self.assertEqual(mb.cpu.reg[A], 0b00100101)

        clearRegisters()
        setFlag()

        mb.cpu.reg[A] = 0b00100101

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF6], 0b0, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)
        self.assertEqual(mb.cpu.reg[A], 0b00100101)

        clearRegisters()
        setFlag()

        mb.cpu.reg[A] = 0b0

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF6], 0b0, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, True, False, False, False)
        self.assertEqual(mb.cpu.reg[A], 0b0)

    def test_opcodeF7(self):  # RST 30
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setBC(0x00FF)
        mb.cpu.reg[SP] = 0xFFFE
        mb.cpu.reg[PC] = 0xbb02
        mb[0xFFFD] = 0x00
        mb[0xFFFE] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF7], 0x00, 0xCB01)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0030)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFE-2)
        self.assertEqual(mb[0xFFFC], 0x01)
        self.assertEqual(mb[0xFFFD], 0xCB)

    def test_opcodeF8(self):  # LDHL SP,v
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xFFFD] = 0x05
        mb.cpu.reg[SP] = 0xFFFA

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF8], 0x03, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0xFFFD)
        testFlags(self, False, False, False, False)

        clearRegisters()
        setFlag()

        mb[0xFFFD] = 0x05
        mb.cpu.reg[SP] = 0xFFFA

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF8], 0x03, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0xFFFD)
        testFlags(self, False, False, False, False)

        clearRegisters()
        setFlag()

        mb[0xFFF9] = 0x05
        mb.cpu.reg[SP] = 0xFFFA

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF8], 0b11111111, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.getHL(), 0xFFF9)
        testFlags(self, False, False, False, False)

    def test_opcodeF9(self):  # LD SP,HL
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xF9], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[SP], 0xCB01)

    def test_opcodeFA(self):  # LD A,(v)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xFA], 0xCB01, 0x0000)
        mb.cpu.executeInstruction(inst)
        self.assertEqual(mb.cpu.reg[A], 0x10)

    def test_opcodeFB(self):  # DI
        # Enabling when disabled
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.interruptMasterEnable = False
        mb.cpu.interruptMasterEnableLatch = False

        self.assertEqual(mb.cpu.interruptMasterEnableLatch, False)
        self.assertEqual(mb.cpu.interruptMasterEnable, False)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xFB], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.interruptMasterEnableLatch, True)
        self.assertEqual(mb.cpu.interruptMasterEnable, False)

        # NOP
        inst = getInstruction(mb.cpu, opcodes.opcodes[0x00], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.interruptMasterEnableLatch, True)
        self.assertEqual(mb.cpu.interruptMasterEnable, True)

        # Enabling when enabled
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.interruptMasterEnable = True
        mb.cpu.interruptMasterEnableLatch = True

        self.assertEqual(mb.cpu.interruptMasterEnableLatch, True)
        self.assertEqual(mb.cpu.interruptMasterEnable, True)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xFB], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.interruptMasterEnableLatch, True)
        self.assertEqual(mb.cpu.interruptMasterEnable, True)

        # NOP
        inst = getInstruction(mb.cpu, opcodes.opcodes[0x00], 0x00, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.interruptMasterEnableLatch, True)
        self.assertEqual(mb.cpu.interruptMasterEnable, True)

    def test_opcodeFE(self):  # CP A, d8
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x05

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xFE], 0x01, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x05)
        testFlags(self, False, True, False, False)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.reg[A] = 0x10

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xFE], 0x01, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x10)
        testFlags(self, False, True, True, False)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setFlag(flagC)

        mb.cpu.reg[A] = 0x1

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xFE], 0xFF, 0x0000)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[A], 0x1)
        testFlags(self, False, True, False, True)

    def test_opcodeFF(self):  # RST 38
        clearRegisters()
        clearFlag()
        clearStack100()

        mb.cpu.setBC(0x00FF)
        mb.cpu.reg[SP] = 0xFFFE
        mb.cpu.reg[PC] = 0xbb02
        mb[0xFFFD] = 0x00
        mb[0xFFFE] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0xFF], 0x00, 0xCB01)
        mb.cpu.executeInstruction(inst)

        self.assertEqual(mb.cpu.reg[PC], 0x0038)
        self.assertEqual(mb.cpu.reg[SP], 0xFFFE-2)
        self.assertEqual(mb[0xFFFC], 0x01)
        self.assertEqual(mb[0xFFFD], 0xCB)

    def test_opcodeCB00(self):  # RLC B
        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0x1)
        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            clearFlag()

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x00+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            self.assertEqual(offsetToRegister(n), 0x02)
            testFlags(self, False, False, False, False)

        setAllRegTo(0xFF)
        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            clearFlag()

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x00+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            self.assertEqual(offsetToRegister(n), 0xFF)
            testFlags(self, False, False, False, True)

        setAllRegTo(0xFF)
        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

                setFlag()

                inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x00+n], None, 0x0000)
                mb.cpu.executeInstruction(inst)

                testFlags(self, False, False, False, True)
                self.assertEqual(offsetToRegister(n), 0xFF)

        setAllRegTo(0x00)
        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

                clearFlag()

                inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x00+n], None, 0x0000)
                mb.cpu.executeInstruction(inst)

                testFlags(self, True, False, False, False)
                self.assertEqual(offsetToRegister(n), 0xFF)

    def test_opcodeCB06(self):  # RLC (HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0xF0
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x06], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, True)
        self.assertEqual(mb[0xCB01], 0xE1)

        setFlag()

        mb[0xCB01] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x06], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, True)
        self.assertEqual(mb[0xCB01], 0xFF)

        clearFlag()

        mb[0xCB01] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x06], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, True, False, False, False)

        self.assertEqual(mb[0xCB01], 0x00)

    def test_opcodeCB08(self):  # RRC B
        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0x2)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            clearFlag()

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x00+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            self.assertEqual(offsetToRegister(n), 0x01)
            testFlags(self, False, False, False, False)

        setAllRegTo(0xFF)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            clearFlag()

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x00+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            self.assertEqual(offsetToRegister(n), 0xFF)
            testFlags(self, False, False, False, True)

        setAllRegTo(0xFF)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

                setFlag()

                inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x00+n], None, 0x0000)
                mb.cpu.executeInstruction(inst)

                testFlags(self, False, False, False, True)
                self.assertEqual(offsetToRegister(n), 0xFF)

        setAllRegTo(0x00)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

                clearFlag()

                inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x00+n], None, 0x0000)
                mb.cpu.executeInstruction(inst)

                testFlags(self, True, False, False, False)
                self.assertEqual(offsetToRegister(n), 0xFF)

    def test_opcodeCB0E(self):  # RRC (HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0xF0
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x0E], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)
        self.assertEqual(mb[0xCB01], 0x78)

        setFlag()

        mb[0xCB01] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x0E], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, True)
        self.assertEqual(mb[0xCB01], 0xFF)

        clearFlag()

        mb[0xCB01] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x0E], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, True, False, False, False)

        self.assertEqual(mb[0xCB01], 0x00)

    def test_opcodeCB10(self):  # RL B
        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0x1)
        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            clearFlag()

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x10+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            self.assertEqual(offsetToRegister(n), 0x02)
            testFlags(self, False, False, False, False)

        setAllRegTo(0xFF)
        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            clearFlag()

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x10+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            self.assertEqual(offsetToRegister(n), 0xFE)
            testFlags(self, False, False, False, True)

        setAllRegTo(0xFF)
        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

                setFlag()

                inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x10+n], None, 0x0000)
                mb.cpu.executeInstruction(inst)

                testFlags(self, False, False, False, True)
                self.assertEqual(offsetToRegister(n), 0xFF)

        setAllRegTo(0x80)
        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

                clearFlag()

                inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x10+n], None, 0x0000)
                mb.cpu.executeInstruction(inst)

                testFlags(self, True, False, False, False)
                self.assertEqual(offsetToRegister(n), 0x01)

    def test_opcodeCB16(self):  # RL (HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0xF0
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x16], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, True)
        self.assertEqual(mb[0xCB01], 0xE0)

        setFlag()

        mb[0xCB01] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x16], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, True)
        self.assertEqual(mb[0xCB01], 0xFF)

        clearFlag()

        mb[0xCB01] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x16], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, True, False, False, False)

        self.assertEqual(mb[0xCB01], 0x00)

        clearFlag()
        mb.cpu.setFlag(flagC)

        mb[0xCB01] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x16], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)

        self.assertEqual(mb[0xCB01], 0x01)

    def test_opcodeCB18(self):  # RR B
        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0x2)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            clearFlag()

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x10+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            self.assertEqual(offsetToRegister(n), 0x01)
            testFlags(self, False, False, False, False)

        setAllRegTo(0xFF)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            clearFlag()

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x10+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            self.assertEqual(offsetToRegister(n), 0x7F)
            testFlags(self, False, False, False, True)

        setAllRegTo(0xFF)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

                setFlag()

                inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x10+n], None, 0x0000)
                mb.cpu.executeInstruction(inst)

                testFlags(self, False, False, False, True)
                self.assertEqual(offsetToRegister(n), 0xFF)

        setAllRegTo(0x00)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

                clearFlag()

                inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x10+n], None, 0x0000)
                mb.cpu.executeInstruction(inst)

                testFlags(self, True, False, False, False)
                self.assertEqual(offsetToRegister(n), 0x00)

        setAllRegTo(0x00)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

                clearFlag()

                inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x10+n], None, 0x0000)
                mb.cpu.executeInstruction(inst)

                testFlags(self, False, False, False, False)
                self.assertEqual(offsetToRegister(n), 0x80)

    def test_opcodeCB1E(self):  # RC (HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0xF0
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x1E], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)
        self.assertEqual(mb[0xCB01], 0x78)

        setFlag()

        mb[0xCB01] = 0xFF

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x1E], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, True)
        self.assertEqual(mb[0xCB01], 0xFF)

        clearFlag()

        mb[0xCB01] = 0x00

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x1E], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, True, False, False, False)

        self.assertEqual(mb[0xCB01], 0x00)

    def test_opcodeCB20(self):  # SLA B
        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0xFF)
        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            mb.cpu.clearFlag(flagC)

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x20+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, False, False, False, True)
            self.assertEqual(offsetToRegister(n), 0xFE)

        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0x7F)
        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x20+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, False, False, False, False)
            self.assertEqual(mb.cpu.reg[B], 0xFE)

        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0x80)
        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x20+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, True, False, False, True)
            self.assertEqual(mb.cpu.reg[B], 0x0)

        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0x0)
        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x20], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, True, False, False, False)
            self.assertEqual(mb.cpu.reg[B], 0x0)

    def test_opcodeCB26(self):  # SLA (HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0xFF
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x26], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, True)
        self.assertEqual(mb[0xCB01], 0xFE)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0x7F
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x26], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)
        self.assertEqual(mb[0xCB01], 0xFE)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0x80
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x26], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, True, False, False, True)
        self.assertEqual(mb[0xCB01], 0x0)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0x0
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x26], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, True, False, False, False)
        self.assertEqual(mb[0xCB01], 0x0)

    def test_opcodeCB28(self):  # SRA B
        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0xFF)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x20+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, False, False, False, True)
            self.assertEqual(offsetToRegister(n), 0xFF)

        clearRegisters()
        clearFlag()
        clearStack100()
        setAllRegTo(0xFE)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x20+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, False, False, False, False)
            self.assertEqual(offsetToRegister(n), 0xFF)

        clearRegisters()
        clearFlag()
        clearStack100()
        setAllRegTo(0x1)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x20+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, True, False, False, True)
            self.assertEqual(offsetToRegister(n), 0x0)

        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0x0)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x20], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, True, False, False, False)
            self.assertEqual(mb.cpu.reg[B], 0x0)

    def test_opcodeCB2E(self):  # SRA (HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0xFF
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x2E], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, True)
        self.assertEqual(mb[0xCB01], 0xFF)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0xFE
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x2E], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)
        self.assertEqual(mb[0xCB01], 0xFF)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0x1
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x2E], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, True, False, False, True)
        self.assertEqual(mb[0xCB01], 0x00)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0x0
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x2E], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, True, False, False, False)
        self.assertEqual(mb[0xCB01], 0x0)

    def test_opcodeCB30(self):  # SWAP B
        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0xFF)

        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x30+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, False, False, False, False)
            self.assertEqual(offsetToRegister(n), 0xFF)

        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0xF0)

        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x30+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, False, False, False, False)
            self.assertEqual(offsetToRegister(n), 0x0F)

        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0xF0)
        for n in range(0x0, 0x8):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x30+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, False, False, False, False)
            self.assertEqual(offsetToRegister(n), 0x0F)

    def test_opcodeCB36(self):  # SWAP (HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0xFF
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x36], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)
        self.assertEqual(mb[0xCB01], 0xFF)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0xF0
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x36], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)
        self.assertEqual(mb[0xCB01], 0x0F)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0x0F
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x36], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)
        self.assertEqual(mb[0xCB01], 0xF0)

    def test_opcodeCB38(self):  # SRL B
        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0xFF)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x30+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, False, False, False, True)
            self.assertEqual(offsetToRegister(n), 0x7F)

        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0xFE)

        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x30+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, False, False, False, False)
            self.assertEqual(offsetToRegister(n), 0x7F)

        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0x01)

        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x30+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, True, False, False, True)
            self.assertEqual(offsetToRegister(n), 0x0)

        clearRegisters()
        clearFlag()
        clearStack100()

        setAllRegTo(0x00)
        for n in range(0x8, 0xF):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x30+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            testFlags(self, True, False, False, False)
            self.assertEqual(offsetToRegister(n), 0x0)

    def test_opcodeCB3E(self):  # SRL (HL)
        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0xFF
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x3E], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, True)
        self.assertEqual(mb[0xCB01], 0x7F)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0xFE
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x3E], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, False, False, False, False)
        self.assertEqual(mb[0xCB01], 0x7F)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0x1
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x3E], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, True, False, False, True)
        self.assertEqual(mb[0xCB01], 0x00)

        clearRegisters()
        clearFlag()
        clearStack100()

        mb[0xCB01] = 0x0
        mb.cpu.setHL(0xCB01)

        inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x3E], None, 0x0000)
        mb.cpu.executeInstruction(inst)

        testFlags(self, True, False, False, False)
        self.assertEqual(mb[0xCB01], 0x0)

    def test_opcodeCB40(self):  # BIT x, R
        for n in range(8):
            # A, F, B, C, D, E, H, L
            if n == 1:  # Skip F
                continue
            else:
                mb.cpu.reg[n] = 0xFF

        for n in range(0xF * 4):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            clearFlag()
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x40+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            testFlags(self, False, False, True, False)

            clearFlag()
            mb.cpu.setFlag(flagN)  # Reset
            mb.cpu.setFlag(flagC)  # Not affected
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x40+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            testFlags(self, False, False, True, True)

        for n in range(8):
            # A, F, B, C, D, E, H, L
            if n == 1:  # Skip F
                continue
            else:
                mb.cpu.reg[n] = 0x00

        for n in range(0xF * 4):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            clearFlag()

            mb.cpu.setFlag(flagN)  # Reset
            mb.cpu.setFlag(flagC)  # Not affected

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x40+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            testFlags(self, True, False, True, True)

    def test_opcodeCB46(self):  # BIT x, (HL)
        for n in range(4):
            mb[0xCB01] = 0xFF
            mb.cpu.setHL(0xCB01)

            clearFlag()
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x46+(n*0x10)], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            testFlags(self, False, False, True, False)

        for n in range(4):
            mb[0xCB01] = 0x00
            mb.cpu.setHL(0xCB01)

            clearFlag()
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x46+(n*0x10)], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            testFlags(self, True, False, True, False)

        for n in range(4):
            mb[0xCB01] = 0xFF
            mb.cpu.setHL(0xCB01)

            clearFlag()
            mb.cpu.setFlag(flagN)  # Reset
            mb.cpu.setFlag(flagC)  # Not affected
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x46+(n*0x10)], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            testFlags(self, False, False, True, True)

    def test_opcodeCB80(self):  # RES x, R
        for n in range(8):
            # A, F, B, C, D, E, H, L
            if n == 1:  # Skip F
                continue
            else:
                mb.cpu.reg[n] = 0xFF

        for n in range(0xF * 4):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            clearFlag()
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x80+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            self.assertEqual(offsetToRegister(n), [254, 252, 248, 240, 224, 192, 128, 0][n/8])
            testFlags(self, False, False, False, False)

            mb.cpu.setFlag(flagN)  # Not affected
            mb.cpu.setFlag(flagC)  # Not affected
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x80+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            self.assertEqual(offsetToRegister(n), [254, 252, 248, 240, 224, 192, 128, 0][n/8])
            testFlags(self, False, True, False, True)

        for n in range(8):
            # A, F, B, C, D, E, H, L
            if n == 1:  # Skip F
                continue
            else:
                mb.cpu.reg[n] = 0x00

        for n in range(0xF * 4):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            setFlag()

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x80+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            self.assertEqual(offsetToRegister(n), 0)
            testFlags(self, True, True, True, True)

    def test_opcodeCB86(self):  # RES x, (HL)
        for n in [0x6, 0xE, 0x16, 0x1E, 0x26, 0x2E, 0x36, 0x3E]:
            mb[0xCB01] = 0xFF
            mb.cpu.setHL(0xCB01)

            clearFlag()
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x80+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            self.assertEqual(mb[0xCB01],  [254, 253, 251, 247, 239, 223, 191, 127][n/8])
            testFlags(self, False, False, False, False)

        for n in [0x6, 0xE, 0x16, 0x1E, 0x26, 0x2E, 0x36, 0x3E]:
            mb[0xCB01] = 0x00
            mb.cpu.setHL(0xCB01)

            clearFlag()
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x80+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            self.assertEqual(mb[0xCB01],  0)
            testFlags(self, False, False, False, False)

        for n in [0x6, 0xE, 0x16, 0x1E, 0x26, 0x2E, 0x36, 0x3E]:
            mb[0xCB01] = 0xFF
            mb.cpu.setHL(0xCB01)

            clearFlag()
            mb.cpu.setFlag(flagN)  # Reset
            mb.cpu.setFlag(flagC)  # Not affected
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0x80+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            self.assertEqual(mb[0xCB01],  [254, 253, 251, 247, 239, 223, 191, 127][n/8])
            testFlags(self, False, True, False, True)

    def test_opcodeCBC0(self):  # SET x, R
        setAllRegTo(0x00)

        for n in range(0xF * 4):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            clearFlag()

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0xC0+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)

            self.assertEqual(offsetToRegister(n), [1, 3, 7, 15, 31, 63, 127, 255][n/8])
            testFlags(self, False, False, False, False)

            mb.cpu.setFlag(flagN)  # Not affected
            mb.cpu.setFlag(flagC)  # Not affected
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0xC0+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            self.assertEqual(offsetToRegister(n), [1, 3, 7, 15, 31, 63, 127, 255][n/8])
            testFlags(self, False, True, False, True)

        setAllRegTo(0xFF)

        for n in range(0xF * 4):
            if (n % 16) == 0x6 or (n % 16) == 0xE:
                continue

            setFlag()

            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0xC0+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            self.assertEqual(offsetToRegister(n), 255)
            testFlags(self, True, True, True, True)

    def test_opcodeCBC6(self):  # SET x, (HL)
        for n in [0x6, 0xE, 0x16, 0x1E, 0x26, 0x2E, 0x36, 0x3E]:
            mb[0xCB01] = 0x00
            mb.cpu.setHL(0xCB01)

            clearFlag()
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0xC0+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            self.assertEqual(mb[0xCB01], [1, 2, 4, 8, 16, 32, 64, 128][n/8])
            testFlags(self, False, False, False, False)

        for n in [0x6, 0xE, 0x16, 0x1E, 0x26, 0x2E, 0x36, 0x3E]:
            mb[0xCB01] = 0xFF
            mb.cpu.setHL(0xCB01)

            clearFlag()
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0xC0+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            self.assertEqual(mb[0xCB01],  0xFF)
            testFlags(self, False, False, False, False)

        for n in [0x6, 0xE, 0x16, 0x1E, 0x26, 0x2E, 0x36, 0x3E]:
            mb[0xCB01] = 0x00
            mb.cpu.setHL(0xCB01)

            clearFlag()
            mb.cpu.setFlag(flagN)  # Reset
            mb.cpu.setFlag(flagC)  # Not affected
            inst = getInstruction(mb.cpu, opcodes.opcodes[0x100+0xC0+n], None, 0x0000)
            mb.cpu.executeInstruction(inst)
            self.assertEqual(mb[0xCB01], [1, 2, 4, 8, 16, 32, 64, 128][n/8])
            testFlags(self, False, True, False, True)

if __name__ == '__main__':
    unittest.main()
