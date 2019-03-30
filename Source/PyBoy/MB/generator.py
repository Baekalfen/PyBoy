# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pdb
import inspect
import os
import urllib2
import re
from HTMLParser import HTMLParser

destination = "opcodes.py"
pxd_destination = "opcodes.pxd"

warning = """\
# -*- encoding: utf-8 -*-
# THIS FILE IS AUTO-GENERATED!!!
# DO NOT MODIFY THIS FILE.
# CHANGES TO THE CODE SHOULD BE MADE IN 'generator.py'.
"""

# from registers import A, B, C, D, E, H, L, SP, PC
# from flags import flagZ, flagN, flagH, flagC
imports = """
import array
flagC, flagH, flagN, flagZ = range(4, 8)
# from flags import flagZ, flagN, flagH, flagC

"""

cimports = """
cimport CPU
cimport cython
from libc.stdint cimport uint8_t, uint16_t, uint32_t

cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef uint16_t flagC, flagH, flagN, flagZ
cdef uint8_t[512] opcodeLengths
cdef uint16_t getOpcodeLength(uint16_t)
@cython.locals(v=cython.int, a=cython.int, b=cython.int, pc=cython.ushort)
cdef int executeOpcode(CPU.CPU, uint16_t)


cdef unsigned char NOOPCODE(CPU.CPU) except -1
"""

def inlineGetSignedInt8(arg):
    return "(({} ^ 0x80) - 128)".format(arg)


opcodes = []

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

        self.counter = 0
        self.tagStack = []

        self.cellLines = []
        self.stop = False
        self._attrs = None


    def handle_starttag(self, tag, attrs):
        if tag != "br":
            self.foundData = False
            self._attrs = attrs
            self.tagStack.append(tag)

    def handle_endtag(self, tag):
        if not self.foundData and self.tagStack[-1] == "td" and self.counter % 0x100 != 0:
            self.counter += 1
            opcodes.append(None) # Blank operations

        self.tagStack.pop()

    def handle_data(self, data):
        if self.stop:
            return

        if len(self.tagStack) == 0:
            return

        self.foundData = True

        if  self.tagStack[-1] == "td":
            self.cellLines.append(data)

            if len(self.cellLines) == 4:
                opcodes.append(
                        self.makeOpcode(
                            self.cellLines,
                            ('bgcolor', '#ccffcc') in self._attrs or
                            ('bgcolor', '#ffcccc') in self._attrs
                        )
                )
                self.counter += 1
                self.cellLines = []

        if self.counter == 0x200:
            self.stop = True

    def makeOpcode(self, lines, bit16):
        opcode = self.counter
        flags = lines.pop()
        cycles = lines.pop()
        length = lines.pop()
        name = lines.pop()

        return opcodeData(opcode, name, length, cycles, bit16, *flags.split())





fname = lambda: inspect.stack()[1][3] # Try [1][3] if it doesn't work

class Operand(object):
    def __init__(self, operand):
        self.postOperation = None
        self.pointer = False
        self.highPointer = False
        self.immediate = False
        self.signed = False
        self.is16BitOp = False
        self.flag = False
        self.operand = operand
        self._get() # Does some initialization

    def _set(self):
        return self.codeGen(True)

    def _get(self):
        return self.codeGen(False)

    def codeGen(self, assign, operand=None):
        if operand is None:
            operand = self.operand

        if operand == "(C)":
            self.highPointer = True
            if assign:
                return "cpu.mb.setitem(0xFF00 + cpu.C, %s)"
            else:
                return "cpu.mb.getitem(0xFF00 + cpu.C)"

        elif operand == "SP+r8":
            self.immediate = True
            self.signed = True

            # post operation set in LD handler!
            return "cpu.SP + " + inlineGetSignedInt8("v")

        elif operand[0] == '(' and operand[-1] == ')':
            self.pointer = True
            if assign:
                code = "cpu.mb.setitem(%s" % self.codeGen(False, operand=re.search('\(([a-zA-Z]+\d*)[\+-]?\)', operand).group(1)) + ", %s)"
            else:
                code = "cpu.mb.getitem(%s)" % self.codeGen(False, operand=re.search('\(([a-zA-Z]+\d*)[\+-]?\)', operand).group(1))

            if '-' in operand or '+' in operand:
                self.postOperation = "cpu.HL %s= 1" % operand[-2] # TODO: Replace with opcode 23 (INC HL)?

            return code

        # Sadly, there is an overlap between the register 'C' and to check for the carry flag 'C'.
        elif operand in [
                'A', 'F', 'B', 'C', 'D', 'E', # registers
                'SP', 'PC', 'HL' # double registers
                ]:
            if assign:
                return "cpu." + operand + " = %s"
            else:
                return "cpu." + operand
        elif operand == 'H':
            if assign:
                return "cpu.HL = (cpu.HL & 0x00FF) | (%s << 8)"
            else:
                return "(cpu.HL >> 8)"

        elif operand == 'L':
            if assign:
                return "cpu.HL = (cpu.HL & 0xFF00) | (%s & 0xFF)"
            else:
                return "(cpu.HL & 0xFF)"

        elif operand in ['AF', 'BC', 'DE']:
            if assign:
                return "cpu.set" + operand + "(%s)"
            else:
                return "((cpu." + operand[0] + " << 8) + cpu." + operand[1] + ")"
        elif operand in [
                'Z', 'C', 'NZ', 'NC' # flags
                ]:
            assert not assign
            self.flag = True
            return "cpu.f"+operand+"()"

        elif operand in ['d8', 'd16', 'a8', 'a16', 'r8']:
            assert not assign
            code = "v"
            self.immediate = True

            if operand == 'r8':
                code = inlineGetSignedInt8(code)
                self.signed = True

            elif operand == 'a8':
                code += " + 0xFF00"
                self.highPointer = True

            return code
        else:
            raise Exception("Didn't match symbol: %s" % operand)

    get = property(_get)
    set = property(_set)


class Literal():
    def __init__(self, value):
        if isinstance(value, str) and value.find('H') > 0:
            self.value = int(value[:-1], 16)
        else:
            self.value = value
        self.code = str(self.value)
        self.immediate = False

    get = property(lambda s: s.code)

class Code():
    def __init__(self, functionName, opcode, name, takesImmediate, length, cycles, branchOp = False):
        self.functionName = functionName
        self.opcode = opcode
        self.name = name
        self.cycles = cycles
        self.takesImmediate = takesImmediate
        self.length = length
        self.lines = []
        self.branchOp = branchOp

    def addLine(self, line):
        self.lines.append(line)

    def addLines(self, lines):
        for l in lines:
            self.lines.append(l)

    def getCode(self):
        code = ""
        code += [
            "def %s_%0.2x(cpu): # %0.2x %s" % (self.functionName, self.opcode, self.opcode, self.name),
            "def %s_%0.2x(cpu, v): # %0.2x %s" % (self.functionName, self.opcode, self.opcode, self.name)
        ][self.takesImmediate]
        code += "\n\t"

        if not self.branchOp:
            self.lines.append("cpu.PC += %d" % self.length)
            self.lines.append("return " + self.cycles[0]) # Choose the 0th cycle count

        code += "\n\t".join(self.lines)


        pxd = [
            "cdef unsigned char %s_%0.2x(CPU.CPU) except -1 # %0.2x %s" % (self.functionName, self.opcode, self.opcode, self.name),
            # TODO: Differentiate between 16-bit values (01,11,21,31 ops) and 8-bit values for 'v'
            "cdef unsigned char %s_%0.2x(CPU.CPU, int v) except -1 # %0.2x %s" % (self.functionName, self.opcode, self.opcode, self.name)
        ][self.takesImmediate]

        if self.opcode == 0x27:
            pxd = "@cython.locals(v=int, flag=uchar, t=int, corr=ushort)\n" + pxd
        else:
            pxd = "@cython.locals(v=int, flag=uchar, t=int)\n" + pxd


        return (pxd, code)


class opcodeData():
    def __init__(self, opcode, name, length, cycles, bit16, flagZ, flagN, flagH, flagC):
        self.opcode = opcode
        self.name = name
        self.length = int(length)
        self.cycles = tuple(cycles.split("/"))
        self.flagZ = flagZ
        self.flagN = flagN
        self.flagH = flagH
        self.flagC = flagC
        self.flags = zip(range(4),[self.flagC, self.flagH, self.flagN, self.flagZ])
        self.is16bitOp = bit16

        self.functionHandlers = {
            "NOP" : self.NOP,
            "HALT" : self.HALT,
            "PREFIX" : self.CB,
            "EI" : self.EI,
            "DI" : self.DI,
            "STOP" : self.STOP,

            "LD" : self.LD,
            "LDH" : self.LDH,

            "ADD" : self.ADD,
            "SUB" : self.SUB,
            "INC" : self.INC,
            "DEC" : self.DEC,
            "ADC" : self.ADC,
            "SBC" : self.SBC,

            "AND" : self.AND,
            "OR" : self.OR,
            "XOR" : self.XOR,
            "CP" : self.CP,

            "PUSH" : self.PUSH,
            "POP" : self.POP,

            "JP" : self.JP,
            "JR" : self.JR,
            "CALL" : self.CALL,
            "RET" : self.RET,
            "RETI" : self.RETI,
            "RST" : self.RST,

            "DAA" : self.DAA,
            "SCF" : self.SCF,
            "CCF" : self.CCF,
            "CPL" : self.CPL,

            "RLA" : self.RLA,
            "RLCA" : self.RLCA,
            "RLC" : self.RLC,
            "RL" : self.RL,
            "RRA" : self.RRA,
            "RRCA" : self.RRCA,
            "RRC" : self.RRC,
            "RR" : self.RR,

            "SLA" : self.SLA,
            "SRA" : self.SRA,
            "SWAP" : self.SWAP,
            "SRL" : self.SRL,
            "BIT" : self.BIT,
            "RES" : self.RES,
            "SET" : self.SET
        }


    def createFunction(self):
        # print self.name.split()[0]
        handler = self.functionHandlers[self.name.split()[0]]
        functionName, functionText = handler()
        if self.opcode > 0xFF:
            self.length -= 1 # Compensate for CB operations being "2 bytes long"
        lookupTuple = (self.length, functionName + "_%0.2x" % self.opcode)

        # print functionText
        return lookupTuple, functionText

    # Special carry and half-carry for E8 and F8: http://forums.nesdev.com/viewtopic.php?p=42138
    # Blargg: "Both of these set carry and half-carry based on the low byte of SP added to the UNSIGNED immediate byte. The Negative and Zero flags are always cleared. They also calculate SP + SIGNED immediate byte and put the result into SP or HL, respectively."
    def handleFlags16bit_E8_F8(self, r0, r1, op, carry = False):
        flagMask = sum(map(lambda (i,f): (f == "-") << (i+4), self.flags))

        if flagMask == 0b11110000:# Only in case we do a dynamic operation, do we include the following calculations
            return ["# No flag operations"]

        lines = []

        lines.append("flag = " + format(sum(map(lambda (i,f): (f == "1") << (i+4), self.flags)), "#010b")) # Sets the ones that always get set by operation

        # flag += (((cpu.SP & 0xF) + (v & 0xF)) > 0xF) << flagH
        if self.flagH == "H":
            c = " %s cpu.fC()" % op if carry else ""
            lines.append("flag += (((%s & 0xF) %s (%s & 0xF)%s) > 0xF) << flagH" % (r0,op,r1,c))

        # flag += (((cpu.SP & 0xFF) + (v & 0xFF)) > 0xFF) << flagC
        if self.flagC == "C":
            lines.append("flag += (((%s & 0xFF) %s (%s & 0xFF)%s) > 0xFF) << flagC" % (r0,op,r1,c))

        lines.append("cpu.F &= " + format(flagMask, "#010b")) # Clears all flags affected by the operation
        lines.append("cpu.F |= flag")
        return lines


    def handleFlags16bit(self, r0, r1, op, carry = False):
        flagMask = sum(map(lambda (i,f): (f == "-") << (i+4), self.flags))

        if flagMask == 0b11110000:# Only in case we do a dynamic operation, do we include the following calculations
            return ["# No flag operations"]

        lines = []

        lines.append("flag = " + format(sum(map(lambda (i,f): (f == "1") << (i+4), self.flags)), "#010b")) # Sets the ones that always get set by operation
        if self.flagH == "H":
            c = " %s cpu.fC()" % op if carry else ""
            lines.append("flag += (((%s & 0xFFF) %s (%s & 0xFFF)%s) > 0xFFF) << flagH" % (r0,op,r1,c))

        if self.flagC == "C":
            lines.append("flag += (t > 0xFFFF) << flagC")

        lines.append("cpu.F &= " + format(flagMask, "#010b")) # Clears all flags affected by the operation
        lines.append("cpu.F |= flag")
        return lines


    def handleFlags8bit(self, r0, r1, op, carry = False):
        flagMask = sum(map(lambda (i,f): (f == "-") << (i+4), self.flags))

        if flagMask == 0b11110000:# Only in case we do a dynamic operation, do we include the following calculations
            return ["# No flag operations"]

        lines = []

        lines.append("flag = " + format(sum(map(lambda (i,f): (f == "1") << (i+4), self.flags)), "#010b")) # Sets the ones that always get set by operation

        if self.flagZ == "Z":
            lines.append("flag += ((t & 0xFF) == 0) << flagZ")

        if self.flagH == "H" and op == '-':
            c = " %s cpu.fC()" % op if carry else ""
            lines.append("flag += (((%s & 0xF) %s (%s & 0xF)%s) < 0) << flagH" % (r0,op,r1,c))
        elif self.flagH == "H":
            c = " %s cpu.fC()" % op if carry else ""
            lines.append("flag += (((%s & 0xF) %s (%s & 0xF)%s) > 0xF) << flagH" % (r0,op,r1,c))

        if self.flagC == "C" and op == '-':
            lines.append("flag += (t < 0) << flagC")
        elif self.flagC == "C":
            lines.append("flag += (t > 0xFF) << flagC")

        lines.append("cpu.F &= " + format(flagMask, "#010b")) # Clears all flags affected by the operation
        lines.append("cpu.F |= flag")
        return lines

    #####################################################################################
    #
    # MISC OPERATIONS
    #

    def NOP(self):
        code = Code(fname(), self.opcode, self.name, 0, self.length, self.cycles)
        return fname(), code.getCode()

    def HALT(self):
        code = Code(fname(), self.opcode, self.name, 0, self.length, self.cycles, branchOp = True)

        #TODO: Implement HALT bug. If master interrupt is disabled, the intruction following HALT is skipped
        code.addLines([
            "if cpu.interruptMasterEnable:",
            "\tcpu.halted = True",
            "else:",
            "\tcpu.PC += 1",
            "return " + self.cycles[0]
        ])
        return fname(), code.getCode()

    def CB(self):
        code = Code(fname(), self.opcode, self.name, 0, self.length, self.cycles)
        code.addLine("raise Exception('CB cannot be called!')")
        return fname(), code.getCode()

    def EI(self):
        code = Code(fname(), self.opcode, self.name, 0, self.length, self.cycles)
        code.addLine("cpu.interruptMasterEnable = True")
        return fname(), code.getCode()

    def DI(self):
        code = Code(fname(), self.opcode, self.name, 0, self.length, self.cycles)
        code.addLine("cpu.interruptMasterEnable = False")
        return fname(), code.getCode()

    def STOP(self):
        code = Code(fname(), self.opcode, self.name, True, self.length, self.cycles)
        code.addLine("pass")
        # code.addLine("raise Exception('STOP not implemented!')")
        return fname(), code.getCode()

    def DAA(self):
        left = Operand('A')
        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles)

        # http://stackoverflow.com/a/29990058/3831206
        # http://forums.nesdev.com/viewtopic.php?t=9088
        code.addLines([
            "t = %s" % left.get,

            "corr = 0",
            "corr |= 0x06 if cpu.fH() else 0x00",
            "corr |= 0x60 if cpu.fC() else 0x00",

            "if cpu.fN():",
            "\tt -= corr",
            "else:",
            "\tcorr |= 0x06 if (t & 0x0F) > 0x09 else 0x00",
            "\tcorr |= 0x60 if t > 0x99 else 0x00",
            "\tt += corr",

            "flag = 0",
            "flag += ((t & 0xFF) == 0) << flagZ",
            "flag += (corr & 0x60 != 0) << flagC",
            "cpu.F &= 0b01000000",
            "cpu.F |= flag",
            "t &= 0xFF",

            left.set % "t"
        ])
        return fname(), code.getCode()

    def SCF(self):
        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles)
        code.addLines(self.handleFlags8bit(None, None, None))
        return fname(), code.getCode()

    def CCF(self):
        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles)
        code.addLines([
            "flag = (cpu.F & 0b00010000) ^ 0b00010000",
            "cpu.F &= 0b10000000",
            "cpu.F |= flag",
        ])
        return fname(), code.getCode()

    def CPL(self):
        left = Operand('A')
        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles)
        code.addLine(left.set % ("(~%s) & 0xFF" % left.get))
        code.addLines(self.handleFlags8bit(None, None, None))
        return fname(), code.getCode()

    #####################################################################################
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

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles)
        if self.is16bitOp and left.immediate and left.pointer:
            code.addLine(left.set % ("%s & 0xFF" % right.get))
            a,b = left.set.split(",")
            code.addLine((a + "+1," + b) % ("%s >> 8" % right.get))
        else:
            print left.set, right.get, hex(self.opcode)
            code.addLine(left.set % right.get) # Special handling of AF, BC, DE

        # Special HL-only operations
        if not left.postOperation is None:
            code.addLine(left.postOperation)
        elif not right.postOperation is None:
            code.addLine(right.postOperation)
        elif self.opcode == 0xF8:
            # E8 and F8 http://forums.nesdev.com/viewtopic.php?p=42138
            code.addLine("t = cpu.HL")
            code.addLines(self.handleFlags16bit_E8_F8("cpu.SP", "v", '+', False))
            code.addLine("cpu.HL &= 0xFFFF")

        return fname(), code.getCode()

    def LDH(self):
        return self.LD()

    #####################################################################################
    #
    # ALU OPERATIONS
    #

    def ALU(self, left, right, op, carry = False):
        # op = '-' if self.flagN == '1' else '+'
        lines = []

        left.assign = False
        right.assign = False
        calc = "t = " + left.get + op + right.get

        if carry:
            calc += op + " cpu.fC()"

        lines.append(calc)

        if self.opcode == 0xE8:
            # E8 and F8 http://forums.nesdev.com/viewtopic.php?p=42138
            lines.extend(self.handleFlags16bit_E8_F8(left.get, "v", op, carry))
            lines.append("t &= 0xFFFF")
        elif self.is16bitOp:
            lines.extend(self.handleFlags16bit(left.get, right.get, op, carry))
            lines.append("t &= 0xFFFF")
        else:
            lines.extend(self.handleFlags8bit(left.get, right.get, op, carry))
            lines.append("t &= 0xFF")

        # HAS TO BE THE LAST INSTRUCTION BECAUSE OF CP!
        lines.append(left.set % "t")
        return lines

    def ADD(self):
        if self.name.find(',') > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = Operand('A')
            right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles)
        code.addLines(self.ALU(left, right, '+'))
        return fname(), code.getCode()

    def SUB(self):
        if self.name.find(',') > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = Operand('A')
            right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles)
        code.addLines(self.ALU(left, right, '-'))
        return fname(), code.getCode()

    def INC(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        right = Literal(1)

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles)
        code.addLines(self.ALU(left, right, '+'))
        return fname(), code.getCode()

    def DEC(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        right = Literal(1)

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles)
        code.addLines(self.ALU(left, right, '-'))
        return fname(), code.getCode()

    def ADC(self):
        if self.name.find(',') > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = Operand('A')
            right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles)
        code.addLines(self.ALU(left, right, '+', carry = True))
        return fname(), code.getCode()

    def SBC(self):
        if self.name.find(',') > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = Operand('A')
            right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles)
        code.addLines(self.ALU(left, right, '-', carry = True))
        return fname(), code.getCode()


    def AND(self):
        if self.name.find(',') > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = Operand('A')
            right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles)
        code.addLines(self.ALU(left, right, '&'))
        return fname(), code.getCode()

    def OR(self):
        if self.name.find(',') > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = Operand('A')
            right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles)
        code.addLines(self.ALU(left, right, '|'))
        return fname(), code.getCode()

    def XOR(self):
        if self.name.find(',') > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = Operand('A')
            right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles)
        code.addLines(self.ALU(left, right, '^'))
        return fname(), code.getCode()

    def CP(self):
        r1 = self.name.split()[1]
        left = Operand('A')
        right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length, self.cycles)
        code.addLines(self.ALU(left, right, '-')[:-1]) # CP is equal to SUB, but without saving the result. Therefore; we discard the last instruction.
        return fname(), code.getCode()


    #####################################################################################
    #
    # PUSH/POP OPERATIONS
    #

    def PUSH(self):
        r0 = self.name.split()[1]
        left = Operand(r0)

        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles)
        if "HL" in left.get:
            code.addLines([
                "cpu.mb.setitem(cpu.SP-1, cpu.HL >> 8) # High",
                "cpu.mb.setitem(cpu.SP-2, cpu.HL & 0xFF) # Low",
                "cpu.SP -= 2"
            ])
        else:
            code.addLine(
                "cpu.mb.setitem(cpu.SP-1, cpu.%s) # High" % left.operand[-2] # A bit of a hack, but you can only push double registers,
                )
            if left.operand == "AF":
                code.addLine(
                    "cpu.mb.setitem(cpu.SP-2, cpu.%s & 0xF0) # Low" % left.operand[-1] # by taking fx 'A' and 'F' directly, we save calculations
                )
            else:
                code.addLine(
                    "cpu.mb.setitem(cpu.SP-2, cpu.%s) # Low" % left.operand[-1] # by taking fx 'A' and 'F' directly, we save calculations
                )
            code.addLine("cpu.SP -= 2")

        return fname(), code.getCode()


    def POP(self):
        r0 = self.name.split()[1]
        left = Operand(r0)

        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles)
        if "HL" in left.get:
            code.addLines([
                (left.set % "(cpu.mb.getitem(cpu.SP+1) << 8) + cpu.mb.getitem(cpu.SP)") + "# High",
                "cpu.SP += 2"
            ])
        else:
            if left.operand[-1] == 'F': # Catching AF
                Fmask = " & 0xF0"
            else:
                Fmask = ""
            code.addLine(
                "cpu.%s = cpu.mb.getitem(cpu.SP+1) # High" % left.operand[-2] # See comment from PUSH
            )
            if left.operand == "AF":
                code.addLine(
                    "cpu.%s = cpu.mb.getitem(cpu.SP)%s & 0xF0 # Low" % (left.operand[-1], Fmask)
                )
            else:
                code.addLine(
                    "cpu.%s = cpu.mb.getitem(cpu.SP)%s # Low" % (left.operand[-1], Fmask)
                )
            code.addLine("cpu.SP += 2")

        return fname(), code.getCode()


    #####################################################################################
    #
    # CONTROL FLOW OPERATIONS
    #

    def JP(self):
        if self.name.find(',') > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = None
            right = Operand(r1)


        r_code = right.get
        if not left is None:
            l_code = left.get
            if l_code[-1] == "C" and not "NC" in l_code:
                left.flag = True
                l_code = "cpu.fC()"
            assert left.flag
        elif right.pointer:
            # FIX: Wrongful syntax of "JP (HL)" actually meaning "JP HL"
            right.pointer = False
            r_code = right.codeGen(False, operand="HL")
        else:
            assert right.immediate

        code = Code(fname(), self.opcode, self.name, right.immediate, self.length, self.cycles, branchOp = True)
        if left is None:
            code.addLines([
                "cpu.PC = %s" % ('v' if right.immediate else r_code),
                "return " + self.cycles[0]
            ])
        else:
            code.addLines([
                "if %s:" % l_code,
                "\tcpu.PC = %s" % ('v' if right.immediate else r_code),
                "\treturn " + self.cycles[0],
                "else:",
                "\tcpu.PC += %s" % self.length,
                "\treturn " + self.cycles[1]
            ])

        return fname(), code.getCode()

    def JR(self):
        if self.name.find(',') > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = None
            right = Operand(r1)


        if not left is None:
            l_code = left.get
            if l_code[-1] == "C" and not "NC" in l_code:
                left.flag = True
                l_code = "cpu.fC()"
            assert left.flag
        assert right.immediate

        code = Code(fname(), self.opcode, self.name, right.immediate, self.length, self.cycles, branchOp = True)
        if left is None:
            code.addLines([
                "cpu.PC += %d + " % self.length + inlineGetSignedInt8("v"),
                "cpu.PC &= 0xFFFF",
                "return " + self.cycles[0]
            ])
        else:
            code.addLines([
                "cpu.PC += %d" % self.length,
                "if %s:" % l_code,
                "\tcpu.PC += " + inlineGetSignedInt8("v"),
                "\tcpu.PC &= 0xFFFF",
                "\treturn " + self.cycles[0],
                "else:",
                "\tcpu.PC &= 0xFFFF",
                "\treturn " + self.cycles[1]
            ])

        return fname(), code.getCode()


    def CALL(self):
        if self.name.find(',') > 0:
            r0, r1 = self.name.split()[1].split(",")
            left = Operand(r0)
            right = Operand(r1)
        else:
            r1 = self.name.split()[1]
            left = None
            right = Operand(r1)


        if not left is None:
            l_code = left.get
            if l_code[-1] == "C" and not "NC" in l_code:
                left.flag = True
                l_code = "cpu.fC()"
            assert left.flag
        assert right.immediate

        code = Code(fname(), self.opcode, self.name, right.immediate, self.length, self.cycles, branchOp = True)

        # Taken from PUSH
        code.addLines([
            "cpu.PC += %s" % self.length,
            "cpu.PC &= 0xFFFF"
        ])

        if left is None:
            code.addLines([
                "cpu.mb.setitem(cpu.SP-1, cpu.PC >> 8) # High",
                "cpu.mb.setitem(cpu.SP-2, cpu.PC & 0xFF) # Low",
                "cpu.SP -= 2",
                "cpu.PC = %s" % ('v' if right.immediate else right.get),
                "return " + self.cycles[0]
            ])
        else:
            code.addLines([
                "if %s:" % l_code,
                "\tcpu.mb.setitem(cpu.SP-1, cpu.PC >> 8) # High",
                "\tcpu.mb.setitem(cpu.SP-2, cpu.PC & 0xFF) # Low",
                "\tcpu.SP -= 2",
                "\tcpu.PC = %s" % ('v' if right.immediate else right.get),
                "\treturn " + self.cycles[0],
                "else:",
                "\treturn " + self.cycles[1]
            ])

        return fname(), code.getCode()

    def RET(self):
        if self.name == "RET":
            left = None
        else:
            r0 = self.name.split()[1]
            left = Operand(r0)

            l_code = left.get
            if not left is None:
                if l_code[-1] == "C" and not "NC" in l_code:
                    left.flag = True
                    l_code = "cpu.fC()"
                assert left.flag

        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles, branchOp = True)
        if left is None:
            code.addLines([
                "cpu.PC = cpu.mb.getitem(cpu.SP+1) << 8 # High",
                "cpu.PC |= cpu.mb.getitem(cpu.SP) # Low",
                "cpu.SP += 2",
                "return " + self.cycles[0]
            ])
        else:
            code.addLines([
                "if %s:" % l_code,
                "\tcpu.PC = cpu.mb.getitem(cpu.SP+1) << 8 # High",
                "\tcpu.PC |= cpu.mb.getitem(cpu.SP) # Low",
                "\tcpu.SP += 2",
                "\treturn " + self.cycles[0],
                "else:",
                "\tcpu.PC += %s" % self.length,
                "\tcpu.PC &= 0xFFFF",
                "\treturn " + self.cycles[1]
            ])

        return fname(), code.getCode()

    def RETI(self):
        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles, branchOp = True)
        code.addLine("cpu.interruptMasterEnable = True")
        code.addLines([
            "cpu.PC = cpu.mb.getitem(cpu.SP+1) << 8 # High",
            "cpu.PC |= cpu.mb.getitem(cpu.SP) # Low",
            "cpu.SP += 2",
            "return " + self.cycles[0]
        ])

        return fname(), code.getCode()

    def RST(self):
        r1 = self.name.split()[1]
        right = Literal(r1)

        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles, branchOp = True)

        # Taken from PUSH and CALL
        code.addLines([
            "cpu.PC += %s" % self.length,
            "cpu.mb.setitem(cpu.SP-1, cpu.PC >> 8) # High",
            "cpu.mb.setitem(cpu.SP-2, cpu.PC & 0xFF) # Low",
            "cpu.SP -= 2"
        ])

        code.addLines([
            "cpu.PC = %s" % (right.code),
            "return " + self.cycles[0]
        ])

        return fname(), code.getCode()

    #####################################################################################
    #
    # ROTATE/SHIFT OPERATIONS
    #

    def RotateLeft(self, name, left, throughCarry = False):
        code = Code(name, self.opcode, self.name, False, self.length, self.cycles)
        left.assign = False
        if throughCarry:
            code.addLine(("t = (%s << 1)" % left.get) + "+ cpu.fC()")
        else:
            code.addLine("t = (%s << 1) + (%s >> 7)" % (left.get, left.get))
        code.addLines(self.handleFlags8bit(left.get, None, None, throughCarry))
        code.addLine("t &= 0xFF")
        left.assign = True
        code.addLine(left.set % "t")

        return code

    def RLA(self):
        left = Operand('A')
        code = self.RotateLeft(fname(), left, throughCarry = True)
        return fname(), code.getCode()

    def RLCA(self):
        left = Operand('A')
        code = self.RotateLeft(fname(), left)
        return fname(), code.getCode()

    def RLC(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        code = self.RotateLeft(fname(), left)
        return fname(), code.getCode()

    def RL(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        code = self.RotateLeft(fname(), left, throughCarry = True)
        return fname(), code.getCode()


    def RotateRight(self, name, left, throughCarry = False):
        code = Code(name, self.opcode, self.name, False, self.length, self.cycles)
        left.assign = False
        if throughCarry:
            #                                                                Trigger "overflow" for carry flag
            code.addLine(("t = (%s >> 1)" % left.get) + "+ (cpu.fC() << 7)" + "+ ((%s & 1) << 8)" % (left.get))
        else:
            #                                                                   Trigger "overflow" for carry flag
            code.addLine("t = (%s >> 1) + ((%s & 1) << 7)" % (left.get, left.get) + "+ ((%s & 1) << 8)" % (left.get))
        code.addLines(self.handleFlags8bit(left.get, None, None, throughCarry))
        code.addLine("t &= 0xFF")
        code.addLine(left.set % "t")
        return code

    def RRA(self):
        left = Operand('A')
        code = self.RotateRight(fname(), left, throughCarry = True)
        return fname(), code.getCode()

    def RRCA(self):
        left = Operand('A')
        code = self.RotateRight(fname(), left)
        return fname(), code.getCode()

    def RRC(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        code = self.RotateRight(fname(), left)
        return fname(), code.getCode()

    def RR(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        code = self.RotateRight(fname(), left, throughCarry = True)
        return fname(), code.getCode()


    def SLA(self):
        r0 = self.name.split()[1]
        left = Operand(r0)

        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles)
        code.addLine("t = (%s << 1)" % left.get)
        code.addLines(self.handleFlags8bit(left.get, None, None, False))
        code.addLine("t &= 0xFF")
        code.addLine(left.set % "t")
        return fname(), code.getCode()

    def SRA(self):
        r0 = self.name.split()[1]
        left = Operand(r0)

        self.flagC = 'C' # FIX: All documentation tells it should have carry enabled

        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles)
        #               Actual shift  MSB unchanged  Trigger "overflow" for carry flag
        code.addLine("t = ((%s >> 1) | (%s & 0x80)) + ((%s & 1) << 8)" % (left.get, left.get, left.get))
        code.addLines(self.handleFlags8bit(left.get, None, None, False))
        code.addLine("t &= 0xFF")
        code.addLine(left.set % "t")
        return fname(), code.getCode()

    def SRL(self):
        r0 = self.name.split()[1]
        left = Operand(r0)

        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles)
        #               Actual shift  Trigger "overflow" for carry flag
        code.addLine("t = (%s >> 1) + ((%s & 1) << 8)" % (left.get, left.get))
        code.addLines(self.handleFlags8bit(left.get, None, None, False))
        code.addLine("t &= 0xFF")
        code.addLine(left.set % "t")
        return fname(), code.getCode()

    def SWAP(self):
        r0 = self.name.split()[1]
        left = Operand(r0)

        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles)
        code.addLine("t = ((%s & 0xF0) >> 4) | ((%s & 0x0F) << 4)" % (left.get, left.get))
        code.addLines(self.handleFlags8bit(left.get, None, None, False))
        code.addLine("t &= 0xFF")
        code.addLine(left.set % "t")
        return fname(), code.getCode()

    #####################################################################################
    #
    # BIT OPERATIONS
    #

    def BIT(self):
        r0, r1 = self.name.split()[1].split(",")
        left = Literal(r0)
        right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles)
        code.addLine("t = %s & (1 << %s)" % (right.get, left.get))
        code.addLines(self.handleFlags8bit(left.get, right.get, None, False))

        return fname(), code.getCode()

    def RES(self):
        r0, r1 = self.name.split()[1].split(",")
        left = Literal(r0)
        right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles)
        code.addLine("t = %s & ~(1 << %s)" % (right.get, left.get))
        code.addLine(right.set % "t")
        return fname(), code.getCode()

    def SET(self):
        r0, r1 = self.name.split()[1].split(",")
        left = Literal(r0)
        right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, False, self.length, self.cycles)
        code.addLine("t = %s | (1 << %s)" % (right.get, left.get))
        code.addLine(right.set % "t")
        return fname(), code.getCode()



def update():
    response = urllib2.urlopen('http://pastraiser.com/cpu/gameboy/gameboy_opcodes.html')
    html = response.read()


    parser = MyHTMLParser()
    parser.feed(html)

    opcodeFunctions = map(lambda x: (None,None) if x is None else x.createFunction(), opcodes)

    with open(destination, "w") as f:
        with open(pxd_destination, "w") as f_pxd:
            f.write(warning)
            f.write(imports)
            f_pxd.write(cimports)
            lookupList = []
            for lookupTuple, code in opcodeFunctions:
                lookupList.append(lookupTuple)

                if code is None:
                    continue

                (pxd, functionText) = code
                f_pxd.write(pxd + "\n")
                f.write(functionText.replace('\t', ' '*4) + "\n\n")

            f.write("def NOOPCODE(cpu):\n    return 0\n\n")

            f.write("def getOpcodeLength(opcode):\n    return opcodeLengths[opcode]\n")
            f.write("""
def executeOpcode(cpu, opcode):
    opLen = getOpcodeLength(opcode)
    v = 0
    pc = cpu.PC
    if opLen == 2:
        # 8-bit immediate
        v = cpu.mb.getitem(pc+1)
    elif opLen == 3:
        # 16-bit immediate
        # Flips order of values due to big-endian
        a = cpu.mb.getitem(pc+2)
        b = cpu.mb.getitem(pc+1)
        v = (a << 8) + b

""")

            indent = 4
            for i,t in enumerate(lookupList):
                t = t if t is not None else (0,"NOOPCODE")
                f.write(" "*indent + ("if" if i==0 else "elif") +" opcode == 0x%0.2x:\n" % i + " "*(indent+4) + "return " + str(t[1]).replace("'",'') + ('(cpu)' if t[0] <= 1 else '(cpu, v)') + "\n")
            f.write('\n\n')

            f.write('opcodeLengths = array.array("B", [\n    ')
            for i,t in enumerate(lookupList):
                t = t if t is not None else (0,"NOOPCODE")
                f.write(str(t[0]).replace("'",'') + ',')
                if (i+1) % 16 == 0:
                    f.write('\n' + " "*4)
                else:
                    f.write(' ')

            f.write('])')
            f.write('\n\n')


            # f.write("\n\n# from opcodes import ")
            # f.write(', '.join(map(lambda (_,__,f): f[5:], lookupList)))


def load():
    # if os.path.exists(destination):
    #     return

    update()

load()

