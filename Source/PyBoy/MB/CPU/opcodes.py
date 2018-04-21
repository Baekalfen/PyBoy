# -*- encoding: utf-8 -*-
# THIS FILE IS AUTO-GENERATED!!!
# DO NOT MODIFY THIS FILE.
# CHANGES TO THE CODE SHOULD BE MADE IN 'generator.py'.

from flags import flagZ, flagN, flagH, flagC
from MathUint8 import getSignedInt8

def NOP_00(self): # 00 NOP
    self.PC += 1
    return 0

def LD_01(self, v): # 01 LD BC,d16
    self.BC = v
    self.PC += 3
    return 0

def LD_02(self): # 02 LD (BC),A
    self.mb[self.BC] = self.A
    self.PC += 1
    return 0

def INC_03(self): # 03 INC BC
    t = self.BC+1
    # No flag operations
    t &= 0xFFFF
    self.BC = t
    self.PC += 1
    return 0

def INC_04(self): # 04 INC B
    t = self.B+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.B & 0xF) + (1 & 0xF)) > 0xF) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.B = t
    self.PC += 1
    return 0

def DEC_05(self): # 05 DEC B
    t = self.B-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.B & 0xF) - (1 & 0xF)) < 0) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.B = t
    self.PC += 1
    return 0

def LD_06(self, v): # 06 LD B,d8
    self.B = v
    self.PC += 2
    return 0

def RLCA_07(self): # 07 RLCA
    t = (self.A << 1) + (self.A >> 7)
    flag = 0b00000000
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def LD_08(self, v): # 08 LD (a16),SP
    self.mb[v] = self.SP & 0xFF
    self.mb[v+1] = self.SP >> 8
    self.PC += 3
    return 0

def ADD_09(self): # 09 ADD HL,BC
    t = self.HL+self.BC
    flag = 0b00000000
    flag += (((self.HL & 0xFFF) + (self.BC & 0xFFF)) > 0xFFF) << flagH
    flag += (t > 0xFFFF) << flagC
    self.F &= 0b10000000
    self.F |= flag
    t &= 0xFFFF
    self.HL = t
    self.PC += 1
    return 0

def LD_0a(self): # 0a LD A,(BC)
    self.A = self.mb[self.BC]
    self.PC += 1
    return 0

def DEC_0b(self): # 0b DEC BC
    t = self.BC-1
    # No flag operations
    t &= 0xFFFF
    self.BC = t
    self.PC += 1
    return 0

def INC_0c(self): # 0c INC C
    t = self.C+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.C & 0xF) + (1 & 0xF)) > 0xF) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.C = t
    self.PC += 1
    return 0

def DEC_0d(self): # 0d DEC C
    t = self.C-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.C & 0xF) - (1 & 0xF)) < 0) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.C = t
    self.PC += 1
    return 0

def LD_0e(self, v): # 0e LD C,d8
    self.C = v
    self.PC += 2
    return 0

def RRCA_0f(self): # 0f RRCA
    t = (self.A >> 1) + ((self.A & 1) << 7)+ ((self.A & 1) << 8)
    flag = 0b00000000
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def STOP_10(self, v): # 10 STOP 0
    pass
    self.PC += 2
    return 0

def LD_11(self, v): # 11 LD DE,d16
    self.DE = v
    self.PC += 3
    return 0

def LD_12(self): # 12 LD (DE),A
    self.mb[self.DE] = self.A
    self.PC += 1
    return 0

def INC_13(self): # 13 INC DE
    t = self.DE+1
    # No flag operations
    t &= 0xFFFF
    self.DE = t
    self.PC += 1
    return 0

def INC_14(self): # 14 INC D
    t = self.D+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.D & 0xF) + (1 & 0xF)) > 0xF) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.D = t
    self.PC += 1
    return 0

def DEC_15(self): # 15 DEC D
    t = self.D-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.D & 0xF) - (1 & 0xF)) < 0) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.D = t
    self.PC += 1
    return 0

def LD_16(self, v): # 16 LD D,d8
    self.D = v
    self.PC += 2
    return 0

def RLA_17(self): # 17 RLA
    t = (self.A << 1)+ self.fC
    flag = 0b00000000
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def JR_18(self, v): # 18 JR r8
    self.PC += 2 + getSignedInt8(v)
    self.PC &= 0xFFFF
    return 0

def ADD_19(self): # 19 ADD HL,DE
    t = self.HL+self.DE
    flag = 0b00000000
    flag += (((self.HL & 0xFFF) + (self.DE & 0xFFF)) > 0xFFF) << flagH
    flag += (t > 0xFFFF) << flagC
    self.F &= 0b10000000
    self.F |= flag
    t &= 0xFFFF
    self.HL = t
    self.PC += 1
    return 0

def LD_1a(self): # 1a LD A,(DE)
    self.A = self.mb[self.DE]
    self.PC += 1
    return 0

def DEC_1b(self): # 1b DEC DE
    t = self.DE-1
    # No flag operations
    t &= 0xFFFF
    self.DE = t
    self.PC += 1
    return 0

def INC_1c(self): # 1c INC E
    t = self.E+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.E & 0xF) + (1 & 0xF)) > 0xF) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.E = t
    self.PC += 1
    return 0

def DEC_1d(self): # 1d DEC E
    t = self.E-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.E & 0xF) - (1 & 0xF)) < 0) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.E = t
    self.PC += 1
    return 0

def LD_1e(self, v): # 1e LD E,d8
    self.E = v
    self.PC += 2
    return 0

def RRA_1f(self): # 1f RRA
    t = (self.A >> 1)+ (self.fC << 7)+ ((self.A & 1) << 8)
    flag = 0b00000000
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def JR_20(self, v): # 20 JR NZ,r8
    self.PC += 2
    if self.fNZ:
        self.PC += getSignedInt8(v)
        self.PC &= 0xFFFF
        return 0
    else:
        self.PC &= 0xFFFF
        return 1

def LD_21(self, v): # 21 LD HL,d16
    self.HL = v
    self.PC += 3
    return 0

def LD_22(self): # 22 LD (HL+),A
    self.mb[self.HL] = self.A
    self.HL += 1
    self.PC += 1
    return 0

def INC_23(self): # 23 INC HL
    t = self.HL+1
    # No flag operations
    t &= 0xFFFF
    self.HL = t
    self.PC += 1
    return 0

def INC_24(self): # 24 INC H
    t = self.H+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.H & 0xF) + (1 & 0xF)) > 0xF) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.H = t
    self.PC += 1
    return 0

def DEC_25(self): # 25 DEC H
    t = self.H-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.H & 0xF) - (1 & 0xF)) < 0) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.H = t
    self.PC += 1
    return 0

def LD_26(self, v): # 26 LD H,d8
    self.H = v
    self.PC += 2
    return 0

def DAA_27(self): # 27 DAA
    t = self.A
    corr = 0
    corr |= 0x06 if self.fH else 0x00
    corr |= 0x60 if self.fC else 0x00
    if self.fN:
        t -= corr
    else:
        corr |= 0x06 if (t & 0x0F) > 0x09 else 0x00
        corr |= 0x60 if t > 0x99 else 0x00
        t += corr
    flag = 0
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (corr & 0x60 != 0) << flagC
    self.F &= 0b01000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def JR_28(self, v): # 28 JR Z,r8
    self.PC += 2
    if self.fZ:
        self.PC += getSignedInt8(v)
        self.PC &= 0xFFFF
        return 0
    else:
        self.PC &= 0xFFFF
        return 1

def ADD_29(self): # 29 ADD HL,HL
    t = self.HL+self.HL
    flag = 0b00000000
    flag += (((self.HL & 0xFFF) + (self.HL & 0xFFF)) > 0xFFF) << flagH
    flag += (t > 0xFFFF) << flagC
    self.F &= 0b10000000
    self.F |= flag
    t &= 0xFFFF
    self.HL = t
    self.PC += 1
    return 0

def LD_2a(self): # 2a LD A,(HL+)
    self.A = self.mb[self.HL]
    self.HL += 1
    self.PC += 1
    return 0

def DEC_2b(self): # 2b DEC HL
    t = self.HL-1
    # No flag operations
    t &= 0xFFFF
    self.HL = t
    self.PC += 1
    return 0

def INC_2c(self): # 2c INC L
    t = self.L+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.L & 0xF) + (1 & 0xF)) > 0xF) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.L = t
    self.PC += 1
    return 0

def DEC_2d(self): # 2d DEC L
    t = self.L-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.L & 0xF) - (1 & 0xF)) < 0) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.L = t
    self.PC += 1
    return 0

def LD_2e(self, v): # 2e LD L,d8
    self.L = v
    self.PC += 2
    return 0

def CPL_2f(self): # 2f CPL
    self.A = (~self.A) & 0xFF
    flag = 0b01100000
    self.F &= 0b10010000
    self.F |= flag
    self.PC += 1
    return 0

def JR_30(self, v): # 30 JR NC,r8
    self.PC += 2
    if self.fNC:
        self.PC += getSignedInt8(v)
        self.PC &= 0xFFFF
        return 0
    else:
        self.PC &= 0xFFFF
        return 1

def LD_31(self, v): # 31 LD SP,d16
    self.SP = v
    self.PC += 3
    return 0

def LD_32(self): # 32 LD (HL-),A
    self.mb[self.HL] = self.A
    self.HL -= 1
    self.PC += 1
    return 0

def INC_33(self): # 33 INC SP
    t = self.SP+1
    # No flag operations
    t &= 0xFFFF
    self.SP = t
    self.PC += 1
    return 0

def INC_34(self): # 34 INC (HL)
    t = self.mb[self.HL]+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.mb[self.HL] & 0xF) + (1 & 0xF)) > 0xF) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.mb[self.HL] = t
    self.PC += 1
    return 0

def DEC_35(self): # 35 DEC (HL)
    t = self.mb[self.HL]-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.mb[self.HL] & 0xF) - (1 & 0xF)) < 0) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.mb[self.HL] = t
    self.PC += 1
    return 0

def LD_36(self, v): # 36 LD (HL),d8
    self.mb[self.HL] = v
    self.PC += 2
    return 0

def SCF_37(self): # 37 SCF
    flag = 0b00010000
    self.F &= 0b10000000
    self.F |= flag
    self.PC += 1
    return 0

def JR_38(self, v): # 38 JR C,r8
    self.PC += 2
    if self.fC:
        self.PC += getSignedInt8(v)
        self.PC &= 0xFFFF
        return 0
    else:
        self.PC &= 0xFFFF
        return 1

def ADD_39(self): # 39 ADD HL,SP
    t = self.HL+self.SP
    flag = 0b00000000
    flag += (((self.HL & 0xFFF) + (self.SP & 0xFFF)) > 0xFFF) << flagH
    flag += (t > 0xFFFF) << flagC
    self.F &= 0b10000000
    self.F |= flag
    t &= 0xFFFF
    self.HL = t
    self.PC += 1
    return 0

def LD_3a(self): # 3a LD A,(HL-)
    self.A = self.mb[self.HL]
    self.HL -= 1
    self.PC += 1
    return 0

def DEC_3b(self): # 3b DEC SP
    t = self.SP-1
    # No flag operations
    t &= 0xFFFF
    self.SP = t
    self.PC += 1
    return 0

def INC_3c(self): # 3c INC A
    t = self.A+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (1 & 0xF)) > 0xF) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def DEC_3d(self): # 3d DEC A
    t = self.A-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (1 & 0xF)) < 0) << flagH
    self.F &= 0b00010000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def LD_3e(self, v): # 3e LD A,d8
    self.A = v
    self.PC += 2
    return 0

def CCF_3f(self): # 3f CCF
    flag = (self.F & 0b00010000) ^ 0b00010000
    self.F &= 0b10000000
    self.F |= flag
    self.PC += 1
    return 0

def LD_40(self): # 40 LD B,B
    self.B = self.B
    self.PC += 1
    return 0

def LD_41(self): # 41 LD B,C
    self.B = self.C
    self.PC += 1
    return 0

def LD_42(self): # 42 LD B,D
    self.B = self.D
    self.PC += 1
    return 0

def LD_43(self): # 43 LD B,E
    self.B = self.E
    self.PC += 1
    return 0

def LD_44(self): # 44 LD B,H
    self.B = self.H
    self.PC += 1
    return 0

def LD_45(self): # 45 LD B,L
    self.B = self.L
    self.PC += 1
    return 0

def LD_46(self): # 46 LD B,(HL)
    self.B = self.mb[self.HL]
    self.PC += 1
    return 0

def LD_47(self): # 47 LD B,A
    self.B = self.A
    self.PC += 1
    return 0

def LD_48(self): # 48 LD C,B
    self.C = self.B
    self.PC += 1
    return 0

def LD_49(self): # 49 LD C,C
    self.C = self.C
    self.PC += 1
    return 0

def LD_4a(self): # 4a LD C,D
    self.C = self.D
    self.PC += 1
    return 0

def LD_4b(self): # 4b LD C,E
    self.C = self.E
    self.PC += 1
    return 0

def LD_4c(self): # 4c LD C,H
    self.C = self.H
    self.PC += 1
    return 0

def LD_4d(self): # 4d LD C,L
    self.C = self.L
    self.PC += 1
    return 0

def LD_4e(self): # 4e LD C,(HL)
    self.C = self.mb[self.HL]
    self.PC += 1
    return 0

def LD_4f(self): # 4f LD C,A
    self.C = self.A
    self.PC += 1
    return 0

def LD_50(self): # 50 LD D,B
    self.D = self.B
    self.PC += 1
    return 0

def LD_51(self): # 51 LD D,C
    self.D = self.C
    self.PC += 1
    return 0

def LD_52(self): # 52 LD D,D
    self.D = self.D
    self.PC += 1
    return 0

def LD_53(self): # 53 LD D,E
    self.D = self.E
    self.PC += 1
    return 0

def LD_54(self): # 54 LD D,H
    self.D = self.H
    self.PC += 1
    return 0

def LD_55(self): # 55 LD D,L
    self.D = self.L
    self.PC += 1
    return 0

def LD_56(self): # 56 LD D,(HL)
    self.D = self.mb[self.HL]
    self.PC += 1
    return 0

def LD_57(self): # 57 LD D,A
    self.D = self.A
    self.PC += 1
    return 0

def LD_58(self): # 58 LD E,B
    self.E = self.B
    self.PC += 1
    return 0

def LD_59(self): # 59 LD E,C
    self.E = self.C
    self.PC += 1
    return 0

def LD_5a(self): # 5a LD E,D
    self.E = self.D
    self.PC += 1
    return 0

def LD_5b(self): # 5b LD E,E
    self.E = self.E
    self.PC += 1
    return 0

def LD_5c(self): # 5c LD E,H
    self.E = self.H
    self.PC += 1
    return 0

def LD_5d(self): # 5d LD E,L
    self.E = self.L
    self.PC += 1
    return 0

def LD_5e(self): # 5e LD E,(HL)
    self.E = self.mb[self.HL]
    self.PC += 1
    return 0

def LD_5f(self): # 5f LD E,A
    self.E = self.A
    self.PC += 1
    return 0

def LD_60(self): # 60 LD H,B
    self.H = self.B
    self.PC += 1
    return 0

def LD_61(self): # 61 LD H,C
    self.H = self.C
    self.PC += 1
    return 0

def LD_62(self): # 62 LD H,D
    self.H = self.D
    self.PC += 1
    return 0

def LD_63(self): # 63 LD H,E
    self.H = self.E
    self.PC += 1
    return 0

def LD_64(self): # 64 LD H,H
    self.H = self.H
    self.PC += 1
    return 0

def LD_65(self): # 65 LD H,L
    self.H = self.L
    self.PC += 1
    return 0

def LD_66(self): # 66 LD H,(HL)
    self.H = self.mb[self.HL]
    self.PC += 1
    return 0

def LD_67(self): # 67 LD H,A
    self.H = self.A
    self.PC += 1
    return 0

def LD_68(self): # 68 LD L,B
    self.L = self.B
    self.PC += 1
    return 0

def LD_69(self): # 69 LD L,C
    self.L = self.C
    self.PC += 1
    return 0

def LD_6a(self): # 6a LD L,D
    self.L = self.D
    self.PC += 1
    return 0

def LD_6b(self): # 6b LD L,E
    self.L = self.E
    self.PC += 1
    return 0

def LD_6c(self): # 6c LD L,H
    self.L = self.H
    self.PC += 1
    return 0

def LD_6d(self): # 6d LD L,L
    self.L = self.L
    self.PC += 1
    return 0

def LD_6e(self): # 6e LD L,(HL)
    self.L = self.mb[self.HL]
    self.PC += 1
    return 0

def LD_6f(self): # 6f LD L,A
    self.L = self.A
    self.PC += 1
    return 0

def LD_70(self): # 70 LD (HL),B
    self.mb[self.HL] = self.B
    self.PC += 1
    return 0

def LD_71(self): # 71 LD (HL),C
    self.mb[self.HL] = self.C
    self.PC += 1
    return 0

def LD_72(self): # 72 LD (HL),D
    self.mb[self.HL] = self.D
    self.PC += 1
    return 0

def LD_73(self): # 73 LD (HL),E
    self.mb[self.HL] = self.E
    self.PC += 1
    return 0

def LD_74(self): # 74 LD (HL),H
    self.mb[self.HL] = self.H
    self.PC += 1
    return 0

def LD_75(self): # 75 LD (HL),L
    self.mb[self.HL] = self.L
    self.PC += 1
    return 0

def HALT_76(self): # 76 HALT
    if self.interruptMasterEnable:
        self.halted = True
    else:
        self.PC += 1
    return 0

def LD_77(self): # 77 LD (HL),A
    self.mb[self.HL] = self.A
    self.PC += 1
    return 0

def LD_78(self): # 78 LD A,B
    self.A = self.B
    self.PC += 1
    return 0

def LD_79(self): # 79 LD A,C
    self.A = self.C
    self.PC += 1
    return 0

def LD_7a(self): # 7a LD A,D
    self.A = self.D
    self.PC += 1
    return 0

def LD_7b(self): # 7b LD A,E
    self.A = self.E
    self.PC += 1
    return 0

def LD_7c(self): # 7c LD A,H
    self.A = self.H
    self.PC += 1
    return 0

def LD_7d(self): # 7d LD A,L
    self.A = self.L
    self.PC += 1
    return 0

def LD_7e(self): # 7e LD A,(HL)
    self.A = self.mb[self.HL]
    self.PC += 1
    return 0

def LD_7f(self): # 7f LD A,A
    self.A = self.A
    self.PC += 1
    return 0

def ADD_80(self): # 80 ADD A,B
    t = self.A+self.B
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.B & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADD_81(self): # 81 ADD A,C
    t = self.A+self.C
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.C & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADD_82(self): # 82 ADD A,D
    t = self.A+self.D
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.D & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADD_83(self): # 83 ADD A,E
    t = self.A+self.E
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.E & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADD_84(self): # 84 ADD A,H
    t = self.A+self.H
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.H & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADD_85(self): # 85 ADD A,L
    t = self.A+self.L
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.L & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADD_86(self): # 86 ADD A,(HL)
    t = self.A+self.mb[self.HL]
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.mb[self.HL] & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADD_87(self): # 87 ADD A,A
    t = self.A+self.A
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.A & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADC_88(self): # 88 ADC A,B
    t = self.A+self.B+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.B & 0xF) + self.fC) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADC_89(self): # 89 ADC A,C
    t = self.A+self.C+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.C & 0xF) + self.fC) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADC_8a(self): # 8a ADC A,D
    t = self.A+self.D+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.D & 0xF) + self.fC) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADC_8b(self): # 8b ADC A,E
    t = self.A+self.E+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.E & 0xF) + self.fC) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADC_8c(self): # 8c ADC A,H
    t = self.A+self.H+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.H & 0xF) + self.fC) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADC_8d(self): # 8d ADC A,L
    t = self.A+self.L+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.L & 0xF) + self.fC) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADC_8e(self): # 8e ADC A,(HL)
    t = self.A+self.mb[self.HL]+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.mb[self.HL] & 0xF) + self.fC) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def ADC_8f(self): # 8f ADC A,A
    t = self.A+self.A+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (self.A & 0xF) + self.fC) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SUB_90(self): # 90 SUB B
    t = self.A-self.B
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.B & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SUB_91(self): # 91 SUB C
    t = self.A-self.C
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.C & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SUB_92(self): # 92 SUB D
    t = self.A-self.D
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.D & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SUB_93(self): # 93 SUB E
    t = self.A-self.E
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.E & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SUB_94(self): # 94 SUB H
    t = self.A-self.H
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.H & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SUB_95(self): # 95 SUB L
    t = self.A-self.L
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.L & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SUB_96(self): # 96 SUB (HL)
    t = self.A-self.mb[self.HL]
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.mb[self.HL] & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SUB_97(self): # 97 SUB A
    t = self.A-self.A
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.A & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SBC_98(self): # 98 SBC A,B
    t = self.A-self.B- self.fC
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.B & 0xF) - self.fC) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SBC_99(self): # 99 SBC A,C
    t = self.A-self.C- self.fC
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.C & 0xF) - self.fC) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SBC_9a(self): # 9a SBC A,D
    t = self.A-self.D- self.fC
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.D & 0xF) - self.fC) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SBC_9b(self): # 9b SBC A,E
    t = self.A-self.E- self.fC
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.E & 0xF) - self.fC) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SBC_9c(self): # 9c SBC A,H
    t = self.A-self.H- self.fC
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.H & 0xF) - self.fC) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SBC_9d(self): # 9d SBC A,L
    t = self.A-self.L- self.fC
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.L & 0xF) - self.fC) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SBC_9e(self): # 9e SBC A,(HL)
    t = self.A-self.mb[self.HL]- self.fC
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.mb[self.HL] & 0xF) - self.fC) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def SBC_9f(self): # 9f SBC A,A
    t = self.A-self.A- self.fC
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.A & 0xF) - self.fC) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def AND_a0(self): # a0 AND B
    t = self.A&self.B
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def AND_a1(self): # a1 AND C
    t = self.A&self.C
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def AND_a2(self): # a2 AND D
    t = self.A&self.D
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def AND_a3(self): # a3 AND E
    t = self.A&self.E
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def AND_a4(self): # a4 AND H
    t = self.A&self.H
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def AND_a5(self): # a5 AND L
    t = self.A&self.L
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def AND_a6(self): # a6 AND (HL)
    t = self.A&self.mb[self.HL]
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def AND_a7(self): # a7 AND A
    t = self.A&self.A
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def XOR_a8(self): # a8 XOR B
    t = self.A^self.B
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def XOR_a9(self): # a9 XOR C
    t = self.A^self.C
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def XOR_aa(self): # aa XOR D
    t = self.A^self.D
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def XOR_ab(self): # ab XOR E
    t = self.A^self.E
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def XOR_ac(self): # ac XOR H
    t = self.A^self.H
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def XOR_ad(self): # ad XOR L
    t = self.A^self.L
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def XOR_ae(self): # ae XOR (HL)
    t = self.A^self.mb[self.HL]
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def XOR_af(self): # af XOR A
    t = self.A^self.A
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def OR_b0(self): # b0 OR B
    t = self.A|self.B
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def OR_b1(self): # b1 OR C
    t = self.A|self.C
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def OR_b2(self): # b2 OR D
    t = self.A|self.D
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def OR_b3(self): # b3 OR E
    t = self.A|self.E
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def OR_b4(self): # b4 OR H
    t = self.A|self.H
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def OR_b5(self): # b5 OR L
    t = self.A|self.L
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def OR_b6(self): # b6 OR (HL)
    t = self.A|self.mb[self.HL]
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def OR_b7(self): # b7 OR A
    t = self.A|self.A
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 1
    return 0

def CP_b8(self): # b8 CP B
    t = self.A-self.B
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.B & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.PC += 1
    return 0

def CP_b9(self): # b9 CP C
    t = self.A-self.C
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.C & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.PC += 1
    return 0

def CP_ba(self): # ba CP D
    t = self.A-self.D
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.D & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.PC += 1
    return 0

def CP_bb(self): # bb CP E
    t = self.A-self.E
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.E & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.PC += 1
    return 0

def CP_bc(self): # bc CP H
    t = self.A-self.H
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.H & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.PC += 1
    return 0

def CP_bd(self): # bd CP L
    t = self.A-self.L
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.L & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.PC += 1
    return 0

def CP_be(self): # be CP (HL)
    t = self.A-self.mb[self.HL]
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.mb[self.HL] & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.PC += 1
    return 0

def CP_bf(self): # bf CP A
    t = self.A-self.A
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (self.A & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.PC += 1
    return 0

def RET_c0(self): # c0 RET NZ
    if self.fNZ:
        self.PC = self.mb[self.SP+1] << 8 # High
        self.PC |= self.mb[self.SP] # Low
        self.SP += 2
        return 0
    else:
        self.PC += 1
        self.PC &= 0xFFFF
        return 1

def POP_c1(self): # c1 POP BC
    self.B = self.mb[self.SP+1] # High
    self.C = self.mb[self.SP] # Low
    self.SP += 2
    self.PC += 1
    return 0

def JP_c2(self, v): # c2 JP NZ,a16
    if self.fNZ:
        self.PC = v
        return 0
    else:
        self.PC += 3
        return 1

def JP_c3(self, v): # c3 JP a16
    self.PC = v
    return 0

def CALL_c4(self, v): # c4 CALL NZ,a16
    self.PC += 3
    self.PC &= 0xFFFF
    if self.fNZ:
        self.mb[self.SP-1] = self.PC >> 8 # High
        self.mb[self.SP-2] = self.PC & 0xFF # Low
        self.SP -= 2
        self.PC = v
        return 0
    else:
        return 1

def PUSH_c5(self): # c5 PUSH BC
    self.mb[self.SP-1] = self.B # High
    self.mb[self.SP-2] = self.C # Low
    self.SP -= 2
    self.PC += 1
    return 0

def ADD_c6(self, v): # c6 ADD A,d8
    t = self.A+v
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (v & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def RST_c7(self): # c7 RST 00H
    self.PC += 1
    self.mb[self.SP-1] = self.PC >> 8 # High
    self.mb[self.SP-2] = self.PC & 0xFF # Low
    self.SP -= 2
    self.PC = 0
    return 0

def RET_c8(self): # c8 RET Z
    if self.fZ:
        self.PC = self.mb[self.SP+1] << 8 # High
        self.PC |= self.mb[self.SP] # Low
        self.SP += 2
        return 0
    else:
        self.PC += 1
        self.PC &= 0xFFFF
        return 1

def RET_c9(self): # c9 RET
    self.PC = self.mb[self.SP+1] << 8 # High
    self.PC |= self.mb[self.SP] # Low
    self.SP += 2
    return 0

def JP_ca(self, v): # ca JP Z,a16
    if self.fZ:
        self.PC = v
        return 0
    else:
        self.PC += 3
        return 1

def CB_cb(self): # cb PREFIX CB
    raise Exception('CB cannot be called!')
    self.PC += 1
    return 0

def CALL_cc(self, v): # cc CALL Z,a16
    self.PC += 3
    self.PC &= 0xFFFF
    if self.fZ:
        self.mb[self.SP-1] = self.PC >> 8 # High
        self.mb[self.SP-2] = self.PC & 0xFF # Low
        self.SP -= 2
        self.PC = v
        return 0
    else:
        return 1

def CALL_cd(self, v): # cd CALL a16
    self.PC += 3
    self.PC &= 0xFFFF
    self.mb[self.SP-1] = self.PC >> 8 # High
    self.mb[self.SP-2] = self.PC & 0xFF # Low
    self.SP -= 2
    self.PC = v
    return 0

def ADC_ce(self, v): # ce ADC A,d8
    t = self.A+v+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) + (v & 0xF) + self.fC) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def RST_cf(self): # cf RST 08H
    self.PC += 1
    self.mb[self.SP-1] = self.PC >> 8 # High
    self.mb[self.SP-2] = self.PC & 0xFF # Low
    self.SP -= 2
    self.PC = 8
    return 0

def RET_d0(self): # d0 RET NC
    if self.fNC:
        self.PC = self.mb[self.SP+1] << 8 # High
        self.PC |= self.mb[self.SP] # Low
        self.SP += 2
        return 0
    else:
        self.PC += 1
        self.PC &= 0xFFFF
        return 1

def POP_d1(self): # d1 POP DE
    self.D = self.mb[self.SP+1] # High
    self.E = self.mb[self.SP] # Low
    self.SP += 2
    self.PC += 1
    return 0

def JP_d2(self, v): # d2 JP NC,a16
    if self.fNC:
        self.PC = v
        return 0
    else:
        self.PC += 3
        return 1

def CALL_d4(self, v): # d4 CALL NC,a16
    self.PC += 3
    self.PC &= 0xFFFF
    if self.fNC:
        self.mb[self.SP-1] = self.PC >> 8 # High
        self.mb[self.SP-2] = self.PC & 0xFF # Low
        self.SP -= 2
        self.PC = v
        return 0
    else:
        return 1

def PUSH_d5(self): # d5 PUSH DE
    self.mb[self.SP-1] = self.D # High
    self.mb[self.SP-2] = self.E # Low
    self.SP -= 2
    self.PC += 1
    return 0

def SUB_d6(self, v): # d6 SUB d8
    t = self.A-v
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (v & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def RST_d7(self): # d7 RST 10H
    self.PC += 1
    self.mb[self.SP-1] = self.PC >> 8 # High
    self.mb[self.SP-2] = self.PC & 0xFF # Low
    self.SP -= 2
    self.PC = 16
    return 0

def RET_d8(self): # d8 RET C
    if self.fC:
        self.PC = self.mb[self.SP+1] << 8 # High
        self.PC |= self.mb[self.SP] # Low
        self.SP += 2
        return 0
    else:
        self.PC += 1
        self.PC &= 0xFFFF
        return 1

def RETI_d9(self): # d9 RETI
    self.interruptMasterEnable = True
    self.PC = self.mb[self.SP+1] << 8 # High
    self.PC |= self.mb[self.SP] # Low
    self.SP += 2
    return 0

def JP_da(self, v): # da JP C,a16
    if self.fC:
        self.PC = v
        return 0
    else:
        self.PC += 3
        return 1

def CALL_dc(self, v): # dc CALL C,a16
    self.PC += 3
    self.PC &= 0xFFFF
    if self.fC:
        self.mb[self.SP-1] = self.PC >> 8 # High
        self.mb[self.SP-2] = self.PC & 0xFF # Low
        self.SP -= 2
        self.PC = v
        return 0
    else:
        return 1

def SBC_de(self, v): # de SBC A,d8
    t = self.A-v- self.fC
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (v & 0xF) - self.fC) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def RST_df(self): # df RST 18H
    self.PC += 1
    self.mb[self.SP-1] = self.PC >> 8 # High
    self.mb[self.SP-2] = self.PC & 0xFF # Low
    self.SP -= 2
    self.PC = 24
    return 0

def LD_e0(self, v): # e0 LDH (a8),A
    self.mb[v + 0xFF00] = self.A
    self.PC += 2
    return 0

def POP_e1(self): # e1 POP HL
    self.HL = (self.mb[self.SP+1] << 8) + self.mb[self.SP] # High
    self.SP += 2
    self.PC += 1
    return 0

def LD_e2(self): # e2 LD (C),A
    self.mb[0xFF00 + self.C] = self.A
    self.PC += 1
    return 0

def PUSH_e5(self): # e5 PUSH HL
    self.mb[self.SP-1] = self.HL >> 8 # High
    self.mb[self.SP-2] = self.HL & 0xFF # Low
    self.SP -= 2
    self.PC += 1
    return 0

def AND_e6(self, v): # e6 AND d8
    t = self.A&v
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def RST_e7(self): # e7 RST 20H
    self.PC += 1
    self.mb[self.SP-1] = self.PC >> 8 # High
    self.mb[self.SP-2] = self.PC & 0xFF # Low
    self.SP -= 2
    self.PC = 32
    return 0

def ADD_e8(self, v): # e8 ADD SP,r8
    t = self.SP+getSignedInt8(v)
    flag = 0b00000000
    flag += (((self.SP & 0xFFF) + (getSignedInt8(v) & 0xFFF)) > 0xFFF) << flagH
    flag += (t > 0xFFFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFFFF
    self.SP = t
    self.PC += 2
    return 0

def JP_e9(self): # e9 JP (HL)
    self.PC = self.HL
    return 0

def LD_ea(self, v): # ea LD (a16),A
    self.mb[v] = self.A
    self.PC += 3
    return 0

def XOR_ee(self, v): # ee XOR d8
    t = self.A^v
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def RST_ef(self): # ef RST 28H
    self.PC += 1
    self.mb[self.SP-1] = self.PC >> 8 # High
    self.mb[self.SP-2] = self.PC & 0xFF # Low
    self.SP -= 2
    self.PC = 40
    return 0

def LD_f0(self, v): # f0 LDH A,(a8)
    self.A = self.mb[v + 0xFF00]
    self.PC += 2
    return 0

def POP_f1(self): # f1 POP AF
    self.A = self.mb[self.SP+1] # High
    self.F = self.mb[self.SP] & 0xF0 # Low
    self.SP += 2
    self.PC += 1
    return 0

def LD_f2(self): # f2 LD A,(C)
    self.A = self.mb[0xFF00 + self.C]
    self.PC += 1
    return 0

def DI_f3(self): # f3 DI
    self.interruptMasterEnable = False
    self.PC += 1
    return 0

def PUSH_f5(self): # f5 PUSH AF
    self.mb[self.SP-1] = self.A # High
    self.mb[self.SP-2] = self.F # Low
    self.SP -= 2
    self.PC += 1
    return 0

def OR_f6(self, v): # f6 OR d8
    t = self.A|v
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def RST_f7(self): # f7 RST 30H
    self.PC += 1
    self.mb[self.SP-1] = self.PC >> 8 # High
    self.mb[self.SP-2] = self.PC & 0xFF # Low
    self.SP -= 2
    self.PC = 48
    return 0

def LD_f8(self, v): # f8 LD HL,SP+r8
    self.HL = self.SP + getSignedInt8(v)
    t = self.HL
    flag = 0b00000000
    flag += (((self.SP & 0xFFF) + (v & 0xFFF)) > 0xFFF) << flagH
    flag += (t > 0xFFFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    self.HL &= 0xFFFF
    self.PC += 2
    return 0

def LD_f9(self): # f9 LD SP,HL
    self.SP = self.HL
    self.PC += 1
    return 0

def LD_fa(self, v): # fa LD A,(a16)
    self.A = self.mb[v]
    self.PC += 3
    return 0

def EI_fb(self): # fb EI
    self.interruptMasterEnable = True
    self.PC += 1
    return 0

def CP_fe(self, v): # fe CP d8
    t = self.A-v
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((self.A & 0xF) - (v & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.PC += 2
    return 0

def RST_ff(self): # ff RST 38H
    self.PC += 1
    self.mb[self.SP-1] = self.PC >> 8 # High
    self.mb[self.SP-2] = self.PC & 0xFF # Low
    self.SP -= 2
    self.PC = 56
    return 0

def RLC_100(self): # 100 RLC B
    t = (self.B << 1) + (self.B >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.B = t
    self.PC += 2
    return 0

def RLC_101(self): # 101 RLC C
    t = (self.C << 1) + (self.C >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.C = t
    self.PC += 2
    return 0

def RLC_102(self): # 102 RLC D
    t = (self.D << 1) + (self.D >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.D = t
    self.PC += 2
    return 0

def RLC_103(self): # 103 RLC E
    t = (self.E << 1) + (self.E >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.E = t
    self.PC += 2
    return 0

def RLC_104(self): # 104 RLC H
    t = (self.H << 1) + (self.H >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.H = t
    self.PC += 2
    return 0

def RLC_105(self): # 105 RLC L
    t = (self.L << 1) + (self.L >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.L = t
    self.PC += 2
    return 0

def RLC_106(self): # 106 RLC (HL)
    t = (self.mb[self.HL] << 1) + (self.mb[self.HL] >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def RLC_107(self): # 107 RLC A
    t = (self.A << 1) + (self.A >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def RRC_108(self): # 108 RRC B
    t = (self.B >> 1) + ((self.B & 1) << 7)+ ((self.B & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.B = t
    self.PC += 2
    return 0

def RRC_109(self): # 109 RRC C
    t = (self.C >> 1) + ((self.C & 1) << 7)+ ((self.C & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.C = t
    self.PC += 2
    return 0

def RRC_10a(self): # 10a RRC D
    t = (self.D >> 1) + ((self.D & 1) << 7)+ ((self.D & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.D = t
    self.PC += 2
    return 0

def RRC_10b(self): # 10b RRC E
    t = (self.E >> 1) + ((self.E & 1) << 7)+ ((self.E & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.E = t
    self.PC += 2
    return 0

def RRC_10c(self): # 10c RRC H
    t = (self.H >> 1) + ((self.H & 1) << 7)+ ((self.H & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.H = t
    self.PC += 2
    return 0

def RRC_10d(self): # 10d RRC L
    t = (self.L >> 1) + ((self.L & 1) << 7)+ ((self.L & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.L = t
    self.PC += 2
    return 0

def RRC_10e(self): # 10e RRC (HL)
    t = (self.mb[self.HL] >> 1) + ((self.mb[self.HL] & 1) << 7)+ ((self.mb[self.HL] & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def RRC_10f(self): # 10f RRC A
    t = (self.A >> 1) + ((self.A & 1) << 7)+ ((self.A & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def RL_110(self): # 110 RL B
    t = (self.B << 1)+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.B = t
    self.PC += 2
    return 0

def RL_111(self): # 111 RL C
    t = (self.C << 1)+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.C = t
    self.PC += 2
    return 0

def RL_112(self): # 112 RL D
    t = (self.D << 1)+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.D = t
    self.PC += 2
    return 0

def RL_113(self): # 113 RL E
    t = (self.E << 1)+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.E = t
    self.PC += 2
    return 0

def RL_114(self): # 114 RL H
    t = (self.H << 1)+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.H = t
    self.PC += 2
    return 0

def RL_115(self): # 115 RL L
    t = (self.L << 1)+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.L = t
    self.PC += 2
    return 0

def RL_116(self): # 116 RL (HL)
    t = (self.mb[self.HL] << 1)+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def RL_117(self): # 117 RL A
    t = (self.A << 1)+ self.fC
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def RR_118(self): # 118 RR B
    t = (self.B >> 1)+ (self.fC << 7)+ ((self.B & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.B = t
    self.PC += 2
    return 0

def RR_119(self): # 119 RR C
    t = (self.C >> 1)+ (self.fC << 7)+ ((self.C & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.C = t
    self.PC += 2
    return 0

def RR_11a(self): # 11a RR D
    t = (self.D >> 1)+ (self.fC << 7)+ ((self.D & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.D = t
    self.PC += 2
    return 0

def RR_11b(self): # 11b RR E
    t = (self.E >> 1)+ (self.fC << 7)+ ((self.E & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.E = t
    self.PC += 2
    return 0

def RR_11c(self): # 11c RR H
    t = (self.H >> 1)+ (self.fC << 7)+ ((self.H & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.H = t
    self.PC += 2
    return 0

def RR_11d(self): # 11d RR L
    t = (self.L >> 1)+ (self.fC << 7)+ ((self.L & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.L = t
    self.PC += 2
    return 0

def RR_11e(self): # 11e RR (HL)
    t = (self.mb[self.HL] >> 1)+ (self.fC << 7)+ ((self.mb[self.HL] & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def RR_11f(self): # 11f RR A
    t = (self.A >> 1)+ (self.fC << 7)+ ((self.A & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def SLA_120(self): # 120 SLA B
    t = (self.B << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.B = t
    self.PC += 2
    return 0

def SLA_121(self): # 121 SLA C
    t = (self.C << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.C = t
    self.PC += 2
    return 0

def SLA_122(self): # 122 SLA D
    t = (self.D << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.D = t
    self.PC += 2
    return 0

def SLA_123(self): # 123 SLA E
    t = (self.E << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.E = t
    self.PC += 2
    return 0

def SLA_124(self): # 124 SLA H
    t = (self.H << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.H = t
    self.PC += 2
    return 0

def SLA_125(self): # 125 SLA L
    t = (self.L << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.L = t
    self.PC += 2
    return 0

def SLA_126(self): # 126 SLA (HL)
    t = (self.mb[self.HL] << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def SLA_127(self): # 127 SLA A
    t = (self.A << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def SRA_128(self): # 128 SRA B
    t = ((self.B >> 1) | (self.B & 0x80)) + ((self.B & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.B = t
    self.PC += 2
    return 0

def SRA_129(self): # 129 SRA C
    t = ((self.C >> 1) | (self.C & 0x80)) + ((self.C & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.C = t
    self.PC += 2
    return 0

def SRA_12a(self): # 12a SRA D
    t = ((self.D >> 1) | (self.D & 0x80)) + ((self.D & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.D = t
    self.PC += 2
    return 0

def SRA_12b(self): # 12b SRA E
    t = ((self.E >> 1) | (self.E & 0x80)) + ((self.E & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.E = t
    self.PC += 2
    return 0

def SRA_12c(self): # 12c SRA H
    t = ((self.H >> 1) | (self.H & 0x80)) + ((self.H & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.H = t
    self.PC += 2
    return 0

def SRA_12d(self): # 12d SRA L
    t = ((self.L >> 1) | (self.L & 0x80)) + ((self.L & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.L = t
    self.PC += 2
    return 0

def SRA_12e(self): # 12e SRA (HL)
    t = ((self.mb[self.HL] >> 1) | (self.mb[self.HL] & 0x80)) + ((self.mb[self.HL] & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def SRA_12f(self): # 12f SRA A
    t = ((self.A >> 1) | (self.A & 0x80)) + ((self.A & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def SWAP_130(self): # 130 SWAP B
    t = ((self.B & 0xF0) >> 4) | ((self.B & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.B = t
    self.PC += 2
    return 0

def SWAP_131(self): # 131 SWAP C
    t = ((self.C & 0xF0) >> 4) | ((self.C & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.C = t
    self.PC += 2
    return 0

def SWAP_132(self): # 132 SWAP D
    t = ((self.D & 0xF0) >> 4) | ((self.D & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.D = t
    self.PC += 2
    return 0

def SWAP_133(self): # 133 SWAP E
    t = ((self.E & 0xF0) >> 4) | ((self.E & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.E = t
    self.PC += 2
    return 0

def SWAP_134(self): # 134 SWAP H
    t = ((self.H & 0xF0) >> 4) | ((self.H & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.H = t
    self.PC += 2
    return 0

def SWAP_135(self): # 135 SWAP L
    t = ((self.L & 0xF0) >> 4) | ((self.L & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.L = t
    self.PC += 2
    return 0

def SWAP_136(self): # 136 SWAP (HL)
    t = ((self.mb[self.HL] & 0xF0) >> 4) | ((self.mb[self.HL] & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def SWAP_137(self): # 137 SWAP A
    t = ((self.A & 0xF0) >> 4) | ((self.A & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def SRL_138(self): # 138 SRL B
    t = (self.B >> 1) + ((self.B & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.B = t
    self.PC += 2
    return 0

def SRL_139(self): # 139 SRL C
    t = (self.C >> 1) + ((self.C & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.C = t
    self.PC += 2
    return 0

def SRL_13a(self): # 13a SRL D
    t = (self.D >> 1) + ((self.D & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.D = t
    self.PC += 2
    return 0

def SRL_13b(self): # 13b SRL E
    t = (self.E >> 1) + ((self.E & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.E = t
    self.PC += 2
    return 0

def SRL_13c(self): # 13c SRL H
    t = (self.H >> 1) + ((self.H & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.H = t
    self.PC += 2
    return 0

def SRL_13d(self): # 13d SRL L
    t = (self.L >> 1) + ((self.L & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.L = t
    self.PC += 2
    return 0

def SRL_13e(self): # 13e SRL (HL)
    t = (self.mb[self.HL] >> 1) + ((self.mb[self.HL] & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def SRL_13f(self): # 13f SRL A
    t = (self.A >> 1) + ((self.A & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    self.F &= 0b00000000
    self.F |= flag
    t &= 0xFF
    self.A = t
    self.PC += 2
    return 0

def BIT_140(self): # 140 BIT 0,B
    t = self.B & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_141(self): # 141 BIT 0,C
    t = self.C & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_142(self): # 142 BIT 0,D
    t = self.D & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_143(self): # 143 BIT 0,E
    t = self.E & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_144(self): # 144 BIT 0,H
    t = self.H & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_145(self): # 145 BIT 0,L
    t = self.L & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_146(self): # 146 BIT 0,(HL)
    t = self.mb[self.HL] & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_147(self): # 147 BIT 0,A
    t = self.A & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_148(self): # 148 BIT 1,B
    t = self.B & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_149(self): # 149 BIT 1,C
    t = self.C & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_14a(self): # 14a BIT 1,D
    t = self.D & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_14b(self): # 14b BIT 1,E
    t = self.E & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_14c(self): # 14c BIT 1,H
    t = self.H & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_14d(self): # 14d BIT 1,L
    t = self.L & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_14e(self): # 14e BIT 1,(HL)
    t = self.mb[self.HL] & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_14f(self): # 14f BIT 1,A
    t = self.A & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_150(self): # 150 BIT 2,B
    t = self.B & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_151(self): # 151 BIT 2,C
    t = self.C & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_152(self): # 152 BIT 2,D
    t = self.D & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_153(self): # 153 BIT 2,E
    t = self.E & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_154(self): # 154 BIT 2,H
    t = self.H & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_155(self): # 155 BIT 2,L
    t = self.L & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_156(self): # 156 BIT 2,(HL)
    t = self.mb[self.HL] & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_157(self): # 157 BIT 2,A
    t = self.A & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_158(self): # 158 BIT 3,B
    t = self.B & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_159(self): # 159 BIT 3,C
    t = self.C & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_15a(self): # 15a BIT 3,D
    t = self.D & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_15b(self): # 15b BIT 3,E
    t = self.E & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_15c(self): # 15c BIT 3,H
    t = self.H & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_15d(self): # 15d BIT 3,L
    t = self.L & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_15e(self): # 15e BIT 3,(HL)
    t = self.mb[self.HL] & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_15f(self): # 15f BIT 3,A
    t = self.A & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_160(self): # 160 BIT 4,B
    t = self.B & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_161(self): # 161 BIT 4,C
    t = self.C & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_162(self): # 162 BIT 4,D
    t = self.D & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_163(self): # 163 BIT 4,E
    t = self.E & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_164(self): # 164 BIT 4,H
    t = self.H & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_165(self): # 165 BIT 4,L
    t = self.L & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_166(self): # 166 BIT 4,(HL)
    t = self.mb[self.HL] & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_167(self): # 167 BIT 4,A
    t = self.A & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_168(self): # 168 BIT 5,B
    t = self.B & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_169(self): # 169 BIT 5,C
    t = self.C & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_16a(self): # 16a BIT 5,D
    t = self.D & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_16b(self): # 16b BIT 5,E
    t = self.E & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_16c(self): # 16c BIT 5,H
    t = self.H & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_16d(self): # 16d BIT 5,L
    t = self.L & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_16e(self): # 16e BIT 5,(HL)
    t = self.mb[self.HL] & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_16f(self): # 16f BIT 5,A
    t = self.A & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_170(self): # 170 BIT 6,B
    t = self.B & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_171(self): # 171 BIT 6,C
    t = self.C & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_172(self): # 172 BIT 6,D
    t = self.D & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_173(self): # 173 BIT 6,E
    t = self.E & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_174(self): # 174 BIT 6,H
    t = self.H & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_175(self): # 175 BIT 6,L
    t = self.L & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_176(self): # 176 BIT 6,(HL)
    t = self.mb[self.HL] & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_177(self): # 177 BIT 6,A
    t = self.A & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_178(self): # 178 BIT 7,B
    t = self.B & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_179(self): # 179 BIT 7,C
    t = self.C & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_17a(self): # 17a BIT 7,D
    t = self.D & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_17b(self): # 17b BIT 7,E
    t = self.E & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_17c(self): # 17c BIT 7,H
    t = self.H & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_17d(self): # 17d BIT 7,L
    t = self.L & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_17e(self): # 17e BIT 7,(HL)
    t = self.mb[self.HL] & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def BIT_17f(self): # 17f BIT 7,A
    t = self.A & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    self.F &= 0b00010000
    self.F |= flag
    self.PC += 2
    return 0

def RES_180(self): # 180 RES 0,B
    t = self.B & ~(1 << 0)
    self.B = t
    self.PC += 2
    return 0

def RES_181(self): # 181 RES 0,C
    t = self.C & ~(1 << 0)
    self.C = t
    self.PC += 2
    return 0

def RES_182(self): # 182 RES 0,D
    t = self.D & ~(1 << 0)
    self.D = t
    self.PC += 2
    return 0

def RES_183(self): # 183 RES 0,E
    t = self.E & ~(1 << 0)
    self.E = t
    self.PC += 2
    return 0

def RES_184(self): # 184 RES 0,H
    t = self.H & ~(1 << 0)
    self.H = t
    self.PC += 2
    return 0

def RES_185(self): # 185 RES 0,L
    t = self.L & ~(1 << 0)
    self.L = t
    self.PC += 2
    return 0

def RES_186(self): # 186 RES 0,(HL)
    t = self.mb[self.HL] & ~(1 << 0)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def RES_187(self): # 187 RES 0,A
    t = self.A & ~(1 << 0)
    self.A = t
    self.PC += 2
    return 0

def RES_188(self): # 188 RES 1,B
    t = self.B & ~(1 << 1)
    self.B = t
    self.PC += 2
    return 0

def RES_189(self): # 189 RES 1,C
    t = self.C & ~(1 << 1)
    self.C = t
    self.PC += 2
    return 0

def RES_18a(self): # 18a RES 1,D
    t = self.D & ~(1 << 1)
    self.D = t
    self.PC += 2
    return 0

def RES_18b(self): # 18b RES 1,E
    t = self.E & ~(1 << 1)
    self.E = t
    self.PC += 2
    return 0

def RES_18c(self): # 18c RES 1,H
    t = self.H & ~(1 << 1)
    self.H = t
    self.PC += 2
    return 0

def RES_18d(self): # 18d RES 1,L
    t = self.L & ~(1 << 1)
    self.L = t
    self.PC += 2
    return 0

def RES_18e(self): # 18e RES 1,(HL)
    t = self.mb[self.HL] & ~(1 << 1)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def RES_18f(self): # 18f RES 1,A
    t = self.A & ~(1 << 1)
    self.A = t
    self.PC += 2
    return 0

def RES_190(self): # 190 RES 2,B
    t = self.B & ~(1 << 2)
    self.B = t
    self.PC += 2
    return 0

def RES_191(self): # 191 RES 2,C
    t = self.C & ~(1 << 2)
    self.C = t
    self.PC += 2
    return 0

def RES_192(self): # 192 RES 2,D
    t = self.D & ~(1 << 2)
    self.D = t
    self.PC += 2
    return 0

def RES_193(self): # 193 RES 2,E
    t = self.E & ~(1 << 2)
    self.E = t
    self.PC += 2
    return 0

def RES_194(self): # 194 RES 2,H
    t = self.H & ~(1 << 2)
    self.H = t
    self.PC += 2
    return 0

def RES_195(self): # 195 RES 2,L
    t = self.L & ~(1 << 2)
    self.L = t
    self.PC += 2
    return 0

def RES_196(self): # 196 RES 2,(HL)
    t = self.mb[self.HL] & ~(1 << 2)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def RES_197(self): # 197 RES 2,A
    t = self.A & ~(1 << 2)
    self.A = t
    self.PC += 2
    return 0

def RES_198(self): # 198 RES 3,B
    t = self.B & ~(1 << 3)
    self.B = t
    self.PC += 2
    return 0

def RES_199(self): # 199 RES 3,C
    t = self.C & ~(1 << 3)
    self.C = t
    self.PC += 2
    return 0

def RES_19a(self): # 19a RES 3,D
    t = self.D & ~(1 << 3)
    self.D = t
    self.PC += 2
    return 0

def RES_19b(self): # 19b RES 3,E
    t = self.E & ~(1 << 3)
    self.E = t
    self.PC += 2
    return 0

def RES_19c(self): # 19c RES 3,H
    t = self.H & ~(1 << 3)
    self.H = t
    self.PC += 2
    return 0

def RES_19d(self): # 19d RES 3,L
    t = self.L & ~(1 << 3)
    self.L = t
    self.PC += 2
    return 0

def RES_19e(self): # 19e RES 3,(HL)
    t = self.mb[self.HL] & ~(1 << 3)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def RES_19f(self): # 19f RES 3,A
    t = self.A & ~(1 << 3)
    self.A = t
    self.PC += 2
    return 0

def RES_1a0(self): # 1a0 RES 4,B
    t = self.B & ~(1 << 4)
    self.B = t
    self.PC += 2
    return 0

def RES_1a1(self): # 1a1 RES 4,C
    t = self.C & ~(1 << 4)
    self.C = t
    self.PC += 2
    return 0

def RES_1a2(self): # 1a2 RES 4,D
    t = self.D & ~(1 << 4)
    self.D = t
    self.PC += 2
    return 0

def RES_1a3(self): # 1a3 RES 4,E
    t = self.E & ~(1 << 4)
    self.E = t
    self.PC += 2
    return 0

def RES_1a4(self): # 1a4 RES 4,H
    t = self.H & ~(1 << 4)
    self.H = t
    self.PC += 2
    return 0

def RES_1a5(self): # 1a5 RES 4,L
    t = self.L & ~(1 << 4)
    self.L = t
    self.PC += 2
    return 0

def RES_1a6(self): # 1a6 RES 4,(HL)
    t = self.mb[self.HL] & ~(1 << 4)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def RES_1a7(self): # 1a7 RES 4,A
    t = self.A & ~(1 << 4)
    self.A = t
    self.PC += 2
    return 0

def RES_1a8(self): # 1a8 RES 5,B
    t = self.B & ~(1 << 5)
    self.B = t
    self.PC += 2
    return 0

def RES_1a9(self): # 1a9 RES 5,C
    t = self.C & ~(1 << 5)
    self.C = t
    self.PC += 2
    return 0

def RES_1aa(self): # 1aa RES 5,D
    t = self.D & ~(1 << 5)
    self.D = t
    self.PC += 2
    return 0

def RES_1ab(self): # 1ab RES 5,E
    t = self.E & ~(1 << 5)
    self.E = t
    self.PC += 2
    return 0

def RES_1ac(self): # 1ac RES 5,H
    t = self.H & ~(1 << 5)
    self.H = t
    self.PC += 2
    return 0

def RES_1ad(self): # 1ad RES 5,L
    t = self.L & ~(1 << 5)
    self.L = t
    self.PC += 2
    return 0

def RES_1ae(self): # 1ae RES 5,(HL)
    t = self.mb[self.HL] & ~(1 << 5)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def RES_1af(self): # 1af RES 5,A
    t = self.A & ~(1 << 5)
    self.A = t
    self.PC += 2
    return 0

def RES_1b0(self): # 1b0 RES 6,B
    t = self.B & ~(1 << 6)
    self.B = t
    self.PC += 2
    return 0

def RES_1b1(self): # 1b1 RES 6,C
    t = self.C & ~(1 << 6)
    self.C = t
    self.PC += 2
    return 0

def RES_1b2(self): # 1b2 RES 6,D
    t = self.D & ~(1 << 6)
    self.D = t
    self.PC += 2
    return 0

def RES_1b3(self): # 1b3 RES 6,E
    t = self.E & ~(1 << 6)
    self.E = t
    self.PC += 2
    return 0

def RES_1b4(self): # 1b4 RES 6,H
    t = self.H & ~(1 << 6)
    self.H = t
    self.PC += 2
    return 0

def RES_1b5(self): # 1b5 RES 6,L
    t = self.L & ~(1 << 6)
    self.L = t
    self.PC += 2
    return 0

def RES_1b6(self): # 1b6 RES 6,(HL)
    t = self.mb[self.HL] & ~(1 << 6)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def RES_1b7(self): # 1b7 RES 6,A
    t = self.A & ~(1 << 6)
    self.A = t
    self.PC += 2
    return 0

def RES_1b8(self): # 1b8 RES 7,B
    t = self.B & ~(1 << 7)
    self.B = t
    self.PC += 2
    return 0

def RES_1b9(self): # 1b9 RES 7,C
    t = self.C & ~(1 << 7)
    self.C = t
    self.PC += 2
    return 0

def RES_1ba(self): # 1ba RES 7,D
    t = self.D & ~(1 << 7)
    self.D = t
    self.PC += 2
    return 0

def RES_1bb(self): # 1bb RES 7,E
    t = self.E & ~(1 << 7)
    self.E = t
    self.PC += 2
    return 0

def RES_1bc(self): # 1bc RES 7,H
    t = self.H & ~(1 << 7)
    self.H = t
    self.PC += 2
    return 0

def RES_1bd(self): # 1bd RES 7,L
    t = self.L & ~(1 << 7)
    self.L = t
    self.PC += 2
    return 0

def RES_1be(self): # 1be RES 7,(HL)
    t = self.mb[self.HL] & ~(1 << 7)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def RES_1bf(self): # 1bf RES 7,A
    t = self.A & ~(1 << 7)
    self.A = t
    self.PC += 2
    return 0

def SET_1c0(self): # 1c0 SET 0,B
    t = self.B | (1 << 0)
    self.B = t
    self.PC += 2
    return 0

def SET_1c1(self): # 1c1 SET 0,C
    t = self.C | (1 << 0)
    self.C = t
    self.PC += 2
    return 0

def SET_1c2(self): # 1c2 SET 0,D
    t = self.D | (1 << 0)
    self.D = t
    self.PC += 2
    return 0

def SET_1c3(self): # 1c3 SET 0,E
    t = self.E | (1 << 0)
    self.E = t
    self.PC += 2
    return 0

def SET_1c4(self): # 1c4 SET 0,H
    t = self.H | (1 << 0)
    self.H = t
    self.PC += 2
    return 0

def SET_1c5(self): # 1c5 SET 0,L
    t = self.L | (1 << 0)
    self.L = t
    self.PC += 2
    return 0

def SET_1c6(self): # 1c6 SET 0,(HL)
    t = self.mb[self.HL] | (1 << 0)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def SET_1c7(self): # 1c7 SET 0,A
    t = self.A | (1 << 0)
    self.A = t
    self.PC += 2
    return 0

def SET_1c8(self): # 1c8 SET 1,B
    t = self.B | (1 << 1)
    self.B = t
    self.PC += 2
    return 0

def SET_1c9(self): # 1c9 SET 1,C
    t = self.C | (1 << 1)
    self.C = t
    self.PC += 2
    return 0

def SET_1ca(self): # 1ca SET 1,D
    t = self.D | (1 << 1)
    self.D = t
    self.PC += 2
    return 0

def SET_1cb(self): # 1cb SET 1,E
    t = self.E | (1 << 1)
    self.E = t
    self.PC += 2
    return 0

def SET_1cc(self): # 1cc SET 1,H
    t = self.H | (1 << 1)
    self.H = t
    self.PC += 2
    return 0

def SET_1cd(self): # 1cd SET 1,L
    t = self.L | (1 << 1)
    self.L = t
    self.PC += 2
    return 0

def SET_1ce(self): # 1ce SET 1,(HL)
    t = self.mb[self.HL] | (1 << 1)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def SET_1cf(self): # 1cf SET 1,A
    t = self.A | (1 << 1)
    self.A = t
    self.PC += 2
    return 0

def SET_1d0(self): # 1d0 SET 2,B
    t = self.B | (1 << 2)
    self.B = t
    self.PC += 2
    return 0

def SET_1d1(self): # 1d1 SET 2,C
    t = self.C | (1 << 2)
    self.C = t
    self.PC += 2
    return 0

def SET_1d2(self): # 1d2 SET 2,D
    t = self.D | (1 << 2)
    self.D = t
    self.PC += 2
    return 0

def SET_1d3(self): # 1d3 SET 2,E
    t = self.E | (1 << 2)
    self.E = t
    self.PC += 2
    return 0

def SET_1d4(self): # 1d4 SET 2,H
    t = self.H | (1 << 2)
    self.H = t
    self.PC += 2
    return 0

def SET_1d5(self): # 1d5 SET 2,L
    t = self.L | (1 << 2)
    self.L = t
    self.PC += 2
    return 0

def SET_1d6(self): # 1d6 SET 2,(HL)
    t = self.mb[self.HL] | (1 << 2)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def SET_1d7(self): # 1d7 SET 2,A
    t = self.A | (1 << 2)
    self.A = t
    self.PC += 2
    return 0

def SET_1d8(self): # 1d8 SET 3,B
    t = self.B | (1 << 3)
    self.B = t
    self.PC += 2
    return 0

def SET_1d9(self): # 1d9 SET 3,C
    t = self.C | (1 << 3)
    self.C = t
    self.PC += 2
    return 0

def SET_1da(self): # 1da SET 3,D
    t = self.D | (1 << 3)
    self.D = t
    self.PC += 2
    return 0

def SET_1db(self): # 1db SET 3,E
    t = self.E | (1 << 3)
    self.E = t
    self.PC += 2
    return 0

def SET_1dc(self): # 1dc SET 3,H
    t = self.H | (1 << 3)
    self.H = t
    self.PC += 2
    return 0

def SET_1dd(self): # 1dd SET 3,L
    t = self.L | (1 << 3)
    self.L = t
    self.PC += 2
    return 0

def SET_1de(self): # 1de SET 3,(HL)
    t = self.mb[self.HL] | (1 << 3)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def SET_1df(self): # 1df SET 3,A
    t = self.A | (1 << 3)
    self.A = t
    self.PC += 2
    return 0

def SET_1e0(self): # 1e0 SET 4,B
    t = self.B | (1 << 4)
    self.B = t
    self.PC += 2
    return 0

def SET_1e1(self): # 1e1 SET 4,C
    t = self.C | (1 << 4)
    self.C = t
    self.PC += 2
    return 0

def SET_1e2(self): # 1e2 SET 4,D
    t = self.D | (1 << 4)
    self.D = t
    self.PC += 2
    return 0

def SET_1e3(self): # 1e3 SET 4,E
    t = self.E | (1 << 4)
    self.E = t
    self.PC += 2
    return 0

def SET_1e4(self): # 1e4 SET 4,H
    t = self.H | (1 << 4)
    self.H = t
    self.PC += 2
    return 0

def SET_1e5(self): # 1e5 SET 4,L
    t = self.L | (1 << 4)
    self.L = t
    self.PC += 2
    return 0

def SET_1e6(self): # 1e6 SET 4,(HL)
    t = self.mb[self.HL] | (1 << 4)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def SET_1e7(self): # 1e7 SET 4,A
    t = self.A | (1 << 4)
    self.A = t
    self.PC += 2
    return 0

def SET_1e8(self): # 1e8 SET 5,B
    t = self.B | (1 << 5)
    self.B = t
    self.PC += 2
    return 0

def SET_1e9(self): # 1e9 SET 5,C
    t = self.C | (1 << 5)
    self.C = t
    self.PC += 2
    return 0

def SET_1ea(self): # 1ea SET 5,D
    t = self.D | (1 << 5)
    self.D = t
    self.PC += 2
    return 0

def SET_1eb(self): # 1eb SET 5,E
    t = self.E | (1 << 5)
    self.E = t
    self.PC += 2
    return 0

def SET_1ec(self): # 1ec SET 5,H
    t = self.H | (1 << 5)
    self.H = t
    self.PC += 2
    return 0

def SET_1ed(self): # 1ed SET 5,L
    t = self.L | (1 << 5)
    self.L = t
    self.PC += 2
    return 0

def SET_1ee(self): # 1ee SET 5,(HL)
    t = self.mb[self.HL] | (1 << 5)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def SET_1ef(self): # 1ef SET 5,A
    t = self.A | (1 << 5)
    self.A = t
    self.PC += 2
    return 0

def SET_1f0(self): # 1f0 SET 6,B
    t = self.B | (1 << 6)
    self.B = t
    self.PC += 2
    return 0

def SET_1f1(self): # 1f1 SET 6,C
    t = self.C | (1 << 6)
    self.C = t
    self.PC += 2
    return 0

def SET_1f2(self): # 1f2 SET 6,D
    t = self.D | (1 << 6)
    self.D = t
    self.PC += 2
    return 0

def SET_1f3(self): # 1f3 SET 6,E
    t = self.E | (1 << 6)
    self.E = t
    self.PC += 2
    return 0

def SET_1f4(self): # 1f4 SET 6,H
    t = self.H | (1 << 6)
    self.H = t
    self.PC += 2
    return 0

def SET_1f5(self): # 1f5 SET 6,L
    t = self.L | (1 << 6)
    self.L = t
    self.PC += 2
    return 0

def SET_1f6(self): # 1f6 SET 6,(HL)
    t = self.mb[self.HL] | (1 << 6)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def SET_1f7(self): # 1f7 SET 6,A
    t = self.A | (1 << 6)
    self.A = t
    self.PC += 2
    return 0

def SET_1f8(self): # 1f8 SET 7,B
    t = self.B | (1 << 7)
    self.B = t
    self.PC += 2
    return 0

def SET_1f9(self): # 1f9 SET 7,C
    t = self.C | (1 << 7)
    self.C = t
    self.PC += 2
    return 0

def SET_1fa(self): # 1fa SET 7,D
    t = self.D | (1 << 7)
    self.D = t
    self.PC += 2
    return 0

def SET_1fb(self): # 1fb SET 7,E
    t = self.E | (1 << 7)
    self.E = t
    self.PC += 2
    return 0

def SET_1fc(self): # 1fc SET 7,H
    t = self.H | (1 << 7)
    self.H = t
    self.PC += 2
    return 0

def SET_1fd(self): # 1fd SET 7,L
    t = self.L | (1 << 7)
    self.L = t
    self.PC += 2
    return 0

def SET_1fe(self): # 1fe SET 7,(HL)
    t = self.mb[self.HL] | (1 << 7)
    self.mb[self.HL] = t
    self.PC += 2
    return 0

def SET_1ff(self): # 1ff SET 7,A
    t = self.A | (1 << 7)
    self.A = t
    self.PC += 2
    return 0

opcodes = [
    (1, (4,), NOP_00),
    (3, (12,), LD_01),
    (1, (8,), LD_02),
    (1, (8,), INC_03),
    (1, (4,), INC_04),
    (1, (4,), DEC_05),
    (2, (8,), LD_06),
    (1, (4,), RLCA_07),
    (3, (20,), LD_08),
    (1, (8,), ADD_09),
    (1, (8,), LD_0a),
    (1, (8,), DEC_0b),
    (1, (4,), INC_0c),
    (1, (4,), DEC_0d),
    (2, (8,), LD_0e),
    (1, (4,), RRCA_0f),
    (2, (4,), STOP_10),
    (3, (12,), LD_11),
    (1, (8,), LD_12),
    (1, (8,), INC_13),
    (1, (4,), INC_14),
    (1, (4,), DEC_15),
    (2, (8,), LD_16),
    (1, (4,), RLA_17),
    (2, (12,), JR_18),
    (1, (8,), ADD_19),
    (1, (8,), LD_1a),
    (1, (8,), DEC_1b),
    (1, (4,), INC_1c),
    (1, (4,), DEC_1d),
    (2, (8,), LD_1e),
    (1, (4,), RRA_1f),
    (2, (12, 8), JR_20),
    (3, (12,), LD_21),
    (1, (8,), LD_22),
    (1, (8,), INC_23),
    (1, (4,), INC_24),
    (1, (4,), DEC_25),
    (2, (8,), LD_26),
    (1, (4,), DAA_27),
    (2, (12, 8), JR_28),
    (1, (8,), ADD_29),
    (1, (8,), LD_2a),
    (1, (8,), DEC_2b),
    (1, (4,), INC_2c),
    (1, (4,), DEC_2d),
    (2, (8,), LD_2e),
    (1, (4,), CPL_2f),
    (2, (12, 8), JR_30),
    (3, (12,), LD_31),
    (1, (8,), LD_32),
    (1, (8,), INC_33),
    (1, (12,), INC_34),
    (1, (12,), DEC_35),
    (2, (12,), LD_36),
    (1, (4,), SCF_37),
    (2, (12, 8), JR_38),
    (1, (8,), ADD_39),
    (1, (8,), LD_3a),
    (1, (8,), DEC_3b),
    (1, (4,), INC_3c),
    (1, (4,), DEC_3d),
    (2, (8,), LD_3e),
    (1, (4,), CCF_3f),
    (1, (4,), LD_40),
    (1, (4,), LD_41),
    (1, (4,), LD_42),
    (1, (4,), LD_43),
    (1, (4,), LD_44),
    (1, (4,), LD_45),
    (1, (8,), LD_46),
    (1, (4,), LD_47),
    (1, (4,), LD_48),
    (1, (4,), LD_49),
    (1, (4,), LD_4a),
    (1, (4,), LD_4b),
    (1, (4,), LD_4c),
    (1, (4,), LD_4d),
    (1, (8,), LD_4e),
    (1, (4,), LD_4f),
    (1, (4,), LD_50),
    (1, (4,), LD_51),
    (1, (4,), LD_52),
    (1, (4,), LD_53),
    (1, (4,), LD_54),
    (1, (4,), LD_55),
    (1, (8,), LD_56),
    (1, (4,), LD_57),
    (1, (4,), LD_58),
    (1, (4,), LD_59),
    (1, (4,), LD_5a),
    (1, (4,), LD_5b),
    (1, (4,), LD_5c),
    (1, (4,), LD_5d),
    (1, (8,), LD_5e),
    (1, (4,), LD_5f),
    (1, (4,), LD_60),
    (1, (4,), LD_61),
    (1, (4,), LD_62),
    (1, (4,), LD_63),
    (1, (4,), LD_64),
    (1, (4,), LD_65),
    (1, (8,), LD_66),
    (1, (4,), LD_67),
    (1, (4,), LD_68),
    (1, (4,), LD_69),
    (1, (4,), LD_6a),
    (1, (4,), LD_6b),
    (1, (4,), LD_6c),
    (1, (4,), LD_6d),
    (1, (8,), LD_6e),
    (1, (4,), LD_6f),
    (1, (8,), LD_70),
    (1, (8,), LD_71),
    (1, (8,), LD_72),
    (1, (8,), LD_73),
    (1, (8,), LD_74),
    (1, (8,), LD_75),
    (1, (4,), HALT_76),
    (1, (8,), LD_77),
    (1, (4,), LD_78),
    (1, (4,), LD_79),
    (1, (4,), LD_7a),
    (1, (4,), LD_7b),
    (1, (4,), LD_7c),
    (1, (4,), LD_7d),
    (1, (8,), LD_7e),
    (1, (4,), LD_7f),
    (1, (4,), ADD_80),
    (1, (4,), ADD_81),
    (1, (4,), ADD_82),
    (1, (4,), ADD_83),
    (1, (4,), ADD_84),
    (1, (4,), ADD_85),
    (1, (8,), ADD_86),
    (1, (4,), ADD_87),
    (1, (4,), ADC_88),
    (1, (4,), ADC_89),
    (1, (4,), ADC_8a),
    (1, (4,), ADC_8b),
    (1, (4,), ADC_8c),
    (1, (4,), ADC_8d),
    (1, (8,), ADC_8e),
    (1, (4,), ADC_8f),
    (1, (4,), SUB_90),
    (1, (4,), SUB_91),
    (1, (4,), SUB_92),
    (1, (4,), SUB_93),
    (1, (4,), SUB_94),
    (1, (4,), SUB_95),
    (1, (8,), SUB_96),
    (1, (4,), SUB_97),
    (1, (4,), SBC_98),
    (1, (4,), SBC_99),
    (1, (4,), SBC_9a),
    (1, (4,), SBC_9b),
    (1, (4,), SBC_9c),
    (1, (4,), SBC_9d),
    (1, (8,), SBC_9e),
    (1, (4,), SBC_9f),
    (1, (4,), AND_a0),
    (1, (4,), AND_a1),
    (1, (4,), AND_a2),
    (1, (4,), AND_a3),
    (1, (4,), AND_a4),
    (1, (4,), AND_a5),
    (1, (8,), AND_a6),
    (1, (4,), AND_a7),
    (1, (4,), XOR_a8),
    (1, (4,), XOR_a9),
    (1, (4,), XOR_aa),
    (1, (4,), XOR_ab),
    (1, (4,), XOR_ac),
    (1, (4,), XOR_ad),
    (1, (8,), XOR_ae),
    (1, (4,), XOR_af),
    (1, (4,), OR_b0),
    (1, (4,), OR_b1),
    (1, (4,), OR_b2),
    (1, (4,), OR_b3),
    (1, (4,), OR_b4),
    (1, (4,), OR_b5),
    (1, (8,), OR_b6),
    (1, (4,), OR_b7),
    (1, (4,), CP_b8),
    (1, (4,), CP_b9),
    (1, (4,), CP_ba),
    (1, (4,), CP_bb),
    (1, (4,), CP_bc),
    (1, (4,), CP_bd),
    (1, (8,), CP_be),
    (1, (4,), CP_bf),
    (1, (20, 8), RET_c0),
    (1, (12,), POP_c1),
    (3, (16, 12), JP_c2),
    (3, (16,), JP_c3),
    (3, (24, 12), CALL_c4),
    (1, (16,), PUSH_c5),
    (2, (8,), ADD_c6),
    (1, (16,), RST_c7),
    (1, (20, 8), RET_c8),
    (1, (16,), RET_c9),
    (3, (16, 12), JP_ca),
    (1, (4,), CB_cb),
    (3, (24, 12), CALL_cc),
    (3, (24,), CALL_cd),
    (2, (8,), ADC_ce),
    (1, (16,), RST_cf),
    (1, (20, 8), RET_d0),
    (1, (12,), POP_d1),
    (3, (16, 12), JP_d2),
    None,
    (3, (24, 12), CALL_d4),
    (1, (16,), PUSH_d5),
    (2, (8,), SUB_d6),
    (1, (16,), RST_d7),
    (1, (20, 8), RET_d8),
    (1, (16,), RETI_d9),
    (3, (16, 12), JP_da),
    None,
    (3, (24, 12), CALL_dc),
    None,
    (2, (8,), SBC_de),
    (1, (16,), RST_df),
    (2, (12,), LD_e0),
    (1, (12,), POP_e1),
    (1, (8,), LD_e2),
    None,
    None,
    (1, (16,), PUSH_e5),
    (2, (8,), AND_e6),
    (1, (16,), RST_e7),
    (2, (16,), ADD_e8),
    (1, (4,), JP_e9),
    (3, (16,), LD_ea),
    None,
    None,
    None,
    (2, (8,), XOR_ee),
    (1, (16,), RST_ef),
    (2, (12,), LD_f0),
    (1, (12,), POP_f1),
    (1, (8,), LD_f2),
    (1, (4,), DI_f3),
    None,
    (1, (16,), PUSH_f5),
    (2, (8,), OR_f6),
    (1, (16,), RST_f7),
    (2, (12,), LD_f8),
    (1, (8,), LD_f9),
    (3, (16,), LD_fa),
    (1, (4,), EI_fb),
    None,
    None,
    (2, (8,), CP_fe),
    (1, (16,), RST_ff),
    (1, (8,), RLC_100),
    (1, (8,), RLC_101),
    (1, (8,), RLC_102),
    (1, (8,), RLC_103),
    (1, (8,), RLC_104),
    (1, (8,), RLC_105),
    (1, (16,), RLC_106),
    (1, (8,), RLC_107),
    (1, (8,), RRC_108),
    (1, (8,), RRC_109),
    (1, (8,), RRC_10a),
    (1, (8,), RRC_10b),
    (1, (8,), RRC_10c),
    (1, (8,), RRC_10d),
    (1, (16,), RRC_10e),
    (1, (8,), RRC_10f),
    (1, (8,), RL_110),
    (1, (8,), RL_111),
    (1, (8,), RL_112),
    (1, (8,), RL_113),
    (1, (8,), RL_114),
    (1, (8,), RL_115),
    (1, (16,), RL_116),
    (1, (8,), RL_117),
    (1, (8,), RR_118),
    (1, (8,), RR_119),
    (1, (8,), RR_11a),
    (1, (8,), RR_11b),
    (1, (8,), RR_11c),
    (1, (8,), RR_11d),
    (1, (16,), RR_11e),
    (1, (8,), RR_11f),
    (1, (8,), SLA_120),
    (1, (8,), SLA_121),
    (1, (8,), SLA_122),
    (1, (8,), SLA_123),
    (1, (8,), SLA_124),
    (1, (8,), SLA_125),
    (1, (16,), SLA_126),
    (1, (8,), SLA_127),
    (1, (8,), SRA_128),
    (1, (8,), SRA_129),
    (1, (8,), SRA_12a),
    (1, (8,), SRA_12b),
    (1, (8,), SRA_12c),
    (1, (8,), SRA_12d),
    (1, (16,), SRA_12e),
    (1, (8,), SRA_12f),
    (1, (8,), SWAP_130),
    (1, (8,), SWAP_131),
    (1, (8,), SWAP_132),
    (1, (8,), SWAP_133),
    (1, (8,), SWAP_134),
    (1, (8,), SWAP_135),
    (1, (16,), SWAP_136),
    (1, (8,), SWAP_137),
    (1, (8,), SRL_138),
    (1, (8,), SRL_139),
    (1, (8,), SRL_13a),
    (1, (8,), SRL_13b),
    (1, (8,), SRL_13c),
    (1, (8,), SRL_13d),
    (1, (16,), SRL_13e),
    (1, (8,), SRL_13f),
    (1, (8,), BIT_140),
    (1, (8,), BIT_141),
    (1, (8,), BIT_142),
    (1, (8,), BIT_143),
    (1, (8,), BIT_144),
    (1, (8,), BIT_145),
    (1, (16,), BIT_146),
    (1, (8,), BIT_147),
    (1, (8,), BIT_148),
    (1, (8,), BIT_149),
    (1, (8,), BIT_14a),
    (1, (8,), BIT_14b),
    (1, (8,), BIT_14c),
    (1, (8,), BIT_14d),
    (1, (16,), BIT_14e),
    (1, (8,), BIT_14f),
    (1, (8,), BIT_150),
    (1, (8,), BIT_151),
    (1, (8,), BIT_152),
    (1, (8,), BIT_153),
    (1, (8,), BIT_154),
    (1, (8,), BIT_155),
    (1, (16,), BIT_156),
    (1, (8,), BIT_157),
    (1, (8,), BIT_158),
    (1, (8,), BIT_159),
    (1, (8,), BIT_15a),
    (1, (8,), BIT_15b),
    (1, (8,), BIT_15c),
    (1, (8,), BIT_15d),
    (1, (16,), BIT_15e),
    (1, (8,), BIT_15f),
    (1, (8,), BIT_160),
    (1, (8,), BIT_161),
    (1, (8,), BIT_162),
    (1, (8,), BIT_163),
    (1, (8,), BIT_164),
    (1, (8,), BIT_165),
    (1, (16,), BIT_166),
    (1, (8,), BIT_167),
    (1, (8,), BIT_168),
    (1, (8,), BIT_169),
    (1, (8,), BIT_16a),
    (1, (8,), BIT_16b),
    (1, (8,), BIT_16c),
    (1, (8,), BIT_16d),
    (1, (16,), BIT_16e),
    (1, (8,), BIT_16f),
    (1, (8,), BIT_170),
    (1, (8,), BIT_171),
    (1, (8,), BIT_172),
    (1, (8,), BIT_173),
    (1, (8,), BIT_174),
    (1, (8,), BIT_175),
    (1, (16,), BIT_176),
    (1, (8,), BIT_177),
    (1, (8,), BIT_178),
    (1, (8,), BIT_179),
    (1, (8,), BIT_17a),
    (1, (8,), BIT_17b),
    (1, (8,), BIT_17c),
    (1, (8,), BIT_17d),
    (1, (16,), BIT_17e),
    (1, (8,), BIT_17f),
    (1, (8,), RES_180),
    (1, (8,), RES_181),
    (1, (8,), RES_182),
    (1, (8,), RES_183),
    (1, (8,), RES_184),
    (1, (8,), RES_185),
    (1, (16,), RES_186),
    (1, (8,), RES_187),
    (1, (8,), RES_188),
    (1, (8,), RES_189),
    (1, (8,), RES_18a),
    (1, (8,), RES_18b),
    (1, (8,), RES_18c),
    (1, (8,), RES_18d),
    (1, (16,), RES_18e),
    (1, (8,), RES_18f),
    (1, (8,), RES_190),
    (1, (8,), RES_191),
    (1, (8,), RES_192),
    (1, (8,), RES_193),
    (1, (8,), RES_194),
    (1, (8,), RES_195),
    (1, (16,), RES_196),
    (1, (8,), RES_197),
    (1, (8,), RES_198),
    (1, (8,), RES_199),
    (1, (8,), RES_19a),
    (1, (8,), RES_19b),
    (1, (8,), RES_19c),
    (1, (8,), RES_19d),
    (1, (16,), RES_19e),
    (1, (8,), RES_19f),
    (1, (8,), RES_1a0),
    (1, (8,), RES_1a1),
    (1, (8,), RES_1a2),
    (1, (8,), RES_1a3),
    (1, (8,), RES_1a4),
    (1, (8,), RES_1a5),
    (1, (16,), RES_1a6),
    (1, (8,), RES_1a7),
    (1, (8,), RES_1a8),
    (1, (8,), RES_1a9),
    (1, (8,), RES_1aa),
    (1, (8,), RES_1ab),
    (1, (8,), RES_1ac),
    (1, (8,), RES_1ad),
    (1, (16,), RES_1ae),
    (1, (8,), RES_1af),
    (1, (8,), RES_1b0),
    (1, (8,), RES_1b1),
    (1, (8,), RES_1b2),
    (1, (8,), RES_1b3),
    (1, (8,), RES_1b4),
    (1, (8,), RES_1b5),
    (1, (16,), RES_1b6),
    (1, (8,), RES_1b7),
    (1, (8,), RES_1b8),
    (1, (8,), RES_1b9),
    (1, (8,), RES_1ba),
    (1, (8,), RES_1bb),
    (1, (8,), RES_1bc),
    (1, (8,), RES_1bd),
    (1, (16,), RES_1be),
    (1, (8,), RES_1bf),
    (1, (8,), SET_1c0),
    (1, (8,), SET_1c1),
    (1, (8,), SET_1c2),
    (1, (8,), SET_1c3),
    (1, (8,), SET_1c4),
    (1, (8,), SET_1c5),
    (1, (16,), SET_1c6),
    (1, (8,), SET_1c7),
    (1, (8,), SET_1c8),
    (1, (8,), SET_1c9),
    (1, (8,), SET_1ca),
    (1, (8,), SET_1cb),
    (1, (8,), SET_1cc),
    (1, (8,), SET_1cd),
    (1, (16,), SET_1ce),
    (1, (8,), SET_1cf),
    (1, (8,), SET_1d0),
    (1, (8,), SET_1d1),
    (1, (8,), SET_1d2),
    (1, (8,), SET_1d3),
    (1, (8,), SET_1d4),
    (1, (8,), SET_1d5),
    (1, (16,), SET_1d6),
    (1, (8,), SET_1d7),
    (1, (8,), SET_1d8),
    (1, (8,), SET_1d9),
    (1, (8,), SET_1da),
    (1, (8,), SET_1db),
    (1, (8,), SET_1dc),
    (1, (8,), SET_1dd),
    (1, (16,), SET_1de),
    (1, (8,), SET_1df),
    (1, (8,), SET_1e0),
    (1, (8,), SET_1e1),
    (1, (8,), SET_1e2),
    (1, (8,), SET_1e3),
    (1, (8,), SET_1e4),
    (1, (8,), SET_1e5),
    (1, (16,), SET_1e6),
    (1, (8,), SET_1e7),
    (1, (8,), SET_1e8),
    (1, (8,), SET_1e9),
    (1, (8,), SET_1ea),
    (1, (8,), SET_1eb),
    (1, (8,), SET_1ec),
    (1, (8,), SET_1ed),
    (1, (16,), SET_1ee),
    (1, (8,), SET_1ef),
    (1, (8,), SET_1f0),
    (1, (8,), SET_1f1),
    (1, (8,), SET_1f2),
    (1, (8,), SET_1f3),
    (1, (8,), SET_1f4),
    (1, (8,), SET_1f5),
    (1, (16,), SET_1f6),
    (1, (8,), SET_1f7),
    (1, (8,), SET_1f8),
    (1, (8,), SET_1f9),
    (1, (8,), SET_1fa),
    (1, (8,), SET_1fb),
    (1, (8,), SET_1fc),
    (1, (8,), SET_1fd),
    (1, (16,), SET_1fe),
    (1, (8,), SET_1ff),
]