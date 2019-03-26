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

warning = """\
# -*- encoding: utf-8 -*-
# THIS FILE IS AUTO-GENERATED!!!
# DO NOT MODIFY THIS FILE.
# CHANGES TO THE CODE SHOULD BE MADE IN 'generator.py'.
"""

# from registers import A, B, C, D, E, H, L, SP, PC
imports = """
from .flags import flagZ, flagN, flagH, flagC
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

class Operand():
    def __init__(self, operand):
        self.code = None
        self.postOperation = None
        self.pointer = False
        self.highPointer = False
        self.immediate = False
        self.signed = False
        self.is16BitOp = False
        self.flag = False

        self.code = self.getCode(operand)

    def getCode(self, operand):
        if operand == "(C)":
            self.highPointer = True
            return "self.mb[0xFF00 + self.C]"

        elif operand == "SP+r8":
            self.immediate = True
            self.signed = True

            # post operation set in LD handler!
            return "self.SP + " + inlineGetSignedInt8("v")

        elif operand[0] == '(' and operand[-1] == ')':
            self.pointer = True
            code = "self.mb[%s]" % self.getCode(re.search('\(([a-zA-Z]+\d*)[\+-]?\)', operand).group(1))

            if '-' in operand or '+' in operand:
                self.postOperation = "self.HL %s= 1" % operand[-2] # TODO: Replace with opcode 23 (INC HL)?

            return code

        # Sadly, there is an overlap between the register 'C' and to check for the carry flag 'C'.
        elif operand in [
                'A', 'F', 'B', 'C', 'D', 'E', 'H', 'L', # registers
                'SP', 'PC', 'AF', 'BC', 'DE', 'HL', # double registers
                ]:
            return "self."+operand
        elif operand in [
                'Z', 'C', 'NZ', 'NC' # flags
                ]:
            self.flag = True
            return "self.f"+operand

        elif operand in ['d8', 'd16', 'a8', 'a16', 'r8']:
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

class Literal():
    def __init__(self, value):
        if isinstance(value, str) and value.find('H') > 0:
            self.value = int(value[:-1], 16)
        else:
            self.value = value
        self.code = str(self.value)
        self.immediate = False

class Code():
    def __init__(self, functionName, opcode, name, takesImmediate, length, branchOp = False):
        self.functionName = functionName
        self.opcode = opcode
        self.name = name
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
            "def %s_%0.2x(self): # %0.2x %s" % (self.functionName, self.opcode, self.opcode, self.name),
            "def %s_%0.2x(self, v): # %0.2x %s" % (self.functionName, self.opcode, self.opcode, self.name)
        ][self.takesImmediate]
        code += "\n\t"

        if not self.branchOp:
            self.lines.append("self.PC += %d" % self.length)
            self.lines.append("return 0") # Choose the 0th cycle count

        code += "\n\t".join(self.lines)

        return code


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
        lookupTuple = (self.length, self.cycles, functionName + "_%0.2x" % self.opcode)

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

        # flag += (((self.SP & 0xF) + (v & 0xF)) > 0xF) << flagH
        if self.flagH == "H":
            c = " %s self.fC()" % op if carry else ""
            lines.append("flag += (((%s & 0xF) %s (%s & 0xF)%s) > 0xF) << flagH" % (r0,op,r1,c))

        # flag += (((self.SP & 0xFF) + (v & 0xFF)) > 0xFF) << flagC
        if self.flagC == "C":
            lines.append("flag += (((%s & 0xFF) %s (%s & 0xFF)%s) > 0xFF) << flagC" % (r0,op,r1,c))

        lines.append("self.F &= " + format(flagMask, "#010b")) # Clears all flags affected by the operation
        lines.append("self.F |= flag")
        return lines

    def handleFlags16bit(self, r0, r1, op, carry = False):
        flagMask = sum(map(lambda (i,f): (f == "-") << (i+4), self.flags))

        if flagMask == 0b11110000:# Only in case we do a dynamic operation, do we include the following calculations
            return ["# No flag operations"]

        lines = []

        lines.append("flag = " + format(sum(map(lambda (i,f): (f == "1") << (i+4), self.flags)), "#010b")) # Sets the ones that always get set by operation
        if self.flagH == "H":
            c = " %s self.fC" % op if carry else ""
            lines.append("flag += (((%s & 0xFFF) %s (%s & 0xFFF)%s) > 0xFFF) << flagH" % (r0,op,r1,c))

        if self.flagC == "C":
            lines.append("flag += (t > 0xFFFF) << flagC")

        lines.append("self.F &= " + format(flagMask, "#010b")) # Clears all flags affected by the operation
        lines.append("self.F |= flag")
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
            c = " %s self.fC" % op if carry else ""
            lines.append("flag += (((%s & 0xF) %s (%s & 0xF)%s) < 0) << flagH" % (r0,op,r1,c))
        elif self.flagH == "H":
            c = " %s self.fC" % op if carry else ""
            lines.append("flag += (((%s & 0xF) %s (%s & 0xF)%s) > 0xF) << flagH" % (r0,op,r1,c))

        if self.flagC == "C" and op == '-':
            lines.append("flag += (t < 0) << flagC")
        elif self.flagC == "C":
            lines.append("flag += (t > 0xFF) << flagC")

        lines.append("self.F &= " + format(flagMask, "#010b")) # Clears all flags affected by the operation
        lines.append("self.F |= flag")
        return lines

    #####################################################################################
    #
    # MISC OPERATIONS
    #

    def NOP(self):
        code = Code(fname(), self.opcode, self.name, 0, self.length)
        return fname(), code.getCode()

    def HALT(self):
        code = Code(fname(), self.opcode, self.name, 0, self.length, branchOp = True)

        #TODO: Implement HALT bug. If master interrupt is disabled, the intruction following HALT is skipped
        code.addLines([
            "if self.interruptMasterEnable:",
            "\tself.halted = True",
            "else:",
            "\tself.PC += 1",
            "return 0"
        ])
        return fname(), code.getCode()

    def CB(self):
        code = Code(fname(), self.opcode, self.name, 0, self.length)
        code.addLine("raise Exception('CB cannot be called!')")
        return fname(), code.getCode()

    def EI(self):
        code = Code(fname(), self.opcode, self.name, 0, self.length)
        code.addLine("self.interruptMasterEnable = True")
        return fname(), code.getCode()

    def DI(self):
        code = Code(fname(), self.opcode, self.name, 0, self.length)
        code.addLine("self.interruptMasterEnable = False")
        return fname(), code.getCode()

    def STOP(self):
        code = Code(fname(), self.opcode, self.name, True, self.length)
        code.addLine("pass")
        # code.addLine("raise Exception('STOP not implemented!')")
        return fname(), code.getCode()

    def DAA(self):
        left = Operand('A')
        code = Code(fname(), self.opcode, self.name, False, self.length)

        # http://stackoverflow.com/a/29990058/3831206
        # http://forums.nesdev.com/viewtopic.php?t=9088
        code.addLines([
            "t = %s" % left.code,

            "corr = 0",
            "corr |= 0x06 if self.fH else 0x00",
            "corr |= 0x60 if self.fC else 0x00",

            "if self.fN:",
            "\tt -= corr",
            "else:",
            "\tcorr |= 0x06 if (t & 0x0F) > 0x09 else 0x00",
            "\tcorr |= 0x60 if t > 0x99 else 0x00",
            "\tt += corr",

            "flag = 0",
            "flag += ((t & 0xFF) == 0) << flagZ",
            "flag += (corr & 0x60 != 0) << flagC",
            "self.F &= 0b01000000",
            "self.F |= flag",
            "t &= 0xFF",

            "%s = t" % left.code
        ])
        return fname(), code.getCode()

    def SCF(self):
        code = Code(fname(), self.opcode, self.name, False, self.length)
        code.addLines(self.handleFlags8bit(None, None, None))
        return fname(), code.getCode()

    def CCF(self):
        code = Code(fname(), self.opcode, self.name, False, self.length)
        code.addLines([
            "flag = (self.F & 0b00010000) ^ 0b00010000",
            "self.F &= 0b10000000",
            "self.F |= flag",
        ])
        return fname(), code.getCode()

    def CPL(self):
        left = Operand('A')
        code = Code(fname(), self.opcode, self.name, False, self.length)
        code.addLine("%s = (~%s) & 0xFF" % (left.code, left.code))
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

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length)
        if self.is16bitOp and left.immediate and left.pointer:
            # import pdb; pdb.set_trace()
            code.addLine(left.code + " = %s & 0xFF" % right.code)
            code.addLine(left.code[:-1] + "+1] = %s >> 8" % right.code)
        else:
            code.addLine(left.code + " = " + right.code)

        if not left.postOperation is None:
            code.addLine(left.postOperation)
        elif not right.postOperation is None:
            code.addLine(right.postOperation)
        elif self.opcode == 0xF8:
            code.addLine("t = self.HL")
            code.addLines(self.handleFlags16bit_E8_F8("self.SP", "v", '+', False))
            code.addLine("self.HL &= 0xFFFF")

        # if self.opcode == 0x08:
        #     import pdb; pdb.set_trace()
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

        calc = "t = " + left.code + op + right.code

        if carry:
            calc += op + " self.fC"

        lines.append(calc)

        if self.opcode == 0xE8:
            # E8 and F8 http://forums.nesdev.com/viewtopic.php?p=42138
            lines.extend(self.handleFlags16bit_E8_F8(left.code, "v", op, carry))
            lines.append("t &= 0xFFFF")
        elif self.is16bitOp:
            lines.extend(self.handleFlags16bit(left.code, right.code, op, carry))
            lines.append("t &= 0xFFFF")
        else:
            lines.extend(self.handleFlags8bit(left.code, right.code, op, carry))
            lines.append("t &= 0xFF")

        lines.append(left.code + " = t") # HAS TO BE THE LAST INSTRUCTION BECAUSE OF CP!
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

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length)
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

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length)
        code.addLines(self.ALU(left, right, '-'))
        return fname(), code.getCode()

    def INC(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        right = Literal(1)

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length)
        code.addLines(self.ALU(left, right, '+'))
        return fname(), code.getCode()

    def DEC(self):
        r0 = self.name.split()[1]
        left = Operand(r0)
        right = Literal(1)

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length)
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

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length)
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

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length)
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

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length)
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

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length)
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

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length)
        code.addLines(self.ALU(left, right, '^'))
        return fname(), code.getCode()

    def CP(self):
        r1 = self.name.split()[1]
        left = Operand('A')
        right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, left.immediate or right.immediate, self.length)
        code.addLines(self.ALU(left, right, '-')[:-1]) # CP is equal to SUB, but without saving the result. Therefore; we discard the last instruction.
        return fname(), code.getCode()


    #####################################################################################
    #
    # PUSH/POP OPERATIONS
    #

    def PUSH(self):
        r0 = self.name.split()[1]
        left = Operand(r0)

        code = Code(fname(), self.opcode, self.name, False, self.length)
        if left.code == "self.HL":
            code.addLines([
                "self.mb[self.SP-1] = %s >> 8 # High" % left.code, # A bit of a hack, but you can only push double registers,
                "self.mb[self.SP-2] = %s & 0xFF # Low" % left.code, # by taking fx 'A' and 'F' directly, we save calculations
                "self.SP -= 2"
            ])
        else:
            code.addLines([
                "self.mb[self.SP-1] = self.%s # High" % left.code[-2], # A bit of a hack, but you can only push double registers,
                "self.mb[self.SP-2] = self.%s # Low" % left.code[-1], # by taking fx 'A' and 'F' directly, we save calculations
                "self.SP -= 2"
            ])

        return fname(), code.getCode()


    def POP(self):
        r0 = self.name.split()[1]
        left = Operand(r0)

        code = Code(fname(), self.opcode, self.name, False, self.length)
        if left.code == "self.HL":
            code.addLines([
                "%s = (self.mb[self.SP+1] << 8) + self.mb[self.SP] # High" % left.code,
                "self.SP += 2"
            ])
        else:
            if left.code[-1] == 'F':
                Fmask = " & 0xF0"
            else:
                Fmask = ""
            code.addLines([
                "self.%s = self.mb[self.SP+1] # High" % left.code[-2], # See comment from PUSH
                "self.%s = self.mb[self.SP]%s # Low" % (left.code[-1], Fmask),
                "self.SP += 2"
            ])

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


        if not left is None:
            if left.code[-1] == "C" and not "NC" in left.code:
                left.flag = True
                left.code = "self.fC"
            assert left.flag
        elif right.pointer:
            # FIX: Wrongful syntax of "JP (HL)" actually meaning "JP HL"
            right.pointer = False
            right.code = right.getCode("HL")
        else:
            assert right.immediate

        code = Code(fname(), self.opcode, self.name, right.immediate, self.length, branchOp = True)
        if left is None:
            code.addLines([
                "self.PC = %s" % ('v' if right.immediate else right.code),
                "return 0"
            ])
        else:
            code.addLines([
                "if %s:" % left.code,
                "\tself.PC = %s" % ('v' if right.immediate else right.code),
                "\treturn 0",
                "else:",
                "\tself.PC += %s" % self.length,
                "\treturn 1"
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
            if left.code[-1] == "C" and not "NC" in left.code:
                left.flag = True
                left.code = "self.fC"
            assert left.flag
        assert right.immediate

        code = Code(fname(), self.opcode, self.name, right.immediate, self.length, branchOp = True)
        if left is None:
            code.addLines([
                "self.PC += %d + " % self.length + inlineGetSignedInt8("v"),
                "self.PC &= 0xFFFF",
                "return 0"
            ])
        else:
            code.addLines([
                "self.PC += %d" % self.length,
                "if %s:" % left.code,
                "\tself.PC += " + inlineGetSignedInt8("v"),
                "\tself.PC &= 0xFFFF",
                "\treturn 0",
                "else:",
                "\tself.PC &= 0xFFFF",
                "\treturn 1"
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
            if left.code[-1] == "C" and not "NC" in left.code:
                left.flag = True
                left.code = "self.fC"
            assert left.flag
        assert right.immediate

        code = Code(fname(), self.opcode, self.name, right.immediate, self.length, branchOp = True)

        # Taken from PUSH
        code.addLines([
            "self.PC += %s" % self.length,
            "self.PC &= 0xFFFF"
        ])

        if left is None:
            code.addLines([
                "self.mb[self.SP-1] = self.PC >> 8 # High",
                "self.mb[self.SP-2] = self.PC & 0xFF # Low",
                "self.SP -= 2",
                "self.PC = %s" % ('v' if right.immediate else right.code),
                "return 0"
            ])
        else:
            code.addLines([
                "if %s:" % left.code,
                "\tself.mb[self.SP-1] = self.PC >> 8 # High",
                "\tself.mb[self.SP-2] = self.PC & 0xFF # Low",
                "\tself.SP -= 2",
                "\tself.PC = %s" % ('v' if right.immediate else right.code),
                "\treturn 0",
                "else:",
                "\treturn 1"
            ])

        return fname(), code.getCode()

    def RET(self):
        if self.name == "RET":
            left = None
        else:
            r0 = self.name.split()[1]
            left = Operand(r0)

            if not left is None:
                if left.code[-1] == "C" and not "NC" in left.code:
                    left.flag = True
                    left.code = "self.fC"
                assert left.flag

        code = Code(fname(), self.opcode, self.name, False, self.length, branchOp = True)
        if left is None:
            code.addLines([
                "self.PC = self.mb[self.SP+1] << 8 # High",
                "self.PC |= self.mb[self.SP] # Low",
                "self.SP += 2",
                "return 0"
            ])
        else:
            code.addLines([
                "if %s:" % left.code,
                "\tself.PC = self.mb[self.SP+1] << 8 # High",
                "\tself.PC |= self.mb[self.SP] # Low",
                "\tself.SP += 2",
                "\treturn 0",
                "else:",
                "\tself.PC += %s" % self.length,
                "\tself.PC &= 0xFFFF",
                "\treturn 1"
            ])

        return fname(), code.getCode()

    def RETI(self):
        code = Code(fname(), self.opcode, self.name, False, self.length, branchOp = True)
        code.addLine("self.interruptMasterEnable = True")
        code.addLines([
            "self.PC = self.mb[self.SP+1] << 8 # High",
            "self.PC |= self.mb[self.SP] # Low",
            "self.SP += 2",
            "return 0"
        ])

        return fname(), code.getCode()

    def RST(self):
        r1 = self.name.split()[1]
        right = Literal(r1)

        code = Code(fname(), self.opcode, self.name, False, self.length, branchOp = True)

        # Taken from PUSH and CALL
        code.addLines([
            "self.PC += %s" % self.length,
            "self.mb[self.SP-1] = self.PC >> 8 # High",
            "self.mb[self.SP-2] = self.PC & 0xFF # Low",
            "self.SP -= 2"
        ])

        code.addLines([
            "self.PC = %s" % (right.code),
            "return 0"
        ])

        return fname(), code.getCode()

    #####################################################################################
    #
    # ROTATE/SHIFT OPERATIONS
    #

    def RotateLeft(self, name, left, throughCarry = False):
        code = Code(name, self.opcode, self.name, False, self.length)
        if throughCarry:
            code.addLine(("t = (%s << 1)" % left.code) + "+ self.fC")
        else:
            code.addLine("t = (%s << 1) + (%s >> 7)" % (left.code, left.code))
        code.addLines(self.handleFlags8bit(left.code, None, None, throughCarry))
        code.addLine("t &= 0xFF")
        code.addLine(left.code + " = t")

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
        code = Code(name, self.opcode, self.name, False, self.length)
        if throughCarry:
            #                                                                Trigger "overflow" for carry flag
            code.addLine(("t = (%s >> 1)" % left.code) + "+ (self.fC << 7)" + "+ ((%s & 1) << 8)" % (left.code))
        else:
            #                                                                   Trigger "overflow" for carry flag
            code.addLine("t = (%s >> 1) + ((%s & 1) << 7)" % (left.code, left.code) + "+ ((%s & 1) << 8)" % (left.code))
        code.addLines(self.handleFlags8bit(left.code, None, None, throughCarry))
        code.addLine("t &= 0xFF")
        code.addLine(left.code + " = t")

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

        code = Code(fname(), self.opcode, self.name, False, self.length)
        code.addLine("t = (%s << 1)" % left.code)
        code.addLines(self.handleFlags8bit(left.code, None, None, False))
        code.addLine("t &= 0xFF")
        code.addLine(left.code + " = t")
        return fname(), code.getCode()

    def SRA(self):
        r0 = self.name.split()[1]
        left = Operand(r0)

        self.flagC = 'C' # FIX: All documentation tells it should have carry enabled

        code = Code(fname(), self.opcode, self.name, False, self.length)
        #               Actual shift  MSB unchanged  Trigger "overflow" for carry flag
        code.addLine("t = ((%s >> 1) | (%s & 0x80)) + ((%s & 1) << 8)" % (left.code, left.code, left.code))
        code.addLines(self.handleFlags8bit(left.code, None, None, False))
        code.addLine("t &= 0xFF")
        code.addLine(left.code + " = t")
        return fname(), code.getCode()

    def SRL(self):
        r0 = self.name.split()[1]
        left = Operand(r0)

        code = Code(fname(), self.opcode, self.name, False, self.length)
        #               Actual shift  Trigger "overflow" for carry flag
        code.addLine("t = (%s >> 1) + ((%s & 1) << 8)" % (left.code, left.code))
        code.addLines(self.handleFlags8bit(left.code, None, None, False))
        code.addLine("t &= 0xFF")
        code.addLine(left.code + " = t")
        return fname(), code.getCode()

    def SWAP(self):
        r0 = self.name.split()[1]
        left = Operand(r0)

        code = Code(fname(), self.opcode, self.name, False, self.length)
        code.addLine("t = ((%s & 0xF0) >> 4) | ((%s & 0x0F) << 4)" % (left.code, left.code))
        code.addLines(self.handleFlags8bit(left.code, None, None, False))
        code.addLine("t &= 0xFF")
        code.addLine(left.code + " = t")
        return fname(), code.getCode()

    #####################################################################################
    #
    # BIT OPERATIONS
    #

    def BIT(self):
        r0, r1 = self.name.split()[1].split(",")
        left = Literal(r0)
        right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, False, self.length)
        code.addLine("t = %s & (1 << %s)" % (right.code, left.code))
        code.addLines(self.handleFlags8bit(left.code, right.code, None, False))

        return fname(), code.getCode()

    def RES(self):
        r0, r1 = self.name.split()[1].split(",")
        left = Literal(r0)
        right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, False, self.length)
        code.addLine("t = %s & ~(1 << %s)" % (right.code, left.code))
        code.addLine("%s = t" % right.code)

        return fname(), code.getCode()

    def SET(self):
        r0, r1 = self.name.split()[1].split(",")
        left = Literal(r0)
        right = Operand(r1)

        code = Code(fname(), self.opcode, self.name, False, self.length)
        code.addLine("t = %s | (1 << %s)" % (right.code, left.code))
        code.addLine("%s = t" % right.code)

        return fname(), code.getCode()



def update():
    response = urllib2.urlopen('http://pastraiser.com/cpu/gameboy/gameboy_opcodes.html')
    html = response.read()


    parser = MyHTMLParser()
    parser.feed(html)

    opcodeFunctions = map(lambda x: (None,None) if x is None else x.createFunction(), opcodes)

    with open(destination, "w") as f:
        f.write(warning)
        f.write(imports)
        lookupList = []
        for lookupTuple, functionText in opcodeFunctions:
            lookupList.append(lookupTuple)

            if functionText is None:
                continue

            f.write(functionText.replace('\t', ' '*4) + "\n\n")

        f.write('opcodes = [\n')
        for t in lookupList:
            f.write(" "*4 + str(t).replace("'",'') + ',\n')
        f.write(']')

        # f.write("\n\n# from opcodes import ")
        # f.write(', '.join(map(lambda (_,__,f): f[5:], lookupList)))


def load():
    # if os.path.exists(destination):
    #     return

    update()

load()
