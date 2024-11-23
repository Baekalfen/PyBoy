#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import re
from html.parser import HTMLParser
from urllib.request import urlopen

destination = "opcodes.py"
pxd_destination = "opcodes.pxd"

warning = """
# THIS FILE IS AUTO-GENERATED!!!
# DO NOT MODIFY THIS FILE.
# CHANGES TO THE CODE SHOULD BE MADE IN 'opcodes_gen.py'.
"""

imports = """
from pyboy import utils
import array

import pyboy
logger = pyboy.logging.get_logger(__name__)

FLAGC, FLAGH, FLAGN, FLAGZ = range(4, 8)

def BRK(cpu):
    cpu.bail = True
    cpu.mb.breakpoint_singlestep = 1
    cpu.mb.breakpoint_singlestep_latch = 0
    # NOTE: We do not increment PC
    return 0

"""

cimports = """
cimport cython
from libc.stdint cimport uint8_t, uint16_t, uint32_t

from pyboy.logging.logging cimport Logger

from . cimport cpu


cdef Logger logger

cdef uint16_t FLAGC, FLAGH, FLAGN, FLAGZ
cdef uint8_t[512] OPCODE_LENGTHS
@cython.locals(v=cython.int, a=cython.int, b=cython.int, pc=cython.ushort)
cdef int execute_opcode(cpu.CPU, uint16_t) noexcept nogil

cdef uint8_t no_opcode(cpu.CPU) noexcept nogil
cdef uint8_t BRK(cpu.CPU) noexcept nogil
"""


def inline_signed_int8(arg):
    return "(({} ^ 0x80) - 0x80)".format(arg)


opcodes = []


class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

        self.counter = 0
        self.tagstack = []

        self.cell_lines = []
        self.stop = False
        self._attrs = None
        self.founddata = False

    def handle_starttag(self, tag, attrs):
        if tag != "br":
            self.founddata = False
            self._attrs = attrs
            self.tagstack.append(tag)

    def handle_endtag(self, tag):
        if not self.founddata and self.tagstack[-1] == "td" and self.counter % 0x100 != 0:
            self.counter += 1
            opcodes.append(None)  # Blank operations
        self.tagstack.pop()

    def handle_data(self, data):
        if self.stop or len(self.tagstack) == 0:
            return

        self.founddata = True

        if self.tagstack[-1] == "td":
            self.cell_lines.append(data)

            if len(self.cell_lines) == 4:
                opcodes.append(
                    self.make_opcode(
                        self.cell_lines, ("bgcolor", "#ccffcc") in self._attrs or ("bgcolor", "#ffcccc") in self._attrs
                    )
                )
                self.counter += 1
                self.cell_lines = []

        if self.counter == 0x200:
            self.stop = True

    def make_opcode(self, lines, bit16):
        opcode = self.counter
        flags = lines.pop()
        cycles = lines.pop()
        length = lines.pop()
        name = lines.pop()

        return OpcodeData(opcode, name, length, cycles, bit16, *flags.split())


class Operand:
    def __init__(self, operand):
        self.postoperation = None
        self.pointer = False
        self.highpointer = False
        self.immediate = False
        self.signed = False
        self.is16bit = False
        self.flag = False
        self.operand = operand
        self.codegen(False)

    @property
    def set(self):
        return self.codegen(True)

    @property
    def get(self):
        return self.codegen(False)

    def codegen(self, assign, operand=None):
        if operand is None:
            operand = self.operand

        if operand == "(C)":
            self.highpointer = True
            if assign:
                return "cpu.mb.setitem(0xFF00 + cpu.C, %s)"
            else:
                return "cpu.mb.getitem(0xFF00 + cpu.C)"

        elif operand == "SP+r8":
            self.immediate = True
            self.signed = True

            # post operation set in LD handler!
            return "cpu.SP + " + inline_signed_int8("v")

        elif operand.startswith("(") and operand.endswith(")"):
            self.pointer = True
            if assign:
                code = (
                    "cpu.mb.setitem(%s"
                    % self.codegen(False, operand=re.search(r"\(([a-zA-Z]+\d*)[\+-]?\)", operand).group(1))
                    + ", %s)"
                )
            else:
                code = "cpu.mb.getitem(%s)" % self.codegen(
                    False, operand=re.search(r"\(([a-zA-Z]+\d*)[\+-]?\)", operand).group(1)
                )

            if "-" in operand or "+" in operand:
                # TODO: Replace with opcode 23 (INC HL)?
                self.postoperation = "cpu.HL %s= 1" % operand[-2]

            return code

        # Sadly, there is an overlap between the register 'C' and to
        # check for the carry flag 'C'.
        elif operand in ["A", "F", "B", "C", "D", "E", "SP", "PC", "HL"]:
            if assign:
                return "cpu." + operand + " = %s"
            else:
                return "cpu." + operand

        elif operand == "H":
            if assign:
                return "cpu.HL = (cpu.HL & 0x00FF) | (%s << 8)"
            else:
                return "(cpu.HL >> 8)"

        elif operand == "L":
            if assign:
                return "cpu.HL = (cpu.HL & 0xFF00) | (%s & 0xFF)"
            else:
                return "(cpu.HL & 0xFF)"

        elif operand in ["AF", "BC", "DE"]:
            if assign:
                return "cpu." + operand[0] + " = %s >> 8" + "\n\t" + "cpu." + operand[1] + " = %s & 0x00FF"
            else:
                return "((cpu." + operand[0] + " << 8) + cpu." + operand[1] + ")"

        elif operand in ["Z", "C", "NZ", "NC"]:  # flags
            assert not assign
            self.flag = True

            if "N" in operand:
                return f"((cpu.F & (1 << FLAG{operand[1]})) == 0)"
            else:
                return f"((cpu.F & (1 << FLAG{operand})) != 0)"
            # return "f_" + operand.lower() + "(cpu)"

        elif operand in ["d8", "d16", "a8", "a16", "r8"]:
            assert not assign
            code = "v"
            self.immediate = True

            if operand == "r8":
                code = inline_signed_int8(code)
                self.signed = True
            elif operand == "a8":
                code += " + 0xFF00"
                self.highpointer = True
            return code

        else:
            raise ValueError("Didn't match symbol: %s" % operand)


class Literal:
    def __init__(self, value):
        if isinstance(value, str) and value.find("H") > 0:
            self.value = int(value[:-1], 16)
        else:
            self.value = value
        self.code = str(self.value)
        self.immediate = False

    @property
    def get(self):
        return self.code


class Code:
    def __init__(self, function_name, opcode, name, takes_immediate, length, cycles, branch_op=False):
        self.function_name = function_name
        self.opcode = opcode
        self.name = name
        self.cycles = cycles
        self.takes_immediate = takes_immediate
        self.length = length
        self.lines = []
        self.branch_op = branch_op

    def addline(self, line):
        self.lines.append(line)

    def addlines(self, lines):
        for l in lines:
            self.lines.append(l)

    def getcode(self):
        code = ""
        code += [
            "def %s_%0.2X(cpu): # %0.2X %s" % (self.function_name, self.opcode, self.opcode, self.name),
            "def %s_%0.2X(cpu, v): # %0.2X %s" % (self.function_name, self.opcode, self.opcode, self.name),
        ][self.takes_immediate]
        code += "\n\t"

        if not self.branch_op:
            self.lines.append("cpu.PC += %d" % self.length)
            self.lines.append("cpu.PC &= 0xFFFF")
            self.lines.append("cpu.cycles += " + self.cycles[0])  # Choose the 0th cycle count

        code += "\n\t".join(self.lines)

        pxd = [
            "cdef uint8_t %s_%0.2X(cpu.CPU) noexcept nogil # %0.2X %s"
            % (self.function_name, self.opcode, self.opcode, self.name),
            # TODO: Differentiate between 16-bit values
            # (01,11,21,31 ops) and 8-bit values for 'v'
            "cdef uint8_t %s_%0.2X(cpu.CPU, int v) noexcept nogil # %0.2X %s"
            % (self.function_name, self.opcode, self.opcode, self.name),
        ][self.takes_immediate]

        if self.opcode == 0x27:
            pxd = "@cython.locals(v=int, flag=uint8_t, t=int, corr=ushort)\n" + pxd
        else:
            pxd = "@cython.locals(v=int, flag=uint8_t, t=int)\n" + pxd

        return (pxd, code)


class OpcodeData:
    def __init__(self, opcode, name, length, cycles, bit16, flag_z, flag_n, flag_h, flag_c):
        self.opcode = opcode
        self.name = name
        self.length = int(length)
        self.cycles = tuple(cycles.split("/"))
        self.flag_z = flag_z
        self.flag_n = flag_n
        self.flag_h = flag_h
        self.flag_c = flag_c
        self.flags = tuple(enumerate([self.flag_c, self.flag_h, self.flag_n, self.flag_z]))
        self.is16bit = bit16

        # TODO: There's no need for this to be so explicit
        self.functionhandlers = {
            "NOP": self.NOP,
            "HALT": self.HALT,
            "PREFIX": self.CB,
            "EI": self.EI,
            "DI": self.DI,
            "STOP": self.STOP,
            "LD": self.LD,
            "LDH": self.LDH,
            "ADD": self.ADD,
            "SUB": self.SUB,
            "INC": self.INC,
            "DEC": self.DEC,
            "ADC": self.ADC,
            "SBC": self.SBC,
            "AND": self.AND,
            "OR": self.OR,
            "XOR": self.XOR,
            "CP": self.CP,
            "PUSH": self.PUSH,
            "POP": self.POP,
            "JP": self.JP,
            "JR": self.JR,
            "CALL": self.CALL,
            "RET": self.RET,
            "RETI": self.RETI,
            "RST": self.RST,
            "DAA": self.DAA,
            "SCF": self.SCF,
            "CCF": self.CCF,
            "CPL": self.CPL,
            "RLA": self.RLA,
            "RLCA": self.RLCA,
            "RLC": self.RLC,
            "RL": self.RL,
            "RRA": self.RRA,
            "RRCA": self.RRCA,
            "RRC": self.RRC,
            "RR": self.RR,
            "SLA": self.SLA,
            "SRA": self.SRA,
            "SWAP": self.SWAP,
            "SRL": self.SRL,
            "BIT": self.BIT,
            "RES": self.RES,
            "SET": self.SET,
        }

    def createfunction(self):
        text = self.functionhandlers[self.name.split()[0]]()
        # Compensate for CB operations being "2 bytes long"
        if self.opcode > 0xFF:
            self.length -= 1
        return (self.length, "%s_%0.2X" % (self.name.split()[0], self.opcode), self.name), text

    # Special carry and half-carry for E8 and F8:
    # http://forums.nesdev.com/viewtopic.php?p=42138
    # Blargg: "Both of these set carry and half-carry based on the low
    # byte of SP added to the UNSIGNED immediate byte. The Negative
    # and Zero flags are always cleared. They also calculate SP +
    # SIGNED immediate byte and put the result into SP or HL,
    # respectively."
    def handleflags16bit_E8_F8(self, r0, r1, op, carry=False):
        flagmask = sum(map(lambda nf: (nf[1] == "-") << (nf[0] + 4), self.flags))

        # Only in case we do a dynamic operation, do we include the
        # following calculations
        if flagmask == 0b11110000:
            return ["# No flag operations"]

        lines = []
        # Sets the flags that always get set by operation
        lines.append("flag = " + format(sum(map(lambda nf: (nf[1] == "1") << (nf[0] + 4), self.flags)), "#010b"))

        # flag += (((cpu.SP & 0xF) + (v & 0xF)) > 0xF) << FLAGH
        if self.flag_h == "H":
            c = " %s ((cpu.F & (1 << FLAGC)) != 0)" % op if carry else ""
            lines.append("flag += (((%s & 0xF) %s (%s & 0xF)%s) > 0xF) << FLAGH" % (r0, op, r1, c))

        # flag += (((cpu.SP & 0xFF) + (v & 0xFF)) > 0xFF) << FLAGC
        if self.flag_c == "C":
            lines.append("flag += (((%s & 0xFF) %s (%s & 0xFF)%s) > 0xFF) << FLAGC" % (r0, op, r1, c))

        # Clears all flags affected by the operation
        lines.append("cpu.F &= " + format(flagmask, "#010b"))
        lines.append("cpu.F |= flag")
        return lines

    def handleflags16bit(self, r0, r1, op, carry=False):
        flagmask = sum(map(lambda nf: (nf[1] == "-") << (nf[0] + 4), self.flags))

        # Only in case we do a dynamic operation, do we include the
        # following calculations
        if flagmask == 0b11110000:
            return ["# No flag operations"]

        lines = []
        # Sets the ones that always get set by operation
        lines.append("flag = " + format(sum(map(lambda nf: (nf[1] == "1") << (nf[0] + 4), self.flags)), "#010b"))

        if self.flag_h == "H":
            c = " %s ((cpu.F & (1 << FLAGC)) != 0)" % op if carry else ""
            lines.append("flag += (((%s & 0xFFF) %s (%s & 0xFFF)%s) > 0xFFF) << FLAGH" % (r0, op, r1, c))

        if self.flag_c == "C":
            lines.append("flag += (t > 0xFFFF) << FLAGC")

        # Clears all flags affected by the operation
        lines.append("cpu.F &= " + format(flagmask, "#010b"))
        lines.append("cpu.F |= flag")
        return lines

    def handleflags8bit(self, r0, r1, op, carry=False):
        flagmask = sum(map(lambda nf: (nf[1] == "-") << (nf[0] + 4), self.flags))

        # Only in case we do a dynamic operation, do we include the
        # following calculations
        if flagmask == 0b11110000:
            return ["# No flag operations"]

        lines = []
        # Sets the ones that always get set by operation
        lines.append("flag = " + format(sum(map(lambda nf: (nf[1] == "1") << (nf[0] + 4), self.flags)), "#010b"))

        if self.flag_z == "Z":
            lines.append("flag += ((t & 0xFF) == 0) << FLAGZ")

        if self.flag_h == "H" and op == "-":
            c = " %s ((cpu.F & (1 << FLAGC)) != 0)" % op if carry else ""
            lines.append("flag += (((%s & 0xF) %s (%s & 0xF)%s) < 0) << FLAGH" % (r0, op, r1, c))
        elif self.flag_h == "H":
            c = " %s ((cpu.F & (1 << FLAGC)) != 0)" % op if carry else ""
            lines.append("flag += (((%s & 0xF) %s (%s & 0xF)%s) > 0xF) << FLAGH" % (r0, op, r1, c))

        if self.flag_c == "C" and op == "-":
            lines.append("flag += (t < 0) << FLAGC")
        elif self.flag_c == "C":
            lines.append("flag += (t > 0xFF) << FLAGC")

        # Clears all flags affected by the operation
        lines.append("cpu.F &= " + format(flagmask, "#010b"))
        lines.append("cpu.F |= flag")
        return lines

    ###################################################################
    #
    # MISC OPERATIONS
    #
    def NOP(self):
        code = Code(self.name.split()[0], self.opcode, self.name, 0, self.length, self.cycles)
        return code.getcode()

    def HALT(self):
        code = Code(self.name.split()[0], self.opcode, self.name, 0, self.length, self.cycles, branch_op=True)

        # TODO: Implement HALT bug.
        code.addlines(
            [
                "cpu.halted = True",
                "cpu.bail = True",
                "cpu.cycles += " + self.cycles[0],
            ]
        )
        return code.getcode()

    def CB(self):
        code = Code(self.name.split()[0], self.opcode, self.name, 0, self.length, self.cycles)
        code.addline("logger.critical('CB cannot be called!')")
        return code.getcode()

    def EI(self):
        code = Code(self.name.split()[0], self.opcode, self.name, 0, self.length, self.cycles)
        code.addlines(
            [
                "cpu.interrupt_master_enable = True",
                "cpu.bail = (cpu.interrupts_flag_register & 0b11111) & (cpu.interrupts_enabled_register & 0b11111)",
            ]
        )
        return code.getcode()

    def DI(self):
        code = Code(self.name.split()[0], self.opcode, self.name, 0, self.length, self.cycles)
        code.addline("cpu.interrupt_master_enable = False")
        return code.getcode()

    def STOP(self):
        code = Code(self.name.split()[0], self.opcode, self.name, True, self.length, self.cycles)
        code.addlines(
            [
                "if cpu.mb.cgb:",
                "    cpu.mb.switch_speed()",
                "    cpu.mb.setitem(0xFF04, 0)",
            ]
        )
        # code.addLine("raise Exception('STOP not implemented!')")
        return code.getcode()

    def DAA(self):
        left = Operand("A")
        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles)

        # http://stackoverflow.com/a/29990058/3831206
        # http://forums.nesdev.com/viewtopic.php?t=9088
        code.addlines(
            [
                "t = %s" % left.get,
                "corr = 0",
                "corr |= 0x06 if ((cpu.F & (1 << FLAGH)) != 0) else 0x00",
                "corr |= 0x60 if ((cpu.F & (1 << FLAGC)) != 0) else 0x00",
                "if (cpu.F & (1 << FLAGN)) != 0:",
                "\tt -= corr",
                "else:",
                "\tcorr |= 0x06 if (t & 0x0F) > 0x09 else 0x00",
                "\tcorr |= 0x60 if t > 0x99 else 0x00",
                "\tt += corr",
                "flag = 0",
                "flag += ((t & 0xFF) == 0) << FLAGZ",
                "flag += (corr & 0x60 != 0) << FLAGC",
                "cpu.F &= 0b01000000",
                "cpu.F |= flag",
                "t &= 0xFF",
                left.set % "t",
            ]
        )
        return code.getcode()

    def SCF(self):
        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles)
        code.addlines(self.handleflags8bit(None, None, None))
        return code.getcode()

    def CCF(self):
        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles)
        code.addlines(
            [
                "flag = (cpu.F & 0b00010000) ^ 0b00010000",
                "cpu.F &= 0b10000000",
                "cpu.F |= flag",
            ]
        )
        return code.getcode()

    def CPL(self):
        left = Operand("A")
        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles)
        code.addline(left.set % ("(~%s) & 0xFF" % left.get))
        code.addlines(self.handleflags8bit(None, None, None))
        return code.getcode()

    ###################################################################
    #
    # LOAD OPERATIONS
    #
    def LD(self):
        r0, r1 = self.name.split()[1].split(",")
        left = Operand(r0)
        right = Operand(r1)

        # FIX: There seems to be a wrong opcode length on E2 and F2
        if self.opcode == 0xE2 or self.opcode == 0xF2:
            self.length = 1

        code = Code(
            self.name.split()[0], self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles
        )

        # These opcodes can be observed reading mid-cycle
        if self.opcode == 0x36:
            code.addline("cpu.cycles += 4")
            code.cycles = (str(int(code.cycles[0]) - 4),)
        elif self.opcode == 0xE0:
            code.addline("cpu.cycles += 4")
            code.cycles = (str(int(code.cycles[0]) - 4),)
        elif self.opcode == 0xEA:
            code.addline("cpu.cycles += 8")
            code.cycles = (str(int(code.cycles[0]) - 8),)
        elif self.opcode == 0xF0:
            code.addline("cpu.cycles += 4")
            code.cycles = (str(int(code.cycles[0]) - 4),)
        elif self.opcode == 0xFA:
            code.addline("cpu.cycles += 8")
            code.cycles = (str(int(code.cycles[0]) - 8),)

        if self.is16bit and left.immediate and left.pointer:
            code.addline(left.set % ("%s & 0xFF" % right.get))
            a, b = left.set.split(",")
            code.addline((a + "+1," + b) % ("%s >> 8" % right.get))
        else:
            # Special handling of AF, BC, DE
            # print(left.set, right.get, hex(self.opcode))
            if left.set.count("%") > 1:
                code.addline(left.set % (right.get, right.get))
            else:
                code.addline(left.set % right.get)

        # Special HL-only operations
        if left.postoperation is not None:
            code.addline(left.postoperation)
            code.addline("cpu.HL &= 0xFFFF")
        elif right.postoperation is not None:
            code.addline(right.postoperation)
            code.addline("cpu.HL &= 0xFFFF")
        elif self.opcode == 0xF8:
            # E8 and F8 http://forums.nesdev.com/viewtopic.php?p=42138
            code.addline("t = cpu.HL")
            code.addlines(self.handleflags16bit_E8_F8("cpu.SP", "v", "+", False))
            code.addline("cpu.HL &= 0xFFFF")

        return code.getcode()

    def LDH(self):
        return self.LD()

    ###################################################################
    #
    # ALU OPERATIONS
    #
    def ALU(self, left, right, op, carry=False):
        lines = []

        left.assign = False
        right.assign = False
        calc = " ".join(["t", "=", left.get, op, right.get])

        if carry:
            calc += " " + op + " ((cpu.F & (1 << FLAGC)) != 0)"

        lines.append(calc)

        if self.opcode == 0xE8:
            # E8 and F8 http://forums.nesdev.com/viewtopic.php?p=42138
            lines.extend(self.handleflags16bit_E8_F8(left.get, "v", op, carry))
            lines.append("t &= 0xFFFF")
        elif self.is16bit:
            lines.extend(self.handleflags16bit(left.get, right.get, op, carry))
            lines.append("t &= 0xFFFF")
        else:
            lines.extend(self.handleflags8bit(left.get, right.get, op, carry))
            lines.append("t &= 0xFF")

        # HAS TO BE THE LAST INSTRUCTION BECAUSE OF CP!
        if left.set.count("%") > 1:
            lines.append(left.set % ("t", "t"))
        else:
            lines.append(left.set % "t")
        return lines

    def ADD(self):
        if self.name.find(",") > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = Operand("A")
            right = Operand(r1)

        code = Code(
            self.name.split()[0], self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles
        )
        code.addlines(self.ALU(left, right, "+"))
        return code.getcode()

    def SUB(self):
        if self.name.find(",") > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = Operand("A")
            right = Operand(r1)

        code = Code(
            self.name.split()[0], self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles
        )
        code.addlines(self.ALU(left, right, "-"))
        return code.getcode()

    def INC(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        right = Literal(1)

        code = Code(
            self.name.split()[0], self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles
        )
        code.addlines(self.ALU(left, right, "+"))

        if self.opcode == 0x34:
            # HACK: Offset the timing by 4 cycles
            # TODO: Probably should be generalized
            code.lines.insert(-1, "cpu.cycles += 4")  # Inject before read
            code.cycles = ("8",)  # 12 - 4

        return code.getcode()

    def DEC(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        right = Literal(1)

        code = Code(
            self.name.split()[0], self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles
        )
        code.addlines(self.ALU(left, right, "-"))

        if self.opcode == 0x35:
            # HACK: Offset the timing by 4 cycles
            # TODO: Probably should be generalized
            code.lines.insert(-1, "cpu.cycles += 4")  # Inject before write
            code.cycles = ("8",)  # 12 - 4

        return code.getcode()

    def ADC(self):
        if self.name.find(",") > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = Operand("A")
            right = Operand(r1)

        code = Code(
            self.name.split()[0], self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles
        )
        code.addlines(self.ALU(left, right, "+", carry=True))
        return code.getcode()

    def SBC(self):
        if self.name.find(",") > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = Operand("A")
            right = Operand(r1)

        code = Code(
            self.name.split()[0], self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles
        )
        code.addlines(self.ALU(left, right, "-", carry=True))
        return code.getcode()

    def AND(self):
        if self.name.find(",") > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = Operand("A")
            right = Operand(r1)

        code = Code(
            self.name.split()[0], self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles
        )
        code.addlines(self.ALU(left, right, "&"))
        return code.getcode()

    def OR(self):
        if self.name.find(",") > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = Operand("A")
            right = Operand(r1)

        code = Code(
            self.name.split()[0], self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles
        )
        code.addlines(self.ALU(left, right, "|"))
        return code.getcode()

    def XOR(self):
        if self.name.find(",") > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = Operand("A")
            right = Operand(r1)

        code = Code(
            self.name.split()[0], self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles
        )
        code.addlines(self.ALU(left, right, "^"))
        return code.getcode()

    def CP(self):
        r1 = self.name.split()[1]
        left = Operand("A")
        right = Operand(r1)

        code = Code(
            self.name.split()[0], self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles
        )
        # CP is equal to SUB, but without saving the result.
        # Therefore; we discard the last instruction.
        code.addlines(self.ALU(left, right, "-")[:-1])
        return code.getcode()

    ###################################################################
    #
    # PUSH/POP OPERATIONS
    #
    def PUSH(self):
        r0 = self.name.split()[1]
        left = Operand(r0)

        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles)
        if "HL" in left.get:
            code.addlines(
                [
                    "cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.HL >> 8) # High",
                    "cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.HL & 0xFF) # Low",
                    "cpu.SP -= 2",
                    "cpu.SP &= 0xFFFF",
                ]
            )
        else:
            # A bit of a hack, but you can only push double registers
            code.addline("cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.%s) # High" % left.operand[-2])
            if left.operand == "AF":
                # by taking fx 'A' and 'F' directly, we save calculations
                code.addline("cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.%s & 0xF0) # Low" % left.operand[-1])
            else:
                # by taking fx 'A' and 'F' directly, we save calculations
                code.addline("cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.%s) # Low" % left.operand[-1])
            code.addline("cpu.SP -= 2")
            code.addline("cpu.SP &= 0xFFFF")

        return code.getcode()

    def POP(self):
        r0 = self.name.split()[1]
        left = Operand(r0)

        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles)
        if "HL" in left.get:
            code.addlines(
                [
                    (left.set % "(cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8) + " "cpu.mb.getitem(cpu.SP)") + " # High",
                    "cpu.SP += 2",
                    "cpu.SP &= 0xFFFF",
                ]
            )
        else:
            if left.operand.endswith("F"):  # Catching AF
                fmask = " & 0xF0"
            else:
                fmask = ""
            # See comment from PUSH
            code.addline("cpu.%s = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) # High" % left.operand[-2])
            if left.operand == "AF":
                code.addline("cpu.%s = cpu.mb.getitem(cpu.SP)%s & 0xF0 # Low" % (left.operand[-1], fmask))
            else:
                code.addline("cpu.%s = cpu.mb.getitem(cpu.SP)%s # Low" % (left.operand[-1], fmask))
            code.addline("cpu.SP += 2")
            code.addline("cpu.SP &= 0xFFFF")

        return code.getcode()

    ###################################################################
    #
    # CONTROL FLOW OPERATIONS
    #
    def JP(self):
        if self.name.find(",") > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = None
            right = Operand(r1)

        r_code = right.get
        if left is not None:
            l_code = left.get
            if l_code.endswith("C") and "NC" not in l_code:
                left.flag = True
                l_code = "((cpu.F & (1 << FLAGC)) != 0)"
            assert left.flag
        elif right.pointer:
            # FIX: Wrongful syntax of "JP (HL)" actually meaning "JP HL"
            right.pointer = False
            r_code = right.codegen(False, operand="HL")
        else:
            assert right.immediate

        code = Code(
            self.name.split()[0], self.opcode, self.name, right.immediate, self.length, self.cycles, branch_op=True
        )
        if left is None:
            code.addlines(["cpu.PC = %s" % ("v" if right.immediate else r_code), "cpu.cycles += " + self.cycles[0]])
        else:
            code.addlines(
                [
                    "if %s:" % l_code,
                    "\tcpu.PC = %s" % ("v" if right.immediate else r_code),
                    "\tcpu.cycles += " + self.cycles[0],
                    "else:",
                    "\tcpu.PC += %s" % self.length,
                    "\tcpu.PC &= 0xFFFF",
                    "\tcpu.cycles += " + self.cycles[1],
                ]
            )

        return code.getcode()

    def JR(self):
        if self.name.find(",") > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = None
            right = Operand(r1)

        if left is not None:
            l_code = left.get
            if l_code.endswith("C") and "NC" not in l_code:
                left.flag = True
                l_code = "((cpu.F & (1 << FLAGC)) != 0)"
            assert left.flag
        assert right.immediate

        code = Code(
            self.name.split()[0], self.opcode, self.name, right.immediate, self.length, self.cycles, branch_op=True
        )
        if left is None:
            code.addlines(
                [
                    "cpu.PC += %d + " % self.length + inline_signed_int8("v"),
                    "cpu.PC &= 0xFFFF",
                    "cpu.cycles += " + self.cycles[0],
                ]
            )
        else:
            code.addlines(
                [
                    "cpu.PC += %d" % self.length,
                    "if %s:" % l_code,
                    "\tcpu.PC += " + inline_signed_int8("v"),
                    "\tcpu.PC &= 0xFFFF",
                    "\tcpu.cycles += " + self.cycles[0],
                    "else:",
                    "\tcpu.PC &= 0xFFFF",
                    "\tcpu.cycles += " + self.cycles[1],
                ]
            )

        return code.getcode()

    def CALL(self):
        if self.name.find(",") > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = None
            right = Operand(r1)

        if left is not None:
            l_code = left.get
            if l_code.endswith("C") and "NC" not in l_code:
                left.flag = True
                l_code = "((cpu.F & (1 << FLAGC)) != 0)"
            assert left.flag
        assert right.immediate

        code = Code(
            self.name.split()[0], self.opcode, self.name, right.immediate, self.length, self.cycles, branch_op=True
        )

        # Taken from PUSH
        code.addlines(
            [
                "cpu.PC += %s" % self.length,
                "cpu.PC &= 0xFFFF",
            ]
        )

        if left is None:
            code.addlines(
                [
                    "cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High",
                    "cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low",
                    "cpu.SP -= 2",
                    "cpu.SP &= 0xFFFF",
                    "cpu.PC = %s" % ("v" if right.immediate else right.get),
                    "cpu.cycles += " + self.cycles[0],
                ]
            )
        else:
            code.addlines(
                [
                    "if %s:" % l_code,
                    "\tcpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High",
                    "\tcpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low",
                    "\tcpu.SP -= 2",
                    "\tcpu.SP &= 0xFFFF",
                    "\tcpu.PC = %s" % ("v" if right.immediate else right.get),
                    "\tcpu.cycles += " + self.cycles[0],
                    "else:",
                    "\tcpu.cycles += " + self.cycles[1],
                ]
            )

        return code.getcode()

    def RET(self):
        if self.name == "RET":
            left = None
        else:
            r0 = self.name.split()[1]
            left = Operand(r0)

            l_code = left.get
            if left is not None:
                if l_code.endswith("C") and "NC" not in l_code:
                    left.flag = True
                    l_code = "((cpu.F & (1 << FLAGC)) != 0)"
                assert left.flag

        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles, branch_op=True)
        if left is None:
            code.addlines(
                [
                    "cpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High",
                    "cpu.PC |= cpu.mb.getitem(cpu.SP) # Low",
                    "cpu.SP += 2",
                    "cpu.SP &= 0xFFFF",
                    "cpu.cycles += " + self.cycles[0],
                ]
            )
        else:
            code.addlines(
                [
                    "if %s:" % l_code,
                    "\tcpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High",
                    "\tcpu.PC |= cpu.mb.getitem(cpu.SP) # Low",
                    "\tcpu.SP += 2",
                    "\tcpu.SP &= 0xFFFF",
                    "\tcpu.cycles += " + self.cycles[0],
                    "else:",
                    "\tcpu.PC += %s" % self.length,
                    "\tcpu.PC &= 0xFFFF",
                    "\tcpu.cycles += " + self.cycles[1],
                ]
            )

        return code.getcode()

    def RETI(self):
        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles, branch_op=True)
        code.addlines(
            [
                "cpu.interrupt_master_enable = True",
                "cpu.bail = (cpu.interrupts_flag_register & 0b11111) & (cpu.interrupts_enabled_register & 0b11111)",
                "cpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High",
                "cpu.PC |= cpu.mb.getitem(cpu.SP) # Low",
                "cpu.SP += 2",
                "cpu.SP &= 0xFFFF",
                "cpu.cycles += " + self.cycles[0],
            ]
        )

        return code.getcode()

    def RST(self):
        r1 = self.name.split()[1]
        right = Literal(r1)

        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles, branch_op=True)

        # Taken from PUSH and CALL
        code.addlines(
            [
                "cpu.PC += %s" % self.length,
                "cpu.PC &= 0xFFFF",
                "cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High",
                "cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low",
                "cpu.SP -= 2",
                "cpu.SP &= 0xFFFF",
            ]
        )

        code.addlines(
            [
                "cpu.PC = %s" % (right.code),
                "cpu.cycles += " + self.cycles[0],
            ]
        )

        return code.getcode()

    ###################################################################
    #
    # ROTATE/SHIFT OPERATIONS
    #
    def rotateleft(self, name, left, throughcarry=False):
        code = Code(name, self.opcode, self.name, False, self.length, self.cycles)
        left.assign = False
        if throughcarry:
            code.addline(("t = (%s << 1)" % left.get) + " + ((cpu.F & (1 << FLAGC)) != 0)")
        else:
            code.addline("t = (%s << 1) + (%s >> 7)" % (left.get, left.get))
        code.addlines(self.handleflags8bit(left.get, None, None, throughcarry))
        code.addline("t &= 0xFF")
        left.assign = True

        if left.operand == "(HL)":
            # HACK: Offset the timing by 4 cycles
            # TODO: Probably should be generalized
            code.lines.insert(0, "cpu.cycles += 4")  # Inject before read
            code.addline("cpu.cycles += 4")
            code.cycles = ("8",)  # 16 - 4 - 4

        code.addline(left.set % "t")
        return code

    def RLA(self):
        left = Operand("A")
        code = self.rotateleft(self.name.split()[0], left, throughcarry=True)
        return code.getcode()

    def RLCA(self):
        left = Operand("A")
        code = self.rotateleft(self.name.split()[0], left)
        return code.getcode()

    def RLC(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        code = self.rotateleft(self.name.split()[0], left)
        return code.getcode()

    def RL(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        code = self.rotateleft(self.name.split()[0], left, throughcarry=True)
        return code.getcode()

    def rotateright(self, name, left, throughcarry=False):
        code = Code(name, self.opcode, self.name, False, self.length, self.cycles)
        left.assign = False
        if throughcarry:
            # Trigger "overflow" for carry flag
            code.addline(
                ("t = (%s >> 1)" % left.get)
                + " + (((cpu.F & (1 << FLAGC)) != 0) << 7)"
                + " + ((%s & 1) << 8)" % (left.get)
            )
        else:
            # Trigger "overflow" for carry flag
            code.addline("t = (%s >> 1) + ((%s & 1) << 7)" % (left.get, left.get) + " + ((%s & 1) << 8)" % (left.get))
        code.addlines(self.handleflags8bit(left.get, None, None, throughcarry))
        code.addline("t &= 0xFF")

        if left.operand == "(HL)":
            # HACK: Offset the timing by 4 cycles
            # TODO: Probably should be generalized
            code.lines.insert(0, "cpu.cycles += 4")  # Inject before read
            code.addline("cpu.cycles += 4")
            code.cycles = ("8",)  # 16 - 4 - 4

        code.addline(left.set % "t")
        return code

    def RRA(self):
        left = Operand("A")
        code = self.rotateright(self.name.split()[0], left, throughcarry=True)
        return code.getcode()

    def RRCA(self):
        left = Operand("A")
        code = self.rotateright(self.name.split()[0], left)
        return code.getcode()

    def RRC(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        code = self.rotateright(self.name.split()[0], left)
        return code.getcode()

    def RR(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        code = self.rotateright(self.name.split()[0], left, throughcarry=True)
        return code.getcode()

    def SLA(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles)
        code.addline("t = (%s << 1)" % left.get)
        code.addlines(self.handleflags8bit(left.get, None, None, False))
        code.addline("t &= 0xFF")

        if left.operand == "(HL)":
            # HACK: Offset the timing by 4 cycles
            # TODO: Probably should be generalized
            code.lines.insert(0, "cpu.cycles += 4")  # Inject before read
            code.addline("cpu.cycles += 4")
            code.cycles = ("8",)  # 16 - 4 - 4

        code.addline(left.set % "t")
        return code.getcode()

    def SRA(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        # FIX: All documentation tells it should have carry enabled
        self.flag_c = "C"
        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles)
        # Actual shift / MSB unchanged / Trigger "overflow" for carry flag
        code.addline("t = ((%s >> 1) | (%s & 0x80)) + ((%s & 1) << 8)" % (left.get, left.get, left.get))
        code.addlines(self.handleflags8bit(left.get, None, None, False))
        code.addline("t &= 0xFF")

        if left.operand == "(HL)":
            # HACK: Offset the timing by 4 cycles
            # TODO: Probably should be generalized
            code.lines.insert(0, "cpu.cycles += 4")  # Inject before read
            code.addline("cpu.cycles += 4")
            code.cycles = ("8",)  # 16 - 4 - 4

        code.addline(left.set % "t")
        return code.getcode()

    def SRL(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles)
        #              Actual shift / Trigger "overflow" for carry flag
        code.addline("t = (%s >> 1) + ((%s & 1) << 8)" % (left.get, left.get))
        code.addlines(self.handleflags8bit(left.get, None, None, False))
        code.addline("t &= 0xFF")

        if left.operand == "(HL)":
            # HACK: Offset the timing by 4 cycles
            # TODO: Probably should be generalized
            code.lines.insert(0, "cpu.cycles += 4")  # Inject before read
            code.addline("cpu.cycles += 4")
            code.cycles = ("8",)  # 16 - 4 - 4

        code.addline(left.set % "t")
        return code.getcode()

    def SWAP(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles)
        code.addline("t = ((%s & 0xF0) >> 4) | ((%s & 0x0F) << 4)" % (left.get, left.get))
        code.addlines(self.handleflags8bit(left.get, None, None, False))
        code.addline("t &= 0xFF")

        if left.operand == "(HL)":
            # HACK: Offset the timing by 4 cycles
            # TODO: Probably should be generalized
            code.lines.insert(0, "cpu.cycles += 4")  # Inject before read
            code.addline("cpu.cycles += 4")
            code.cycles = ("8",)  # 16 - 4 - 4

        code.addline(left.set % "t")
        return code.getcode()

    ###################################################################
    #
    # BIT OPERATIONS
    #
    def BIT(self):
        r0, r1 = self.name.split()[1].split(",")
        left = Literal(r0)
        right = Operand(r1)
        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles)

        # FIX: Correct cycle count is 12, not 16!
        if right.operand == "(HL)":
            # HACK: Offset the timing by 4 cycles
            # TODO: Probably should be generalized
            code.addline("cpu.cycles += 4")
            code.cycles = ("8",)  # 12 - 4

        code.addline("t = %s & (1 << %s)" % (right.get, left.get))
        code.addlines(self.handleflags8bit(left.get, right.get, None, False))

        return code.getcode()

    def RES(self):
        r0, r1 = self.name.split()[1].split(",")
        left = Literal(r0)
        right = Operand(r1)

        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles)
        code.addline("t = %s & ~(1 << %s)" % (right.get, left.get))

        if right.operand == "(HL)":
            # HACK: Offset the timing by 4 cycles
            # TODO: Probably should be generalized
            code.lines.insert(0, "cpu.cycles += 4")  # Inject before read
            code.addline("cpu.cycles += 4")
            code.cycles = ("8",)  # 16 - 4 - 4

        code.addline(right.set % "t")
        return code.getcode()

    def SET(self):
        r0, r1 = self.name.split()[1].split(",")
        left = Literal(r0)
        right = Operand(r1)
        code = Code(self.name.split()[0], self.opcode, self.name, False, self.length, self.cycles)
        code.addline("t = %s | (1 << %s)" % (right.get, left.get))

        if right.operand == "(HL)":
            # HACK: Offset the timing by 4 cycles
            # TODO: Probably should be generalized
            code.lines.insert(0, "cpu.cycles += 4")  # Inject before read
            code.addline("cpu.cycles += 4")
            code.cycles = ("8",)  # 16 - 4 - 4

        code.addline(right.set % "t")
        return code.getcode()


def update():
    response = urlopen("http://pastraiser.com/cpu/gameboy/gameboy_opcodes.html")
    html = response.read().replace(b"&nbsp;", b"<br>").decode()

    parser = MyHTMLParser()
    parser.feed(html)

    opcodefunctions = map(lambda x: (None, None) if x is None else x.createfunction(), opcodes)

    with open(destination, "w") as f, open(pxd_destination, "w") as f_pxd:
        f.write(warning)
        f.write(imports)
        f_pxd.write(warning)
        f_pxd.write(cimports)
        lookuplist = []
        for lookuptuple, code in opcodefunctions:
            lookuplist.append(lookuptuple)

            if code is None:
                continue

            (pxd, functiontext) = code

            # breakpoint()
            f_pxd.write(pxd + "\n")
            f.write(functiontext.replace("\t", " " * 4) + "\n\n\n")

        # We create a new opcode to use as a software breakpoint instruction.
        # I hope the irony of the opcode number is not lost.
        lookuplist[0xDB] = (1, "BRK", "Breakpoint/Illegal opcode")

        f.write("def no_opcode(cpu):\n    return 0\n\n\n")

        f.write(
            """
def execute_opcode(cpu, opcode):
    oplen = OPCODE_LENGTHS[opcode]
    v = 0
    pc = cpu.PC
    if oplen == 2:
        # 8-bit immediate
        v = cpu.mb.getitem(pc+1)
    elif oplen == 3:
        # 16-bit immediate
        # Flips order of values due to big-endian
        a = cpu.mb.getitem(pc+2)
        b = cpu.mb.getitem(pc+1)
        v = (a << 8) + b

"""
        )

        indent = 4
        for i, t in enumerate(lookuplist):
            t = t if t is not None else (0, "no_opcode", "")
            f.write(
                " " * indent
                + ("if" if i == 0 else "elif")
                + " opcode == 0x%0.2X:\n" % i
                + " " * (indent + 4)
                + "return "
                + str(t[1]).replace("'", "")
                + ("(cpu)" if t[0] <= 1 else "(cpu, v)")
                + "\n"
            )
        f.write("\n\n")

        f.write('OPCODE_LENGTHS = array.array("B", [\n    ')
        for i, t in enumerate(lookuplist):
            t = t if t is not None else (0, "no_opcode", "")
            f.write(str(t[0]).replace("'", "") + ",")
            if (i + 1) % 16 == 0:
                f.write("\n" + " " * 4)
            else:
                f.write(" ")

        f.write("])\n")

        f.write("\n\n")
        f.write("CPU_COMMANDS = [\n    ")
        for _, t in enumerate(lookuplist):
            t = t if t is not None else (0, "no_opcode", "")
            f.write(f'"{t[2]}",\n' + " " * 4)

        f.write("]\n")


def load():
    # if os.path.exists(destination):
    #     return
    update()


if __name__ == "__main__":
    load()
