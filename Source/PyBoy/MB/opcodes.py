# -*- encoding: utf-8 -*-
# THIS FILE IS AUTO-GENERATED!!!
# DO NOT MODIFY THIS FILE.
# CHANGES TO THE CODE SHOULD BE MADE IN 'generator.py'.

import numpy as np
flagC, flagH, flagN, flagZ = range(4, 8)
# from flags import flagZ, flagN, flagH, flagC

def NOP_00(cpu): # 00 NOP
    cpu.PC += 1
    return 4

def LD_01(cpu, v): # 01 LD BC,d16
    cpu.setBC(v)
    cpu.PC += 3
    return 12

def LD_02(cpu): # 02 LD (BC),A
    cpu.mb[((cpu.B << 8) + cpu.C)] = cpu.A
    cpu.PC += 1
    return 8

def INC_03(cpu): # 03 INC BC
    t = ((cpu.B << 8) + cpu.C)+1
    # No flag operations
    t &= 0xFFFF
    cpu.setBC(t)
    cpu.PC += 1
    return 8

def INC_04(cpu): # 04 INC B
    t = cpu.B+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.B & 0xF) + (1 & 0xF)) > 0xF) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 1
    return 4

def DEC_05(cpu): # 05 DEC B
    t = cpu.B-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.B & 0xF) - (1 & 0xF)) < 0) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 1
    return 4

def LD_06(cpu, v): # 06 LD B,d8
    cpu.B = v
    cpu.PC += 2
    return 8

def RLCA_07(cpu): # 07 RLCA
    t = (cpu.A << 1) + (cpu.A >> 7)
    flag = 0b00000000
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def LD_08(cpu, v): # 08 LD (a16),SP
    cpu.mb[v] = cpu.SP & 0xFF
    cpu.mb[v+1] = cpu.SP >> 8
    cpu.PC += 3
    return 20

def ADD_09(cpu): # 09 ADD HL,BC
    t = cpu.HL+((cpu.B << 8) + cpu.C)
    flag = 0b00000000
    flag += (((cpu.HL & 0xFFF) + (((cpu.B << 8) + cpu.C) & 0xFFF)) > 0xFFF) << flagH
    flag += (t > 0xFFFF) << flagC
    cpu.F &= 0b10000000
    cpu.F |= flag
    t &= 0xFFFF
    cpu.HL = t
    cpu.PC += 1
    return 8

def LD_0a(cpu): # 0a LD A,(BC)
    cpu.A = cpu.mb[((cpu.B << 8) + cpu.C)]
    cpu.PC += 1
    return 8

def DEC_0b(cpu): # 0b DEC BC
    t = ((cpu.B << 8) + cpu.C)-1
    # No flag operations
    t &= 0xFFFF
    cpu.setBC(t)
    cpu.PC += 1
    return 8

def INC_0c(cpu): # 0c INC C
    t = cpu.C+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.C & 0xF) + (1 & 0xF)) > 0xF) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 1
    return 4

def DEC_0d(cpu): # 0d DEC C
    t = cpu.C-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.C & 0xF) - (1 & 0xF)) < 0) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 1
    return 4

def LD_0e(cpu, v): # 0e LD C,d8
    cpu.C = v
    cpu.PC += 2
    return 8

def RRCA_0f(cpu): # 0f RRCA
    t = (cpu.A >> 1) + ((cpu.A & 1) << 7)+ ((cpu.A & 1) << 8)
    flag = 0b00000000
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def STOP_10(cpu, v): # 10 STOP 0
    pass
    cpu.PC += 2
    return 4

def LD_11(cpu, v): # 11 LD DE,d16
    cpu.setDE(v)
    cpu.PC += 3
    return 12

def LD_12(cpu): # 12 LD (DE),A
    cpu.mb[((cpu.D << 8) + cpu.E)] = cpu.A
    cpu.PC += 1
    return 8

def INC_13(cpu): # 13 INC DE
    t = ((cpu.D << 8) + cpu.E)+1
    # No flag operations
    t &= 0xFFFF
    cpu.setDE(t)
    cpu.PC += 1
    return 8

def INC_14(cpu): # 14 INC D
    t = cpu.D+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.D & 0xF) + (1 & 0xF)) > 0xF) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 1
    return 4

def DEC_15(cpu): # 15 DEC D
    t = cpu.D-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.D & 0xF) - (1 & 0xF)) < 0) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 1
    return 4

def LD_16(cpu, v): # 16 LD D,d8
    cpu.D = v
    cpu.PC += 2
    return 8

def RLA_17(cpu): # 17 RLA
    t = (cpu.A << 1)+ cpu.fC()
    flag = 0b00000000
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def JR_18(cpu, v): # 18 JR r8
    cpu.PC += 2 + (((v + 128) & 255) - 128)
    cpu.PC &= 0xFFFF
    return 12

def ADD_19(cpu): # 19 ADD HL,DE
    t = cpu.HL+((cpu.D << 8) + cpu.E)
    flag = 0b00000000
    flag += (((cpu.HL & 0xFFF) + (((cpu.D << 8) + cpu.E) & 0xFFF)) > 0xFFF) << flagH
    flag += (t > 0xFFFF) << flagC
    cpu.F &= 0b10000000
    cpu.F |= flag
    t &= 0xFFFF
    cpu.HL = t
    cpu.PC += 1
    return 8

def LD_1a(cpu): # 1a LD A,(DE)
    cpu.A = cpu.mb[((cpu.D << 8) + cpu.E)]
    cpu.PC += 1
    return 8

def DEC_1b(cpu): # 1b DEC DE
    t = ((cpu.D << 8) + cpu.E)-1
    # No flag operations
    t &= 0xFFFF
    cpu.setDE(t)
    cpu.PC += 1
    return 8

def INC_1c(cpu): # 1c INC E
    t = cpu.E+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.E & 0xF) + (1 & 0xF)) > 0xF) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 1
    return 4

def DEC_1d(cpu): # 1d DEC E
    t = cpu.E-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.E & 0xF) - (1 & 0xF)) < 0) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 1
    return 4

def LD_1e(cpu, v): # 1e LD E,d8
    cpu.E = v
    cpu.PC += 2
    return 8

def RRA_1f(cpu): # 1f RRA
    t = (cpu.A >> 1)+ (cpu.fC() << 7)+ ((cpu.A & 1) << 8)
    flag = 0b00000000
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def JR_20(cpu, v): # 20 JR NZ,r8
    cpu.PC += 2
    if cpu.fNZ():
        cpu.PC += (((v + 128) & 255) - 128)
        cpu.PC &= 0xFFFF
        return 12
    else:
        cpu.PC &= 0xFFFF
        return 8

def LD_21(cpu, v): # 21 LD HL,d16
    cpu.HL = v
    cpu.PC += 3
    return 12

def LD_22(cpu): # 22 LD (HL+),A
    cpu.mb[cpu.HL] = cpu.A
    cpu.HL += 1
    cpu.PC += 1
    return 8

def INC_23(cpu): # 23 INC HL
    t = cpu.HL+1
    # No flag operations
    t &= 0xFFFF
    cpu.HL = t
    cpu.PC += 1
    return 8

def INC_24(cpu): # 24 INC H
    t = (cpu.HL >> 8)+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += ((((cpu.HL >> 8) & 0xF) + (1 & 0xF)) > 0xF) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 1
    return 4

def DEC_25(cpu): # 25 DEC H
    t = (cpu.HL >> 8)-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += ((((cpu.HL >> 8) & 0xF) - (1 & 0xF)) < 0) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 1
    return 4

def LD_26(cpu, v): # 26 LD H,d8
    cpu.HL = (cpu.HL & 0x00FF) | (v << 8)
    cpu.PC += 2
    return 8

def DAA_27(cpu): # 27 DAA
    t = cpu.A
    corr = 0
    corr |= 0x06 if cpu.fH() else 0x00
    corr |= 0x60 if cpu.fC() else 0x00
    if cpu.fN():
        t -= corr
    else:
        corr |= 0x06 if (t & 0x0F) > 0x09 else 0x00
        corr |= 0x60 if t > 0x99 else 0x00
        t += corr
    flag = 0
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (corr & 0x60 != 0) << flagC
    cpu.F &= 0b01000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def JR_28(cpu, v): # 28 JR Z,r8
    cpu.PC += 2
    if cpu.fZ():
        cpu.PC += (((v + 128) & 255) - 128)
        cpu.PC &= 0xFFFF
        return 12
    else:
        cpu.PC &= 0xFFFF
        return 8

def ADD_29(cpu): # 29 ADD HL,HL
    t = cpu.HL+cpu.HL
    flag = 0b00000000
    flag += (((cpu.HL & 0xFFF) + (cpu.HL & 0xFFF)) > 0xFFF) << flagH
    flag += (t > 0xFFFF) << flagC
    cpu.F &= 0b10000000
    cpu.F |= flag
    t &= 0xFFFF
    cpu.HL = t
    cpu.PC += 1
    return 8

def LD_2a(cpu): # 2a LD A,(HL+)
    cpu.A = cpu.mb[cpu.HL]
    cpu.HL += 1
    cpu.PC += 1
    return 8

def DEC_2b(cpu): # 2b DEC HL
    t = cpu.HL-1
    # No flag operations
    t &= 0xFFFF
    cpu.HL = t
    cpu.PC += 1
    return 8

def INC_2c(cpu): # 2c INC L
    t = (cpu.HL & 0xFF)+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += ((((cpu.HL & 0xFF) & 0xF) + (1 & 0xF)) > 0xF) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 1
    return 4

def DEC_2d(cpu): # 2d DEC L
    t = (cpu.HL & 0xFF)-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += ((((cpu.HL & 0xFF) & 0xF) - (1 & 0xF)) < 0) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 1
    return 4

def LD_2e(cpu, v): # 2e LD L,d8
    cpu.HL = (cpu.HL & 0xFF00) | (v & 0xFF)
    cpu.PC += 2
    return 8

def CPL_2f(cpu): # 2f CPL
    cpu.A = (~cpu.A) & 0xFF
    flag = 0b01100000
    cpu.F &= 0b10010000
    cpu.F |= flag
    cpu.PC += 1
    return 4

def JR_30(cpu, v): # 30 JR NC,r8
    cpu.PC += 2
    if cpu.fNC():
        cpu.PC += (((v + 128) & 255) - 128)
        cpu.PC &= 0xFFFF
        return 12
    else:
        cpu.PC &= 0xFFFF
        return 8

def LD_31(cpu, v): # 31 LD SP,d16
    cpu.SP = v
    cpu.PC += 3
    return 12

def LD_32(cpu): # 32 LD (HL-),A
    cpu.mb[cpu.HL] = cpu.A
    cpu.HL -= 1
    cpu.PC += 1
    return 8

def INC_33(cpu): # 33 INC SP
    t = cpu.SP+1
    # No flag operations
    t &= 0xFFFF
    cpu.SP = t
    cpu.PC += 1
    return 8

def INC_34(cpu): # 34 INC (HL)
    t = cpu.mb[cpu.HL]+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.mb[cpu.HL] & 0xF) + (1 & 0xF)) > 0xF) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb[cpu.HL] = t
    cpu.PC += 1
    return 12

def DEC_35(cpu): # 35 DEC (HL)
    t = cpu.mb[cpu.HL]-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.mb[cpu.HL] & 0xF) - (1 & 0xF)) < 0) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb[cpu.HL] = t
    cpu.PC += 1
    return 12

def LD_36(cpu, v): # 36 LD (HL),d8
    cpu.mb[cpu.HL] = v
    cpu.PC += 2
    return 12

def SCF_37(cpu): # 37 SCF
    flag = 0b00010000
    cpu.F &= 0b10000000
    cpu.F |= flag
    cpu.PC += 1
    return 4

def JR_38(cpu, v): # 38 JR C,r8
    cpu.PC += 2
    if cpu.fC():
        cpu.PC += (((v + 128) & 255) - 128)
        cpu.PC &= 0xFFFF
        return 12
    else:
        cpu.PC &= 0xFFFF
        return 8

def ADD_39(cpu): # 39 ADD HL,SP
    t = cpu.HL+cpu.SP
    flag = 0b00000000
    flag += (((cpu.HL & 0xFFF) + (cpu.SP & 0xFFF)) > 0xFFF) << flagH
    flag += (t > 0xFFFF) << flagC
    cpu.F &= 0b10000000
    cpu.F |= flag
    t &= 0xFFFF
    cpu.HL = t
    cpu.PC += 1
    return 8

def LD_3a(cpu): # 3a LD A,(HL-)
    cpu.A = cpu.mb[cpu.HL]
    cpu.HL -= 1
    cpu.PC += 1
    return 8

def DEC_3b(cpu): # 3b DEC SP
    t = cpu.SP-1
    # No flag operations
    t &= 0xFFFF
    cpu.SP = t
    cpu.PC += 1
    return 8

def INC_3c(cpu): # 3c INC A
    t = cpu.A+1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (1 & 0xF)) > 0xF) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def DEC_3d(cpu): # 3d DEC A
    t = cpu.A-1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (1 & 0xF)) < 0) << flagH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def LD_3e(cpu, v): # 3e LD A,d8
    cpu.A = v
    cpu.PC += 2
    return 8

def CCF_3f(cpu): # 3f CCF
    flag = (cpu.F & 0b00010000) ^ 0b00010000
    cpu.F &= 0b10000000
    cpu.F |= flag
    cpu.PC += 1
    return 4

def LD_40(cpu): # 40 LD B,B
    cpu.B = cpu.B
    cpu.PC += 1
    return 4

def LD_41(cpu): # 41 LD B,C
    cpu.B = cpu.C
    cpu.PC += 1
    return 4

def LD_42(cpu): # 42 LD B,D
    cpu.B = cpu.D
    cpu.PC += 1
    return 4

def LD_43(cpu): # 43 LD B,E
    cpu.B = cpu.E
    cpu.PC += 1
    return 4

def LD_44(cpu): # 44 LD B,H
    cpu.B = (cpu.HL >> 8)
    cpu.PC += 1
    return 4

def LD_45(cpu): # 45 LD B,L
    cpu.B = (cpu.HL & 0xFF)
    cpu.PC += 1
    return 4

def LD_46(cpu): # 46 LD B,(HL)
    cpu.B = cpu.mb[cpu.HL]
    cpu.PC += 1
    return 8

def LD_47(cpu): # 47 LD B,A
    cpu.B = cpu.A
    cpu.PC += 1
    return 4

def LD_48(cpu): # 48 LD C,B
    cpu.C = cpu.B
    cpu.PC += 1
    return 4

def LD_49(cpu): # 49 LD C,C
    cpu.C = cpu.C
    cpu.PC += 1
    return 4

def LD_4a(cpu): # 4a LD C,D
    cpu.C = cpu.D
    cpu.PC += 1
    return 4

def LD_4b(cpu): # 4b LD C,E
    cpu.C = cpu.E
    cpu.PC += 1
    return 4

def LD_4c(cpu): # 4c LD C,H
    cpu.C = (cpu.HL >> 8)
    cpu.PC += 1
    return 4

def LD_4d(cpu): # 4d LD C,L
    cpu.C = (cpu.HL & 0xFF)
    cpu.PC += 1
    return 4

def LD_4e(cpu): # 4e LD C,(HL)
    cpu.C = cpu.mb[cpu.HL]
    cpu.PC += 1
    return 8

def LD_4f(cpu): # 4f LD C,A
    cpu.C = cpu.A
    cpu.PC += 1
    return 4

def LD_50(cpu): # 50 LD D,B
    cpu.D = cpu.B
    cpu.PC += 1
    return 4

def LD_51(cpu): # 51 LD D,C
    cpu.D = cpu.C
    cpu.PC += 1
    return 4

def LD_52(cpu): # 52 LD D,D
    cpu.D = cpu.D
    cpu.PC += 1
    return 4

def LD_53(cpu): # 53 LD D,E
    cpu.D = cpu.E
    cpu.PC += 1
    return 4

def LD_54(cpu): # 54 LD D,H
    cpu.D = (cpu.HL >> 8)
    cpu.PC += 1
    return 4

def LD_55(cpu): # 55 LD D,L
    cpu.D = (cpu.HL & 0xFF)
    cpu.PC += 1
    return 4

def LD_56(cpu): # 56 LD D,(HL)
    cpu.D = cpu.mb[cpu.HL]
    cpu.PC += 1
    return 8

def LD_57(cpu): # 57 LD D,A
    cpu.D = cpu.A
    cpu.PC += 1
    return 4

def LD_58(cpu): # 58 LD E,B
    cpu.E = cpu.B
    cpu.PC += 1
    return 4

def LD_59(cpu): # 59 LD E,C
    cpu.E = cpu.C
    cpu.PC += 1
    return 4

def LD_5a(cpu): # 5a LD E,D
    cpu.E = cpu.D
    cpu.PC += 1
    return 4

def LD_5b(cpu): # 5b LD E,E
    cpu.E = cpu.E
    cpu.PC += 1
    return 4

def LD_5c(cpu): # 5c LD E,H
    cpu.E = (cpu.HL >> 8)
    cpu.PC += 1
    return 4

def LD_5d(cpu): # 5d LD E,L
    cpu.E = (cpu.HL & 0xFF)
    cpu.PC += 1
    return 4

def LD_5e(cpu): # 5e LD E,(HL)
    cpu.E = cpu.mb[cpu.HL]
    cpu.PC += 1
    return 8

def LD_5f(cpu): # 5f LD E,A
    cpu.E = cpu.A
    cpu.PC += 1
    return 4

def LD_60(cpu): # 60 LD H,B
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.B << 8)
    cpu.PC += 1
    return 4

def LD_61(cpu): # 61 LD H,C
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.C << 8)
    cpu.PC += 1
    return 4

def LD_62(cpu): # 62 LD H,D
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.D << 8)
    cpu.PC += 1
    return 4

def LD_63(cpu): # 63 LD H,E
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.E << 8)
    cpu.PC += 1
    return 4

def LD_64(cpu): # 64 LD H,H
    cpu.HL = (cpu.HL & 0x00FF) | ((cpu.HL >> 8) << 8)
    cpu.PC += 1
    return 4

def LD_65(cpu): # 65 LD H,L
    cpu.HL = (cpu.HL & 0x00FF) | ((cpu.HL & 0xFF) << 8)
    cpu.PC += 1
    return 4

def LD_66(cpu): # 66 LD H,(HL)
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.mb[cpu.HL] << 8)
    cpu.PC += 1
    return 8

def LD_67(cpu): # 67 LD H,A
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.A << 8)
    cpu.PC += 1
    return 4

def LD_68(cpu): # 68 LD L,B
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.B & 0xFF)
    cpu.PC += 1
    return 4

def LD_69(cpu): # 69 LD L,C
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.C & 0xFF)
    cpu.PC += 1
    return 4

def LD_6a(cpu): # 6a LD L,D
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.D & 0xFF)
    cpu.PC += 1
    return 4

def LD_6b(cpu): # 6b LD L,E
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.E & 0xFF)
    cpu.PC += 1
    return 4

def LD_6c(cpu): # 6c LD L,H
    cpu.HL = (cpu.HL & 0xFF00) | ((cpu.HL >> 8) & 0xFF)
    cpu.PC += 1
    return 4

def LD_6d(cpu): # 6d LD L,L
    cpu.HL = (cpu.HL & 0xFF00) | ((cpu.HL & 0xFF) & 0xFF)
    cpu.PC += 1
    return 4

def LD_6e(cpu): # 6e LD L,(HL)
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.mb[cpu.HL] & 0xFF)
    cpu.PC += 1
    return 8

def LD_6f(cpu): # 6f LD L,A
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.A & 0xFF)
    cpu.PC += 1
    return 4

def LD_70(cpu): # 70 LD (HL),B
    cpu.mb[cpu.HL] = cpu.B
    cpu.PC += 1
    return 8

def LD_71(cpu): # 71 LD (HL),C
    cpu.mb[cpu.HL] = cpu.C
    cpu.PC += 1
    return 8

def LD_72(cpu): # 72 LD (HL),D
    cpu.mb[cpu.HL] = cpu.D
    cpu.PC += 1
    return 8

def LD_73(cpu): # 73 LD (HL),E
    cpu.mb[cpu.HL] = cpu.E
    cpu.PC += 1
    return 8

def LD_74(cpu): # 74 LD (HL),H
    cpu.mb[cpu.HL] = (cpu.HL >> 8)
    cpu.PC += 1
    return 8

def LD_75(cpu): # 75 LD (HL),L
    cpu.mb[cpu.HL] = (cpu.HL & 0xFF)
    cpu.PC += 1
    return 8

def HALT_76(cpu): # 76 HALT
    if cpu.interruptMasterEnable:
        cpu.halted = True
    else:
        cpu.PC += 1
    return 4

def LD_77(cpu): # 77 LD (HL),A
    cpu.mb[cpu.HL] = cpu.A
    cpu.PC += 1
    return 8

def LD_78(cpu): # 78 LD A,B
    cpu.A = cpu.B
    cpu.PC += 1
    return 4

def LD_79(cpu): # 79 LD A,C
    cpu.A = cpu.C
    cpu.PC += 1
    return 4

def LD_7a(cpu): # 7a LD A,D
    cpu.A = cpu.D
    cpu.PC += 1
    return 4

def LD_7b(cpu): # 7b LD A,E
    cpu.A = cpu.E
    cpu.PC += 1
    return 4

def LD_7c(cpu): # 7c LD A,H
    cpu.A = (cpu.HL >> 8)
    cpu.PC += 1
    return 4

def LD_7d(cpu): # 7d LD A,L
    cpu.A = (cpu.HL & 0xFF)
    cpu.PC += 1
    return 4

def LD_7e(cpu): # 7e LD A,(HL)
    cpu.A = cpu.mb[cpu.HL]
    cpu.PC += 1
    return 8

def LD_7f(cpu): # 7f LD A,A
    cpu.A = cpu.A
    cpu.PC += 1
    return 4

def ADD_80(cpu): # 80 ADD A,B
    t = cpu.A+cpu.B
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (cpu.B & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def ADD_81(cpu): # 81 ADD A,C
    t = cpu.A+cpu.C
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (cpu.C & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def ADD_82(cpu): # 82 ADD A,D
    t = cpu.A+cpu.D
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (cpu.D & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def ADD_83(cpu): # 83 ADD A,E
    t = cpu.A+cpu.E
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (cpu.E & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def ADD_84(cpu): # 84 ADD A,H
    t = cpu.A+(cpu.HL >> 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + ((cpu.HL >> 8) & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def ADD_85(cpu): # 85 ADD A,L
    t = cpu.A+(cpu.HL & 0xFF)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + ((cpu.HL & 0xFF) & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def ADD_86(cpu): # 86 ADD A,(HL)
    t = cpu.A+cpu.mb[cpu.HL]
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (cpu.mb[cpu.HL] & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 8

def ADD_87(cpu): # 87 ADD A,A
    t = cpu.A+cpu.A
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (cpu.A & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def ADC_88(cpu): # 88 ADC A,B
    t = cpu.A+cpu.B+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (cpu.B & 0xF) + cpu.fC()) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def ADC_89(cpu): # 89 ADC A,C
    t = cpu.A+cpu.C+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (cpu.C & 0xF) + cpu.fC()) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def ADC_8a(cpu): # 8a ADC A,D
    t = cpu.A+cpu.D+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (cpu.D & 0xF) + cpu.fC()) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def ADC_8b(cpu): # 8b ADC A,E
    t = cpu.A+cpu.E+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (cpu.E & 0xF) + cpu.fC()) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def ADC_8c(cpu): # 8c ADC A,H
    t = cpu.A+(cpu.HL >> 8)+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + ((cpu.HL >> 8) & 0xF) + cpu.fC()) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def ADC_8d(cpu): # 8d ADC A,L
    t = cpu.A+(cpu.HL & 0xFF)+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + ((cpu.HL & 0xFF) & 0xF) + cpu.fC()) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def ADC_8e(cpu): # 8e ADC A,(HL)
    t = cpu.A+cpu.mb[cpu.HL]+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (cpu.mb[cpu.HL] & 0xF) + cpu.fC()) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 8

def ADC_8f(cpu): # 8f ADC A,A
    t = cpu.A+cpu.A+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (cpu.A & 0xF) + cpu.fC()) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def SUB_90(cpu): # 90 SUB B
    t = cpu.A-cpu.B
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.B & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def SUB_91(cpu): # 91 SUB C
    t = cpu.A-cpu.C
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.C & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def SUB_92(cpu): # 92 SUB D
    t = cpu.A-cpu.D
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.D & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def SUB_93(cpu): # 93 SUB E
    t = cpu.A-cpu.E
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.E & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def SUB_94(cpu): # 94 SUB H
    t = cpu.A-(cpu.HL >> 8)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - ((cpu.HL >> 8) & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def SUB_95(cpu): # 95 SUB L
    t = cpu.A-(cpu.HL & 0xFF)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - ((cpu.HL & 0xFF) & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def SUB_96(cpu): # 96 SUB (HL)
    t = cpu.A-cpu.mb[cpu.HL]
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.mb[cpu.HL] & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 8

def SUB_97(cpu): # 97 SUB A
    t = cpu.A-cpu.A
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.A & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def SBC_98(cpu): # 98 SBC A,B
    t = cpu.A-cpu.B- cpu.fC()
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.B & 0xF) - cpu.fC()) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def SBC_99(cpu): # 99 SBC A,C
    t = cpu.A-cpu.C- cpu.fC()
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.C & 0xF) - cpu.fC()) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def SBC_9a(cpu): # 9a SBC A,D
    t = cpu.A-cpu.D- cpu.fC()
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.D & 0xF) - cpu.fC()) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def SBC_9b(cpu): # 9b SBC A,E
    t = cpu.A-cpu.E- cpu.fC()
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.E & 0xF) - cpu.fC()) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def SBC_9c(cpu): # 9c SBC A,H
    t = cpu.A-(cpu.HL >> 8)- cpu.fC()
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - ((cpu.HL >> 8) & 0xF) - cpu.fC()) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def SBC_9d(cpu): # 9d SBC A,L
    t = cpu.A-(cpu.HL & 0xFF)- cpu.fC()
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - ((cpu.HL & 0xFF) & 0xF) - cpu.fC()) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def SBC_9e(cpu): # 9e SBC A,(HL)
    t = cpu.A-cpu.mb[cpu.HL]- cpu.fC()
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.mb[cpu.HL] & 0xF) - cpu.fC()) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 8

def SBC_9f(cpu): # 9f SBC A,A
    t = cpu.A-cpu.A- cpu.fC()
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.A & 0xF) - cpu.fC()) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def AND_a0(cpu): # a0 AND B
    t = cpu.A&cpu.B
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def AND_a1(cpu): # a1 AND C
    t = cpu.A&cpu.C
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def AND_a2(cpu): # a2 AND D
    t = cpu.A&cpu.D
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def AND_a3(cpu): # a3 AND E
    t = cpu.A&cpu.E
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def AND_a4(cpu): # a4 AND H
    t = cpu.A&(cpu.HL >> 8)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def AND_a5(cpu): # a5 AND L
    t = cpu.A&(cpu.HL & 0xFF)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def AND_a6(cpu): # a6 AND (HL)
    t = cpu.A&cpu.mb[cpu.HL]
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 8

def AND_a7(cpu): # a7 AND A
    t = cpu.A&cpu.A
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def XOR_a8(cpu): # a8 XOR B
    t = cpu.A^cpu.B
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def XOR_a9(cpu): # a9 XOR C
    t = cpu.A^cpu.C
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def XOR_aa(cpu): # aa XOR D
    t = cpu.A^cpu.D
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def XOR_ab(cpu): # ab XOR E
    t = cpu.A^cpu.E
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def XOR_ac(cpu): # ac XOR H
    t = cpu.A^(cpu.HL >> 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def XOR_ad(cpu): # ad XOR L
    t = cpu.A^(cpu.HL & 0xFF)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def XOR_ae(cpu): # ae XOR (HL)
    t = cpu.A^cpu.mb[cpu.HL]
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 8

def XOR_af(cpu): # af XOR A
    t = cpu.A^cpu.A
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def OR_b0(cpu): # b0 OR B
    t = cpu.A|cpu.B
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def OR_b1(cpu): # b1 OR C
    t = cpu.A|cpu.C
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def OR_b2(cpu): # b2 OR D
    t = cpu.A|cpu.D
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def OR_b3(cpu): # b3 OR E
    t = cpu.A|cpu.E
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def OR_b4(cpu): # b4 OR H
    t = cpu.A|(cpu.HL >> 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def OR_b5(cpu): # b5 OR L
    t = cpu.A|(cpu.HL & 0xFF)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def OR_b6(cpu): # b6 OR (HL)
    t = cpu.A|cpu.mb[cpu.HL]
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 8

def OR_b7(cpu): # b7 OR A
    t = cpu.A|cpu.A
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    return 4

def CP_b8(cpu): # b8 CP B
    t = cpu.A-cpu.B
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.B & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    return 4

def CP_b9(cpu): # b9 CP C
    t = cpu.A-cpu.C
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.C & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    return 4

def CP_ba(cpu): # ba CP D
    t = cpu.A-cpu.D
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.D & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    return 4

def CP_bb(cpu): # bb CP E
    t = cpu.A-cpu.E
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.E & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    return 4

def CP_bc(cpu): # bc CP H
    t = cpu.A-(cpu.HL >> 8)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - ((cpu.HL >> 8) & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    return 4

def CP_bd(cpu): # bd CP L
    t = cpu.A-(cpu.HL & 0xFF)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - ((cpu.HL & 0xFF) & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    return 4

def CP_be(cpu): # be CP (HL)
    t = cpu.A-cpu.mb[cpu.HL]
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.mb[cpu.HL] & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    return 8

def CP_bf(cpu): # bf CP A
    t = cpu.A-cpu.A
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (cpu.A & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    return 4

def RET_c0(cpu): # c0 RET NZ
    if cpu.fNZ():
        cpu.PC = cpu.mb[cpu.SP+1] << 8 # High
        cpu.PC |= cpu.mb[cpu.SP] # Low
        cpu.SP += 2
        return 20
    else:
        cpu.PC += 1
        cpu.PC &= 0xFFFF
        return 8

def POP_c1(cpu): # c1 POP BC
    cpu.B = cpu.mb[cpu.SP+1] # High
    cpu.C = cpu.mb[cpu.SP] # Low
    cpu.SP += 2
    cpu.PC += 1
    return 12

def JP_c2(cpu, v): # c2 JP NZ,a16
    if cpu.fNZ():
        cpu.PC = v
        return 16
    else:
        cpu.PC += 3
        return 12

def JP_c3(cpu, v): # c3 JP a16
    cpu.PC = v
    return 16

def CALL_c4(cpu, v): # c4 CALL NZ,a16
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    if cpu.fNZ():
        cpu.mb[cpu.SP-1] = cpu.PC >> 8 # High
        cpu.mb[cpu.SP-2] = cpu.PC & 0xFF # Low
        cpu.SP -= 2
        cpu.PC = v
        return 24
    else:
        return 12

def PUSH_c5(cpu): # c5 PUSH BC
    cpu.mb[cpu.SP-1] = cpu.B # High
    cpu.mb[cpu.SP-2] = cpu.C # Low
    cpu.SP -= 2
    cpu.PC += 1
    return 16

def ADD_c6(cpu, v): # c6 ADD A,d8
    t = cpu.A+v
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (v & 0xF)) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def RST_c7(cpu): # c7 RST 00H
    cpu.PC += 1
    cpu.mb[cpu.SP-1] = cpu.PC >> 8 # High
    cpu.mb[cpu.SP-2] = cpu.PC & 0xFF # Low
    cpu.SP -= 2
    cpu.PC = 0
    return 16

def RET_c8(cpu): # c8 RET Z
    if cpu.fZ():
        cpu.PC = cpu.mb[cpu.SP+1] << 8 # High
        cpu.PC |= cpu.mb[cpu.SP] # Low
        cpu.SP += 2
        return 20
    else:
        cpu.PC += 1
        cpu.PC &= 0xFFFF
        return 8

def RET_c9(cpu): # c9 RET
    cpu.PC = cpu.mb[cpu.SP+1] << 8 # High
    cpu.PC |= cpu.mb[cpu.SP] # Low
    cpu.SP += 2
    return 16

def JP_ca(cpu, v): # ca JP Z,a16
    if cpu.fZ():
        cpu.PC = v
        return 16
    else:
        cpu.PC += 3
        return 12

def CB_cb(cpu): # cb PREFIX CB
    raise Exception('CB cannot be called!')
    cpu.PC += 1
    return 4

def CALL_cc(cpu, v): # cc CALL Z,a16
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    if cpu.fZ():
        cpu.mb[cpu.SP-1] = cpu.PC >> 8 # High
        cpu.mb[cpu.SP-2] = cpu.PC & 0xFF # Low
        cpu.SP -= 2
        cpu.PC = v
        return 24
    else:
        return 12

def CALL_cd(cpu, v): # cd CALL a16
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    cpu.mb[cpu.SP-1] = cpu.PC >> 8 # High
    cpu.mb[cpu.SP-2] = cpu.PC & 0xFF # Low
    cpu.SP -= 2
    cpu.PC = v
    return 24

def ADC_ce(cpu, v): # ce ADC A,d8
    t = cpu.A+v+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) + (v & 0xF) + cpu.fC()) > 0xF) << flagH
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def RST_cf(cpu): # cf RST 08H
    cpu.PC += 1
    cpu.mb[cpu.SP-1] = cpu.PC >> 8 # High
    cpu.mb[cpu.SP-2] = cpu.PC & 0xFF # Low
    cpu.SP -= 2
    cpu.PC = 8
    return 16

def RET_d0(cpu): # d0 RET NC
    if cpu.fNC():
        cpu.PC = cpu.mb[cpu.SP+1] << 8 # High
        cpu.PC |= cpu.mb[cpu.SP] # Low
        cpu.SP += 2
        return 20
    else:
        cpu.PC += 1
        cpu.PC &= 0xFFFF
        return 8

def POP_d1(cpu): # d1 POP DE
    cpu.D = cpu.mb[cpu.SP+1] # High
    cpu.E = cpu.mb[cpu.SP] # Low
    cpu.SP += 2
    cpu.PC += 1
    return 12

def JP_d2(cpu, v): # d2 JP NC,a16
    if cpu.fNC():
        cpu.PC = v
        return 16
    else:
        cpu.PC += 3
        return 12

def CALL_d4(cpu, v): # d4 CALL NC,a16
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    if cpu.fNC():
        cpu.mb[cpu.SP-1] = cpu.PC >> 8 # High
        cpu.mb[cpu.SP-2] = cpu.PC & 0xFF # Low
        cpu.SP -= 2
        cpu.PC = v
        return 24
    else:
        return 12

def PUSH_d5(cpu): # d5 PUSH DE
    cpu.mb[cpu.SP-1] = cpu.D # High
    cpu.mb[cpu.SP-2] = cpu.E # Low
    cpu.SP -= 2
    cpu.PC += 1
    return 16

def SUB_d6(cpu, v): # d6 SUB d8
    t = cpu.A-v
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (v & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def RST_d7(cpu): # d7 RST 10H
    cpu.PC += 1
    cpu.mb[cpu.SP-1] = cpu.PC >> 8 # High
    cpu.mb[cpu.SP-2] = cpu.PC & 0xFF # Low
    cpu.SP -= 2
    cpu.PC = 16
    return 16

def RET_d8(cpu): # d8 RET C
    if cpu.fC():
        cpu.PC = cpu.mb[cpu.SP+1] << 8 # High
        cpu.PC |= cpu.mb[cpu.SP] # Low
        cpu.SP += 2
        return 20
    else:
        cpu.PC += 1
        cpu.PC &= 0xFFFF
        return 8

def RETI_d9(cpu): # d9 RETI
    cpu.interruptMasterEnable = True
    cpu.PC = cpu.mb[cpu.SP+1] << 8 # High
    cpu.PC |= cpu.mb[cpu.SP] # Low
    cpu.SP += 2
    return 16

def JP_da(cpu, v): # da JP C,a16
    if cpu.fC():
        cpu.PC = v
        return 16
    else:
        cpu.PC += 3
        return 12

def CALL_dc(cpu, v): # dc CALL C,a16
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    if cpu.fC():
        cpu.mb[cpu.SP-1] = cpu.PC >> 8 # High
        cpu.mb[cpu.SP-2] = cpu.PC & 0xFF # Low
        cpu.SP -= 2
        cpu.PC = v
        return 24
    else:
        return 12

def SBC_de(cpu, v): # de SBC A,d8
    t = cpu.A-v- cpu.fC()
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (v & 0xF) - cpu.fC()) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def RST_df(cpu): # df RST 18H
    cpu.PC += 1
    cpu.mb[cpu.SP-1] = cpu.PC >> 8 # High
    cpu.mb[cpu.SP-2] = cpu.PC & 0xFF # Low
    cpu.SP -= 2
    cpu.PC = 24
    return 16

def LD_e0(cpu, v): # e0 LDH (a8),A
    cpu.mb[v + 0xFF00] = cpu.A
    cpu.PC += 2
    return 12

def POP_e1(cpu): # e1 POP HL
    cpu.HL = (cpu.mb[cpu.SP+1] << 8) + cpu.mb[cpu.SP] # High
    cpu.SP += 2
    cpu.PC += 1
    return 12

def LD_e2(cpu): # e2 LD (C),A
    cpu.mb[0xFF00 + cpu.C] = cpu.A
    cpu.PC += 1
    return 8

def PUSH_e5(cpu): # e5 PUSH HL
    cpu.mb[cpu.SP-1] = cpu.HL >> 8 # High
    cpu.mb[cpu.SP-2] = cpu.HL & 0xFF # Low
    cpu.SP -= 2
    cpu.PC += 1
    return 16

def AND_e6(cpu, v): # e6 AND d8
    t = cpu.A&v
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def RST_e7(cpu): # e7 RST 20H
    cpu.PC += 1
    cpu.mb[cpu.SP-1] = cpu.PC >> 8 # High
    cpu.mb[cpu.SP-2] = cpu.PC & 0xFF # Low
    cpu.SP -= 2
    cpu.PC = 32
    return 16

def ADD_e8(cpu, v): # e8 ADD SP,r8
    t = cpu.SP+(((v + 128) & 255) - 128)
    flag = 0b00000000
    flag += (((cpu.SP & 0xF) + (v & 0xF)) > 0xF) << flagH
    flag += (((cpu.SP & 0xFF) + (v & 0xFF)) > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFFFF
    cpu.SP = t
    cpu.PC += 2
    return 16

def JP_e9(cpu): # e9 JP (HL)
    cpu.PC = cpu.HL
    return 4

def LD_ea(cpu, v): # ea LD (a16),A
    cpu.mb[v] = cpu.A
    cpu.PC += 3
    return 16

def XOR_ee(cpu, v): # ee XOR d8
    t = cpu.A^v
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def RST_ef(cpu): # ef RST 28H
    cpu.PC += 1
    cpu.mb[cpu.SP-1] = cpu.PC >> 8 # High
    cpu.mb[cpu.SP-2] = cpu.PC & 0xFF # Low
    cpu.SP -= 2
    cpu.PC = 40
    return 16

def LD_f0(cpu, v): # f0 LDH A,(a8)
    cpu.A = cpu.mb[v + 0xFF00]
    cpu.PC += 2
    return 12

def POP_f1(cpu): # f1 POP AF
    cpu.A = cpu.mb[cpu.SP+1] # High
    cpu.F = cpu.mb[cpu.SP] # Low
    cpu.SP += 2
    cpu.PC += 1
    return 12

def LD_f2(cpu): # f2 LD A,(C)
    cpu.A = cpu.mb[0xFF00 + cpu.C]
    cpu.PC += 1
    return 8

def DI_f3(cpu): # f3 DI
    cpu.interruptMasterEnable = False
    cpu.PC += 1
    return 4

def PUSH_f5(cpu): # f5 PUSH AF
    cpu.mb[cpu.SP-1] = cpu.A # High
    cpu.mb[cpu.SP-2] = cpu.F # Low
    cpu.SP -= 2
    cpu.PC += 1
    return 16

def OR_f6(cpu, v): # f6 OR d8
    t = cpu.A|v
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def RST_f7(cpu): # f7 RST 30H
    cpu.PC += 1
    cpu.mb[cpu.SP-1] = cpu.PC >> 8 # High
    cpu.mb[cpu.SP-2] = cpu.PC & 0xFF # Low
    cpu.SP -= 2
    cpu.PC = 48
    return 16

def LD_f8(cpu, v): # f8 LD HL,SP+r8
    cpu.HL = cpu.SP + (((v + 128) & 255) - 128)
    t = cpu.HL
    flag = 0b00000000
    flag += (((cpu.SP & 0xF) + (v & 0xF)) > 0xF) << flagH
    flag += (((cpu.SP & 0xFF) + (v & 0xFF)) > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    cpu.HL &= 0xFFFF
    cpu.PC += 2
    return 12

def LD_f9(cpu): # f9 LD SP,HL
    cpu.SP = cpu.HL
    cpu.PC += 1
    return 8

def LD_fa(cpu, v): # fa LD A,(a16)
    cpu.A = cpu.mb[v]
    cpu.PC += 3
    return 16

def EI_fb(cpu): # fb EI
    cpu.interruptMasterEnable = True
    cpu.PC += 1
    return 4

def CP_fe(cpu, v): # fe CP d8
    t = cpu.A-v
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (((cpu.A & 0xF) - (v & 0xF)) < 0) << flagH
    flag += (t < 0) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 2
    return 8

def RST_ff(cpu): # ff RST 38H
    cpu.PC += 1
    cpu.mb[cpu.SP-1] = cpu.PC >> 8 # High
    cpu.mb[cpu.SP-2] = cpu.PC & 0xFF # Low
    cpu.SP -= 2
    cpu.PC = 56
    return 16

def RLC_100(cpu): # 100 RLC B
    t = (cpu.B << 1) + (cpu.B >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    return 8

def RLC_101(cpu): # 101 RLC C
    t = (cpu.C << 1) + (cpu.C >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    return 8

def RLC_102(cpu): # 102 RLC D
    t = (cpu.D << 1) + (cpu.D >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    return 8

def RLC_103(cpu): # 103 RLC E
    t = (cpu.E << 1) + (cpu.E >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    return 8

def RLC_104(cpu): # 104 RLC H
    t = ((cpu.HL >> 8) << 1) + ((cpu.HL >> 8) >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def RLC_105(cpu): # 105 RLC L
    t = ((cpu.HL & 0xFF) << 1) + ((cpu.HL & 0xFF) >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def RLC_106(cpu): # 106 RLC (HL)
    t = (cpu.mb[cpu.HL] << 1) + (cpu.mb[cpu.HL] >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def RLC_107(cpu): # 107 RLC A
    t = (cpu.A << 1) + (cpu.A >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def RRC_108(cpu): # 108 RRC B
    t = (cpu.B >> 1) + ((cpu.B & 1) << 7)+ ((cpu.B & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    return 8

def RRC_109(cpu): # 109 RRC C
    t = (cpu.C >> 1) + ((cpu.C & 1) << 7)+ ((cpu.C & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    return 8

def RRC_10a(cpu): # 10a RRC D
    t = (cpu.D >> 1) + ((cpu.D & 1) << 7)+ ((cpu.D & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    return 8

def RRC_10b(cpu): # 10b RRC E
    t = (cpu.E >> 1) + ((cpu.E & 1) << 7)+ ((cpu.E & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    return 8

def RRC_10c(cpu): # 10c RRC H
    t = ((cpu.HL >> 8) >> 1) + (((cpu.HL >> 8) & 1) << 7)+ (((cpu.HL >> 8) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def RRC_10d(cpu): # 10d RRC L
    t = ((cpu.HL & 0xFF) >> 1) + (((cpu.HL & 0xFF) & 1) << 7)+ (((cpu.HL & 0xFF) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def RRC_10e(cpu): # 10e RRC (HL)
    t = (cpu.mb[cpu.HL] >> 1) + ((cpu.mb[cpu.HL] & 1) << 7)+ ((cpu.mb[cpu.HL] & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def RRC_10f(cpu): # 10f RRC A
    t = (cpu.A >> 1) + ((cpu.A & 1) << 7)+ ((cpu.A & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def RL_110(cpu): # 110 RL B
    t = (cpu.B << 1)+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    return 8

def RL_111(cpu): # 111 RL C
    t = (cpu.C << 1)+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    return 8

def RL_112(cpu): # 112 RL D
    t = (cpu.D << 1)+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    return 8

def RL_113(cpu): # 113 RL E
    t = (cpu.E << 1)+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    return 8

def RL_114(cpu): # 114 RL H
    t = ((cpu.HL >> 8) << 1)+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def RL_115(cpu): # 115 RL L
    t = ((cpu.HL & 0xFF) << 1)+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def RL_116(cpu): # 116 RL (HL)
    t = (cpu.mb[cpu.HL] << 1)+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def RL_117(cpu): # 117 RL A
    t = (cpu.A << 1)+ cpu.fC()
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def RR_118(cpu): # 118 RR B
    t = (cpu.B >> 1)+ (cpu.fC() << 7)+ ((cpu.B & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    return 8

def RR_119(cpu): # 119 RR C
    t = (cpu.C >> 1)+ (cpu.fC() << 7)+ ((cpu.C & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    return 8

def RR_11a(cpu): # 11a RR D
    t = (cpu.D >> 1)+ (cpu.fC() << 7)+ ((cpu.D & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    return 8

def RR_11b(cpu): # 11b RR E
    t = (cpu.E >> 1)+ (cpu.fC() << 7)+ ((cpu.E & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    return 8

def RR_11c(cpu): # 11c RR H
    t = ((cpu.HL >> 8) >> 1)+ (cpu.fC() << 7)+ (((cpu.HL >> 8) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def RR_11d(cpu): # 11d RR L
    t = ((cpu.HL & 0xFF) >> 1)+ (cpu.fC() << 7)+ (((cpu.HL & 0xFF) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def RR_11e(cpu): # 11e RR (HL)
    t = (cpu.mb[cpu.HL] >> 1)+ (cpu.fC() << 7)+ ((cpu.mb[cpu.HL] & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def RR_11f(cpu): # 11f RR A
    t = (cpu.A >> 1)+ (cpu.fC() << 7)+ ((cpu.A & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def SLA_120(cpu): # 120 SLA B
    t = (cpu.B << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    return 8

def SLA_121(cpu): # 121 SLA C
    t = (cpu.C << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    return 8

def SLA_122(cpu): # 122 SLA D
    t = (cpu.D << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    return 8

def SLA_123(cpu): # 123 SLA E
    t = (cpu.E << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    return 8

def SLA_124(cpu): # 124 SLA H
    t = ((cpu.HL >> 8) << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def SLA_125(cpu): # 125 SLA L
    t = ((cpu.HL & 0xFF) << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def SLA_126(cpu): # 126 SLA (HL)
    t = (cpu.mb[cpu.HL] << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def SLA_127(cpu): # 127 SLA A
    t = (cpu.A << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def SRA_128(cpu): # 128 SRA B
    t = ((cpu.B >> 1) | (cpu.B & 0x80)) + ((cpu.B & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    return 8

def SRA_129(cpu): # 129 SRA C
    t = ((cpu.C >> 1) | (cpu.C & 0x80)) + ((cpu.C & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    return 8

def SRA_12a(cpu): # 12a SRA D
    t = ((cpu.D >> 1) | (cpu.D & 0x80)) + ((cpu.D & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    return 8

def SRA_12b(cpu): # 12b SRA E
    t = ((cpu.E >> 1) | (cpu.E & 0x80)) + ((cpu.E & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    return 8

def SRA_12c(cpu): # 12c SRA H
    t = (((cpu.HL >> 8) >> 1) | ((cpu.HL >> 8) & 0x80)) + (((cpu.HL >> 8) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def SRA_12d(cpu): # 12d SRA L
    t = (((cpu.HL & 0xFF) >> 1) | ((cpu.HL & 0xFF) & 0x80)) + (((cpu.HL & 0xFF) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def SRA_12e(cpu): # 12e SRA (HL)
    t = ((cpu.mb[cpu.HL] >> 1) | (cpu.mb[cpu.HL] & 0x80)) + ((cpu.mb[cpu.HL] & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def SRA_12f(cpu): # 12f SRA A
    t = ((cpu.A >> 1) | (cpu.A & 0x80)) + ((cpu.A & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def SWAP_130(cpu): # 130 SWAP B
    t = ((cpu.B & 0xF0) >> 4) | ((cpu.B & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    return 8

def SWAP_131(cpu): # 131 SWAP C
    t = ((cpu.C & 0xF0) >> 4) | ((cpu.C & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    return 8

def SWAP_132(cpu): # 132 SWAP D
    t = ((cpu.D & 0xF0) >> 4) | ((cpu.D & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    return 8

def SWAP_133(cpu): # 133 SWAP E
    t = ((cpu.E & 0xF0) >> 4) | ((cpu.E & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    return 8

def SWAP_134(cpu): # 134 SWAP H
    t = (((cpu.HL >> 8) & 0xF0) >> 4) | (((cpu.HL >> 8) & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def SWAP_135(cpu): # 135 SWAP L
    t = (((cpu.HL & 0xFF) & 0xF0) >> 4) | (((cpu.HL & 0xFF) & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def SWAP_136(cpu): # 136 SWAP (HL)
    t = ((cpu.mb[cpu.HL] & 0xF0) >> 4) | ((cpu.mb[cpu.HL] & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def SWAP_137(cpu): # 137 SWAP A
    t = ((cpu.A & 0xF0) >> 4) | ((cpu.A & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def SRL_138(cpu): # 138 SRL B
    t = (cpu.B >> 1) + ((cpu.B & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    return 8

def SRL_139(cpu): # 139 SRL C
    t = (cpu.C >> 1) + ((cpu.C & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    return 8

def SRL_13a(cpu): # 13a SRL D
    t = (cpu.D >> 1) + ((cpu.D & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    return 8

def SRL_13b(cpu): # 13b SRL E
    t = (cpu.E >> 1) + ((cpu.E & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    return 8

def SRL_13c(cpu): # 13c SRL H
    t = ((cpu.HL >> 8) >> 1) + (((cpu.HL >> 8) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def SRL_13d(cpu): # 13d SRL L
    t = ((cpu.HL & 0xFF) >> 1) + (((cpu.HL & 0xFF) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def SRL_13e(cpu): # 13e SRL (HL)
    t = (cpu.mb[cpu.HL] >> 1) + ((cpu.mb[cpu.HL] & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def SRL_13f(cpu): # 13f SRL A
    t = (cpu.A >> 1) + ((cpu.A & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << flagZ
    flag += (t > 0xFF) << flagC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    return 8

def BIT_140(cpu): # 140 BIT 0,B
    t = cpu.B & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_141(cpu): # 141 BIT 0,C
    t = cpu.C & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_142(cpu): # 142 BIT 0,D
    t = cpu.D & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_143(cpu): # 143 BIT 0,E
    t = cpu.E & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_144(cpu): # 144 BIT 0,H
    t = (cpu.HL >> 8) & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_145(cpu): # 145 BIT 0,L
    t = (cpu.HL & 0xFF) & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_146(cpu): # 146 BIT 0,(HL)
    t = cpu.mb[cpu.HL] & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 16

def BIT_147(cpu): # 147 BIT 0,A
    t = cpu.A & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_148(cpu): # 148 BIT 1,B
    t = cpu.B & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_149(cpu): # 149 BIT 1,C
    t = cpu.C & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_14a(cpu): # 14a BIT 1,D
    t = cpu.D & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_14b(cpu): # 14b BIT 1,E
    t = cpu.E & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_14c(cpu): # 14c BIT 1,H
    t = (cpu.HL >> 8) & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_14d(cpu): # 14d BIT 1,L
    t = (cpu.HL & 0xFF) & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_14e(cpu): # 14e BIT 1,(HL)
    t = cpu.mb[cpu.HL] & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 16

def BIT_14f(cpu): # 14f BIT 1,A
    t = cpu.A & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_150(cpu): # 150 BIT 2,B
    t = cpu.B & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_151(cpu): # 151 BIT 2,C
    t = cpu.C & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_152(cpu): # 152 BIT 2,D
    t = cpu.D & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_153(cpu): # 153 BIT 2,E
    t = cpu.E & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_154(cpu): # 154 BIT 2,H
    t = (cpu.HL >> 8) & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_155(cpu): # 155 BIT 2,L
    t = (cpu.HL & 0xFF) & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_156(cpu): # 156 BIT 2,(HL)
    t = cpu.mb[cpu.HL] & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 16

def BIT_157(cpu): # 157 BIT 2,A
    t = cpu.A & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_158(cpu): # 158 BIT 3,B
    t = cpu.B & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_159(cpu): # 159 BIT 3,C
    t = cpu.C & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_15a(cpu): # 15a BIT 3,D
    t = cpu.D & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_15b(cpu): # 15b BIT 3,E
    t = cpu.E & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_15c(cpu): # 15c BIT 3,H
    t = (cpu.HL >> 8) & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_15d(cpu): # 15d BIT 3,L
    t = (cpu.HL & 0xFF) & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_15e(cpu): # 15e BIT 3,(HL)
    t = cpu.mb[cpu.HL] & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 16

def BIT_15f(cpu): # 15f BIT 3,A
    t = cpu.A & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_160(cpu): # 160 BIT 4,B
    t = cpu.B & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_161(cpu): # 161 BIT 4,C
    t = cpu.C & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_162(cpu): # 162 BIT 4,D
    t = cpu.D & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_163(cpu): # 163 BIT 4,E
    t = cpu.E & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_164(cpu): # 164 BIT 4,H
    t = (cpu.HL >> 8) & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_165(cpu): # 165 BIT 4,L
    t = (cpu.HL & 0xFF) & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_166(cpu): # 166 BIT 4,(HL)
    t = cpu.mb[cpu.HL] & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 16

def BIT_167(cpu): # 167 BIT 4,A
    t = cpu.A & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_168(cpu): # 168 BIT 5,B
    t = cpu.B & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_169(cpu): # 169 BIT 5,C
    t = cpu.C & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_16a(cpu): # 16a BIT 5,D
    t = cpu.D & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_16b(cpu): # 16b BIT 5,E
    t = cpu.E & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_16c(cpu): # 16c BIT 5,H
    t = (cpu.HL >> 8) & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_16d(cpu): # 16d BIT 5,L
    t = (cpu.HL & 0xFF) & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_16e(cpu): # 16e BIT 5,(HL)
    t = cpu.mb[cpu.HL] & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 16

def BIT_16f(cpu): # 16f BIT 5,A
    t = cpu.A & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_170(cpu): # 170 BIT 6,B
    t = cpu.B & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_171(cpu): # 171 BIT 6,C
    t = cpu.C & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_172(cpu): # 172 BIT 6,D
    t = cpu.D & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_173(cpu): # 173 BIT 6,E
    t = cpu.E & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_174(cpu): # 174 BIT 6,H
    t = (cpu.HL >> 8) & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_175(cpu): # 175 BIT 6,L
    t = (cpu.HL & 0xFF) & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_176(cpu): # 176 BIT 6,(HL)
    t = cpu.mb[cpu.HL] & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 16

def BIT_177(cpu): # 177 BIT 6,A
    t = cpu.A & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_178(cpu): # 178 BIT 7,B
    t = cpu.B & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_179(cpu): # 179 BIT 7,C
    t = cpu.C & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_17a(cpu): # 17a BIT 7,D
    t = cpu.D & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_17b(cpu): # 17b BIT 7,E
    t = cpu.E & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_17c(cpu): # 17c BIT 7,H
    t = (cpu.HL >> 8) & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_17d(cpu): # 17d BIT 7,L
    t = (cpu.HL & 0xFF) & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def BIT_17e(cpu): # 17e BIT 7,(HL)
    t = cpu.mb[cpu.HL] & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 16

def BIT_17f(cpu): # 17f BIT 7,A
    t = cpu.A & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << flagZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    return 8

def RES_180(cpu): # 180 RES 0,B
    t = cpu.B & ~(1 << 0)
    cpu.B = t
    cpu.PC += 2
    return 8

def RES_181(cpu): # 181 RES 0,C
    t = cpu.C & ~(1 << 0)
    cpu.C = t
    cpu.PC += 2
    return 8

def RES_182(cpu): # 182 RES 0,D
    t = cpu.D & ~(1 << 0)
    cpu.D = t
    cpu.PC += 2
    return 8

def RES_183(cpu): # 183 RES 0,E
    t = cpu.E & ~(1 << 0)
    cpu.E = t
    cpu.PC += 2
    return 8

def RES_184(cpu): # 184 RES 0,H
    t = (cpu.HL >> 8) & ~(1 << 0)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def RES_185(cpu): # 185 RES 0,L
    t = (cpu.HL & 0xFF) & ~(1 << 0)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def RES_186(cpu): # 186 RES 0,(HL)
    t = cpu.mb[cpu.HL] & ~(1 << 0)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def RES_187(cpu): # 187 RES 0,A
    t = cpu.A & ~(1 << 0)
    cpu.A = t
    cpu.PC += 2
    return 8

def RES_188(cpu): # 188 RES 1,B
    t = cpu.B & ~(1 << 1)
    cpu.B = t
    cpu.PC += 2
    return 8

def RES_189(cpu): # 189 RES 1,C
    t = cpu.C & ~(1 << 1)
    cpu.C = t
    cpu.PC += 2
    return 8

def RES_18a(cpu): # 18a RES 1,D
    t = cpu.D & ~(1 << 1)
    cpu.D = t
    cpu.PC += 2
    return 8

def RES_18b(cpu): # 18b RES 1,E
    t = cpu.E & ~(1 << 1)
    cpu.E = t
    cpu.PC += 2
    return 8

def RES_18c(cpu): # 18c RES 1,H
    t = (cpu.HL >> 8) & ~(1 << 1)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def RES_18d(cpu): # 18d RES 1,L
    t = (cpu.HL & 0xFF) & ~(1 << 1)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def RES_18e(cpu): # 18e RES 1,(HL)
    t = cpu.mb[cpu.HL] & ~(1 << 1)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def RES_18f(cpu): # 18f RES 1,A
    t = cpu.A & ~(1 << 1)
    cpu.A = t
    cpu.PC += 2
    return 8

def RES_190(cpu): # 190 RES 2,B
    t = cpu.B & ~(1 << 2)
    cpu.B = t
    cpu.PC += 2
    return 8

def RES_191(cpu): # 191 RES 2,C
    t = cpu.C & ~(1 << 2)
    cpu.C = t
    cpu.PC += 2
    return 8

def RES_192(cpu): # 192 RES 2,D
    t = cpu.D & ~(1 << 2)
    cpu.D = t
    cpu.PC += 2
    return 8

def RES_193(cpu): # 193 RES 2,E
    t = cpu.E & ~(1 << 2)
    cpu.E = t
    cpu.PC += 2
    return 8

def RES_194(cpu): # 194 RES 2,H
    t = (cpu.HL >> 8) & ~(1 << 2)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def RES_195(cpu): # 195 RES 2,L
    t = (cpu.HL & 0xFF) & ~(1 << 2)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def RES_196(cpu): # 196 RES 2,(HL)
    t = cpu.mb[cpu.HL] & ~(1 << 2)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def RES_197(cpu): # 197 RES 2,A
    t = cpu.A & ~(1 << 2)
    cpu.A = t
    cpu.PC += 2
    return 8

def RES_198(cpu): # 198 RES 3,B
    t = cpu.B & ~(1 << 3)
    cpu.B = t
    cpu.PC += 2
    return 8

def RES_199(cpu): # 199 RES 3,C
    t = cpu.C & ~(1 << 3)
    cpu.C = t
    cpu.PC += 2
    return 8

def RES_19a(cpu): # 19a RES 3,D
    t = cpu.D & ~(1 << 3)
    cpu.D = t
    cpu.PC += 2
    return 8

def RES_19b(cpu): # 19b RES 3,E
    t = cpu.E & ~(1 << 3)
    cpu.E = t
    cpu.PC += 2
    return 8

def RES_19c(cpu): # 19c RES 3,H
    t = (cpu.HL >> 8) & ~(1 << 3)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def RES_19d(cpu): # 19d RES 3,L
    t = (cpu.HL & 0xFF) & ~(1 << 3)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def RES_19e(cpu): # 19e RES 3,(HL)
    t = cpu.mb[cpu.HL] & ~(1 << 3)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def RES_19f(cpu): # 19f RES 3,A
    t = cpu.A & ~(1 << 3)
    cpu.A = t
    cpu.PC += 2
    return 8

def RES_1a0(cpu): # 1a0 RES 4,B
    t = cpu.B & ~(1 << 4)
    cpu.B = t
    cpu.PC += 2
    return 8

def RES_1a1(cpu): # 1a1 RES 4,C
    t = cpu.C & ~(1 << 4)
    cpu.C = t
    cpu.PC += 2
    return 8

def RES_1a2(cpu): # 1a2 RES 4,D
    t = cpu.D & ~(1 << 4)
    cpu.D = t
    cpu.PC += 2
    return 8

def RES_1a3(cpu): # 1a3 RES 4,E
    t = cpu.E & ~(1 << 4)
    cpu.E = t
    cpu.PC += 2
    return 8

def RES_1a4(cpu): # 1a4 RES 4,H
    t = (cpu.HL >> 8) & ~(1 << 4)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def RES_1a5(cpu): # 1a5 RES 4,L
    t = (cpu.HL & 0xFF) & ~(1 << 4)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def RES_1a6(cpu): # 1a6 RES 4,(HL)
    t = cpu.mb[cpu.HL] & ~(1 << 4)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def RES_1a7(cpu): # 1a7 RES 4,A
    t = cpu.A & ~(1 << 4)
    cpu.A = t
    cpu.PC += 2
    return 8

def RES_1a8(cpu): # 1a8 RES 5,B
    t = cpu.B & ~(1 << 5)
    cpu.B = t
    cpu.PC += 2
    return 8

def RES_1a9(cpu): # 1a9 RES 5,C
    t = cpu.C & ~(1 << 5)
    cpu.C = t
    cpu.PC += 2
    return 8

def RES_1aa(cpu): # 1aa RES 5,D
    t = cpu.D & ~(1 << 5)
    cpu.D = t
    cpu.PC += 2
    return 8

def RES_1ab(cpu): # 1ab RES 5,E
    t = cpu.E & ~(1 << 5)
    cpu.E = t
    cpu.PC += 2
    return 8

def RES_1ac(cpu): # 1ac RES 5,H
    t = (cpu.HL >> 8) & ~(1 << 5)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def RES_1ad(cpu): # 1ad RES 5,L
    t = (cpu.HL & 0xFF) & ~(1 << 5)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def RES_1ae(cpu): # 1ae RES 5,(HL)
    t = cpu.mb[cpu.HL] & ~(1 << 5)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def RES_1af(cpu): # 1af RES 5,A
    t = cpu.A & ~(1 << 5)
    cpu.A = t
    cpu.PC += 2
    return 8

def RES_1b0(cpu): # 1b0 RES 6,B
    t = cpu.B & ~(1 << 6)
    cpu.B = t
    cpu.PC += 2
    return 8

def RES_1b1(cpu): # 1b1 RES 6,C
    t = cpu.C & ~(1 << 6)
    cpu.C = t
    cpu.PC += 2
    return 8

def RES_1b2(cpu): # 1b2 RES 6,D
    t = cpu.D & ~(1 << 6)
    cpu.D = t
    cpu.PC += 2
    return 8

def RES_1b3(cpu): # 1b3 RES 6,E
    t = cpu.E & ~(1 << 6)
    cpu.E = t
    cpu.PC += 2
    return 8

def RES_1b4(cpu): # 1b4 RES 6,H
    t = (cpu.HL >> 8) & ~(1 << 6)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def RES_1b5(cpu): # 1b5 RES 6,L
    t = (cpu.HL & 0xFF) & ~(1 << 6)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def RES_1b6(cpu): # 1b6 RES 6,(HL)
    t = cpu.mb[cpu.HL] & ~(1 << 6)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def RES_1b7(cpu): # 1b7 RES 6,A
    t = cpu.A & ~(1 << 6)
    cpu.A = t
    cpu.PC += 2
    return 8

def RES_1b8(cpu): # 1b8 RES 7,B
    t = cpu.B & ~(1 << 7)
    cpu.B = t
    cpu.PC += 2
    return 8

def RES_1b9(cpu): # 1b9 RES 7,C
    t = cpu.C & ~(1 << 7)
    cpu.C = t
    cpu.PC += 2
    return 8

def RES_1ba(cpu): # 1ba RES 7,D
    t = cpu.D & ~(1 << 7)
    cpu.D = t
    cpu.PC += 2
    return 8

def RES_1bb(cpu): # 1bb RES 7,E
    t = cpu.E & ~(1 << 7)
    cpu.E = t
    cpu.PC += 2
    return 8

def RES_1bc(cpu): # 1bc RES 7,H
    t = (cpu.HL >> 8) & ~(1 << 7)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def RES_1bd(cpu): # 1bd RES 7,L
    t = (cpu.HL & 0xFF) & ~(1 << 7)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def RES_1be(cpu): # 1be RES 7,(HL)
    t = cpu.mb[cpu.HL] & ~(1 << 7)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def RES_1bf(cpu): # 1bf RES 7,A
    t = cpu.A & ~(1 << 7)
    cpu.A = t
    cpu.PC += 2
    return 8

def SET_1c0(cpu): # 1c0 SET 0,B
    t = cpu.B | (1 << 0)
    cpu.B = t
    cpu.PC += 2
    return 8

def SET_1c1(cpu): # 1c1 SET 0,C
    t = cpu.C | (1 << 0)
    cpu.C = t
    cpu.PC += 2
    return 8

def SET_1c2(cpu): # 1c2 SET 0,D
    t = cpu.D | (1 << 0)
    cpu.D = t
    cpu.PC += 2
    return 8

def SET_1c3(cpu): # 1c3 SET 0,E
    t = cpu.E | (1 << 0)
    cpu.E = t
    cpu.PC += 2
    return 8

def SET_1c4(cpu): # 1c4 SET 0,H
    t = (cpu.HL >> 8) | (1 << 0)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def SET_1c5(cpu): # 1c5 SET 0,L
    t = (cpu.HL & 0xFF) | (1 << 0)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def SET_1c6(cpu): # 1c6 SET 0,(HL)
    t = cpu.mb[cpu.HL] | (1 << 0)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def SET_1c7(cpu): # 1c7 SET 0,A
    t = cpu.A | (1 << 0)
    cpu.A = t
    cpu.PC += 2
    return 8

def SET_1c8(cpu): # 1c8 SET 1,B
    t = cpu.B | (1 << 1)
    cpu.B = t
    cpu.PC += 2
    return 8

def SET_1c9(cpu): # 1c9 SET 1,C
    t = cpu.C | (1 << 1)
    cpu.C = t
    cpu.PC += 2
    return 8

def SET_1ca(cpu): # 1ca SET 1,D
    t = cpu.D | (1 << 1)
    cpu.D = t
    cpu.PC += 2
    return 8

def SET_1cb(cpu): # 1cb SET 1,E
    t = cpu.E | (1 << 1)
    cpu.E = t
    cpu.PC += 2
    return 8

def SET_1cc(cpu): # 1cc SET 1,H
    t = (cpu.HL >> 8) | (1 << 1)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def SET_1cd(cpu): # 1cd SET 1,L
    t = (cpu.HL & 0xFF) | (1 << 1)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def SET_1ce(cpu): # 1ce SET 1,(HL)
    t = cpu.mb[cpu.HL] | (1 << 1)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def SET_1cf(cpu): # 1cf SET 1,A
    t = cpu.A | (1 << 1)
    cpu.A = t
    cpu.PC += 2
    return 8

def SET_1d0(cpu): # 1d0 SET 2,B
    t = cpu.B | (1 << 2)
    cpu.B = t
    cpu.PC += 2
    return 8

def SET_1d1(cpu): # 1d1 SET 2,C
    t = cpu.C | (1 << 2)
    cpu.C = t
    cpu.PC += 2
    return 8

def SET_1d2(cpu): # 1d2 SET 2,D
    t = cpu.D | (1 << 2)
    cpu.D = t
    cpu.PC += 2
    return 8

def SET_1d3(cpu): # 1d3 SET 2,E
    t = cpu.E | (1 << 2)
    cpu.E = t
    cpu.PC += 2
    return 8

def SET_1d4(cpu): # 1d4 SET 2,H
    t = (cpu.HL >> 8) | (1 << 2)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def SET_1d5(cpu): # 1d5 SET 2,L
    t = (cpu.HL & 0xFF) | (1 << 2)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def SET_1d6(cpu): # 1d6 SET 2,(HL)
    t = cpu.mb[cpu.HL] | (1 << 2)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def SET_1d7(cpu): # 1d7 SET 2,A
    t = cpu.A | (1 << 2)
    cpu.A = t
    cpu.PC += 2
    return 8

def SET_1d8(cpu): # 1d8 SET 3,B
    t = cpu.B | (1 << 3)
    cpu.B = t
    cpu.PC += 2
    return 8

def SET_1d9(cpu): # 1d9 SET 3,C
    t = cpu.C | (1 << 3)
    cpu.C = t
    cpu.PC += 2
    return 8

def SET_1da(cpu): # 1da SET 3,D
    t = cpu.D | (1 << 3)
    cpu.D = t
    cpu.PC += 2
    return 8

def SET_1db(cpu): # 1db SET 3,E
    t = cpu.E | (1 << 3)
    cpu.E = t
    cpu.PC += 2
    return 8

def SET_1dc(cpu): # 1dc SET 3,H
    t = (cpu.HL >> 8) | (1 << 3)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def SET_1dd(cpu): # 1dd SET 3,L
    t = (cpu.HL & 0xFF) | (1 << 3)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def SET_1de(cpu): # 1de SET 3,(HL)
    t = cpu.mb[cpu.HL] | (1 << 3)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def SET_1df(cpu): # 1df SET 3,A
    t = cpu.A | (1 << 3)
    cpu.A = t
    cpu.PC += 2
    return 8

def SET_1e0(cpu): # 1e0 SET 4,B
    t = cpu.B | (1 << 4)
    cpu.B = t
    cpu.PC += 2
    return 8

def SET_1e1(cpu): # 1e1 SET 4,C
    t = cpu.C | (1 << 4)
    cpu.C = t
    cpu.PC += 2
    return 8

def SET_1e2(cpu): # 1e2 SET 4,D
    t = cpu.D | (1 << 4)
    cpu.D = t
    cpu.PC += 2
    return 8

def SET_1e3(cpu): # 1e3 SET 4,E
    t = cpu.E | (1 << 4)
    cpu.E = t
    cpu.PC += 2
    return 8

def SET_1e4(cpu): # 1e4 SET 4,H
    t = (cpu.HL >> 8) | (1 << 4)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def SET_1e5(cpu): # 1e5 SET 4,L
    t = (cpu.HL & 0xFF) | (1 << 4)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def SET_1e6(cpu): # 1e6 SET 4,(HL)
    t = cpu.mb[cpu.HL] | (1 << 4)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def SET_1e7(cpu): # 1e7 SET 4,A
    t = cpu.A | (1 << 4)
    cpu.A = t
    cpu.PC += 2
    return 8

def SET_1e8(cpu): # 1e8 SET 5,B
    t = cpu.B | (1 << 5)
    cpu.B = t
    cpu.PC += 2
    return 8

def SET_1e9(cpu): # 1e9 SET 5,C
    t = cpu.C | (1 << 5)
    cpu.C = t
    cpu.PC += 2
    return 8

def SET_1ea(cpu): # 1ea SET 5,D
    t = cpu.D | (1 << 5)
    cpu.D = t
    cpu.PC += 2
    return 8

def SET_1eb(cpu): # 1eb SET 5,E
    t = cpu.E | (1 << 5)
    cpu.E = t
    cpu.PC += 2
    return 8

def SET_1ec(cpu): # 1ec SET 5,H
    t = (cpu.HL >> 8) | (1 << 5)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def SET_1ed(cpu): # 1ed SET 5,L
    t = (cpu.HL & 0xFF) | (1 << 5)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def SET_1ee(cpu): # 1ee SET 5,(HL)
    t = cpu.mb[cpu.HL] | (1 << 5)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def SET_1ef(cpu): # 1ef SET 5,A
    t = cpu.A | (1 << 5)
    cpu.A = t
    cpu.PC += 2
    return 8

def SET_1f0(cpu): # 1f0 SET 6,B
    t = cpu.B | (1 << 6)
    cpu.B = t
    cpu.PC += 2
    return 8

def SET_1f1(cpu): # 1f1 SET 6,C
    t = cpu.C | (1 << 6)
    cpu.C = t
    cpu.PC += 2
    return 8

def SET_1f2(cpu): # 1f2 SET 6,D
    t = cpu.D | (1 << 6)
    cpu.D = t
    cpu.PC += 2
    return 8

def SET_1f3(cpu): # 1f3 SET 6,E
    t = cpu.E | (1 << 6)
    cpu.E = t
    cpu.PC += 2
    return 8

def SET_1f4(cpu): # 1f4 SET 6,H
    t = (cpu.HL >> 8) | (1 << 6)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def SET_1f5(cpu): # 1f5 SET 6,L
    t = (cpu.HL & 0xFF) | (1 << 6)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def SET_1f6(cpu): # 1f6 SET 6,(HL)
    t = cpu.mb[cpu.HL] | (1 << 6)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def SET_1f7(cpu): # 1f7 SET 6,A
    t = cpu.A | (1 << 6)
    cpu.A = t
    cpu.PC += 2
    return 8

def SET_1f8(cpu): # 1f8 SET 7,B
    t = cpu.B | (1 << 7)
    cpu.B = t
    cpu.PC += 2
    return 8

def SET_1f9(cpu): # 1f9 SET 7,C
    t = cpu.C | (1 << 7)
    cpu.C = t
    cpu.PC += 2
    return 8

def SET_1fa(cpu): # 1fa SET 7,D
    t = cpu.D | (1 << 7)
    cpu.D = t
    cpu.PC += 2
    return 8

def SET_1fb(cpu): # 1fb SET 7,E
    t = cpu.E | (1 << 7)
    cpu.E = t
    cpu.PC += 2
    return 8

def SET_1fc(cpu): # 1fc SET 7,H
    t = (cpu.HL >> 8) | (1 << 7)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    return 8

def SET_1fd(cpu): # 1fd SET 7,L
    t = (cpu.HL & 0xFF) | (1 << 7)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    return 8

def SET_1fe(cpu): # 1fe SET 7,(HL)
    t = cpu.mb[cpu.HL] | (1 << 7)
    cpu.mb[cpu.HL] = t
    cpu.PC += 2
    return 16

def SET_1ff(cpu): # 1ff SET 7,A
    t = cpu.A | (1 << 7)
    cpu.A = t
    cpu.PC += 2
    return 8

def NOOPCODE(cpu):
    return 0

def getOpcodeLength(opcode):
    return opcodeLengths[opcode]

def executeOpcode(cpu, opcode):
    opLen = getOpcodeLength(opcode)
    v = 0
    pc = cpu.PC
    if opLen == 2:
        # 8-bit immediate
        v = cpu.mb[pc+1]
    elif opLen == 3:
        # 16-bit immediate
        # Flips order of values due to big-endian
        a = cpu.mb[pc+2]
        b = cpu.mb[pc+1]
        v = (a << 8) + b

    if opcode == 0x00:
        return NOP_00(cpu)
    elif opcode == 0x01:
        return LD_01(cpu, v)
    elif opcode == 0x02:
        return LD_02(cpu)
    elif opcode == 0x03:
        return INC_03(cpu)
    elif opcode == 0x04:
        return INC_04(cpu)
    elif opcode == 0x05:
        return DEC_05(cpu)
    elif opcode == 0x06:
        return LD_06(cpu, v)
    elif opcode == 0x07:
        return RLCA_07(cpu)
    elif opcode == 0x08:
        return LD_08(cpu, v)
    elif opcode == 0x09:
        return ADD_09(cpu)
    elif opcode == 0x0a:
        return LD_0a(cpu)
    elif opcode == 0x0b:
        return DEC_0b(cpu)
    elif opcode == 0x0c:
        return INC_0c(cpu)
    elif opcode == 0x0d:
        return DEC_0d(cpu)
    elif opcode == 0x0e:
        return LD_0e(cpu, v)
    elif opcode == 0x0f:
        return RRCA_0f(cpu)
    elif opcode == 0x10:
        return STOP_10(cpu, v)
    elif opcode == 0x11:
        return LD_11(cpu, v)
    elif opcode == 0x12:
        return LD_12(cpu)
    elif opcode == 0x13:
        return INC_13(cpu)
    elif opcode == 0x14:
        return INC_14(cpu)
    elif opcode == 0x15:
        return DEC_15(cpu)
    elif opcode == 0x16:
        return LD_16(cpu, v)
    elif opcode == 0x17:
        return RLA_17(cpu)
    elif opcode == 0x18:
        return JR_18(cpu, v)
    elif opcode == 0x19:
        return ADD_19(cpu)
    elif opcode == 0x1a:
        return LD_1a(cpu)
    elif opcode == 0x1b:
        return DEC_1b(cpu)
    elif opcode == 0x1c:
        return INC_1c(cpu)
    elif opcode == 0x1d:
        return DEC_1d(cpu)
    elif opcode == 0x1e:
        return LD_1e(cpu, v)
    elif opcode == 0x1f:
        return RRA_1f(cpu)
    elif opcode == 0x20:
        return JR_20(cpu, v)
    elif opcode == 0x21:
        return LD_21(cpu, v)
    elif opcode == 0x22:
        return LD_22(cpu)
    elif opcode == 0x23:
        return INC_23(cpu)
    elif opcode == 0x24:
        return INC_24(cpu)
    elif opcode == 0x25:
        return DEC_25(cpu)
    elif opcode == 0x26:
        return LD_26(cpu, v)
    elif opcode == 0x27:
        return DAA_27(cpu)
    elif opcode == 0x28:
        return JR_28(cpu, v)
    elif opcode == 0x29:
        return ADD_29(cpu)
    elif opcode == 0x2a:
        return LD_2a(cpu)
    elif opcode == 0x2b:
        return DEC_2b(cpu)
    elif opcode == 0x2c:
        return INC_2c(cpu)
    elif opcode == 0x2d:
        return DEC_2d(cpu)
    elif opcode == 0x2e:
        return LD_2e(cpu, v)
    elif opcode == 0x2f:
        return CPL_2f(cpu)
    elif opcode == 0x30:
        return JR_30(cpu, v)
    elif opcode == 0x31:
        return LD_31(cpu, v)
    elif opcode == 0x32:
        return LD_32(cpu)
    elif opcode == 0x33:
        return INC_33(cpu)
    elif opcode == 0x34:
        return INC_34(cpu)
    elif opcode == 0x35:
        return DEC_35(cpu)
    elif opcode == 0x36:
        return LD_36(cpu, v)
    elif opcode == 0x37:
        return SCF_37(cpu)
    elif opcode == 0x38:
        return JR_38(cpu, v)
    elif opcode == 0x39:
        return ADD_39(cpu)
    elif opcode == 0x3a:
        return LD_3a(cpu)
    elif opcode == 0x3b:
        return DEC_3b(cpu)
    elif opcode == 0x3c:
        return INC_3c(cpu)
    elif opcode == 0x3d:
        return DEC_3d(cpu)
    elif opcode == 0x3e:
        return LD_3e(cpu, v)
    elif opcode == 0x3f:
        return CCF_3f(cpu)
    elif opcode == 0x40:
        return LD_40(cpu)
    elif opcode == 0x41:
        return LD_41(cpu)
    elif opcode == 0x42:
        return LD_42(cpu)
    elif opcode == 0x43:
        return LD_43(cpu)
    elif opcode == 0x44:
        return LD_44(cpu)
    elif opcode == 0x45:
        return LD_45(cpu)
    elif opcode == 0x46:
        return LD_46(cpu)
    elif opcode == 0x47:
        return LD_47(cpu)
    elif opcode == 0x48:
        return LD_48(cpu)
    elif opcode == 0x49:
        return LD_49(cpu)
    elif opcode == 0x4a:
        return LD_4a(cpu)
    elif opcode == 0x4b:
        return LD_4b(cpu)
    elif opcode == 0x4c:
        return LD_4c(cpu)
    elif opcode == 0x4d:
        return LD_4d(cpu)
    elif opcode == 0x4e:
        return LD_4e(cpu)
    elif opcode == 0x4f:
        return LD_4f(cpu)
    elif opcode == 0x50:
        return LD_50(cpu)
    elif opcode == 0x51:
        return LD_51(cpu)
    elif opcode == 0x52:
        return LD_52(cpu)
    elif opcode == 0x53:
        return LD_53(cpu)
    elif opcode == 0x54:
        return LD_54(cpu)
    elif opcode == 0x55:
        return LD_55(cpu)
    elif opcode == 0x56:
        return LD_56(cpu)
    elif opcode == 0x57:
        return LD_57(cpu)
    elif opcode == 0x58:
        return LD_58(cpu)
    elif opcode == 0x59:
        return LD_59(cpu)
    elif opcode == 0x5a:
        return LD_5a(cpu)
    elif opcode == 0x5b:
        return LD_5b(cpu)
    elif opcode == 0x5c:
        return LD_5c(cpu)
    elif opcode == 0x5d:
        return LD_5d(cpu)
    elif opcode == 0x5e:
        return LD_5e(cpu)
    elif opcode == 0x5f:
        return LD_5f(cpu)
    elif opcode == 0x60:
        return LD_60(cpu)
    elif opcode == 0x61:
        return LD_61(cpu)
    elif opcode == 0x62:
        return LD_62(cpu)
    elif opcode == 0x63:
        return LD_63(cpu)
    elif opcode == 0x64:
        return LD_64(cpu)
    elif opcode == 0x65:
        return LD_65(cpu)
    elif opcode == 0x66:
        return LD_66(cpu)
    elif opcode == 0x67:
        return LD_67(cpu)
    elif opcode == 0x68:
        return LD_68(cpu)
    elif opcode == 0x69:
        return LD_69(cpu)
    elif opcode == 0x6a:
        return LD_6a(cpu)
    elif opcode == 0x6b:
        return LD_6b(cpu)
    elif opcode == 0x6c:
        return LD_6c(cpu)
    elif opcode == 0x6d:
        return LD_6d(cpu)
    elif opcode == 0x6e:
        return LD_6e(cpu)
    elif opcode == 0x6f:
        return LD_6f(cpu)
    elif opcode == 0x70:
        return LD_70(cpu)
    elif opcode == 0x71:
        return LD_71(cpu)
    elif opcode == 0x72:
        return LD_72(cpu)
    elif opcode == 0x73:
        return LD_73(cpu)
    elif opcode == 0x74:
        return LD_74(cpu)
    elif opcode == 0x75:
        return LD_75(cpu)
    elif opcode == 0x76:
        return HALT_76(cpu)
    elif opcode == 0x77:
        return LD_77(cpu)
    elif opcode == 0x78:
        return LD_78(cpu)
    elif opcode == 0x79:
        return LD_79(cpu)
    elif opcode == 0x7a:
        return LD_7a(cpu)
    elif opcode == 0x7b:
        return LD_7b(cpu)
    elif opcode == 0x7c:
        return LD_7c(cpu)
    elif opcode == 0x7d:
        return LD_7d(cpu)
    elif opcode == 0x7e:
        return LD_7e(cpu)
    elif opcode == 0x7f:
        return LD_7f(cpu)
    elif opcode == 0x80:
        return ADD_80(cpu)
    elif opcode == 0x81:
        return ADD_81(cpu)
    elif opcode == 0x82:
        return ADD_82(cpu)
    elif opcode == 0x83:
        return ADD_83(cpu)
    elif opcode == 0x84:
        return ADD_84(cpu)
    elif opcode == 0x85:
        return ADD_85(cpu)
    elif opcode == 0x86:
        return ADD_86(cpu)
    elif opcode == 0x87:
        return ADD_87(cpu)
    elif opcode == 0x88:
        return ADC_88(cpu)
    elif opcode == 0x89:
        return ADC_89(cpu)
    elif opcode == 0x8a:
        return ADC_8a(cpu)
    elif opcode == 0x8b:
        return ADC_8b(cpu)
    elif opcode == 0x8c:
        return ADC_8c(cpu)
    elif opcode == 0x8d:
        return ADC_8d(cpu)
    elif opcode == 0x8e:
        return ADC_8e(cpu)
    elif opcode == 0x8f:
        return ADC_8f(cpu)
    elif opcode == 0x90:
        return SUB_90(cpu)
    elif opcode == 0x91:
        return SUB_91(cpu)
    elif opcode == 0x92:
        return SUB_92(cpu)
    elif opcode == 0x93:
        return SUB_93(cpu)
    elif opcode == 0x94:
        return SUB_94(cpu)
    elif opcode == 0x95:
        return SUB_95(cpu)
    elif opcode == 0x96:
        return SUB_96(cpu)
    elif opcode == 0x97:
        return SUB_97(cpu)
    elif opcode == 0x98:
        return SBC_98(cpu)
    elif opcode == 0x99:
        return SBC_99(cpu)
    elif opcode == 0x9a:
        return SBC_9a(cpu)
    elif opcode == 0x9b:
        return SBC_9b(cpu)
    elif opcode == 0x9c:
        return SBC_9c(cpu)
    elif opcode == 0x9d:
        return SBC_9d(cpu)
    elif opcode == 0x9e:
        return SBC_9e(cpu)
    elif opcode == 0x9f:
        return SBC_9f(cpu)
    elif opcode == 0xa0:
        return AND_a0(cpu)
    elif opcode == 0xa1:
        return AND_a1(cpu)
    elif opcode == 0xa2:
        return AND_a2(cpu)
    elif opcode == 0xa3:
        return AND_a3(cpu)
    elif opcode == 0xa4:
        return AND_a4(cpu)
    elif opcode == 0xa5:
        return AND_a5(cpu)
    elif opcode == 0xa6:
        return AND_a6(cpu)
    elif opcode == 0xa7:
        return AND_a7(cpu)
    elif opcode == 0xa8:
        return XOR_a8(cpu)
    elif opcode == 0xa9:
        return XOR_a9(cpu)
    elif opcode == 0xaa:
        return XOR_aa(cpu)
    elif opcode == 0xab:
        return XOR_ab(cpu)
    elif opcode == 0xac:
        return XOR_ac(cpu)
    elif opcode == 0xad:
        return XOR_ad(cpu)
    elif opcode == 0xae:
        return XOR_ae(cpu)
    elif opcode == 0xaf:
        return XOR_af(cpu)
    elif opcode == 0xb0:
        return OR_b0(cpu)
    elif opcode == 0xb1:
        return OR_b1(cpu)
    elif opcode == 0xb2:
        return OR_b2(cpu)
    elif opcode == 0xb3:
        return OR_b3(cpu)
    elif opcode == 0xb4:
        return OR_b4(cpu)
    elif opcode == 0xb5:
        return OR_b5(cpu)
    elif opcode == 0xb6:
        return OR_b6(cpu)
    elif opcode == 0xb7:
        return OR_b7(cpu)
    elif opcode == 0xb8:
        return CP_b8(cpu)
    elif opcode == 0xb9:
        return CP_b9(cpu)
    elif opcode == 0xba:
        return CP_ba(cpu)
    elif opcode == 0xbb:
        return CP_bb(cpu)
    elif opcode == 0xbc:
        return CP_bc(cpu)
    elif opcode == 0xbd:
        return CP_bd(cpu)
    elif opcode == 0xbe:
        return CP_be(cpu)
    elif opcode == 0xbf:
        return CP_bf(cpu)
    elif opcode == 0xc0:
        return RET_c0(cpu)
    elif opcode == 0xc1:
        return POP_c1(cpu)
    elif opcode == 0xc2:
        return JP_c2(cpu, v)
    elif opcode == 0xc3:
        return JP_c3(cpu, v)
    elif opcode == 0xc4:
        return CALL_c4(cpu, v)
    elif opcode == 0xc5:
        return PUSH_c5(cpu)
    elif opcode == 0xc6:
        return ADD_c6(cpu, v)
    elif opcode == 0xc7:
        return RST_c7(cpu)
    elif opcode == 0xc8:
        return RET_c8(cpu)
    elif opcode == 0xc9:
        return RET_c9(cpu)
    elif opcode == 0xca:
        return JP_ca(cpu, v)
    elif opcode == 0xcb:
        return CB_cb(cpu)
    elif opcode == 0xcc:
        return CALL_cc(cpu, v)
    elif opcode == 0xcd:
        return CALL_cd(cpu, v)
    elif opcode == 0xce:
        return ADC_ce(cpu, v)
    elif opcode == 0xcf:
        return RST_cf(cpu)
    elif opcode == 0xd0:
        return RET_d0(cpu)
    elif opcode == 0xd1:
        return POP_d1(cpu)
    elif opcode == 0xd2:
        return JP_d2(cpu, v)
    elif opcode == 0xd3:
        return NOOPCODE(cpu)
    elif opcode == 0xd4:
        return CALL_d4(cpu, v)
    elif opcode == 0xd5:
        return PUSH_d5(cpu)
    elif opcode == 0xd6:
        return SUB_d6(cpu, v)
    elif opcode == 0xd7:
        return RST_d7(cpu)
    elif opcode == 0xd8:
        return RET_d8(cpu)
    elif opcode == 0xd9:
        return RETI_d9(cpu)
    elif opcode == 0xda:
        return JP_da(cpu, v)
    elif opcode == 0xdb:
        return NOOPCODE(cpu)
    elif opcode == 0xdc:
        return CALL_dc(cpu, v)
    elif opcode == 0xdd:
        return NOOPCODE(cpu)
    elif opcode == 0xde:
        return SBC_de(cpu, v)
    elif opcode == 0xdf:
        return RST_df(cpu)
    elif opcode == 0xe0:
        return LD_e0(cpu, v)
    elif opcode == 0xe1:
        return POP_e1(cpu)
    elif opcode == 0xe2:
        return LD_e2(cpu)
    elif opcode == 0xe3:
        return NOOPCODE(cpu)
    elif opcode == 0xe4:
        return NOOPCODE(cpu)
    elif opcode == 0xe5:
        return PUSH_e5(cpu)
    elif opcode == 0xe6:
        return AND_e6(cpu, v)
    elif opcode == 0xe7:
        return RST_e7(cpu)
    elif opcode == 0xe8:
        return ADD_e8(cpu, v)
    elif opcode == 0xe9:
        return JP_e9(cpu)
    elif opcode == 0xea:
        return LD_ea(cpu, v)
    elif opcode == 0xeb:
        return NOOPCODE(cpu)
    elif opcode == 0xec:
        return NOOPCODE(cpu)
    elif opcode == 0xed:
        return NOOPCODE(cpu)
    elif opcode == 0xee:
        return XOR_ee(cpu, v)
    elif opcode == 0xef:
        return RST_ef(cpu)
    elif opcode == 0xf0:
        return LD_f0(cpu, v)
    elif opcode == 0xf1:
        return POP_f1(cpu)
    elif opcode == 0xf2:
        return LD_f2(cpu)
    elif opcode == 0xf3:
        return DI_f3(cpu)
    elif opcode == 0xf4:
        return NOOPCODE(cpu)
    elif opcode == 0xf5:
        return PUSH_f5(cpu)
    elif opcode == 0xf6:
        return OR_f6(cpu, v)
    elif opcode == 0xf7:
        return RST_f7(cpu)
    elif opcode == 0xf8:
        return LD_f8(cpu, v)
    elif opcode == 0xf9:
        return LD_f9(cpu)
    elif opcode == 0xfa:
        return LD_fa(cpu, v)
    elif opcode == 0xfb:
        return EI_fb(cpu)
    elif opcode == 0xfc:
        return NOOPCODE(cpu)
    elif opcode == 0xfd:
        return NOOPCODE(cpu)
    elif opcode == 0xfe:
        return CP_fe(cpu, v)
    elif opcode == 0xff:
        return RST_ff(cpu)
    elif opcode == 0x100:
        return RLC_100(cpu)
    elif opcode == 0x101:
        return RLC_101(cpu)
    elif opcode == 0x102:
        return RLC_102(cpu)
    elif opcode == 0x103:
        return RLC_103(cpu)
    elif opcode == 0x104:
        return RLC_104(cpu)
    elif opcode == 0x105:
        return RLC_105(cpu)
    elif opcode == 0x106:
        return RLC_106(cpu)
    elif opcode == 0x107:
        return RLC_107(cpu)
    elif opcode == 0x108:
        return RRC_108(cpu)
    elif opcode == 0x109:
        return RRC_109(cpu)
    elif opcode == 0x10a:
        return RRC_10a(cpu)
    elif opcode == 0x10b:
        return RRC_10b(cpu)
    elif opcode == 0x10c:
        return RRC_10c(cpu)
    elif opcode == 0x10d:
        return RRC_10d(cpu)
    elif opcode == 0x10e:
        return RRC_10e(cpu)
    elif opcode == 0x10f:
        return RRC_10f(cpu)
    elif opcode == 0x110:
        return RL_110(cpu)
    elif opcode == 0x111:
        return RL_111(cpu)
    elif opcode == 0x112:
        return RL_112(cpu)
    elif opcode == 0x113:
        return RL_113(cpu)
    elif opcode == 0x114:
        return RL_114(cpu)
    elif opcode == 0x115:
        return RL_115(cpu)
    elif opcode == 0x116:
        return RL_116(cpu)
    elif opcode == 0x117:
        return RL_117(cpu)
    elif opcode == 0x118:
        return RR_118(cpu)
    elif opcode == 0x119:
        return RR_119(cpu)
    elif opcode == 0x11a:
        return RR_11a(cpu)
    elif opcode == 0x11b:
        return RR_11b(cpu)
    elif opcode == 0x11c:
        return RR_11c(cpu)
    elif opcode == 0x11d:
        return RR_11d(cpu)
    elif opcode == 0x11e:
        return RR_11e(cpu)
    elif opcode == 0x11f:
        return RR_11f(cpu)
    elif opcode == 0x120:
        return SLA_120(cpu)
    elif opcode == 0x121:
        return SLA_121(cpu)
    elif opcode == 0x122:
        return SLA_122(cpu)
    elif opcode == 0x123:
        return SLA_123(cpu)
    elif opcode == 0x124:
        return SLA_124(cpu)
    elif opcode == 0x125:
        return SLA_125(cpu)
    elif opcode == 0x126:
        return SLA_126(cpu)
    elif opcode == 0x127:
        return SLA_127(cpu)
    elif opcode == 0x128:
        return SRA_128(cpu)
    elif opcode == 0x129:
        return SRA_129(cpu)
    elif opcode == 0x12a:
        return SRA_12a(cpu)
    elif opcode == 0x12b:
        return SRA_12b(cpu)
    elif opcode == 0x12c:
        return SRA_12c(cpu)
    elif opcode == 0x12d:
        return SRA_12d(cpu)
    elif opcode == 0x12e:
        return SRA_12e(cpu)
    elif opcode == 0x12f:
        return SRA_12f(cpu)
    elif opcode == 0x130:
        return SWAP_130(cpu)
    elif opcode == 0x131:
        return SWAP_131(cpu)
    elif opcode == 0x132:
        return SWAP_132(cpu)
    elif opcode == 0x133:
        return SWAP_133(cpu)
    elif opcode == 0x134:
        return SWAP_134(cpu)
    elif opcode == 0x135:
        return SWAP_135(cpu)
    elif opcode == 0x136:
        return SWAP_136(cpu)
    elif opcode == 0x137:
        return SWAP_137(cpu)
    elif opcode == 0x138:
        return SRL_138(cpu)
    elif opcode == 0x139:
        return SRL_139(cpu)
    elif opcode == 0x13a:
        return SRL_13a(cpu)
    elif opcode == 0x13b:
        return SRL_13b(cpu)
    elif opcode == 0x13c:
        return SRL_13c(cpu)
    elif opcode == 0x13d:
        return SRL_13d(cpu)
    elif opcode == 0x13e:
        return SRL_13e(cpu)
    elif opcode == 0x13f:
        return SRL_13f(cpu)
    elif opcode == 0x140:
        return BIT_140(cpu)
    elif opcode == 0x141:
        return BIT_141(cpu)
    elif opcode == 0x142:
        return BIT_142(cpu)
    elif opcode == 0x143:
        return BIT_143(cpu)
    elif opcode == 0x144:
        return BIT_144(cpu)
    elif opcode == 0x145:
        return BIT_145(cpu)
    elif opcode == 0x146:
        return BIT_146(cpu)
    elif opcode == 0x147:
        return BIT_147(cpu)
    elif opcode == 0x148:
        return BIT_148(cpu)
    elif opcode == 0x149:
        return BIT_149(cpu)
    elif opcode == 0x14a:
        return BIT_14a(cpu)
    elif opcode == 0x14b:
        return BIT_14b(cpu)
    elif opcode == 0x14c:
        return BIT_14c(cpu)
    elif opcode == 0x14d:
        return BIT_14d(cpu)
    elif opcode == 0x14e:
        return BIT_14e(cpu)
    elif opcode == 0x14f:
        return BIT_14f(cpu)
    elif opcode == 0x150:
        return BIT_150(cpu)
    elif opcode == 0x151:
        return BIT_151(cpu)
    elif opcode == 0x152:
        return BIT_152(cpu)
    elif opcode == 0x153:
        return BIT_153(cpu)
    elif opcode == 0x154:
        return BIT_154(cpu)
    elif opcode == 0x155:
        return BIT_155(cpu)
    elif opcode == 0x156:
        return BIT_156(cpu)
    elif opcode == 0x157:
        return BIT_157(cpu)
    elif opcode == 0x158:
        return BIT_158(cpu)
    elif opcode == 0x159:
        return BIT_159(cpu)
    elif opcode == 0x15a:
        return BIT_15a(cpu)
    elif opcode == 0x15b:
        return BIT_15b(cpu)
    elif opcode == 0x15c:
        return BIT_15c(cpu)
    elif opcode == 0x15d:
        return BIT_15d(cpu)
    elif opcode == 0x15e:
        return BIT_15e(cpu)
    elif opcode == 0x15f:
        return BIT_15f(cpu)
    elif opcode == 0x160:
        return BIT_160(cpu)
    elif opcode == 0x161:
        return BIT_161(cpu)
    elif opcode == 0x162:
        return BIT_162(cpu)
    elif opcode == 0x163:
        return BIT_163(cpu)
    elif opcode == 0x164:
        return BIT_164(cpu)
    elif opcode == 0x165:
        return BIT_165(cpu)
    elif opcode == 0x166:
        return BIT_166(cpu)
    elif opcode == 0x167:
        return BIT_167(cpu)
    elif opcode == 0x168:
        return BIT_168(cpu)
    elif opcode == 0x169:
        return BIT_169(cpu)
    elif opcode == 0x16a:
        return BIT_16a(cpu)
    elif opcode == 0x16b:
        return BIT_16b(cpu)
    elif opcode == 0x16c:
        return BIT_16c(cpu)
    elif opcode == 0x16d:
        return BIT_16d(cpu)
    elif opcode == 0x16e:
        return BIT_16e(cpu)
    elif opcode == 0x16f:
        return BIT_16f(cpu)
    elif opcode == 0x170:
        return BIT_170(cpu)
    elif opcode == 0x171:
        return BIT_171(cpu)
    elif opcode == 0x172:
        return BIT_172(cpu)
    elif opcode == 0x173:
        return BIT_173(cpu)
    elif opcode == 0x174:
        return BIT_174(cpu)
    elif opcode == 0x175:
        return BIT_175(cpu)
    elif opcode == 0x176:
        return BIT_176(cpu)
    elif opcode == 0x177:
        return BIT_177(cpu)
    elif opcode == 0x178:
        return BIT_178(cpu)
    elif opcode == 0x179:
        return BIT_179(cpu)
    elif opcode == 0x17a:
        return BIT_17a(cpu)
    elif opcode == 0x17b:
        return BIT_17b(cpu)
    elif opcode == 0x17c:
        return BIT_17c(cpu)
    elif opcode == 0x17d:
        return BIT_17d(cpu)
    elif opcode == 0x17e:
        return BIT_17e(cpu)
    elif opcode == 0x17f:
        return BIT_17f(cpu)
    elif opcode == 0x180:
        return RES_180(cpu)
    elif opcode == 0x181:
        return RES_181(cpu)
    elif opcode == 0x182:
        return RES_182(cpu)
    elif opcode == 0x183:
        return RES_183(cpu)
    elif opcode == 0x184:
        return RES_184(cpu)
    elif opcode == 0x185:
        return RES_185(cpu)
    elif opcode == 0x186:
        return RES_186(cpu)
    elif opcode == 0x187:
        return RES_187(cpu)
    elif opcode == 0x188:
        return RES_188(cpu)
    elif opcode == 0x189:
        return RES_189(cpu)
    elif opcode == 0x18a:
        return RES_18a(cpu)
    elif opcode == 0x18b:
        return RES_18b(cpu)
    elif opcode == 0x18c:
        return RES_18c(cpu)
    elif opcode == 0x18d:
        return RES_18d(cpu)
    elif opcode == 0x18e:
        return RES_18e(cpu)
    elif opcode == 0x18f:
        return RES_18f(cpu)
    elif opcode == 0x190:
        return RES_190(cpu)
    elif opcode == 0x191:
        return RES_191(cpu)
    elif opcode == 0x192:
        return RES_192(cpu)
    elif opcode == 0x193:
        return RES_193(cpu)
    elif opcode == 0x194:
        return RES_194(cpu)
    elif opcode == 0x195:
        return RES_195(cpu)
    elif opcode == 0x196:
        return RES_196(cpu)
    elif opcode == 0x197:
        return RES_197(cpu)
    elif opcode == 0x198:
        return RES_198(cpu)
    elif opcode == 0x199:
        return RES_199(cpu)
    elif opcode == 0x19a:
        return RES_19a(cpu)
    elif opcode == 0x19b:
        return RES_19b(cpu)
    elif opcode == 0x19c:
        return RES_19c(cpu)
    elif opcode == 0x19d:
        return RES_19d(cpu)
    elif opcode == 0x19e:
        return RES_19e(cpu)
    elif opcode == 0x19f:
        return RES_19f(cpu)
    elif opcode == 0x1a0:
        return RES_1a0(cpu)
    elif opcode == 0x1a1:
        return RES_1a1(cpu)
    elif opcode == 0x1a2:
        return RES_1a2(cpu)
    elif opcode == 0x1a3:
        return RES_1a3(cpu)
    elif opcode == 0x1a4:
        return RES_1a4(cpu)
    elif opcode == 0x1a5:
        return RES_1a5(cpu)
    elif opcode == 0x1a6:
        return RES_1a6(cpu)
    elif opcode == 0x1a7:
        return RES_1a7(cpu)
    elif opcode == 0x1a8:
        return RES_1a8(cpu)
    elif opcode == 0x1a9:
        return RES_1a9(cpu)
    elif opcode == 0x1aa:
        return RES_1aa(cpu)
    elif opcode == 0x1ab:
        return RES_1ab(cpu)
    elif opcode == 0x1ac:
        return RES_1ac(cpu)
    elif opcode == 0x1ad:
        return RES_1ad(cpu)
    elif opcode == 0x1ae:
        return RES_1ae(cpu)
    elif opcode == 0x1af:
        return RES_1af(cpu)
    elif opcode == 0x1b0:
        return RES_1b0(cpu)
    elif opcode == 0x1b1:
        return RES_1b1(cpu)
    elif opcode == 0x1b2:
        return RES_1b2(cpu)
    elif opcode == 0x1b3:
        return RES_1b3(cpu)
    elif opcode == 0x1b4:
        return RES_1b4(cpu)
    elif opcode == 0x1b5:
        return RES_1b5(cpu)
    elif opcode == 0x1b6:
        return RES_1b6(cpu)
    elif opcode == 0x1b7:
        return RES_1b7(cpu)
    elif opcode == 0x1b8:
        return RES_1b8(cpu)
    elif opcode == 0x1b9:
        return RES_1b9(cpu)
    elif opcode == 0x1ba:
        return RES_1ba(cpu)
    elif opcode == 0x1bb:
        return RES_1bb(cpu)
    elif opcode == 0x1bc:
        return RES_1bc(cpu)
    elif opcode == 0x1bd:
        return RES_1bd(cpu)
    elif opcode == 0x1be:
        return RES_1be(cpu)
    elif opcode == 0x1bf:
        return RES_1bf(cpu)
    elif opcode == 0x1c0:
        return SET_1c0(cpu)
    elif opcode == 0x1c1:
        return SET_1c1(cpu)
    elif opcode == 0x1c2:
        return SET_1c2(cpu)
    elif opcode == 0x1c3:
        return SET_1c3(cpu)
    elif opcode == 0x1c4:
        return SET_1c4(cpu)
    elif opcode == 0x1c5:
        return SET_1c5(cpu)
    elif opcode == 0x1c6:
        return SET_1c6(cpu)
    elif opcode == 0x1c7:
        return SET_1c7(cpu)
    elif opcode == 0x1c8:
        return SET_1c8(cpu)
    elif opcode == 0x1c9:
        return SET_1c9(cpu)
    elif opcode == 0x1ca:
        return SET_1ca(cpu)
    elif opcode == 0x1cb:
        return SET_1cb(cpu)
    elif opcode == 0x1cc:
        return SET_1cc(cpu)
    elif opcode == 0x1cd:
        return SET_1cd(cpu)
    elif opcode == 0x1ce:
        return SET_1ce(cpu)
    elif opcode == 0x1cf:
        return SET_1cf(cpu)
    elif opcode == 0x1d0:
        return SET_1d0(cpu)
    elif opcode == 0x1d1:
        return SET_1d1(cpu)
    elif opcode == 0x1d2:
        return SET_1d2(cpu)
    elif opcode == 0x1d3:
        return SET_1d3(cpu)
    elif opcode == 0x1d4:
        return SET_1d4(cpu)
    elif opcode == 0x1d5:
        return SET_1d5(cpu)
    elif opcode == 0x1d6:
        return SET_1d6(cpu)
    elif opcode == 0x1d7:
        return SET_1d7(cpu)
    elif opcode == 0x1d8:
        return SET_1d8(cpu)
    elif opcode == 0x1d9:
        return SET_1d9(cpu)
    elif opcode == 0x1da:
        return SET_1da(cpu)
    elif opcode == 0x1db:
        return SET_1db(cpu)
    elif opcode == 0x1dc:
        return SET_1dc(cpu)
    elif opcode == 0x1dd:
        return SET_1dd(cpu)
    elif opcode == 0x1de:
        return SET_1de(cpu)
    elif opcode == 0x1df:
        return SET_1df(cpu)
    elif opcode == 0x1e0:
        return SET_1e0(cpu)
    elif opcode == 0x1e1:
        return SET_1e1(cpu)
    elif opcode == 0x1e2:
        return SET_1e2(cpu)
    elif opcode == 0x1e3:
        return SET_1e3(cpu)
    elif opcode == 0x1e4:
        return SET_1e4(cpu)
    elif opcode == 0x1e5:
        return SET_1e5(cpu)
    elif opcode == 0x1e6:
        return SET_1e6(cpu)
    elif opcode == 0x1e7:
        return SET_1e7(cpu)
    elif opcode == 0x1e8:
        return SET_1e8(cpu)
    elif opcode == 0x1e9:
        return SET_1e9(cpu)
    elif opcode == 0x1ea:
        return SET_1ea(cpu)
    elif opcode == 0x1eb:
        return SET_1eb(cpu)
    elif opcode == 0x1ec:
        return SET_1ec(cpu)
    elif opcode == 0x1ed:
        return SET_1ed(cpu)
    elif opcode == 0x1ee:
        return SET_1ee(cpu)
    elif opcode == 0x1ef:
        return SET_1ef(cpu)
    elif opcode == 0x1f0:
        return SET_1f0(cpu)
    elif opcode == 0x1f1:
        return SET_1f1(cpu)
    elif opcode == 0x1f2:
        return SET_1f2(cpu)
    elif opcode == 0x1f3:
        return SET_1f3(cpu)
    elif opcode == 0x1f4:
        return SET_1f4(cpu)
    elif opcode == 0x1f5:
        return SET_1f5(cpu)
    elif opcode == 0x1f6:
        return SET_1f6(cpu)
    elif opcode == 0x1f7:
        return SET_1f7(cpu)
    elif opcode == 0x1f8:
        return SET_1f8(cpu)
    elif opcode == 0x1f9:
        return SET_1f9(cpu)
    elif opcode == 0x1fa:
        return SET_1fa(cpu)
    elif opcode == 0x1fb:
        return SET_1fb(cpu)
    elif opcode == 0x1fc:
        return SET_1fc(cpu)
    elif opcode == 0x1fd:
        return SET_1fd(cpu)
    elif opcode == 0x1fe:
        return SET_1fe(cpu)
    elif opcode == 0x1ff:
        return SET_1ff(cpu)


opcodeLengths = np.asarray([
    1, 3, 1, 1, 1, 1, 2, 1, 3, 1, 1, 1, 1, 1, 2, 1,
    2, 3, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1,
    2, 3, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1,
    2, 3, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 3, 3, 3, 1, 2, 1, 1, 1, 3, 1, 3, 3, 2, 1,
    1, 1, 3, 0, 3, 1, 2, 1, 1, 1, 3, 0, 3, 0, 2, 1,
    2, 1, 1, 0, 0, 1, 2, 1, 2, 1, 3, 0, 0, 0, 2, 1,
    2, 1, 1, 1, 0, 1, 2, 1, 2, 1, 3, 1, 0, 0, 2, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    ], dtype=np.uint8)

