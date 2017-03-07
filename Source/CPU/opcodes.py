# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import CoreDump
#http://stackoverflow.com/questions/8294618/define-a-lambda-expression-that-raises-an-exception
def coredump(ex):
    raise CoreDump.CoreDump(ex)

from registers import A, B, C, D, E, H, L, SP, PC
from flags import flagZ, flagN, flagH, flagC

import sys
sys.path.append("..")
from MathUint8 import *


# Python evaluates 'None or None to None', but 'None or True to True'
# successful jumps do 'setPC(...) or True' to adjust the cycles
# 'if None' is evaluated as 'if False'


inc = lambda r: lambda s, e: s.setReg(r, s.CPU_INC8(s.reg[r])) or s.setPC(e)
dec = lambda r: lambda s, e: s.setReg(r, s.CPU_DEC8(s.reg[r])) or s.setPC(e)
inc16 = lambda r: lambda s, e: s.setReg(r, s.CPU_INC16(s.reg[r])) or s.setPC(e)
dec16 = lambda r: lambda s, e: s.setReg(r, s.CPU_DEC16(s.reg[r])) or s.setPC(e)
exeLDi = lambda r: lambda s, v, e: s.setReg(r, v) or s.setPC(e)

opcode_0x = [(1, (4,), lambda s, e: s.setPC(e)),                      # 00 - "No Operation" ("NOP")
             (3, (12,), lambda s, v, e: s.setBC(v) or s.setPC(e)),  # 01 - "Load 16-bit immediate into BC" ("LD BC,d16")
             (1, (8,), lambda s, e: s.MB.__setitem__(s.getBC(), s.reg[A]) or s.setPC(e)),  # 02 - "Save A to address pointed by BC" ("LD(s.BC),A")
             (1, (8,), lambda s, e: s.setBC(s.getBC()+1) or s.setPC(e)),  # 03 - "Increment 16-bit BC" ("INC BC")
             (1, (4,), inc(B)),         # 04 - "Increment B" ("INC B")
             (1, (4,), dec(B)),         # 05 - "Decrement B" ("DEC B")
             (2, (8,), exeLDi(B)),      # 06 - "Load 8-bit immediate into B" ("LD B,v")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_RLC(s.reg[A])) or s.setPC(e)),  # 07 - "Rotate A left with carry" ("RLC A")
             (3, (20,), lambda s, v, e: s.MB.__setitem__(v, s.reg[SP] & 0xFF) or s.MB.__setitem__(v+1, (s.reg[SP] & 0xFF00) >> 8) or s.setPC(e)),  # 08 - "Save SP to given address" ("LD (v), s.SP")
             (1, (8,), lambda s, e: s.setHL(s.CPU_ADD16(s.getHL(), s.getBC())) or s.setPC(e)),    # 09 - "Add 16-bit BC to HL" ("ADD HL,BC")
             (1, (8,), lambda s, e: s.setReg(A, s.MB[s.getBC()]) or s.setPC(e)),   # 0A - "Load A from address pointed to by BC" ("LD A,(s.BC)")
             (1, (8,), lambda s, e: s.setBC(s.getBC()-1) or s.setPC(e)),                 # 0B - "Decrement 16-bit BC" ("DEC BC")
             (1, (4,), inc(C)),                  # 0C - "Increment C" ("INC C")
             (1, (4,), dec(C)),                  # 0D - "Decrement C" ("DEC C")
             (2, (8,), exeLDi(C)),      # 0E - "Load 8-bit immediate into C" ("LD C,v")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_RRC(s.reg[A])) or s.setPC(e))]  # 0F - "Rotate A right with carry" ("RRC A")

opcode_1x = [(1, (4,), lambda s, e: s.CPU_STOP(e)),                           # 10 - "Stop processor" ("STOP")
             (3, (12,), lambda s, v, e: s.setDE(v) or s.setPC(e)),     # 11 - "Load 16-bit immediate into DE" ("LD DE,d16")
             (1, (8,), lambda s, e: s.MB.__setitem__(s.getDE(), s.reg[A]) or s.setPC(e)),   # 12 - "Save A to address pointed by DE" ("LD(s.DE),A")
             (1, (8,), lambda s, e: s.setDE(s.getDE()+1) or s.setPC(e)),                 # 13 - "Increment 16-bit DE" ("INC DE")
             (1, (4,), inc(D)),                  # 14 - "Increment D" ("INC D")
             (1, (4,), dec(D)),                  # 15 - "Decrement D" ("DEC D")
             (2, (8,), exeLDi(D)),       # 16 - "Load 8-bit immediate into D" ("LD D,v")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_RL(s.reg[A])) or s.setPC(e)),                   # 17 - "Rotate A left" ("RL A")
             (2, (12,), lambda s, v, e: s.setReg(PC, getSignedInt8(v) + e)),                  # 18 - "Relative jump by signed immediate" ("JR r8")
             (1, (8,), lambda s, e: s.setHL(s.CPU_ADD16(s.getHL(), s.getDE())) or s.setPC(e)),     # 19 - "Add 16-bit DE to HL" ("ADD HL,DE")
             (1, (8,), lambda s, e: s.setReg(A, s.MB[s.getDE()]) or s.setPC(e)),   # 1A - "Load A from address pointed to by DE" ("LD A, s.DE")
             (1, (8,), lambda s, e: s.setDE(s.getDE()-1) or s.setPC(e)),                 # 1B - "Decrement 16-bit DE" ("DEC DE")
             (1, (4,), inc(E)),                  # 1C - "Increment E" ("INC E")
             (1, (4,), dec(E)),                  # 1D - "Decrement E" ("DEC E")
             (2, (8,), exeLDi(E)),       # 1E - "Load 8-bit immediate into E" ("LD E,v")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_RR(s.reg[A])) or s.setPC(e))]                   # 1F - "Rotate A right" ("RR A")


opcode_2x = [(2, (12, 8), lambda s, v, e: s.setPC(e+getSignedInt8(v)) if not s.testFlag(flagZ) else s.setPC(e)),      # 20 - "Relative jump by signed immediate if last result was not zero" ("JR NZ,r8")
             (3, (12,), lambda s, v, e: s.setHL(v) or s.setPC(e)),     # 21 - "Load 16-bit immediate into HL" ("LD HL,d16")
             (1, (8,), lambda s, e: s.MB.__setitem__(s.getHL(), s.reg[A]) or (s.setHL(s.getHL() + 1) or s.setPC(e))),  # 22 - "Save A to address pointed by HL, and increment HL" ("LDI (HL),A")
             (1, (8,), lambda s, e: s.setHL(s.getHL()+1) or s.setPC(e)),                 # 23 - "Increment 16-bit HL" ("INC HL")
             (1, (4,), inc(H)),     # 24 - "Increment H" ("INC H")
             (1, (4,), dec(H)),     # 25 - "Decrement H" ("DEC H")
             (2, (8,), exeLDi(H)),  # 26 - "Load 8-bit immediate into H" ("LD H,v")
             (1, (4,), lambda s, e: s.CPU_DAA() or s.setPC(e)),  # 27 - "Adjust A for BCD addition" ("DAA")
             (2, (12, 8), lambda s, v, e: (s.testFlag(flagZ) and (s.setPC((e)+getSignedInt8(v)) or True)) or s.setPC(e)),       # 28 - "Relative jump by signed immediate if last result was zero" ("JR Z,r8")
             (1, (8,), lambda s, e: s.setHL(s.CPU_ADD16(s.getHL(), s.getHL())) or s.setPC(e)),     # 29 - "Add 16-bit HL to HL" ("ADD HL,HL")
             (1, (8,), lambda s, e: s.setReg(A, s.MB[s.getHL()]) or(s.setHL(s.getHL() + 1) or s.setPC(e))),   # 2A - "Load A from address pointed to by HL, and increment HL ("LDI A,(HL)")
             (1, (8,), lambda s, e: s.setHL(s.getHL()-1) or s.setPC(e)),                 # 2B - "Decrement 16-bit HL" ("DEC HL")
             (1, (4,), inc(L)),                  # 2C - "Increment L" ("INC L")
             (1, (4,), dec(L)),                  # 2D - "Decrement L" ("DEC L")
             (2, (8,), exeLDi(L)),       # 2E - "Load 8-bit immediate into L" ("LD L,v")
             (1, (4,), lambda s, e: s.setReg(A, ~s.reg[A] & 0xFF) or s.setPC(e))]                          # 2F - "Complement (logical NOT) on A" ("CPL")

opcode_3x = [(2, (12, 8), lambda s, v, e: (not s.testFlag(flagC) and (s.setPC(e+getSignedInt8(v)) or True)) or s.setPC(e)),      # 30 - "Relative jump by signed immediate if last result caused no carry" ("JR NC,r8")
             (3, (12,), lambda s, v, e: s.setReg(SP, v) or s.setPC(e)),      # 31 - "Load 16-bit immediate into SP" ("LD SP,d16")
             (1, (8,), lambda s, e:(s.MB.__setitem__(s.getHL(), s.reg[A]) or s.setHL(s.getHL()-1)) or s.setPC(e)),  # 32 - "Save A to address pointed by HL, and decrement HL" ("LDD (HL),A")
             (1, (8,), inc16(SP)),                 # 33 - "Increment 16-bit HL" ("INC SP")
             (1, (12,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_INC8(s.MB[s.getHL()])) or s.setPC(e)),  # 34 - "Increment value pointed by HL" ("INC (HL)
             (1, (12,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_DEC8(s.MB[s.getHL()])) or s.setPC(e)),  # 35 - "Decrement value pointed by HL" ("DEC (HL)
             (2, (12,), lambda s, v, e: s.MB.__setitem__(s.getHL(), v) or s.setPC(e)),  # 36 - "Load 8-bit immediate into address pointed by HL" ("LD (HL),v")
             (1, (4,), lambda s, e: s.setFlag(flagC) or s.clearFlag(flagH) or s.clearFlag(flagN) or s.setPC(e)),  # 37 - "Set carry flag" ("SCF")
             (2, (12, 8), lambda s, v, e: (s.testFlag(flagC) and (s.setPC((e)+getSignedInt8(v)) or True)) or s.setPC(e)),  # 38 - "Relative jump by signed immediate if last result caused carry" ("JR C,r8")
             (1, (8,), lambda s, e: s.setHL(s.CPU_ADD16(s.getHL(), s.reg[SP])) or s.setPC(e)),  # 39 - "Add 16-bit SP to HL" ("ADD HL, s.SP")
             (1, (8,), lambda s, e: (s.setReg(A, s.MB[s.getHL()]) or s.setHL(s.getHL()-1)) or s.setPC(e)),  # 3A - "Load A from address pointed to by HL, and decrement HL" ("LDD A,(HL)
             (1, (8,), dec16(SP)),  # 3B - "Decrement 16-bit SP" ("DEC SP")
             (1, (4,), inc(A)),  # 3C - "Increment A" ("INC A")
             (1, (4,), dec(A)),  # 3D - "Decrement A" ("DEC A")
             (2, (8,), lambda s, v, e: s.setReg(A, v) or s.setPC(e)),       # 3E - "Load 8-bit immediate into A" ("LD A,v")
             (1, (4,), lambda s, e: s.clearFlag(flagN) or s.setFlag(flagH, s.testFlag(flagC)) or s.setFlag(flagC, not s.testFlag(flagC)) or s.setPC(e))]  # 3F - "Clear carry flag" ("CCF")

exeLD = lambda a, b: lambda s, e: s.setReg(a, s.reg[b]) or s.setPC(e)
exeLDaddr = lambda b: lambda s, e: s.MB.__setitem__(s.getHL(), s.reg[b]) or s.setPC(e)

opcode_4x = [(1, (4,), exeLD(B, B)),        # 40 - "Copy B to B" ("LD B,B")
             (1, (4,), exeLD(B, C)),        # 41 - "Copy C to B" ("LD B,C")
             (1, (4,), exeLD(B, D)),        # 42 - "Copy D to B" ("LD B,D")
             (1, (4,), exeLD(B, E)),        # 43 - "Copy E to B" ("LD B,E")
             (1, (4,), exeLD(B, H)),        # 44 - "Copy H to B" ("LD B,H")
             (1, (4,), exeLD(B, L)),        # 45 - "Copy L to B" ("LD B,L")
             (1, (8,), lambda s, e: s.setReg(B, s.MB[s.getHL()]) or s.setPC(e)),  # 46 - "Copy value pointed by HL to B" ("LD B,(HL)
             (1, (4,), exeLD(B, A)),        # 47 - "Copy A to B" ("LD B,A")
             (1, (4,), exeLD(C, B)),        # 48 - "Copy B to C" ("LD C,B")
             (1, (4,), exeLD(C, C)),        # 49 - "Copy C to C" ("LD C,C")
             (1, (4,), exeLD(C, D)),        # 4A - "Copy D to C" ("LD C,D")
             (1, (4,), exeLD(C, E)),        # 4B - "Copy E to C" ("LD C,E")
             (1, (4,), exeLD(C, H)),        # 4C - "Copy H to C" ("LD C,H")
             (1, (4,), exeLD(C, L)),        # 4D - "Copy L to C" ("LD C,L")
             (1, (8,), lambda s, e: s.setReg(C, s.MB[s.getHL()]) or s.setPC(e)),  # 4E - "Copy value pointed by HL to C" ("LD C,(HL)
             (1, (4,), exeLD(C, A))]        # 4F - "Copy A to C" ("LD C,A")


opcode_5x = [(1, (4,), exeLD(D, B)),        # 50 - "Copy B to D" ("LD D,B")
             (1, (4,), exeLD(D, C)),        # 51 - "Copy C to D" ("LD D,C")
             (1, (4,), exeLD(D, D)),        # 52 - "Copy D to D" ("LD D,D")
             (1, (4,), exeLD(D, E)),        # 53 - "Copy E to D" ("LD D,E")
             (1, (4,), exeLD(D, H)),        # 54 - "Copy H to D" ("LD D,H")
             (1, (4,), exeLD(D, L)),        # 55 - "Copy L to D" ("LD D,L")
             (1, (8,), lambda s, e: s.setReg(D, s.MB[s.getHL()]) or s.setPC(e)),  # 56 - "Copy value pointed by HL to D" ("LD D,(HL)
             (1, (4,), exeLD(D, A)),        # 57 - "Copy A to D" ("LD D,A")
             (1, (4,), exeLD(E, B)),        # 58 - "Copy B to E" ("LD E,B")
             (1, (4,), exeLD(E, C)),        # 59 - "Copy C to E" ("LD E,C")
             (1, (4,), exeLD(E, D)),        # 5A - "Copy D to E" ("LD E,D")
             (1, (4,), exeLD(E, E)),        # 5B - "Copy E to E" ("LD E,E")
             (1, (4,), exeLD(E, H)),        # 5C - "Copy H to E" ("LD E,H")
             (1, (4,), exeLD(E, L)),        # 5D - "Copy L to E" ("LD E,L")
             (1, (8,), lambda s, e: s.setReg(E, s.MB[s.getHL()]) or s.setPC(e)),  # 5E - "Copy value pointed by HL to E" ("LD E,(HL)
             (1, (4,), exeLD(E, A))]        # 5F - "Copy A to E" ("LD E,A")


opcode_6x = [(1, (4,), exeLD(H, B)),        # 60 - "Copy B to H" ("LD H,B")
             (1, (4,), exeLD(H, C)),        # 61 - "Copy C to H" ("LD H,C")
             (1, (4,), exeLD(H, D)),        # 62 - "Copy D to H" ("LD H,D")
             (1, (4,), exeLD(H, E)),        # 63 - "Copy E to H" ("LD H,E")
             (1, (4,), exeLD(H, H)),        # 64 - "Copy H to H" ("LD H,H")
             (1, (4,), exeLD(H, L)),        # 65 - "Copy L to H" ("LD H,L")
             (1, (8,), lambda s, e: s.setReg(H, s.MB[s.getHL()]) or s.setPC(e)),  # 66 - "Copy value pointed by HL to H" ("LD H,(s.H)
             (1, (4,), exeLD(H, A)),        # 67 - "Copy A to H" ("LD H,A")
             (1, (4,), exeLD(L, B)),        # 68 - "Copy B to L" ("LD L,B")
             (1, (4,), exeLD(L, C)),        # 69 - "Copy C to L" ("LD L,C")
             (1, (4,), exeLD(L, D)),        # 6A - "Copy D to L" ("LD L,D")
             (1, (4,), exeLD(L, E)),        # 6B - "Copy E to L" ("LD L,E")
             (1, (4,), exeLD(L, H)),        # 6C - "Copy H to L" ("LD L,H")
             (1, (4,), exeLD(L, L)),        # 6D - "Copy L to L" ("LD L,L")
             (1, (8,), lambda s, e: s.setReg(L, s.MB[s.getHL()]) or s.setPC(e)),  # 6E - "Copy value pointed by HL to L" ("LD L,(s.H)
             (1, (4,), exeLD(L, A))]        # 6F - "Copy A to L" ("LD L,A")


opcode_7x = [(1, (8,), exeLDaddr(B)),  # 70 - "Copy B to address pointed by HL" ("LD (HL),B")
             (1, (8,), exeLDaddr(C)),  # 71 - "Copy C to address pointed by HL" ("LD (HL),C")
             (1, (8,), exeLDaddr(D)),  # 72 - "Copy D to address pointed by HL" ("LD (HL),D")
             (1, (8,), exeLDaddr(E)),  # 73 - "Copy E to address pointed by HL" ("LD (HL),E")
             (1, (8,), exeLDaddr(H)),  # 74 - "Copy H to address pointed by HL" ("LD (HL),H")
             (1, (8,), exeLDaddr(L)),  # 75 - "Copy L to address pointed by HL" ("LD (HL),L")
             #TODO: Implement HALT bug. If master interrupt is disabled, the intruction following HALT is skipped
             (1, (4,), lambda s, e: s.CPU_HALT()), # 76 - "Halt processor" ("HALT")
             # (1, (4,), lambda s, e: s.CPU_HALT() if s.interruptMasterEnable else s.setPC(e)), # 76 - "Halt processor" ("HALT")
             (1, (8,), exeLDaddr(A)),  # 77 - "Copy A to address pointed by HL" ("LD (HL),A")
             (1, (4,), exeLD(A, B)),        # 78 - "Copy B to A" ("LD A,B")
             (1, (4,), exeLD(A, C)),        # 79 - "Copy C to A" ("LD A,C")
             (1, (4,), exeLD(A, D)),        # 7A - "Copy D to A" ("LD A,D")
             (1, (4,), exeLD(A, E)),        # 7B - "Copy E to A" ("LD A,E")
             (1, (4,), exeLD(A, H)),        # 7C - "Copy H to A" ("LD A,H")
             (1, (4,), exeLD(A, L)),        # 7D - "Copy L to A" ("LD A,L")
             (1, (8,), lambda s, e: s.setReg(A, s.MB[s.getHL()]) or s.setPC(e)),  # 7E - "Copy value pointed by HL to A" ("LD A,(HL)
             (1, (4,), lambda s, e: s.setReg(A, s.reg[A]) or s.setPC(e))]        # 7F - "Copy A to A" ("LD A,A")

#exeALU = lambda f, a, b: lambda s, e: s.setReg(A, s.ALU8(s.reg[a], s.reg[b], f, (True, True, True, True))) or s.setPC(e)
#exeALUC = lambda f, a, b: lambda s, e: s.setReg(A, s.ALU8(s.reg[a], s.reg[b], f, (True, True, True, True), carry=s.testCarryFlag())) or s.setPC(e)  # Mayby not so good.. always negative?
exeALUSubC = lambda a, b: lambda s, e: s.setReg(A, s.CPU_SBC8(s.reg[a], s.reg[b])) or s.setPC(e)
exeALUSub = lambda a, b: lambda s, e: s.setReg(A, s.CPU_SUB8(s.reg[a], s.reg[b])) or s.setPC(e)

LocAND = lambda a, b: a & b
LocXOR = lambda a, b: a ^ b
# sub = lambda a, b: a - b
# add = lambda a, b: a + b

opcode_8x = [(1, (4,), lambda s, e: s.setReg(A,s.CPU_ADD8(s.reg[A], s.reg[B])) or s.setPC(e)),                     # 80 - "Add B to A" ("ADD A,B")
             (1, (4,), lambda s, e: s.setReg(A,s.CPU_ADD8(s.reg[A], s.reg[C])) or s.setPC(e)),                     # 81 - "Add C to A" ("ADD A,C")
             (1, (4,), lambda s, e: s.setReg(A,s.CPU_ADD8(s.reg[A], s.reg[D])) or s.setPC(e)),                     # 82 - "Add D to A" ("ADD A,D")
             (1, (4,), lambda s, e: s.setReg(A,s.CPU_ADD8(s.reg[A], s.reg[E])) or s.setPC(e)),                     # 83 - "Add E to A" ("ADD A,E")
             (1, (4,), lambda s, e: s.setReg(A,s.CPU_ADD8(s.reg[A], s.reg[H])) or s.setPC(e)),                     # 84 - "Add H to A" ("ADD A,H")
             (1, (4,), lambda s, e: s.setReg(A,s.CPU_ADD8(s.reg[A], s.reg[L])) or s.setPC(e)),                     # 85 - "Add L to A" ("ADD A,L")
             (1, (8,), lambda s, e: s.setReg(A,s.CPU_ADD8(s.reg[A], s.MB[s.getHL()])) or s.setPC(e)),  # 86 - "Add value pointed by HL to A" ("ADD A,(HL)
             (1, (4,), lambda s, e: s.setReg(A,s.CPU_ADD8(s.reg[A], s.reg[A])) or s.setPC(e)),                     # 87 - "Add A to A" ("ADD A,A")

             (1, (4,), lambda s, e: s.setReg(A,s.CPU_ADC8(s.reg[A], s.reg[B])) or s.setPC(e)),                    # 88 - "Add B and carry flag to A" ("ADC A,B")
             (1, (4,), lambda s, e: s.setReg(A,s.CPU_ADC8(s.reg[A], s.reg[C])) or s.setPC(e)),                    # 89 - "Add C and carry flag to A" ("ADC A,C")
             (1, (4,), lambda s, e: s.setReg(A,s.CPU_ADC8(s.reg[A], s.reg[D])) or s.setPC(e)),                    # 8A - "Add D and carry flag to A" ("ADC A,D")
             (1, (4,), lambda s, e: s.setReg(A,s.CPU_ADC8(s.reg[A], s.reg[E])) or s.setPC(e)),                    # 8B - "Add E and carry flag to A" ("ADC A,E")
             (1, (4,), lambda s, e: s.setReg(A,s.CPU_ADC8(s.reg[A], s.reg[H])) or s.setPC(e)),                    # 8C - "Add H and carry flag to A" ("ADC A,H")
             (1, (4,), lambda s, e: s.setReg(A,s.CPU_ADC8(s.reg[A], s.reg[L])) or s.setPC(e)),                    # 8D - "Add and carry flag L to A" ("ADC A,L")
             (1, (8,), lambda s, e: s.setReg(A,s.CPU_ADC8(s.reg[A], s.MB[s.getHL()])) or s.setPC(e)),  # 8E - "Add value pointed by HL and carry flag to A" ("ADC A,(HL)
             (1, (4,), lambda s, e: s.setReg(A,s.CPU_ADC8(s.reg[A], s.reg[A])) or s.setPC(e))]                    # 8F - "Add A and carry flag to A" ("ADC A,A")


opcode_9x = [(1, (4,), exeALUSub(A, B)),                  # 90 -  "Subtract B from A" ("SUB A,B")
             (1, (4,), exeALUSub(A, C)),                  # 91 -  "Subtract C from A" ("SUB A,C")
             (1, (4,), exeALUSub(A, D)),                  # 92 -  "Subtract D from A" ("SUB A,D")
             (1, (4,), exeALUSub(A, E)),                  # 93 -  "Subtract E from A" ("SUB A,E")
             (1, (4,), exeALUSub(A, H)),                  # 94 -  "Subtract H from A" ("SUB A,H")
             (1, (4,), exeALUSub(A, L)),                  # 95 -  "Subtract L from A" ("SUB A,L")
             (1, (8,), lambda s, e: s.setReg(A, s.CPU_SUB8(s.reg[A], s.MB[s.getHL()])) or s.setPC(e)),  # 96 -  "Subtract value pointed by HL from A" ("SUB A,(HL)
             (1, (4,), exeALUSub(A, A)),                 # 97 -  "Subtract A from A" ("SUB A,A")

             (1, (4,), exeALUSubC(A, B)),                 # 98 -  "Subtract B and carry flag from A" ("SBC A,B")
             (1, (4,), exeALUSubC(A, C)),                 # 99 -  "Subtract C and carry flag from A" ("SBC A,C")
             (1, (4,), exeALUSubC(A, D)),                 # 9A -  "Subtract D and carry flag from A" ("SBC A,D")
             (1, (4,), exeALUSubC(A, E)),                 # 9B -  "Subtract E and carry flag from A" ("SBC A,E")
             (1, (4,), exeALUSubC(A, H)),                 # 9C -  "Subtract H and carry flag from A" ("SBC A,H")
             (1, (4,), exeALUSubC(A, L)),                 # 9D -  "Subtract L and carry flag from A" ("SBC A,L")
             (1, (8,), lambda s, e: s.setReg(A, s.CPU_SBC8(s.reg[A], s.MB[s.getHL()])) or s.setPC(e)),  # 9E -  "Subtract value pointed by HL and carry flag from A" ("SBC A,(HL)
             (1, (4,), exeALUSubC(A, A))]                  # 9F -  "Subtract A and carry flag from A" ("SBC A,A")


opcode_Ax = [(1, (4,), lambda s, e: s.setReg(A, s.CPU_AND8(s.reg[A], s.reg[B])) or s.setPC(e)),                  # A0 -  "Logical AND B against A" ("AND B")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_AND8(s.reg[A], s.reg[C])) or s.setPC(e)),                  # A1 -  "Logical AND C against A" ("AND C")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_AND8(s.reg[A], s.reg[D])) or s.setPC(e)),                  # A2 -  "Logical AND D against A" ("AND D")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_AND8(s.reg[A], s.reg[E])) or s.setPC(e)),                  # A3 -  "Logical AND E against A" ("AND E")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_AND8(s.reg[A], s.reg[H])) or s.setPC(e)),                  # A4 -  "Logical AND H against A" ("AND H")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_AND8(s.reg[A], s.reg[L])) or s.setPC(e)),                  # A5 -  "Logical AND L against A" ("AND L")
             (1, (8,), lambda s, e: s.setReg(A, s.CPU_AND8(s.reg[A], s.MB[s.getHL()])) or s.setPC(e)),                 # A6 -  "Logical AND value pointed by HL against A" ("AND (HL)
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_AND8(s.reg[A], s.reg[A])) or s.setPC(e)),                  # A7 -  "Logical AND A against A" ("AND A")

             (1, (4,), lambda s, e: s.setReg(A, s.CPU_XOR8(s.reg[A], s.reg[B])) or s.setPC(e)),                  # A8 -  "Logical XOR B against A" ("XOR B")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_XOR8(s.reg[A], s.reg[C])) or s.setPC(e)),                  # A9 -  "Logical XOR C against A" ("XOR C")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_XOR8(s.reg[A], s.reg[D])) or s.setPC(e)),                  # AA -  "Logical XOR D against A" ("XOR D")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_XOR8(s.reg[A], s.reg[E])) or s.setPC(e)),                  # AB -  "Logical XOR E against A" ("XOR E")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_XOR8(s.reg[A], s.reg[H])) or s.setPC(e)),                  # AC -  "Logical XOR H against A" ("XOR H")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_XOR8(s.reg[A], s.reg[L])) or s.setPC(e)),                  # AD -  "Logical XOR L against A" ("XOR L")
             (1, (8,), lambda s, e: s.setReg(A, s.CPU_XOR8(s.reg[A], s.MB[s.getHL()])) or s.setPC(e)),                 # AE -  "Logical XOR value pointed by HL against A" ("XOR (HL)
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_XOR8(s.reg[A], s.reg[A])) or s.setPC(e))]                  # AF -  "Logical XOR A against A" ("XOR A")

opcode_Bx = [(1, (4,), lambda s, e: s.setReg(A, s.CPU_OR8(s.reg[A], s.reg[B])) or s.setPC(e)),                   # B0 -  "Logical OR B against A" ("OR B")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_OR8(s.reg[A], s.reg[C])) or s.setPC(e)),                   # B1 -  "Logical OR C against A" ("OR C")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_OR8(s.reg[A], s.reg[D])) or s.setPC(e)),                   # B2 -  "Logical OR D against A" ("OR D")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_OR8(s.reg[A], s.reg[E])) or s.setPC(e)),                   # B3 -  "Logical OR E against A" ("OR E")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_OR8(s.reg[A], s.reg[H])) or s.setPC(e)),                   # B4 -  "Logical OR H against A" ("OR H")
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_OR8(s.reg[A], s.reg[L])) or s.setPC(e)),                   # B5 -  "Logical OR L against A" ("OR L")
             (1, (8,), lambda s, e: s.setReg(A, s.CPU_OR8(s.reg[A], s.MB[s.getHL()])) or s.setPC(e)),           # B6 -  "Logical OR value pointed by HL against A" ("OR (HL)
             (1, (4,), lambda s, e: s.setReg(A, s.CPU_OR8(s.reg[A], s.reg[A])) or s.setPC(e)),                   # B7 -  "Logical OR A against A" ("OR A")

             (1, (4,), lambda s, e: s.CPU_CP(s.reg[A], s.reg[B]) or s.setPC(e)),                           # B8 -  "Compare B against A" ("CP B")
             (1, (4,), lambda s, e: s.CPU_CP(s.reg[A], s.reg[C]) or s.setPC(e)),                           # B9 -  "Compare C against A" ("CP C")
             (1, (4,), lambda s, e: s.CPU_CP(s.reg[A], s.reg[D]) or s.setPC(e)),                           # BA -  "Compare D against A" ("CP D")
             (1, (4,), lambda s, e: s.CPU_CP(s.reg[A], s.reg[E]) or s.setPC(e)),                           # BB -  "Compare E against A" ("CP E")
             (1, (4,), lambda s, e: s.CPU_CP(s.reg[A], s.reg[H]) or s.setPC(e)),                           # BC -  "Compare H against A" ("CP H")
             (1, (4,), lambda s, e: s.CPU_CP(s.reg[A], s.reg[L]) or s.setPC(e)),                           # BD -  "Compare L against A" ("CP L")
             (1, (8,), lambda s, e: s.CPU_CP(s.reg[A], s.MB[s.getHL()]) or s.setPC(e)),  # BE -  "Compare value pointed by HL against A" ("CP (HL)
             (1, (4,), lambda s, e: s.CPU_CP(s.reg[A], s.reg[A]) or s.setPC(e))]                           # BF -  "Compare A against A" ("CP A")


def addPushToStack(s, e):
    s.debugCallStack.append(("PUSH", hex(e)))


def addPopToStack(s):
    try:
        s.debugCallStack.pop()
    except IndexError:
        pass
        # s.logger("Tried to pop from empty call stack")

opcode_Cx = [(1, (20, 8), lambda s, e: (addPopToStack(s) or s.setPC(s.CPU_RET())) if not s.testFlag(flagZ) else s.setPC(e)),                   # C0 -  "Return if last result was not zero" ("RET NZ")
             (1, (12,), lambda s, e: s.setBC(s.CPU_POP()) or s.setPC(e)),                # C1 -  "Pop 16-bit value from stack into BC" ("POP BC")
             (3, (16, 12), lambda s, v, e: s.setPC(v) if not s.testFlag(flagZ) else s.setPC(e)),     # C2 -  "Absolute jump to 16-bit location if last result was not zero" ("JP NZ,v")
             (3, (16,), lambda s, v, e: s.setPC(v)),               # C3 -  "Absolute jump to 16-bit location" ("JP v")
             (3, (24, 12), lambda s, v, e: (s.CPU_PUSH(e) or addPushToStack(s, e) or s.setPC(v)) if not s.testFlag(flagZ) else s.setPC(e)),#not s.testFlag(flagZ) and (s.CPU_PUSH(e) or addPushToStack(s, e) or s.setPC(v))),   # C4 -  "Call routine at 16-bit location if last result was not zero" ("CALL NZ,v")
             (1, (16,), lambda s, e: s.CPU_PUSH(s.getBC()) or s.setPC(e)),               # C5 -  "Push 16-bit BC onto stack" ("PUSH BC")
             (2, (8,), lambda s, v, e: s.setReg(A, s.CPU_ADD8(s.reg[A], v)) or s.setPC(e)),   # C6 -  "Add 8-bit immediate to A" ("ADD A,v")
             (1, (16,), lambda s, e: s.CPU_PUSH(e) or addPushToStack(s, e) or s.setPC(0x0000)),                  # C7 -  "Call routine at address 0000h" ("RST 0")
             (1, (20, 8), lambda s, e: (addPopToStack(s) or s.setPC(s.CPU_RET())) if s.testFlag(flagZ) else s.setPC(e)),                    # C8 -  "Return if last result was zero" ("RET Z")
             (1, (16,), lambda s, e: addPopToStack(s) or s.setPC(s.CPU_RET())),                           # C9 -  "Return to calling routine" ("RET")
             (3, (16, 12), lambda s, v, e: s.setPC(v) if s.testFlag(flagZ) else s.setPC(e)),      # CA -  "Absolute jump to 16-bit location if last result was zero" ("JP Z,v")
             (1, (4,), lambda s, e: coredump(Exception("CB should never be called"))),                           # CB -  "Extended operations (two-byte instruction code)" ("Ext ops")
             (3, (24, 12), lambda s, v, e: (s.CPU_PUSH(e) or addPushToStack(s, e) or s.setPC(v)) if s.testFlag(flagZ) else s.setPC(e)),    # CC -  "Call routine at 16-bit location if last result was zero" ("CALL Z,v")
             (3, (24,), lambda s, v, e: s.CPU_PUSH(e) or addPushToStack(s, e) or s.setPC(v)),             # CD -  "Call routine at 16-bit location" ("CALL v")
             (2, (8,), lambda s, v, e: s.setReg(A, s.CPU_ADD8(s.reg[A], v + s.testFlag(flagC))) or s.setPC(e)),   # CE -  "Add 8-bit immediate and carry to A" ("ADC A,v")
             (1, (16,), lambda s, e: s.CPU_PUSH(e) or s.setPC(0x0008))]                # CF -  "Call routine at address 0008h" ("RST 8")

opcode_Dx = [(1, (20, 8), lambda s, e: (addPopToStack(s) or s.setPC(s.CPU_RET())) if not s.testFlag(flagC) else s.setPC(e)),                   # D0 -  "Return if last result caused no carry" ("RET NC")
             (1, (12,), lambda s, e: s.setDE(s.CPU_POP()) or s.setPC(e)),                # D1 -  "Pop 16-bit value from stack into DE" ("POP DE")
             (3, (16, 12), lambda s, v, e: s.setPC(v) if not s.testFlag(flagC) else s.setPC(e)),     # D2 -  "Absolute jump to 16-bit location if last result caused no carry" ("JP NC,v")
             (1, (0,), lambda s, e: coredump(Exception("opcode not supported by Z80"))),                            # D3 -  "Operation removed in this CPU" ("XX")
             (3, (24, 12), lambda s, v, e: (s.CPU_PUSH(e) or addPushToStack(s, e) or s.setPC(v)) if not s.testFlag(flagC) else s.setPC(e)),   # D4 -  "Call routine at 16-bit location if last result caused no carry" ("CALL NC,v")
             (1, (16,), lambda s, e: s.CPU_PUSH(s.getDE()) or s.setPC(e)),               # D5 -  "Push 16-bit DE onto stack" ("PUSH DE")
             (2, (8,), lambda s, v, e: s.setReg(A, s.CPU_SUB8(s.reg[A], v)) or s.setPC(e)),   # D6 -  "Subtract 8-bit immediate from A" ("SUB A,v")
             (1, (16,), lambda s, e: s.CPU_PUSH(e) or s.setPC(0x0010)),                  # D7 -  "Call routine at address 0010h" ("RST 10")
             (1, (20, 8), lambda s, e: (addPopToStack(s) or s.setPC(s.CPU_RET())) if s.testFlag(flagC) else s.setPC(e)),                 # D8 -  "Return if last result caused carry" ("RET C")
             (1, (16,), lambda s, e: s.CPU_EI() or addPopToStack(s) or s.setPC(s.CPU_RET())),                          # D9 -  "Enable interrupts and return to calling routine" ("RETI")
             (3, (16, 12), lambda s, v, e: s.setPC(v) if s.testFlag(flagC) else s.setPC(e)),   # DA -  "Absolute jump to 16-bit location if last result caused carry" ("JP C,v")
             (1, (0,), lambda s, e: coredump(Exception("opcode not supported by Z80"))),                            # DB -  "Operation removed in this CPU" ("XX")
             (3, (24, 12), lambda s, v, e: (s.CPU_PUSH(e) or addPushToStack(s, e) or s.setPC(v)) if s.testFlag(flagC) else s.setPC(e)),  # DC -  "Call routine at 16-bit location if last result caused carry" ("CALL C,v")
             (1, (0,), lambda s, e: coredump(Exception("opcode not supported by Z80"))),                            # DD -  "Operation removed in this CPU" ("XX")
             (2, (8,), lambda s, v, e: s.setReg(A, s.CPU_SBC8(s.reg[A], v)) or s.setPC(e)),   # DE -  "Subtract 8-bit immediate and carry from A" ("SBC A,v")
             (1, (16,), lambda s, e: s.CPU_PUSH(e) or s.setPC(0x0018))]             # DF -  "Call routine at address 0018h" ("RST 18")

opcode_Ex = [(2, (12,), lambda s, v, e: s.MB.__setitem__(0xFF00+v, s.reg[A]) or s.setPC(e)),  # E0 -  "Save A at address pointed to by (FF00h + 8-bit immediate)" ("LDH (a8),A")
             (1, (12,), lambda s, e: s.setHL(s.CPU_POP()) or s.setPC(e)),                # E1 -  "Pop 16-bit value from stack into HL" ("POP HL")
             (1, (8,), lambda s, e: s.MB.__setitem__(0xFF00+s.reg[C], s.reg[A]) or s.setPC(e)),  # E2 -  "Save A at address pointed to by (FF00h + s.C)" ("LDH(s.C),A")
             (1, (0,), lambda s, e: coredump(Exception("opcode not supported by Z80"))),                            # E3 -  "Operation removed in this CPU" ("XX")
             (1, (0,), lambda s, e: coredump(Exception("opcode not supported by Z80"))),                            # E4 -  "Operation removed in this CPU" ("XX")
             (1, (16,), lambda s, e: s.CPU_PUSH(s.getHL()) or s.setPC(e)),               # E5 -  "Push 16-bit HL onto stack" ("PUSH HL")
             (2, (8,), lambda s, v, e: s.setReg(A, s.CPU_AND8(s.reg[A], v)) or s.setPC(e)),  # E6 -  "Logical AND 8-bit immediate against A" ("AND v")
             (1, (16,), lambda s, e: s.CPU_PUSH(e) or s.setPC(0x0020)),               # E7 -  "Call routine at address 0020h" ("RST 20")
             (2, (16,), lambda s, v, e: s.setReg(SP, s.CPU_ADD16(s.reg[SP], getSignedInt8(v))) or s.setPC(e)),  # E8 -  "Add signed 8-bit immediate to SP" ("ADD SP,r8")
             (1, (4,), lambda s, e: s.setPC(s.getHL())),  # E9 -  "Jump to 16-bit value pointed by HL" ("JP(s.getHL())
             (3, (16,), lambda s, v, e: s.MB.__setitem__(v, s.reg[A]) or s.setPC(e)),  # EA -  "Save A at given 16-bit address" ("LD (v),A")
             (1, (0,), lambda s, e: coredump(Exception("opcode not supported by Z80"))),                            # EB -  "Operation removed in this CPU" ("XX")
             (1, (0,), lambda s, e: coredump(Exception("opcode not supported by Z80"))),                            # EC -  "Operation removed in this CPU" ("XX")
             (1, (0,), lambda s, e: coredump(Exception("opcode not supported by Z80"))),                            # ED -  "Operation removed in this CPU" ("XX")
             (2, (8,), lambda s, v, e: s.setReg(A, s.CPU_XOR8(s.reg[A], v)) or s.setPC(e)),  # EE -  "Logical XOR 8-bit immediate against A" ("XOR v")
             (1, (16,), lambda s, e: s.CPU_PUSH(e) or s.setPC(0x0028))]          # EF -  "Call routine at address 0028h" ("RST 28")

opcode_Fx = [(2, (12,), lambda s, v, e: s.setReg(A, s.MB[v+0xFF00]) or s.setPC(e)),  # F0 -  "Load A from address pointed to by (FF00h + 8-bit immediate)" ("LDH A,(a8)
             (1, (12,), lambda s, e: s.setAF(s.CPU_POP()) or s.setPC(e)),                # F1 -  "Pop 16-bit value from stack into AF" ("POP AF")
             #WARN: This one seems wrong:
             # (1, (0,), lambda s, e: coredump(Exception("opcode not supported by Z80"))),                            # F2 -  "Operation removed in this CPU" ("XX")
             (2, (12,), lambda s, v, e: s.setReg(A, s.MB[0xFF00+s.reg[C]]) or s.setPC(e)),  # F2 - no$gmb says LD a, (0xFF00+c)
             (1, (4,), lambda s, e: s.CPU_DI() or s.setPC(e)),                            # F3 -  "DIsable interrupts" ("DI")
             (1, (0,), lambda s, e: coredump(Exception("opcode not supported by Z80"))),                            # F4 -  "Operation removed in this CPU" ("XX")
             (1, (16,), lambda s, e: s.CPU_PUSH(s.getAF()) or s.setPC(e)),               # F5 -  "Push 16-bit AF onto stack" ("PUSH AF")
             (2, (8,), lambda s, v, e: s.setReg(A, s.CPU_OR8(s.reg[A], v)) or s.setPC(e)),  # F6 -  "Logical OR 8-bit immediate against A" ("OR v")
             (1, (16,), lambda s, e: s.CPU_PUSH(e) or s.setPC(0x0030)),               # F7 -  "Call routine at address 0030h" ("RST 30")
             (2, (12,), lambda s, v, e: (s.setHL(s.CPU_ADD16(s.reg[SP], getSignedInt8(v))) or s.clearFlag(flagZ) or s.clearFlag(flagN)) or s.setPC(e)),  # F8 -  "Add signed 8-bit immediate to SP and save result in HL" ("LDHL SP,v")
             (1, (8,), lambda s, e: s.setReg(SP, s.getHL()) or s.setPC(e)),    # F9 -  "Copy HL to SP" ("LD SP,HL")
             (3, (16,), lambda s, v, e: s.setReg(A, s.MB[v]) or s.setPC(e)),  # FA -  "Load A from given 16-bit address" ("LD A,(v)
             (1, (4,), lambda s, e: s.CPU_EI() or s.setPC(e)),                            # FB -  "Enable interrupts" ("EI")
             (1, (0,), lambda s, e: coredump(Exception("opcode not supported by Z80"))),                            # FC -  "Operation removed in this CPU" ("XX")
             (1, (0,), lambda s, e: coredump(Exception("opcode not supported by Z80"))),                            # FD -  "Operation removed in this CPU" ("XX")
             (2, (8,), lambda s, v, e: s.CPU_CP(s.reg[A], v) or s.setPC(e)),                # FE -  "Compare 8-bit immediate against A" ("CP v")
             (1, (16,), lambda s, e: s.CPU_PUSH(e) or s.setPC(0x0038))]          # FF -  "Call routine at address 0038h" ("RST 38")


rlc = lambda r: lambda s, e: s.setReg(r, s.CPU_EXT_RLC(s.reg[r])) or s.setPC(e)
rrc = lambda r: lambda s, e: s.setReg(r, s.CPU_EXT_RRC(s.reg[r])) or s.setPC(e)

# CB_prefix = []
CB_prefix_0x = [(1, (8,), rlc(B)),          # 00 - "Rotate B left with carry"
                (1, (8,), rlc(C)),          # 01 - "Rotate C left with carry"
                (1, (8,), rlc(D)),          # 02 - "Rotate D left with carry"
                (1, (8,), rlc(E)),          # 03 - "Rotate E left with carry"
                (1, (8,), rlc(H)),          # 04 - "Rotate H left with carry"
                (1, (8,), rlc(L)),          # 05 - "Rotate L left with carry"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_RLC(s.MB[s.getHL()])) or s.setPC(e)),  # 06 - "Rotate value pointed by HL left with carry"
                (1, (8,), rlc(A)),          # 07 - "Rotate A left with carry"
                (1, (8,), rrc(B)),          # 08 - "Rotate B right with carry"
                (1, (8,), rrc(C)),          # 09 - "Rotate C right with carry"
                (1, (8,), rrc(D)),          # 0A - "Rotate D right with carry"
                (1, (8,), rrc(E)),          # 0B - "Rotate E right with carry"
                (1, (8,), rrc(H)),          # 0C - "Rotate H right with carry"
                (1, (8,), rrc(L)),          # 0D - "Rotate L right with carry"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_RRC(s.MB[s.getHL()])) or s.setPC(e)),  # 0E - "Rotate value pointed by HL right with carry"
                (1, (8,), rrc(A))]          # 0F - "Rotate A right with carry"

rr = lambda r: lambda s, e: s.setReg(r, s.CPU_EXT_RR(s.reg[r])) or s.setPC(e)
rl = lambda r: lambda s, e: s.setReg(r, s.CPU_EXT_RL(s.reg[r])) or s.setPC(e)
CB_prefix_1x = [(1, (8,), rl(B)),           # 10 - "Rotate B left"
                (1, (8,), rl(C)),           # 11 - "Rotate C left"
                (1, (8,), rl(D)),           # 12 - "Rotate D left"
                (1, (8,), rl(E)),           # 13 - "Rotate E left"
                (1, (8,), rl(H)),           # 14 - "Rotate H left"
                (1, (8,), rl(L)),           # 15 - "Rotate L left"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_RL(s.MB[s.getHL()])) or s.setPC(e)),  # 16 - "Rotate value pointed by HL left"
                (1, (8,), rl(A)),           # 17 - "Rotate A left"
                (1, (8,), rr(B)),           # 18 - "Rotate B right"
                (1, (8,), rr(C)),           # 19 - "Rotate C right"
                (1, (8,), rr(D)),           # 1A - "Rotate D right"
                (1, (8,), rr(E)),           # 1B - "Rotate E right"
                (1, (8,), rr(H)),           # 1C - "Rotate H right"
                (1, (8,), rr(L)),           # 1D - "Rotate L right"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_RR(s.MB[s.getHL()])) or s.setPC(e)),  # 1E - "Rotate value pointed by HL right"
                (1, (8,), rr(A))]           # 1F - "Rotate A right"

ext_sla = lambda r: lambda s, e: s.setReg(r, s.CPU_EXT_SLA(s.reg[r])) or s.setPC(e)
ext_sra = lambda r: lambda s, e: s.setReg(r, s.CPU_EXT_SRA(s.reg[r])) or s.setPC(e)

CB_prefix_2x = [(1, (8,), ext_sla(B)),          # 20 - "Shift B left preserving sign"
                (1, (8,), ext_sla(C)),          # 21 - "Shift C left preserving sign"
                (1, (8,), ext_sla(D)),          # 22 - "Shift D left preserving sign"
                (1, (8,), ext_sla(E)),          # 23 - "Shift E left preserving sign"
                (1, (8,), ext_sla(H)),          # 24 - "Shift H left preserving sign"
                (1, (8,), ext_sla(L)),          # 25 - "Shift L left preserving sign"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_SLA(s.MB[s.getHL()])) or s.setPC(e)),  # 26 - "Shift value pointed by HL left preserving sign"
                (1, (8,), ext_sla(A)),          # 27 - "Shift A left preserving sign"
                (1, (8,), ext_sra(B)),          # 28 - "Shift B right preserving sign"
                (1, (8,), ext_sra(C)),          # 29 - "Shift C right preserving sign"
                (1, (8,), ext_sra(D)),          # 2A - "Shift D right preserving sign"
                (1, (8,), ext_sra(E)),          # 2B - "Shift E right preserving sign"
                (1, (8,), ext_sra(H)),          # 2C - "Shift H right preserving sign"
                (1, (8,), ext_sra(L)),          # 2D - "Shift L right preserving sign"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_SRA(s.MB[s.getHL()])) or s.setPC(e)),  # 2E - "Shift value pointed by HL right preserving sign"
                (1, (8,), ext_sra(A))]           # 2F - "Shift A right preserving sign"

ext_swap = lambda r: lambda s, e: s.setReg(r, s.CPU_EXT_SWAP(s.reg[r])) or s.setPC(e)
ext_srl = lambda r: lambda s, e: s.setReg(r, s.CPU_EXT_SRL(s.reg[r])) or s.setPC(e)

CB_prefix_3x = [(1, (8,), ext_swap(B)),         # 30 - "Swap nibbles in B"
                (1, (8,), ext_swap(C)),         # 31 - "Swap nibbles in C"
                (1, (8,), ext_swap(D)),         # 32 - "Swap nibbles in D"
                (1, (8,), ext_swap(E)),         # 33 - "Swap nibbles in E"
                (1, (8,), ext_swap(H)),         # 34 - "Swap nibbles in H"
                (1, (8,), ext_swap(L)),         # 35 - "Swap nibbles in L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_SWAP(s.MB[s.getHL()])) or s.setPC(e)),  # 36 - "Swap nibbles in value pointed by HL"
                (1, (8,), ext_swap(A)),         # 37 - "Swap nibbles in A"
                (1, (8,), ext_srl(B)),          # 38 - "Shift B right"
                (1, (8,), ext_srl(C)),          # 39 - "Shift C right"
                (1, (8,), ext_srl(D)),          # 3A - "Shift D right"
                (1, (8,), ext_srl(E)),          # 3B - "Shift E right"
                (1, (8,), ext_srl(H)),          # 3C - "Shift H right"
                (1, (8,), ext_srl(L)),          # 3D - "Shift L right"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_SRL(s.MB[s.getHL()])) or s.setPC(e)),  # 3E - "Shift value pointed by HL right"
                (1, (8,), ext_srl(A))]          # 3F - "Shift A right"

ext_bit = lambda b, r: lambda s, e: s.CPU_EXT_BIT(b, s.reg[r]) or s.setPC(e)

CB_prefix_4x = [(1, (8,), ext_bit(0, B)),        # 40 - "Test bit 0 of B"
                (1, (8,), ext_bit(0, C)),        # 41 - "Test bit 0 of C"
                (1, (8,), ext_bit(0, D)),        # 42 - "Test bit 0 of D"
                (1, (8,), ext_bit(0, E)),        # 43 - "Test bit 0 of E"
                (1, (8,), ext_bit(0, H)),        # 44 - "Test bit 0 of H"
                (1, (8,), ext_bit(0, L)),        # 45 - "Test bit 0 of L"
                (1, (16,), lambda s, e: s.CPU_EXT_BIT(0, s.MB[s.getHL()]) or s.setPC(e)),  # 46 - "Test bit 0 of value pointed by HL"
                (1, (8,), ext_bit(0, A)),        # 47 - "Test bit 0 of A"
                (1, (8,), ext_bit(1, B)),        # 48 - "Test bit 1 of B"
                (1, (8,), ext_bit(1, C)),        # 49 - "Test bit 1 of C"
                (1, (8,), ext_bit(1, D)),        # 4A - "Test bit 1 of D"
                (1, (8,), ext_bit(1, E)),        # 4B - "Test bit 1 of E"
                (1, (8,), ext_bit(1, H)),        # 4C - "Test bit 1 of H"
                (1, (8,), ext_bit(1, L)),        # 4D - "Test bit 1 of L"
                (1, (16,), lambda s, e: s.CPU_EXT_BIT(1, s.MB[s.getHL()]) or s.setPC(e)),  # 4E - "Test bit 1 of value pointed by HL"
                (1, (8,), ext_bit(1, A))]        # 4F - "Test bit 1 of A"

CB_prefix_5x = [(1, (8,), ext_bit(2, B)),        # 50 - "Test bit 2 of B"
                (1, (8,), ext_bit(2, C)),        # 51 - "Test bit 2 of C"
                (1, (8,), ext_bit(2, D)),        # 52 - "Test bit 2 of D"
                (1, (8,), ext_bit(2, E)),        # 53 - "Test bit 2 of E"
                (1, (8,), ext_bit(2, H)),        # 54 - "Test bit 2 of H"
                (1, (8,), ext_bit(2, L)),        # 55 - "Test bit 2 of L"
                (1, (16,), lambda s, e: s.CPU_EXT_BIT(2, s.MB[s.getHL()]) or s.setPC(e)),  # 56 - "Test bit 2 of value pointed by HL"
                (1, (8,), ext_bit(2, A)),        # 57 - "Test bit 2 of A"
                (1, (8,), ext_bit(3, B)),        # 58 - "Test bit 3 of B"
                (1, (8,), ext_bit(3, C)),        # 59 - "Test bit 3 of C"
                (1, (8,), ext_bit(3, D)),        # 5A - "Test bit 3 of D"
                (1, (8,), ext_bit(3, E)),        # 5B - "Test bit 3 of E"
                (1, (8,), ext_bit(3, H)),        # 5C - "Test bit 3 of H"
                (1, (8,), ext_bit(3, L)),        # 5D - "Test bit 3 of L"
                (1, (16,), lambda s, e: s.CPU_EXT_BIT(3, s.MB[s.getHL()]) or s.setPC(e)),  # 5E - "Test bit 3 of value pointed by HL"
                (1, (8,), ext_bit(3, A))]        # 5F - "Test bit 3 of A"

CB_prefix_6x = [(1, (8,), ext_bit(4, B)),        # 60 - "Test bit 4 of B"
                (1, (8,), ext_bit(4, C)),        # 61 - "Test bit 4 of C"
                (1, (8,), ext_bit(4, D)),        # 62 - "Test bit 4 of D"
                (1, (8,), ext_bit(4, E)),        # 63 - "Test bit 4 of E"
                (1, (8,), ext_bit(4, H)),        # 64 - "Test bit 4 of H"
                (1, (8,), ext_bit(4, L)),        # 65 - "Test bit 4 of L"
                (1, (16,), lambda s, e: s.CPU_EXT_BIT(4, s.MB[s.getHL()]) or s.setPC(e)),  # 66 - "Test bit 4 of value pointed by HL"
                (1, (8,), ext_bit(4, A)),        # 67 - "Test bit 4 of A"
                (1, (8,), ext_bit(5, B)),        # 68 - "Test bit 5 of B"
                (1, (8,), ext_bit(5, C)),        # 69 - "Test bit 5 of C"
                (1, (8,), ext_bit(5, D)),        # 6A - "Test bit 5 of D"
                (1, (8,), ext_bit(5, E)),        # 6B - "Test bit 5 of E"
                (1, (8,), ext_bit(5, H)),        # 6C - "Test bit 5 of H"
                (1, (8,), ext_bit(5, L)),        # 6D - "Test bit 5 of L"
                (1, (16,), lambda s, e: s.CPU_EXT_BIT(5, s.MB[s.getHL()]) or s.setPC(e)),  # 6E - "Test bit 5 of value pointed by HL"
                (1, (8,), ext_bit(5, A))]        # 6F - "Test bit 5 of A"

CB_prefix_7x = [(1, (8,), ext_bit(6, B)),        # 70 - "Test bit 6 of B"
                (1, (8,), ext_bit(6, C)),        # 71 - "Test bit 6 of C"
                (1, (8,), ext_bit(6, D)),        # 72 - "Test bit 6 of D"
                (1, (8,), ext_bit(6, E)),        # 73 - "Test bit 6 of E"
                (1, (8,), ext_bit(6, H)),        # 74 - "Test bit 6 of H"
                (1, (8,), ext_bit(6, L)),        # 75 - "Test bit 6 of L"
                (1, (16,), lambda s, e: s.CPU_EXT_BIT(6, s.MB[s.getHL()]) or s.setPC(e)),  # 76 - "Test bit 6 of value pointed by HL"
                (1, (8,), ext_bit(6, A)),        # 77 - "Test bit 6 of A"
                (1, (8,), ext_bit(7, B)),        # 78 - "Test bit 7 of B"
                (1, (8,), ext_bit(7, C)),        # 79 - "Test bit 7 of C"
                (1, (8,), ext_bit(7, D)),        # 7A - "Test bit 7 of D"
                (1, (8,), ext_bit(7, E)),        # 7B - "Test bit 7 of E"
                (1, (8,), ext_bit(7, H)),        # 7C - "Test bit 7 of H"
                (1, (8,), ext_bit(7, L)),        # 7D - "Test bit 7 of L"
                (1, (16,), lambda s, e: s.CPU_EXT_BIT(7, s.MB[s.getHL()]) or s.setPC(e)),  # 7E - "Test bit 7 of value pointed by HL"
                (1, (8,), ext_bit(7, A))]        # 7F - "Test bit 7 of A"


ext_clr = lambda b, r: lambda s, e: s.setReg(r, s.CPU_EXT_RES(b, s.reg[r])) or s.setPC(e)

CB_prefix_8x = [(1, (8,), ext_clr(0, B)),        # 80 - "Clear (reset) bit 0 of B"
                (1, (8,), ext_clr(0, C)),        # 81 - "Clear (reset) bit 0 of C"
                (1, (8,), ext_clr(0, D)),        # 82 - "Clear (reset) bit 0 of D"
                (1, (8,), ext_clr(0, E)),        # 83 - "Clear (reset) bit 0 of E"
                (1, (8,), ext_clr(0, H)),        # 84 - "Clear (reset) bit 0 of H"
                (1, (8,), ext_clr(0, L)),        # 85 - "Clear (reset) bit 0 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_RES(0, s.MB[s.getHL()])) or s.setPC(e)),  # 86 - "Clear (reset) bit 0 of value pointed by HL"
                (1, (8,), ext_clr(0, A)),        # 87 - "Clear (reset) bit 0 of A"
                (1, (8,), ext_clr(1, B)),        # 88 - "Clear (reset) bit 1 of B"
                (1, (8,), ext_clr(1, C)),        # 89 - "Clear (reset) bit 1 of C"
                (1, (8,), ext_clr(1, D)),        # 8A - "Clear (reset) bit 1 of D"
                (1, (8,), ext_clr(1, E)),        # 8B - "Clear (reset) bit 1 of E"
                (1, (8,), ext_clr(1, H)),        # 8C - "Clear (reset) bit 1 of H"
                (1, (8,), ext_clr(1, L)),        # 8D - "Clear (reset) bit 1 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_RES(1, s.MB[s.getHL()])) or s.setPC(e)),  # 8E - "Clear (reset) bit 1 of value pointed by HL"
                (1, (8,), ext_clr(1, A))]        # 8F - "Clear (reset) bit 1 of A"

CB_prefix_9x = [(1, (8,), ext_clr(2, B)),        # 90 - "Clear (reset) bit 2 of B"
                (1, (8,), ext_clr(2, C)),        # 91 - "Clear (reset) bit 2 of C"
                (1, (8,), ext_clr(2, D)),        # 92 - "Clear (reset) bit 2 of D"
                (1, (8,), ext_clr(2, E)),        # 93 - "Clear (reset) bit 2 of E"
                (1, (8,), ext_clr(2, H)),        # 94 - "Clear (reset) bit 2 of H"
                (1, (8,), ext_clr(2, L)),        # 95 - "Clear (reset) bit 2 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_RES(2, s.MB[s.getHL()])) or s.setPC(e)),  # 96 - "Clear (reset) bit 2 of value pointed by HL"
                (1, (8,), ext_clr(2, A)),        # 97 - "Clear (reset) bit 2 of A"
                (1, (8,), ext_clr(3, B)),        # 98 - "Clear (reset) bit 3 of B"
                (1, (8,), ext_clr(3, C)),        # 99 - "Clear (reset) bit 3 of C"
                (1, (8,), ext_clr(3, D)),        # 9A - "Clear (reset) bit 3 of D"
                (1, (8,), ext_clr(3, E)),        # 9B - "Clear (reset) bit 3 of E"
                (1, (8,), ext_clr(3, H)),        # 9C - "Clear (reset) bit 3 of H"
                (1, (8,), ext_clr(3, L)),        # 9D - "Clear (reset) bit 3 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_RES(3, s.MB[s.getHL()])) or s.setPC(e)),  # 9E - "Clear (reset) bit 3 of value pointed by HL"
                (1, (8,), ext_clr(3, A))]        # 9F - "Clear (reset) bit 3 of A"

CB_prefix_Ax = [(1, (8,), ext_clr(4, B)),        # A0 - "Clear (reset) bit 4 of B"
                (1, (8,), ext_clr(4, C)),        # A1 - "Clear (reset) bit 4 of C"
                (1, (8,), ext_clr(4, D)),        # A2 - "Clear (reset) bit 4 of D"
                (1, (8,), ext_clr(4, E)),        # A3 - "Clear (reset) bit 4 of E"
                (1, (8,), ext_clr(4, H)),        # A4 - "Clear (reset) bit 4 of H"
                (1, (8,), ext_clr(4, L)),        # A5 - "Clear (reset) bit 4 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_RES(4, s.MB[s.getHL()])) or s.setPC(e)),  # A6 - "Clear (reset) bit 4 of value pointed by HL"
                (1, (8,), ext_clr(4, A)),        # A7 - "Clear (reset) bit 4 of A"
                (1, (8,), ext_clr(5, B)),        # A8 - "Clear (reset) bit 5 of B"
                (1, (8,), ext_clr(5, C)),        # A9 - "Clear (reset) bit 5 of C"
                (1, (8,), ext_clr(5, D)),        # AA - "Clear (reset) bit 5 of D"
                (1, (8,), ext_clr(5, E)),        # AB - "Clear (reset) bit 5 of E"
                (1, (8,), ext_clr(5, H)),        # AC - "Clear (reset) bit 5 of H"
                (1, (8,), ext_clr(5, L)),        # AD - "Clear (reset) bit 5 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_RES(5, s.MB[s.getHL()])) or s.setPC(e)),  # AE - "Clear (reset) bit 5 of value pointed by HL"
                (1, (8,), ext_clr(5, A))]        # AF - "Clear (reset) bit 5 of A"

CB_prefix_Bx = [(1, (8,), ext_clr(6, B)),        # B0 - "Clear (reset) bit 6 of B"
                (1, (8,), ext_clr(6, C)),        # B1 - "Clear (reset) bit 6 of C"
                (1, (8,), ext_clr(6, D)),        # B2 - "Clear (reset) bit 6 of D"
                (1, (8,), ext_clr(6, E)),        # B3 - "Clear (reset) bit 6 of E"
                (1, (8,), ext_clr(6, H)),        # B4 - "Clear (reset) bit 6 of H"
                (1, (8,), ext_clr(6, L)),        # B5 - "Clear (reset) bit 6 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_RES(6, s.MB[s.getHL()])) or s.setPC(e)),  # B6 - "Clear (reset) bit 6 of value pointed by HL"
                (1, (8,), ext_clr(6, A)),        # B7 - "Clear (reset) bit 6 of A"
                (1, (8,), ext_clr(7, B)),        # B8 - "Clear (reset) bit 7 of B"
                (1, (8,), ext_clr(7, C)),        # B9 - "Clear (reset) bit 7 of C"
                (1, (8,), ext_clr(7, D)),        # BA - "Clear (reset) bit 7 of D"
                (1, (8,), ext_clr(7, E)),        # BB - "Clear (reset) bit 7 of E"
                (1, (8,), ext_clr(7, H)),        # BC - "Clear (reset) bit 7 of H"
                (1, (8,), ext_clr(7, L)),        # BD - "Clear (reset) bit 7 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_RES(7, s.MB[s.getHL()])) or s.setPC(e)),  # BE - "Clear (reset) bit 7 of value pointed by HL"
                (1, (8,), ext_clr(7, A))]        # BF - "Clear (reset) bit 7 of A"

ext_set = lambda b, r: lambda s, e: s.setReg(r, s.CPU_EXT_SET(b, s.reg[r])) or s.setPC(e)

CB_prefix_Cx = [(1, (8,), ext_set(0, B)),        # C0 - "Set bit 0 of B"
                (1, (8,), ext_set(0, C)),        # C1 - "Set bit 0 of C"
                (1, (8,), ext_set(0, D)),        # C2 - "Set bit 0 of D"
                (1, (8,), ext_set(0, E)),        # C3 - "Set bit 0 of E"
                (1, (8,), ext_set(0, H)),        # C4 - "Set bit 0 of H"
                (1, (8,), ext_set(0, L)),        # C5 - "Set bit 0 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_SET(0, s.MB[s.getHL()])) or s.setPC(e)),  # C6 - "Set bit 0 of value pointed by HL"
                (1, (8,), ext_set(0, A)),        # C7 - "Set bit 0 of A"
                (1, (8,), ext_set(1, B)),        # C8 - "Set bit 1 of B"
                (1, (8,), ext_set(1, C)),        # C9 - "Set bit 1 of C"
                (1, (8,), ext_set(1, D)),        # CA - "Set bit 1 of D"
                (1, (8,), ext_set(1, E)),        # CB - "Set bit 1 of E"
                (1, (8,), ext_set(1, H)),        # CC - "Set bit 1 of H"
                (1, (8,), ext_set(1, L)),        # CD - "Set bit 1 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_SET(1, s.MB[s.getHL()])) or s.setPC(e)),  # CE - "Set bit 1 of value pointed by HL"
                (1, (8,), ext_set(1, A))]        # CF - "Set bit 1 of A"

CB_prefix_Dx = [(1, (8,), ext_set(2, B)),        # D0 - "Set bit 2 of B"
                (1, (8,), ext_set(2, C)),        # D1 - "Set bit 2 of C"
                (1, (8,), ext_set(2, D)),        # D2 - "Set bit 2 of D"
                (1, (8,), ext_set(2, E)),        # D3 - "Set bit 2 of E"
                (1, (8,), ext_set(2, H)),        # D4 - "Set bit 2 of H"
                (1, (8,), ext_set(2, L)),        # D5 - "Set bit 2 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_SET(2, s.MB[s.getHL()])) or s.setPC(e)),  # D6 - "Set bit 2 of value pointed by HL"
                (1, (8,), ext_set(2, A)),        # D7 - "Set bit 2 of A"
                (1, (8,), ext_set(3, B)),        # D8 - "Set bit 3 of B"
                (1, (8,), ext_set(3, C)),        # D9 - "Set bit 3 of C"
                (1, (8,), ext_set(3, D)),        # DA - "Set bit 3 of D"
                (1, (8,), ext_set(3, E)),        # DB - "Set bit 3 of E"
                (1, (8,), ext_set(3, H)),        # DC - "Set bit 3 of H"
                (1, (8,), ext_set(3, L)),        # DD - "Set bit 3 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_SET(3, s.MB[s.getHL()])) or s.setPC(e)),  # DE - "Set bit 3 of value pointed by HL"
                (1, (8,), ext_set(3, A))]        # DF - "Set bit 3 of A"

CB_prefix_Ex = [(1, (8,), ext_set(4, B)),        # E0 - "Set bit 4 of B"
                (1, (8,), ext_set(4, C)),        # E1 - "Set bit 4 of C"
                (1, (8,), ext_set(4, D)),        # E2 - "Set bit 4 of D"
                (1, (8,), ext_set(4, E)),        # E3 - "Set bit 4 of E"
                (1, (8,), ext_set(4, H)),        # E4 - "Set bit 4 of H"
                (1, (8,), ext_set(4, L)),        # E5 - "Set bit 4 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_SET(4, s.MB[s.getHL()])) or s.setPC(e)),  # E6 - "Set bit 4 of value pointed by HL"
                (1, (8,), ext_set(4, A)),        # E7 - "Set bit 4 of A"
                (1, (8,), ext_set(5, B)),        # E8 - "Set bit 5 of B"
                (1, (8,), ext_set(5, C)),        # E9 - "Set bit 5 of C"
                (1, (8,), ext_set(5, D)),        # EA - "Set bit 5 of D"
                (1, (8,), ext_set(5, E)),        # EB - "Set bit 5 of E"
                (1, (8,), ext_set(5, H)),        # EC - "Set bit 5 of H"
                (1, (8,), ext_set(5, L)),        # ED - "Set bit 5 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_SET(5, s.MB[s.getHL()])) or s.setPC(e)),  # EE - "Set bit 5 of value pointed by HL"
                (1, (8,), ext_set(5, A))]        # EF - "Set bit 5 of A"

CB_prefix_Fx = [(1, (8,), ext_set(6, B)),        # F0 - "Set bit 6 of B"
                (1, (8,), ext_set(6, C)),        # F1 - "Set bit 6 of C"
                (1, (8,), ext_set(6, D)),        # F2 - "Set bit 6 of D"
                (1, (8,), ext_set(6, E)),        # F3 - "Set bit 6 of E"
                (1, (8,), ext_set(6, H)),        # F4 - "Set bit 6 of H"
                (1, (8,), ext_set(6, L)),        # F5 - "Set bit 6 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_SET(6, s.MB[s.getHL()])) or s.setPC(e)),  # F6 - "Set bit 6 of value pointed by HL"
                (1, (8,), ext_set(6, A)),        # F7 - "Set bit 6 of A"
                (1, (8,), ext_set(7, B)),        # F8 - "Set bit 7 of B"
                (1, (8,), ext_set(7, C)),        # F9 - "Set bit 7 of C"
                (1, (8,), ext_set(7, D)),        # FA - "Set bit 7 of D"
                (1, (8,), ext_set(7, E)),        # FB - "Set bit 7 of E"
                (1, (8,), ext_set(7, H)),        # FC - "Set bit 7 of H"
                (1, (8,), ext_set(7, L)),        # FD - "Set bit 7 of L"
                (1, (16,), lambda s, e: s.MB.__setitem__(s.getHL(), s.CPU_EXT_SET(7, s.MB[s.getHL()])) or s.setPC(e)),  # FE - "Set bit 7 of value pointed by HL"
                (1, (8,), ext_set(7, A))]        # FF - "Set bit 7 of A"

opcodes = []
opcodes.extend(opcode_0x)
opcodes.extend(opcode_1x)
opcodes.extend(opcode_2x)
opcodes.extend(opcode_3x)
opcodes.extend(opcode_4x)
opcodes.extend(opcode_5x)
opcodes.extend(opcode_6x)
opcodes.extend(opcode_7x)
opcodes.extend(opcode_8x)
opcodes.extend(opcode_9x)
opcodes.extend(opcode_Ax)
opcodes.extend(opcode_Bx)
opcodes.extend(opcode_Cx)
opcodes.extend(opcode_Dx)
opcodes.extend(opcode_Ex)
opcodes.extend(opcode_Fx)
opcodes.extend(CB_prefix_0x)
opcodes.extend(CB_prefix_1x)
opcodes.extend(CB_prefix_2x)
opcodes.extend(CB_prefix_3x)
opcodes.extend(CB_prefix_4x)
opcodes.extend(CB_prefix_5x)
opcodes.extend(CB_prefix_6x)
opcodes.extend(CB_prefix_7x)
opcodes.extend(CB_prefix_8x)
opcodes.extend(CB_prefix_9x)
opcodes.extend(CB_prefix_Ax)
opcodes.extend(CB_prefix_Bx)
opcodes.extend(CB_prefix_Cx)
opcodes.extend(CB_prefix_Dx)
opcodes.extend(CB_prefix_Ex)
opcodes.extend(CB_prefix_Fx)
