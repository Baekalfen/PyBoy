
# THIS FILE IS AUTO-GENERATED!!!
# DO NOT MODIFY THIS FILE.
# CHANGES TO THE CODE SHOULD BE MADE IN 'opcodes_gen.py'.

import logging
import array

logger = logging.getLogger(__name__)

FLAGC, FLAGH, FLAGN, FLAGZ = range(4, 8)


def NOP_00(cpu): # 00 NOP
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_01(cpu): # 01 LD BC,d16
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    cpu.set_bc(v)
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    return 12


def LD_02(cpu): # 02 LD (BC),A
    cpu.mb.setitem(((cpu.B << 8) + cpu.C), cpu.A)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def INC_03(cpu): # 03 INC BC
    t = ((cpu.B << 8) + cpu.C) + 1
    # No flag operations
    t &= 0xFFFF
    cpu.set_bc(t)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def INC_04(cpu): # 04 INC B
    t = cpu.B + 1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.B & 0xF) + (1 & 0xF)) > 0xF) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def DEC_05(cpu): # 05 DEC B
    t = cpu.B - 1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.B & 0xF) - (1 & 0xF)) < 0) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_06(cpu): # 06 LD B,d8
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.B = v
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RLCA_07(cpu): # 07 RLCA
    t = (cpu.A << 1) + (cpu.A >> 7)
    flag = 0b00000000
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_08(cpu): # 08 LD (a16),SP
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    cpu.mb.setitem(v, cpu.SP & 0xFF)
    cpu.mb.setitem(v+1, cpu.SP >> 8)
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    return 20


def ADD_09(cpu): # 09 ADD HL,BC
    t = cpu.HL + ((cpu.B << 8) + cpu.C)
    flag = 0b00000000
    flag += (((cpu.HL & 0xFFF) + (((cpu.B << 8) + cpu.C) & 0xFFF)) > 0xFFF) << FLAGH
    flag += (t > 0xFFFF) << FLAGC
    cpu.F &= 0b10000000
    cpu.F |= flag
    t &= 0xFFFF
    cpu.HL = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_0A(cpu): # 0A LD A,(BC)
    cpu.A = cpu.mb.getitem(((cpu.B << 8) + cpu.C))
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def DEC_0B(cpu): # 0B DEC BC
    t = ((cpu.B << 8) + cpu.C) - 1
    # No flag operations
    t &= 0xFFFF
    cpu.set_bc(t)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def INC_0C(cpu): # 0C INC C
    t = cpu.C + 1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.C & 0xF) + (1 & 0xF)) > 0xF) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def DEC_0D(cpu): # 0D DEC C
    t = cpu.C - 1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.C & 0xF) - (1 & 0xF)) < 0) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_0E(cpu): # 0E LD C,d8
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.C = v
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RRCA_0F(cpu): # 0F RRCA
    t = (cpu.A >> 1) + ((cpu.A & 1) << 7) + ((cpu.A & 1) << 8)
    flag = 0b00000000
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def STOP_10(cpu): # 10 STOP 0
    if cpu.mb.cgb:
        cpu.mb.switch_speed()
        cpu.mb.setitem(0xFF04, 0)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 4


def LD_11(cpu): # 11 LD DE,d16
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    cpu.set_de(v)
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    return 12


def LD_12(cpu): # 12 LD (DE),A
    cpu.mb.setitem(((cpu.D << 8) + cpu.E), cpu.A)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def INC_13(cpu): # 13 INC DE
    t = ((cpu.D << 8) + cpu.E) + 1
    # No flag operations
    t &= 0xFFFF
    cpu.set_de(t)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def INC_14(cpu): # 14 INC D
    t = cpu.D + 1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.D & 0xF) + (1 & 0xF)) > 0xF) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def DEC_15(cpu): # 15 DEC D
    t = cpu.D - 1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.D & 0xF) - (1 & 0xF)) < 0) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_16(cpu): # 16 LD D,d8
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.D = v
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RLA_17(cpu): # 17 RLA
    t = (cpu.A << 1) + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def JR_18(cpu): # 18 JR r8
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.PC += 2 + ((v ^ 0x80) - 0x80)
    cpu.PC &= 0xFFFF
    return 12


def ADD_19(cpu): # 19 ADD HL,DE
    t = cpu.HL + ((cpu.D << 8) + cpu.E)
    flag = 0b00000000
    flag += (((cpu.HL & 0xFFF) + (((cpu.D << 8) + cpu.E) & 0xFFF)) > 0xFFF) << FLAGH
    flag += (t > 0xFFFF) << FLAGC
    cpu.F &= 0b10000000
    cpu.F |= flag
    t &= 0xFFFF
    cpu.HL = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_1A(cpu): # 1A LD A,(DE)
    cpu.A = cpu.mb.getitem(((cpu.D << 8) + cpu.E))
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def DEC_1B(cpu): # 1B DEC DE
    t = ((cpu.D << 8) + cpu.E) - 1
    # No flag operations
    t &= 0xFFFF
    cpu.set_de(t)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def INC_1C(cpu): # 1C INC E
    t = cpu.E + 1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.E & 0xF) + (1 & 0xF)) > 0xF) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def DEC_1D(cpu): # 1D DEC E
    t = cpu.E - 1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.E & 0xF) - (1 & 0xF)) < 0) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_1E(cpu): # 1E LD E,d8
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.E = v
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RRA_1F(cpu): # 1F RRA
    t = (cpu.A >> 1) + (((cpu.F & (1 << FLAGC)) != 0) << 7) + ((cpu.A & 1) << 8)
    flag = 0b00000000
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def JR_20(cpu): # 20 JR NZ,r8
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.PC += 2
    if ((cpu.F & (1 << FLAGZ)) == 0):
        cpu.PC += ((v ^ 0x80) - 0x80)
        cpu.PC &= 0xFFFF
        return 12
    else:
        cpu.PC &= 0xFFFF
        return 8


def LD_21(cpu): # 21 LD HL,d16
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    cpu.HL = v
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    return 12


def LD_22(cpu): # 22 LD (HL+),A
    cpu.mb.setitem(cpu.HL, cpu.A)
    cpu.HL += 1
    cpu.HL &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def INC_23(cpu): # 23 INC HL
    t = cpu.HL + 1
    # No flag operations
    t &= 0xFFFF
    cpu.HL = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def INC_24(cpu): # 24 INC H
    t = (cpu.HL >> 8) + 1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += ((((cpu.HL >> 8) & 0xF) + (1 & 0xF)) > 0xF) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def DEC_25(cpu): # 25 DEC H
    t = (cpu.HL >> 8) - 1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += ((((cpu.HL >> 8) & 0xF) - (1 & 0xF)) < 0) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_26(cpu): # 26 LD H,d8
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.HL = (cpu.HL & 0x00FF) | (v << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def DAA_27(cpu): # 27 DAA
    t = cpu.A
    corr = 0
    corr |= 0x06 if ((cpu.F & (1 << FLAGH)) != 0) else 0x00
    corr |= 0x60 if ((cpu.F & (1 << FLAGC)) != 0) else 0x00
    if (cpu.F & (1 << FLAGN)) != 0:
        t -= corr
    else:
        corr |= 0x06 if (t & 0x0F) > 0x09 else 0x00
        corr |= 0x60 if t > 0x99 else 0x00
        t += corr
    flag = 0
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (corr & 0x60 != 0) << FLAGC
    cpu.F &= 0b01000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def JR_28(cpu): # 28 JR Z,r8
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.PC += 2
    if ((cpu.F & (1 << FLAGZ)) != 0):
        cpu.PC += ((v ^ 0x80) - 0x80)
        cpu.PC &= 0xFFFF
        return 12
    else:
        cpu.PC &= 0xFFFF
        return 8


def ADD_29(cpu): # 29 ADD HL,HL
    t = cpu.HL + cpu.HL
    flag = 0b00000000
    flag += (((cpu.HL & 0xFFF) + (cpu.HL & 0xFFF)) > 0xFFF) << FLAGH
    flag += (t > 0xFFFF) << FLAGC
    cpu.F &= 0b10000000
    cpu.F |= flag
    t &= 0xFFFF
    cpu.HL = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_2A(cpu): # 2A LD A,(HL+)
    cpu.A = cpu.mb.getitem(cpu.HL)
    cpu.HL += 1
    cpu.HL &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def DEC_2B(cpu): # 2B DEC HL
    t = cpu.HL - 1
    # No flag operations
    t &= 0xFFFF
    cpu.HL = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def INC_2C(cpu): # 2C INC L
    t = (cpu.HL & 0xFF) + 1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += ((((cpu.HL & 0xFF) & 0xF) + (1 & 0xF)) > 0xF) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def DEC_2D(cpu): # 2D DEC L
    t = (cpu.HL & 0xFF) - 1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += ((((cpu.HL & 0xFF) & 0xF) - (1 & 0xF)) < 0) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_2E(cpu): # 2E LD L,d8
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.HL = (cpu.HL & 0xFF00) | (v & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def CPL_2F(cpu): # 2F CPL
    cpu.A = (~cpu.A) & 0xFF
    flag = 0b01100000
    cpu.F &= 0b10010000
    cpu.F |= flag
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def JR_30(cpu): # 30 JR NC,r8
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.PC += 2
    if ((cpu.F & (1 << FLAGC)) == 0):
        cpu.PC += ((v ^ 0x80) - 0x80)
        cpu.PC &= 0xFFFF
        return 12
    else:
        cpu.PC &= 0xFFFF
        return 8


def LD_31(cpu): # 31 LD SP,d16
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    cpu.SP = v
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    return 12


def LD_32(cpu): # 32 LD (HL-),A
    cpu.mb.setitem(cpu.HL, cpu.A)
    cpu.HL -= 1
    cpu.HL &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def INC_33(cpu): # 33 INC SP
    t = cpu.SP + 1
    # No flag operations
    t &= 0xFFFF
    cpu.SP = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def INC_34(cpu): # 34 INC (HL)
    t = cpu.mb.getitem(cpu.HL) + 1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.mb.getitem(cpu.HL) & 0xF) + (1 & 0xF)) > 0xF) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 12


def DEC_35(cpu): # 35 DEC (HL)
    t = cpu.mb.getitem(cpu.HL) - 1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.mb.getitem(cpu.HL) & 0xF) - (1 & 0xF)) < 0) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 12


def LD_36(cpu): # 36 LD (HL),d8
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.mb.setitem(cpu.HL, v)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 12


def SCF_37(cpu): # 37 SCF
    flag = 0b00010000
    cpu.F &= 0b10000000
    cpu.F |= flag
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def JR_38(cpu): # 38 JR C,r8
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.PC += 2
    if ((cpu.F & (1 << FLAGC)) != 0):
        cpu.PC += ((v ^ 0x80) - 0x80)
        cpu.PC &= 0xFFFF
        return 12
    else:
        cpu.PC &= 0xFFFF
        return 8


def ADD_39(cpu): # 39 ADD HL,SP
    t = cpu.HL + cpu.SP
    flag = 0b00000000
    flag += (((cpu.HL & 0xFFF) + (cpu.SP & 0xFFF)) > 0xFFF) << FLAGH
    flag += (t > 0xFFFF) << FLAGC
    cpu.F &= 0b10000000
    cpu.F |= flag
    t &= 0xFFFF
    cpu.HL = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_3A(cpu): # 3A LD A,(HL-)
    cpu.A = cpu.mb.getitem(cpu.HL)
    cpu.HL -= 1
    cpu.HL &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def DEC_3B(cpu): # 3B DEC SP
    t = cpu.SP - 1
    # No flag operations
    t &= 0xFFFF
    cpu.SP = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def INC_3C(cpu): # 3C INC A
    t = cpu.A + 1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (1 & 0xF)) > 0xF) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def DEC_3D(cpu): # 3D DEC A
    t = cpu.A - 1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (1 & 0xF)) < 0) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_3E(cpu): # 3E LD A,d8
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.A = v
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def CCF_3F(cpu): # 3F CCF
    flag = (cpu.F & 0b00010000) ^ 0b00010000
    cpu.F &= 0b10000000
    cpu.F |= flag
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_40(cpu): # 40 LD B,B
    cpu.B = cpu.B
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_41(cpu): # 41 LD B,C
    cpu.B = cpu.C
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_42(cpu): # 42 LD B,D
    cpu.B = cpu.D
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_43(cpu): # 43 LD B,E
    cpu.B = cpu.E
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_44(cpu): # 44 LD B,H
    cpu.B = (cpu.HL >> 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_45(cpu): # 45 LD B,L
    cpu.B = (cpu.HL & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_46(cpu): # 46 LD B,(HL)
    cpu.B = cpu.mb.getitem(cpu.HL)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_47(cpu): # 47 LD B,A
    cpu.B = cpu.A
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_48(cpu): # 48 LD C,B
    cpu.C = cpu.B
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_49(cpu): # 49 LD C,C
    cpu.C = cpu.C
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_4A(cpu): # 4A LD C,D
    cpu.C = cpu.D
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_4B(cpu): # 4B LD C,E
    cpu.C = cpu.E
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_4C(cpu): # 4C LD C,H
    cpu.C = (cpu.HL >> 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_4D(cpu): # 4D LD C,L
    cpu.C = (cpu.HL & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_4E(cpu): # 4E LD C,(HL)
    cpu.C = cpu.mb.getitem(cpu.HL)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_4F(cpu): # 4F LD C,A
    cpu.C = cpu.A
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_50(cpu): # 50 LD D,B
    cpu.D = cpu.B
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_51(cpu): # 51 LD D,C
    cpu.D = cpu.C
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_52(cpu): # 52 LD D,D
    cpu.D = cpu.D
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_53(cpu): # 53 LD D,E
    cpu.D = cpu.E
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_54(cpu): # 54 LD D,H
    cpu.D = (cpu.HL >> 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_55(cpu): # 55 LD D,L
    cpu.D = (cpu.HL & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_56(cpu): # 56 LD D,(HL)
    cpu.D = cpu.mb.getitem(cpu.HL)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_57(cpu): # 57 LD D,A
    cpu.D = cpu.A
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_58(cpu): # 58 LD E,B
    cpu.E = cpu.B
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_59(cpu): # 59 LD E,C
    cpu.E = cpu.C
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_5A(cpu): # 5A LD E,D
    cpu.E = cpu.D
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_5B(cpu): # 5B LD E,E
    cpu.E = cpu.E
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_5C(cpu): # 5C LD E,H
    cpu.E = (cpu.HL >> 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_5D(cpu): # 5D LD E,L
    cpu.E = (cpu.HL & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_5E(cpu): # 5E LD E,(HL)
    cpu.E = cpu.mb.getitem(cpu.HL)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_5F(cpu): # 5F LD E,A
    cpu.E = cpu.A
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_60(cpu): # 60 LD H,B
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.B << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_61(cpu): # 61 LD H,C
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.C << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_62(cpu): # 62 LD H,D
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.D << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_63(cpu): # 63 LD H,E
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.E << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_64(cpu): # 64 LD H,H
    cpu.HL = (cpu.HL & 0x00FF) | ((cpu.HL >> 8) << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_65(cpu): # 65 LD H,L
    cpu.HL = (cpu.HL & 0x00FF) | ((cpu.HL & 0xFF) << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_66(cpu): # 66 LD H,(HL)
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.mb.getitem(cpu.HL) << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_67(cpu): # 67 LD H,A
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.A << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_68(cpu): # 68 LD L,B
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.B & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_69(cpu): # 69 LD L,C
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.C & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_6A(cpu): # 6A LD L,D
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.D & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_6B(cpu): # 6B LD L,E
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.E & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_6C(cpu): # 6C LD L,H
    cpu.HL = (cpu.HL & 0xFF00) | ((cpu.HL >> 8) & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_6D(cpu): # 6D LD L,L
    cpu.HL = (cpu.HL & 0xFF00) | ((cpu.HL & 0xFF) & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_6E(cpu): # 6E LD L,(HL)
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.mb.getitem(cpu.HL) & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_6F(cpu): # 6F LD L,A
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.A & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_70(cpu): # 70 LD (HL),B
    cpu.mb.setitem(cpu.HL, cpu.B)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_71(cpu): # 71 LD (HL),C
    cpu.mb.setitem(cpu.HL, cpu.C)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_72(cpu): # 72 LD (HL),D
    cpu.mb.setitem(cpu.HL, cpu.D)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_73(cpu): # 73 LD (HL),E
    cpu.mb.setitem(cpu.HL, cpu.E)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_74(cpu): # 74 LD (HL),H
    cpu.mb.setitem(cpu.HL, (cpu.HL >> 8))
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_75(cpu): # 75 LD (HL),L
    cpu.mb.setitem(cpu.HL, (cpu.HL & 0xFF))
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def HALT_76(cpu): # 76 HALT
    cpu.halted = True
    return 4


def LD_77(cpu): # 77 LD (HL),A
    cpu.mb.setitem(cpu.HL, cpu.A)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_78(cpu): # 78 LD A,B
    cpu.A = cpu.B
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_79(cpu): # 79 LD A,C
    cpu.A = cpu.C
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_7A(cpu): # 7A LD A,D
    cpu.A = cpu.D
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_7B(cpu): # 7B LD A,E
    cpu.A = cpu.E
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_7C(cpu): # 7C LD A,H
    cpu.A = (cpu.HL >> 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_7D(cpu): # 7D LD A,L
    cpu.A = (cpu.HL & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def LD_7E(cpu): # 7E LD A,(HL)
    cpu.A = cpu.mb.getitem(cpu.HL)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_7F(cpu): # 7F LD A,A
    cpu.A = cpu.A
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def ADD_80(cpu): # 80 ADD A,B
    t = cpu.A + cpu.B
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (cpu.B & 0xF)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def ADD_81(cpu): # 81 ADD A,C
    t = cpu.A + cpu.C
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (cpu.C & 0xF)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def ADD_82(cpu): # 82 ADD A,D
    t = cpu.A + cpu.D
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (cpu.D & 0xF)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def ADD_83(cpu): # 83 ADD A,E
    t = cpu.A + cpu.E
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (cpu.E & 0xF)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def ADD_84(cpu): # 84 ADD A,H
    t = cpu.A + (cpu.HL >> 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + ((cpu.HL >> 8) & 0xF)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def ADD_85(cpu): # 85 ADD A,L
    t = cpu.A + (cpu.HL & 0xFF)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + ((cpu.HL & 0xFF) & 0xF)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def ADD_86(cpu): # 86 ADD A,(HL)
    t = cpu.A + cpu.mb.getitem(cpu.HL)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (cpu.mb.getitem(cpu.HL) & 0xF)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def ADD_87(cpu): # 87 ADD A,A
    t = cpu.A + cpu.A
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (cpu.A & 0xF)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def ADC_88(cpu): # 88 ADC A,B
    t = cpu.A + cpu.B + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (cpu.B & 0xF) + ((cpu.F & (1 << FLAGC)) != 0)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def ADC_89(cpu): # 89 ADC A,C
    t = cpu.A + cpu.C + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (cpu.C & 0xF) + ((cpu.F & (1 << FLAGC)) != 0)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def ADC_8A(cpu): # 8A ADC A,D
    t = cpu.A + cpu.D + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (cpu.D & 0xF) + ((cpu.F & (1 << FLAGC)) != 0)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def ADC_8B(cpu): # 8B ADC A,E
    t = cpu.A + cpu.E + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (cpu.E & 0xF) + ((cpu.F & (1 << FLAGC)) != 0)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def ADC_8C(cpu): # 8C ADC A,H
    t = cpu.A + (cpu.HL >> 8) + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + ((cpu.HL >> 8) & 0xF) + ((cpu.F & (1 << FLAGC)) != 0)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def ADC_8D(cpu): # 8D ADC A,L
    t = cpu.A + (cpu.HL & 0xFF) + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + ((cpu.HL & 0xFF) & 0xF) + ((cpu.F & (1 << FLAGC)) != 0)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def ADC_8E(cpu): # 8E ADC A,(HL)
    t = cpu.A + cpu.mb.getitem(cpu.HL) + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (cpu.mb.getitem(cpu.HL) & 0xF) + ((cpu.F & (1 << FLAGC)) != 0)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def ADC_8F(cpu): # 8F ADC A,A
    t = cpu.A + cpu.A + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (cpu.A & 0xF) + ((cpu.F & (1 << FLAGC)) != 0)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def SUB_90(cpu): # 90 SUB B
    t = cpu.A - cpu.B
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.B & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def SUB_91(cpu): # 91 SUB C
    t = cpu.A - cpu.C
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.C & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def SUB_92(cpu): # 92 SUB D
    t = cpu.A - cpu.D
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.D & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def SUB_93(cpu): # 93 SUB E
    t = cpu.A - cpu.E
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.E & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def SUB_94(cpu): # 94 SUB H
    t = cpu.A - (cpu.HL >> 8)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - ((cpu.HL >> 8) & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def SUB_95(cpu): # 95 SUB L
    t = cpu.A - (cpu.HL & 0xFF)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - ((cpu.HL & 0xFF) & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def SUB_96(cpu): # 96 SUB (HL)
    t = cpu.A - cpu.mb.getitem(cpu.HL)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.mb.getitem(cpu.HL) & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def SUB_97(cpu): # 97 SUB A
    t = cpu.A - cpu.A
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.A & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def SBC_98(cpu): # 98 SBC A,B
    t = cpu.A - cpu.B - ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.B & 0xF) - ((cpu.F & (1 << FLAGC)) != 0)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def SBC_99(cpu): # 99 SBC A,C
    t = cpu.A - cpu.C - ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.C & 0xF) - ((cpu.F & (1 << FLAGC)) != 0)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def SBC_9A(cpu): # 9A SBC A,D
    t = cpu.A - cpu.D - ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.D & 0xF) - ((cpu.F & (1 << FLAGC)) != 0)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def SBC_9B(cpu): # 9B SBC A,E
    t = cpu.A - cpu.E - ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.E & 0xF) - ((cpu.F & (1 << FLAGC)) != 0)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def SBC_9C(cpu): # 9C SBC A,H
    t = cpu.A - (cpu.HL >> 8) - ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - ((cpu.HL >> 8) & 0xF) - ((cpu.F & (1 << FLAGC)) != 0)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def SBC_9D(cpu): # 9D SBC A,L
    t = cpu.A - (cpu.HL & 0xFF) - ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - ((cpu.HL & 0xFF) & 0xF) - ((cpu.F & (1 << FLAGC)) != 0)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def SBC_9E(cpu): # 9E SBC A,(HL)
    t = cpu.A - cpu.mb.getitem(cpu.HL) - ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.mb.getitem(cpu.HL) & 0xF) - ((cpu.F & (1 << FLAGC)) != 0)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def SBC_9F(cpu): # 9F SBC A,A
    t = cpu.A - cpu.A - ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.A & 0xF) - ((cpu.F & (1 << FLAGC)) != 0)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def AND_A0(cpu): # A0 AND B
    t = cpu.A & cpu.B
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def AND_A1(cpu): # A1 AND C
    t = cpu.A & cpu.C
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def AND_A2(cpu): # A2 AND D
    t = cpu.A & cpu.D
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def AND_A3(cpu): # A3 AND E
    t = cpu.A & cpu.E
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def AND_A4(cpu): # A4 AND H
    t = cpu.A & (cpu.HL >> 8)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def AND_A5(cpu): # A5 AND L
    t = cpu.A & (cpu.HL & 0xFF)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def AND_A6(cpu): # A6 AND (HL)
    t = cpu.A & cpu.mb.getitem(cpu.HL)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def AND_A7(cpu): # A7 AND A
    t = cpu.A & cpu.A
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def XOR_A8(cpu): # A8 XOR B
    t = cpu.A ^ cpu.B
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def XOR_A9(cpu): # A9 XOR C
    t = cpu.A ^ cpu.C
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def XOR_AA(cpu): # AA XOR D
    t = cpu.A ^ cpu.D
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def XOR_AB(cpu): # AB XOR E
    t = cpu.A ^ cpu.E
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def XOR_AC(cpu): # AC XOR H
    t = cpu.A ^ (cpu.HL >> 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def XOR_AD(cpu): # AD XOR L
    t = cpu.A ^ (cpu.HL & 0xFF)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def XOR_AE(cpu): # AE XOR (HL)
    t = cpu.A ^ cpu.mb.getitem(cpu.HL)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def XOR_AF(cpu): # AF XOR A
    t = cpu.A ^ cpu.A
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def OR_B0(cpu): # B0 OR B
    t = cpu.A | cpu.B
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def OR_B1(cpu): # B1 OR C
    t = cpu.A | cpu.C
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def OR_B2(cpu): # B2 OR D
    t = cpu.A | cpu.D
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def OR_B3(cpu): # B3 OR E
    t = cpu.A | cpu.E
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def OR_B4(cpu): # B4 OR H
    t = cpu.A | (cpu.HL >> 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def OR_B5(cpu): # B5 OR L
    t = cpu.A | (cpu.HL & 0xFF)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def OR_B6(cpu): # B6 OR (HL)
    t = cpu.A | cpu.mb.getitem(cpu.HL)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def OR_B7(cpu): # B7 OR A
    t = cpu.A | cpu.A
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def CP_B8(cpu): # B8 CP B
    t = cpu.A - cpu.B
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.B & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def CP_B9(cpu): # B9 CP C
    t = cpu.A - cpu.C
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.C & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def CP_BA(cpu): # BA CP D
    t = cpu.A - cpu.D
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.D & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def CP_BB(cpu): # BB CP E
    t = cpu.A - cpu.E
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.E & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def CP_BC(cpu): # BC CP H
    t = cpu.A - (cpu.HL >> 8)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - ((cpu.HL >> 8) & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def CP_BD(cpu): # BD CP L
    t = cpu.A - (cpu.HL & 0xFF)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - ((cpu.HL & 0xFF) & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def CP_BE(cpu): # BE CP (HL)
    t = cpu.A - cpu.mb.getitem(cpu.HL)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.mb.getitem(cpu.HL) & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def CP_BF(cpu): # BF CP A
    t = cpu.A - cpu.A
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (cpu.A & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def RET_C0(cpu): # C0 RET NZ
    if ((cpu.F & (1 << FLAGZ)) == 0):
        cpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High
        cpu.PC |= cpu.mb.getitem(cpu.SP) # Low
        cpu.SP += 2
        cpu.SP &= 0xFFFF
        return 20
    else:
        cpu.PC += 1
        cpu.PC &= 0xFFFF
        return 8


def POP_C1(cpu): # C1 POP BC
    cpu.B = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) # High
    cpu.C = cpu.mb.getitem(cpu.SP) # Low
    cpu.SP += 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 12


def JP_C2(cpu): # C2 JP NZ,a16
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    if ((cpu.F & (1 << FLAGZ)) == 0):
        cpu.PC = v
        return 16
    else:
        cpu.PC += 3
        cpu.PC &= 0xFFFF
        return 12


def JP_C3(cpu): # C3 JP a16
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    cpu.PC = v
    return 16


def CALL_C4(cpu): # C4 CALL NZ,a16
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    if ((cpu.F & (1 << FLAGZ)) == 0):
        cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
        cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
        cpu.SP -= 2
        cpu.SP &= 0xFFFF
        cpu.PC = v
        return 24
    else:
        return 12


def PUSH_C5(cpu): # C5 PUSH BC
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.B) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.C) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 16


def ADD_C6(cpu): # C6 ADD A,d8
    v = cpu.mb.getitem(cpu.PC+1)
    t = cpu.A + v
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (v & 0xF)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RST_C7(cpu): # C7 RST 00H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 0
    return 16


def RET_C8(cpu): # C8 RET Z
    if ((cpu.F & (1 << FLAGZ)) != 0):
        cpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High
        cpu.PC |= cpu.mb.getitem(cpu.SP) # Low
        cpu.SP += 2
        cpu.SP &= 0xFFFF
        return 20
    else:
        cpu.PC += 1
        cpu.PC &= 0xFFFF
        return 8


def RET_C9(cpu): # C9 RET
    cpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High
    cpu.PC |= cpu.mb.getitem(cpu.SP) # Low
    cpu.SP += 2
    cpu.SP &= 0xFFFF
    return 16


def JP_CA(cpu): # CA JP Z,a16
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    if ((cpu.F & (1 << FLAGZ)) != 0):
        cpu.PC = v
        return 16
    else:
        cpu.PC += 3
        cpu.PC &= 0xFFFF
        return 12


def PREFIX_CB(cpu): # CB PREFIX CB
    opcode = cpu.mb.getitem(cpu.PC + 1)
    opcode += 0x100 # Internally shifting look-up table
    return OPCODES[opcode](cpu)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def CALL_CC(cpu): # CC CALL Z,a16
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    if ((cpu.F & (1 << FLAGZ)) != 0):
        cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
        cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
        cpu.SP -= 2
        cpu.SP &= 0xFFFF
        cpu.PC = v
        return 24
    else:
        return 12


def CALL_CD(cpu): # CD CALL a16
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = v
    return 24


def ADC_CE(cpu): # CE ADC A,d8
    v = cpu.mb.getitem(cpu.PC+1)
    t = cpu.A + v + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) + (v & 0xF) + ((cpu.F & (1 << FLAGC)) != 0)) > 0xF) << FLAGH
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RST_CF(cpu): # CF RST 08H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 8
    return 16


def RET_D0(cpu): # D0 RET NC
    if ((cpu.F & (1 << FLAGC)) == 0):
        cpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High
        cpu.PC |= cpu.mb.getitem(cpu.SP) # Low
        cpu.SP += 2
        cpu.SP &= 0xFFFF
        return 20
    else:
        cpu.PC += 1
        cpu.PC &= 0xFFFF
        return 8


def POP_D1(cpu): # D1 POP DE
    cpu.D = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) # High
    cpu.E = cpu.mb.getitem(cpu.SP) # Low
    cpu.SP += 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 12


def JP_D2(cpu): # D2 JP NC,a16
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    if ((cpu.F & (1 << FLAGC)) == 0):
        cpu.PC = v
        return 16
    else:
        cpu.PC += 3
        cpu.PC &= 0xFFFF
        return 12


def CALL_D4(cpu): # D4 CALL NC,a16
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    if ((cpu.F & (1 << FLAGC)) == 0):
        cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
        cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
        cpu.SP -= 2
        cpu.SP &= 0xFFFF
        cpu.PC = v
        return 24
    else:
        return 12


def PUSH_D5(cpu): # D5 PUSH DE
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.D) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.E) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 16


def SUB_D6(cpu): # D6 SUB d8
    v = cpu.mb.getitem(cpu.PC+1)
    t = cpu.A - v
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (v & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RST_D7(cpu): # D7 RST 10H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 16
    return 16


def RET_D8(cpu): # D8 RET C
    if ((cpu.F & (1 << FLAGC)) != 0):
        cpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High
        cpu.PC |= cpu.mb.getitem(cpu.SP) # Low
        cpu.SP += 2
        cpu.SP &= 0xFFFF
        return 20
    else:
        cpu.PC += 1
        cpu.PC &= 0xFFFF
        return 8


def RETI_D9(cpu): # D9 RETI
    cpu.interrupt_master_enable = True
    cpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High
    cpu.PC |= cpu.mb.getitem(cpu.SP) # Low
    cpu.SP += 2
    cpu.SP &= 0xFFFF
    return 16


def JP_DA(cpu): # DA JP C,a16
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    if ((cpu.F & (1 << FLAGC)) != 0):
        cpu.PC = v
        return 16
    else:
        cpu.PC += 3
        cpu.PC &= 0xFFFF
        return 12


def CALL_DC(cpu): # DC CALL C,a16
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    if ((cpu.F & (1 << FLAGC)) != 0):
        cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
        cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
        cpu.SP -= 2
        cpu.SP &= 0xFFFF
        cpu.PC = v
        return 24
    else:
        return 12


def SBC_DE(cpu): # DE SBC A,d8
    v = cpu.mb.getitem(cpu.PC+1)
    t = cpu.A - v - ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (v & 0xF) - ((cpu.F & (1 << FLAGC)) != 0)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RST_DF(cpu): # DF RST 18H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 24
    return 16


def LDH_E0(cpu): # E0 LDH (a8),A
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.mb.setitem(v + 0xFF00, cpu.A)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 12


def POP_E1(cpu): # E1 POP HL
    cpu.HL = (cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8) + cpu.mb.getitem(cpu.SP) # High
    cpu.SP += 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 12


def LD_E2(cpu): # E2 LD (C),A
    cpu.mb.setitem(0xFF00 + cpu.C, cpu.A)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def PUSH_E5(cpu): # E5 PUSH HL
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.HL >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.HL & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 16


def AND_E6(cpu): # E6 AND d8
    v = cpu.mb.getitem(cpu.PC+1)
    t = cpu.A & v
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RST_E7(cpu): # E7 RST 20H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 32
    return 16


def ADD_E8(cpu): # E8 ADD SP,r8
    v = cpu.mb.getitem(cpu.PC+1)
    t = cpu.SP + ((v ^ 0x80) - 0x80)
    flag = 0b00000000
    flag += (((cpu.SP & 0xF) + (v & 0xF)) > 0xF) << FLAGH
    flag += (((cpu.SP & 0xFF) + (v & 0xFF)) > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFFFF
    cpu.SP = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def JP_E9(cpu): # E9 JP (HL)
    cpu.PC = cpu.HL
    return 4


def LD_EA(cpu): # EA LD (a16),A
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    cpu.mb.setitem(v, cpu.A)
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    return 16


def XOR_EE(cpu): # EE XOR d8
    v = cpu.mb.getitem(cpu.PC+1)
    t = cpu.A ^ v
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RST_EF(cpu): # EF RST 28H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 40
    return 16


def LDH_F0(cpu): # F0 LDH A,(a8)
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.A = cpu.mb.getitem(v + 0xFF00)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 12


def POP_F1(cpu): # F1 POP AF
    cpu.A = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) # High
    cpu.F = cpu.mb.getitem(cpu.SP) & 0xF0 & 0xF0 # Low
    cpu.SP += 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 12


def LD_F2(cpu): # F2 LD A,(C)
    cpu.A = cpu.mb.getitem(0xFF00 + cpu.C)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def DI_F3(cpu): # F3 DI
    cpu.interrupt_master_enable = False
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def PUSH_F5(cpu): # F5 PUSH AF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.A) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.F & 0xF0) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 16


def OR_F6(cpu): # F6 OR d8
    v = cpu.mb.getitem(cpu.PC+1)
    t = cpu.A | v
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RST_F7(cpu): # F7 RST 30H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 48
    return 16


def LD_F8(cpu): # F8 LD HL,SP+r8
    v = cpu.mb.getitem(cpu.PC+1)
    cpu.HL = cpu.SP + ((v ^ 0x80) - 0x80)
    t = cpu.HL
    flag = 0b00000000
    flag += (((cpu.SP & 0xF) + (v & 0xF)) > 0xF) << FLAGH
    flag += (((cpu.SP & 0xFF) + (v & 0xFF)) > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    cpu.HL &= 0xFFFF
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 12


def LD_F9(cpu): # F9 LD SP,HL
    cpu.SP = cpu.HL
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 8


def LD_FA(cpu): # FA LD A,(a16)
    v = (cpu.mb.getitem(cpu.PC+2) << 8) + cpu.mb.getitem(cpu.PC+1)
    cpu.A = cpu.mb.getitem(v)
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    return 16


def EI_FB(cpu): # FB EI
    cpu.interrupt_master_enable = True
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    return 4


def CP_FE(cpu): # FE CP d8
    v = cpu.mb.getitem(cpu.PC+1)
    t = cpu.A - v
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.A & 0xF) - (v & 0xF)) < 0) << FLAGH
    flag += (t < 0) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RST_FF(cpu): # FF RST 38H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 56
    return 16


def RLC_100(cpu): # 100 RLC B
    t = (cpu.B << 1) + (cpu.B >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RLC_101(cpu): # 101 RLC C
    t = (cpu.C << 1) + (cpu.C >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RLC_102(cpu): # 102 RLC D
    t = (cpu.D << 1) + (cpu.D >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RLC_103(cpu): # 103 RLC E
    t = (cpu.E << 1) + (cpu.E >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RLC_104(cpu): # 104 RLC H
    t = ((cpu.HL >> 8) << 1) + ((cpu.HL >> 8) >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RLC_105(cpu): # 105 RLC L
    t = ((cpu.HL & 0xFF) << 1) + ((cpu.HL & 0xFF) >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RLC_106(cpu): # 106 RLC (HL)
    t = (cpu.mb.getitem(cpu.HL) << 1) + (cpu.mb.getitem(cpu.HL) >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def RLC_107(cpu): # 107 RLC A
    t = (cpu.A << 1) + (cpu.A >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RRC_108(cpu): # 108 RRC B
    t = (cpu.B >> 1) + ((cpu.B & 1) << 7) + ((cpu.B & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RRC_109(cpu): # 109 RRC C
    t = (cpu.C >> 1) + ((cpu.C & 1) << 7) + ((cpu.C & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RRC_10A(cpu): # 10A RRC D
    t = (cpu.D >> 1) + ((cpu.D & 1) << 7) + ((cpu.D & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RRC_10B(cpu): # 10B RRC E
    t = (cpu.E >> 1) + ((cpu.E & 1) << 7) + ((cpu.E & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RRC_10C(cpu): # 10C RRC H
    t = ((cpu.HL >> 8) >> 1) + (((cpu.HL >> 8) & 1) << 7) + (((cpu.HL >> 8) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RRC_10D(cpu): # 10D RRC L
    t = ((cpu.HL & 0xFF) >> 1) + (((cpu.HL & 0xFF) & 1) << 7) + (((cpu.HL & 0xFF) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RRC_10E(cpu): # 10E RRC (HL)
    t = (cpu.mb.getitem(cpu.HL) >> 1) + ((cpu.mb.getitem(cpu.HL) & 1) << 7) + ((cpu.mb.getitem(cpu.HL) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def RRC_10F(cpu): # 10F RRC A
    t = (cpu.A >> 1) + ((cpu.A & 1) << 7) + ((cpu.A & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RL_110(cpu): # 110 RL B
    t = (cpu.B << 1) + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RL_111(cpu): # 111 RL C
    t = (cpu.C << 1) + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RL_112(cpu): # 112 RL D
    t = (cpu.D << 1) + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RL_113(cpu): # 113 RL E
    t = (cpu.E << 1) + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RL_114(cpu): # 114 RL H
    t = ((cpu.HL >> 8) << 1) + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RL_115(cpu): # 115 RL L
    t = ((cpu.HL & 0xFF) << 1) + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RL_116(cpu): # 116 RL (HL)
    t = (cpu.mb.getitem(cpu.HL) << 1) + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def RL_117(cpu): # 117 RL A
    t = (cpu.A << 1) + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RR_118(cpu): # 118 RR B
    t = (cpu.B >> 1) + (((cpu.F & (1 << FLAGC)) != 0) << 7) + ((cpu.B & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RR_119(cpu): # 119 RR C
    t = (cpu.C >> 1) + (((cpu.F & (1 << FLAGC)) != 0) << 7) + ((cpu.C & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RR_11A(cpu): # 11A RR D
    t = (cpu.D >> 1) + (((cpu.F & (1 << FLAGC)) != 0) << 7) + ((cpu.D & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RR_11B(cpu): # 11B RR E
    t = (cpu.E >> 1) + (((cpu.F & (1 << FLAGC)) != 0) << 7) + ((cpu.E & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RR_11C(cpu): # 11C RR H
    t = ((cpu.HL >> 8) >> 1) + (((cpu.F & (1 << FLAGC)) != 0) << 7) + (((cpu.HL >> 8) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RR_11D(cpu): # 11D RR L
    t = ((cpu.HL & 0xFF) >> 1) + (((cpu.F & (1 << FLAGC)) != 0) << 7) + (((cpu.HL & 0xFF) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RR_11E(cpu): # 11E RR (HL)
    t = (cpu.mb.getitem(cpu.HL) >> 1) + (((cpu.F & (1 << FLAGC)) != 0) << 7) + ((cpu.mb.getitem(cpu.HL) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def RR_11F(cpu): # 11F RR A
    t = (cpu.A >> 1) + (((cpu.F & (1 << FLAGC)) != 0) << 7) + ((cpu.A & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SLA_120(cpu): # 120 SLA B
    t = (cpu.B << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SLA_121(cpu): # 121 SLA C
    t = (cpu.C << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SLA_122(cpu): # 122 SLA D
    t = (cpu.D << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SLA_123(cpu): # 123 SLA E
    t = (cpu.E << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SLA_124(cpu): # 124 SLA H
    t = ((cpu.HL >> 8) << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SLA_125(cpu): # 125 SLA L
    t = ((cpu.HL & 0xFF) << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SLA_126(cpu): # 126 SLA (HL)
    t = (cpu.mb.getitem(cpu.HL) << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def SLA_127(cpu): # 127 SLA A
    t = (cpu.A << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SRA_128(cpu): # 128 SRA B
    t = ((cpu.B >> 1) | (cpu.B & 0x80)) + ((cpu.B & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SRA_129(cpu): # 129 SRA C
    t = ((cpu.C >> 1) | (cpu.C & 0x80)) + ((cpu.C & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SRA_12A(cpu): # 12A SRA D
    t = ((cpu.D >> 1) | (cpu.D & 0x80)) + ((cpu.D & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SRA_12B(cpu): # 12B SRA E
    t = ((cpu.E >> 1) | (cpu.E & 0x80)) + ((cpu.E & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SRA_12C(cpu): # 12C SRA H
    t = (((cpu.HL >> 8) >> 1) | ((cpu.HL >> 8) & 0x80)) + (((cpu.HL >> 8) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SRA_12D(cpu): # 12D SRA L
    t = (((cpu.HL & 0xFF) >> 1) | ((cpu.HL & 0xFF) & 0x80)) + (((cpu.HL & 0xFF) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SRA_12E(cpu): # 12E SRA (HL)
    t = ((cpu.mb.getitem(cpu.HL) >> 1) | (cpu.mb.getitem(cpu.HL) & 0x80)) + ((cpu.mb.getitem(cpu.HL) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def SRA_12F(cpu): # 12F SRA A
    t = ((cpu.A >> 1) | (cpu.A & 0x80)) + ((cpu.A & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SWAP_130(cpu): # 130 SWAP B
    t = ((cpu.B & 0xF0) >> 4) | ((cpu.B & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SWAP_131(cpu): # 131 SWAP C
    t = ((cpu.C & 0xF0) >> 4) | ((cpu.C & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SWAP_132(cpu): # 132 SWAP D
    t = ((cpu.D & 0xF0) >> 4) | ((cpu.D & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SWAP_133(cpu): # 133 SWAP E
    t = ((cpu.E & 0xF0) >> 4) | ((cpu.E & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SWAP_134(cpu): # 134 SWAP H
    t = (((cpu.HL >> 8) & 0xF0) >> 4) | (((cpu.HL >> 8) & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SWAP_135(cpu): # 135 SWAP L
    t = (((cpu.HL & 0xFF) & 0xF0) >> 4) | (((cpu.HL & 0xFF) & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SWAP_136(cpu): # 136 SWAP (HL)
    t = ((cpu.mb.getitem(cpu.HL) & 0xF0) >> 4) | ((cpu.mb.getitem(cpu.HL) & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def SWAP_137(cpu): # 137 SWAP A
    t = ((cpu.A & 0xF0) >> 4) | ((cpu.A & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SRL_138(cpu): # 138 SRL B
    t = (cpu.B >> 1) + ((cpu.B & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SRL_139(cpu): # 139 SRL C
    t = (cpu.C >> 1) + ((cpu.C & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SRL_13A(cpu): # 13A SRL D
    t = (cpu.D >> 1) + ((cpu.D & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SRL_13B(cpu): # 13B SRL E
    t = (cpu.E >> 1) + ((cpu.E & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SRL_13C(cpu): # 13C SRL H
    t = ((cpu.HL >> 8) >> 1) + (((cpu.HL >> 8) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SRL_13D(cpu): # 13D SRL L
    t = ((cpu.HL & 0xFF) >> 1) + (((cpu.HL & 0xFF) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SRL_13E(cpu): # 13E SRL (HL)
    t = (cpu.mb.getitem(cpu.HL) >> 1) + ((cpu.mb.getitem(cpu.HL) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def SRL_13F(cpu): # 13F SRL A
    t = (cpu.A >> 1) + ((cpu.A & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_140(cpu): # 140 BIT 0,B
    t = cpu.B & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_141(cpu): # 141 BIT 0,C
    t = cpu.C & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_142(cpu): # 142 BIT 0,D
    t = cpu.D & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_143(cpu): # 143 BIT 0,E
    t = cpu.E & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_144(cpu): # 144 BIT 0,H
    t = (cpu.HL >> 8) & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_145(cpu): # 145 BIT 0,L
    t = (cpu.HL & 0xFF) & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_146(cpu): # 146 BIT 0,(HL)
    t = cpu.mb.getitem(cpu.HL) & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def BIT_147(cpu): # 147 BIT 0,A
    t = cpu.A & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_148(cpu): # 148 BIT 1,B
    t = cpu.B & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_149(cpu): # 149 BIT 1,C
    t = cpu.C & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_14A(cpu): # 14A BIT 1,D
    t = cpu.D & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_14B(cpu): # 14B BIT 1,E
    t = cpu.E & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_14C(cpu): # 14C BIT 1,H
    t = (cpu.HL >> 8) & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_14D(cpu): # 14D BIT 1,L
    t = (cpu.HL & 0xFF) & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_14E(cpu): # 14E BIT 1,(HL)
    t = cpu.mb.getitem(cpu.HL) & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def BIT_14F(cpu): # 14F BIT 1,A
    t = cpu.A & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_150(cpu): # 150 BIT 2,B
    t = cpu.B & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_151(cpu): # 151 BIT 2,C
    t = cpu.C & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_152(cpu): # 152 BIT 2,D
    t = cpu.D & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_153(cpu): # 153 BIT 2,E
    t = cpu.E & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_154(cpu): # 154 BIT 2,H
    t = (cpu.HL >> 8) & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_155(cpu): # 155 BIT 2,L
    t = (cpu.HL & 0xFF) & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_156(cpu): # 156 BIT 2,(HL)
    t = cpu.mb.getitem(cpu.HL) & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def BIT_157(cpu): # 157 BIT 2,A
    t = cpu.A & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_158(cpu): # 158 BIT 3,B
    t = cpu.B & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_159(cpu): # 159 BIT 3,C
    t = cpu.C & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_15A(cpu): # 15A BIT 3,D
    t = cpu.D & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_15B(cpu): # 15B BIT 3,E
    t = cpu.E & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_15C(cpu): # 15C BIT 3,H
    t = (cpu.HL >> 8) & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_15D(cpu): # 15D BIT 3,L
    t = (cpu.HL & 0xFF) & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_15E(cpu): # 15E BIT 3,(HL)
    t = cpu.mb.getitem(cpu.HL) & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def BIT_15F(cpu): # 15F BIT 3,A
    t = cpu.A & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_160(cpu): # 160 BIT 4,B
    t = cpu.B & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_161(cpu): # 161 BIT 4,C
    t = cpu.C & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_162(cpu): # 162 BIT 4,D
    t = cpu.D & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_163(cpu): # 163 BIT 4,E
    t = cpu.E & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_164(cpu): # 164 BIT 4,H
    t = (cpu.HL >> 8) & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_165(cpu): # 165 BIT 4,L
    t = (cpu.HL & 0xFF) & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_166(cpu): # 166 BIT 4,(HL)
    t = cpu.mb.getitem(cpu.HL) & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def BIT_167(cpu): # 167 BIT 4,A
    t = cpu.A & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_168(cpu): # 168 BIT 5,B
    t = cpu.B & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_169(cpu): # 169 BIT 5,C
    t = cpu.C & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_16A(cpu): # 16A BIT 5,D
    t = cpu.D & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_16B(cpu): # 16B BIT 5,E
    t = cpu.E & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_16C(cpu): # 16C BIT 5,H
    t = (cpu.HL >> 8) & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_16D(cpu): # 16D BIT 5,L
    t = (cpu.HL & 0xFF) & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_16E(cpu): # 16E BIT 5,(HL)
    t = cpu.mb.getitem(cpu.HL) & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def BIT_16F(cpu): # 16F BIT 5,A
    t = cpu.A & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_170(cpu): # 170 BIT 6,B
    t = cpu.B & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_171(cpu): # 171 BIT 6,C
    t = cpu.C & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_172(cpu): # 172 BIT 6,D
    t = cpu.D & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_173(cpu): # 173 BIT 6,E
    t = cpu.E & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_174(cpu): # 174 BIT 6,H
    t = (cpu.HL >> 8) & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_175(cpu): # 175 BIT 6,L
    t = (cpu.HL & 0xFF) & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_176(cpu): # 176 BIT 6,(HL)
    t = cpu.mb.getitem(cpu.HL) & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def BIT_177(cpu): # 177 BIT 6,A
    t = cpu.A & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_178(cpu): # 178 BIT 7,B
    t = cpu.B & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_179(cpu): # 179 BIT 7,C
    t = cpu.C & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_17A(cpu): # 17A BIT 7,D
    t = cpu.D & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_17B(cpu): # 17B BIT 7,E
    t = cpu.E & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_17C(cpu): # 17C BIT 7,H
    t = (cpu.HL >> 8) & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_17D(cpu): # 17D BIT 7,L
    t = (cpu.HL & 0xFF) & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def BIT_17E(cpu): # 17E BIT 7,(HL)
    t = cpu.mb.getitem(cpu.HL) & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def BIT_17F(cpu): # 17F BIT 7,A
    t = cpu.A & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_180(cpu): # 180 RES 0,B
    t = cpu.B & ~(1 << 0)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_181(cpu): # 181 RES 0,C
    t = cpu.C & ~(1 << 0)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_182(cpu): # 182 RES 0,D
    t = cpu.D & ~(1 << 0)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_183(cpu): # 183 RES 0,E
    t = cpu.E & ~(1 << 0)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_184(cpu): # 184 RES 0,H
    t = (cpu.HL >> 8) & ~(1 << 0)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_185(cpu): # 185 RES 0,L
    t = (cpu.HL & 0xFF) & ~(1 << 0)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_186(cpu): # 186 RES 0,(HL)
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 0)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def RES_187(cpu): # 187 RES 0,A
    t = cpu.A & ~(1 << 0)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_188(cpu): # 188 RES 1,B
    t = cpu.B & ~(1 << 1)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_189(cpu): # 189 RES 1,C
    t = cpu.C & ~(1 << 1)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_18A(cpu): # 18A RES 1,D
    t = cpu.D & ~(1 << 1)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_18B(cpu): # 18B RES 1,E
    t = cpu.E & ~(1 << 1)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_18C(cpu): # 18C RES 1,H
    t = (cpu.HL >> 8) & ~(1 << 1)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_18D(cpu): # 18D RES 1,L
    t = (cpu.HL & 0xFF) & ~(1 << 1)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_18E(cpu): # 18E RES 1,(HL)
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 1)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def RES_18F(cpu): # 18F RES 1,A
    t = cpu.A & ~(1 << 1)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_190(cpu): # 190 RES 2,B
    t = cpu.B & ~(1 << 2)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_191(cpu): # 191 RES 2,C
    t = cpu.C & ~(1 << 2)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_192(cpu): # 192 RES 2,D
    t = cpu.D & ~(1 << 2)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_193(cpu): # 193 RES 2,E
    t = cpu.E & ~(1 << 2)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_194(cpu): # 194 RES 2,H
    t = (cpu.HL >> 8) & ~(1 << 2)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_195(cpu): # 195 RES 2,L
    t = (cpu.HL & 0xFF) & ~(1 << 2)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_196(cpu): # 196 RES 2,(HL)
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 2)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def RES_197(cpu): # 197 RES 2,A
    t = cpu.A & ~(1 << 2)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_198(cpu): # 198 RES 3,B
    t = cpu.B & ~(1 << 3)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_199(cpu): # 199 RES 3,C
    t = cpu.C & ~(1 << 3)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_19A(cpu): # 19A RES 3,D
    t = cpu.D & ~(1 << 3)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_19B(cpu): # 19B RES 3,E
    t = cpu.E & ~(1 << 3)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_19C(cpu): # 19C RES 3,H
    t = (cpu.HL >> 8) & ~(1 << 3)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_19D(cpu): # 19D RES 3,L
    t = (cpu.HL & 0xFF) & ~(1 << 3)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_19E(cpu): # 19E RES 3,(HL)
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 3)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def RES_19F(cpu): # 19F RES 3,A
    t = cpu.A & ~(1 << 3)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1A0(cpu): # 1A0 RES 4,B
    t = cpu.B & ~(1 << 4)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1A1(cpu): # 1A1 RES 4,C
    t = cpu.C & ~(1 << 4)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1A2(cpu): # 1A2 RES 4,D
    t = cpu.D & ~(1 << 4)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1A3(cpu): # 1A3 RES 4,E
    t = cpu.E & ~(1 << 4)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1A4(cpu): # 1A4 RES 4,H
    t = (cpu.HL >> 8) & ~(1 << 4)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1A5(cpu): # 1A5 RES 4,L
    t = (cpu.HL & 0xFF) & ~(1 << 4)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1A6(cpu): # 1A6 RES 4,(HL)
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 4)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def RES_1A7(cpu): # 1A7 RES 4,A
    t = cpu.A & ~(1 << 4)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1A8(cpu): # 1A8 RES 5,B
    t = cpu.B & ~(1 << 5)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1A9(cpu): # 1A9 RES 5,C
    t = cpu.C & ~(1 << 5)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1AA(cpu): # 1AA RES 5,D
    t = cpu.D & ~(1 << 5)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1AB(cpu): # 1AB RES 5,E
    t = cpu.E & ~(1 << 5)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1AC(cpu): # 1AC RES 5,H
    t = (cpu.HL >> 8) & ~(1 << 5)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1AD(cpu): # 1AD RES 5,L
    t = (cpu.HL & 0xFF) & ~(1 << 5)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1AE(cpu): # 1AE RES 5,(HL)
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 5)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def RES_1AF(cpu): # 1AF RES 5,A
    t = cpu.A & ~(1 << 5)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1B0(cpu): # 1B0 RES 6,B
    t = cpu.B & ~(1 << 6)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1B1(cpu): # 1B1 RES 6,C
    t = cpu.C & ~(1 << 6)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1B2(cpu): # 1B2 RES 6,D
    t = cpu.D & ~(1 << 6)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1B3(cpu): # 1B3 RES 6,E
    t = cpu.E & ~(1 << 6)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1B4(cpu): # 1B4 RES 6,H
    t = (cpu.HL >> 8) & ~(1 << 6)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1B5(cpu): # 1B5 RES 6,L
    t = (cpu.HL & 0xFF) & ~(1 << 6)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1B6(cpu): # 1B6 RES 6,(HL)
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 6)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def RES_1B7(cpu): # 1B7 RES 6,A
    t = cpu.A & ~(1 << 6)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1B8(cpu): # 1B8 RES 7,B
    t = cpu.B & ~(1 << 7)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1B9(cpu): # 1B9 RES 7,C
    t = cpu.C & ~(1 << 7)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1BA(cpu): # 1BA RES 7,D
    t = cpu.D & ~(1 << 7)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1BB(cpu): # 1BB RES 7,E
    t = cpu.E & ~(1 << 7)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1BC(cpu): # 1BC RES 7,H
    t = (cpu.HL >> 8) & ~(1 << 7)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1BD(cpu): # 1BD RES 7,L
    t = (cpu.HL & 0xFF) & ~(1 << 7)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def RES_1BE(cpu): # 1BE RES 7,(HL)
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 7)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def RES_1BF(cpu): # 1BF RES 7,A
    t = cpu.A & ~(1 << 7)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1C0(cpu): # 1C0 SET 0,B
    t = cpu.B | (1 << 0)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1C1(cpu): # 1C1 SET 0,C
    t = cpu.C | (1 << 0)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1C2(cpu): # 1C2 SET 0,D
    t = cpu.D | (1 << 0)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1C3(cpu): # 1C3 SET 0,E
    t = cpu.E | (1 << 0)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1C4(cpu): # 1C4 SET 0,H
    t = (cpu.HL >> 8) | (1 << 0)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1C5(cpu): # 1C5 SET 0,L
    t = (cpu.HL & 0xFF) | (1 << 0)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1C6(cpu): # 1C6 SET 0,(HL)
    t = cpu.mb.getitem(cpu.HL) | (1 << 0)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def SET_1C7(cpu): # 1C7 SET 0,A
    t = cpu.A | (1 << 0)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1C8(cpu): # 1C8 SET 1,B
    t = cpu.B | (1 << 1)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1C9(cpu): # 1C9 SET 1,C
    t = cpu.C | (1 << 1)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1CA(cpu): # 1CA SET 1,D
    t = cpu.D | (1 << 1)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1CB(cpu): # 1CB SET 1,E
    t = cpu.E | (1 << 1)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1CC(cpu): # 1CC SET 1,H
    t = (cpu.HL >> 8) | (1 << 1)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1CD(cpu): # 1CD SET 1,L
    t = (cpu.HL & 0xFF) | (1 << 1)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1CE(cpu): # 1CE SET 1,(HL)
    t = cpu.mb.getitem(cpu.HL) | (1 << 1)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def SET_1CF(cpu): # 1CF SET 1,A
    t = cpu.A | (1 << 1)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1D0(cpu): # 1D0 SET 2,B
    t = cpu.B | (1 << 2)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1D1(cpu): # 1D1 SET 2,C
    t = cpu.C | (1 << 2)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1D2(cpu): # 1D2 SET 2,D
    t = cpu.D | (1 << 2)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1D3(cpu): # 1D3 SET 2,E
    t = cpu.E | (1 << 2)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1D4(cpu): # 1D4 SET 2,H
    t = (cpu.HL >> 8) | (1 << 2)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1D5(cpu): # 1D5 SET 2,L
    t = (cpu.HL & 0xFF) | (1 << 2)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1D6(cpu): # 1D6 SET 2,(HL)
    t = cpu.mb.getitem(cpu.HL) | (1 << 2)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def SET_1D7(cpu): # 1D7 SET 2,A
    t = cpu.A | (1 << 2)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1D8(cpu): # 1D8 SET 3,B
    t = cpu.B | (1 << 3)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1D9(cpu): # 1D9 SET 3,C
    t = cpu.C | (1 << 3)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1DA(cpu): # 1DA SET 3,D
    t = cpu.D | (1 << 3)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1DB(cpu): # 1DB SET 3,E
    t = cpu.E | (1 << 3)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1DC(cpu): # 1DC SET 3,H
    t = (cpu.HL >> 8) | (1 << 3)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1DD(cpu): # 1DD SET 3,L
    t = (cpu.HL & 0xFF) | (1 << 3)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1DE(cpu): # 1DE SET 3,(HL)
    t = cpu.mb.getitem(cpu.HL) | (1 << 3)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def SET_1DF(cpu): # 1DF SET 3,A
    t = cpu.A | (1 << 3)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1E0(cpu): # 1E0 SET 4,B
    t = cpu.B | (1 << 4)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1E1(cpu): # 1E1 SET 4,C
    t = cpu.C | (1 << 4)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1E2(cpu): # 1E2 SET 4,D
    t = cpu.D | (1 << 4)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1E3(cpu): # 1E3 SET 4,E
    t = cpu.E | (1 << 4)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1E4(cpu): # 1E4 SET 4,H
    t = (cpu.HL >> 8) | (1 << 4)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1E5(cpu): # 1E5 SET 4,L
    t = (cpu.HL & 0xFF) | (1 << 4)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1E6(cpu): # 1E6 SET 4,(HL)
    t = cpu.mb.getitem(cpu.HL) | (1 << 4)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def SET_1E7(cpu): # 1E7 SET 4,A
    t = cpu.A | (1 << 4)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1E8(cpu): # 1E8 SET 5,B
    t = cpu.B | (1 << 5)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1E9(cpu): # 1E9 SET 5,C
    t = cpu.C | (1 << 5)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1EA(cpu): # 1EA SET 5,D
    t = cpu.D | (1 << 5)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1EB(cpu): # 1EB SET 5,E
    t = cpu.E | (1 << 5)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1EC(cpu): # 1EC SET 5,H
    t = (cpu.HL >> 8) | (1 << 5)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1ED(cpu): # 1ED SET 5,L
    t = (cpu.HL & 0xFF) | (1 << 5)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1EE(cpu): # 1EE SET 5,(HL)
    t = cpu.mb.getitem(cpu.HL) | (1 << 5)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def SET_1EF(cpu): # 1EF SET 5,A
    t = cpu.A | (1 << 5)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1F0(cpu): # 1F0 SET 6,B
    t = cpu.B | (1 << 6)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1F1(cpu): # 1F1 SET 6,C
    t = cpu.C | (1 << 6)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1F2(cpu): # 1F2 SET 6,D
    t = cpu.D | (1 << 6)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1F3(cpu): # 1F3 SET 6,E
    t = cpu.E | (1 << 6)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1F4(cpu): # 1F4 SET 6,H
    t = (cpu.HL >> 8) | (1 << 6)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1F5(cpu): # 1F5 SET 6,L
    t = (cpu.HL & 0xFF) | (1 << 6)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1F6(cpu): # 1F6 SET 6,(HL)
    t = cpu.mb.getitem(cpu.HL) | (1 << 6)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def SET_1F7(cpu): # 1F7 SET 6,A
    t = cpu.A | (1 << 6)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1F8(cpu): # 1F8 SET 7,B
    t = cpu.B | (1 << 7)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1F9(cpu): # 1F9 SET 7,C
    t = cpu.C | (1 << 7)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1FA(cpu): # 1FA SET 7,D
    t = cpu.D | (1 << 7)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1FB(cpu): # 1FB SET 7,E
    t = cpu.E | (1 << 7)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1FC(cpu): # 1FC SET 7,H
    t = (cpu.HL >> 8) | (1 << 7)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1FD(cpu): # 1FD SET 7,L
    t = (cpu.HL & 0xFF) | (1 << 7)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def SET_1FE(cpu): # 1FE SET 7,(HL)
    t = cpu.mb.getitem(cpu.HL) | (1 << 7)
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 16


def SET_1FF(cpu): # 1FF SET 7,A
    t = cpu.A | (1 << 7)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    return 8


def no_opcode(cpu):
    return 0


OPCODES = [
    NOP_00,
    LD_01,
    LD_02,
    INC_03,
    INC_04,
    DEC_05,
    LD_06,
    RLCA_07,
    LD_08,
    ADD_09,
    LD_0A,
    DEC_0B,
    INC_0C,
    DEC_0D,
    LD_0E,
    RRCA_0F,
    STOP_10,
    LD_11,
    LD_12,
    INC_13,
    INC_14,
    DEC_15,
    LD_16,
    RLA_17,
    JR_18,
    ADD_19,
    LD_1A,
    DEC_1B,
    INC_1C,
    DEC_1D,
    LD_1E,
    RRA_1F,
    JR_20,
    LD_21,
    LD_22,
    INC_23,
    INC_24,
    DEC_25,
    LD_26,
    DAA_27,
    JR_28,
    ADD_29,
    LD_2A,
    DEC_2B,
    INC_2C,
    DEC_2D,
    LD_2E,
    CPL_2F,
    JR_30,
    LD_31,
    LD_32,
    INC_33,
    INC_34,
    DEC_35,
    LD_36,
    SCF_37,
    JR_38,
    ADD_39,
    LD_3A,
    DEC_3B,
    INC_3C,
    DEC_3D,
    LD_3E,
    CCF_3F,
    LD_40,
    LD_41,
    LD_42,
    LD_43,
    LD_44,
    LD_45,
    LD_46,
    LD_47,
    LD_48,
    LD_49,
    LD_4A,
    LD_4B,
    LD_4C,
    LD_4D,
    LD_4E,
    LD_4F,
    LD_50,
    LD_51,
    LD_52,
    LD_53,
    LD_54,
    LD_55,
    LD_56,
    LD_57,
    LD_58,
    LD_59,
    LD_5A,
    LD_5B,
    LD_5C,
    LD_5D,
    LD_5E,
    LD_5F,
    LD_60,
    LD_61,
    LD_62,
    LD_63,
    LD_64,
    LD_65,
    LD_66,
    LD_67,
    LD_68,
    LD_69,
    LD_6A,
    LD_6B,
    LD_6C,
    LD_6D,
    LD_6E,
    LD_6F,
    LD_70,
    LD_71,
    LD_72,
    LD_73,
    LD_74,
    LD_75,
    HALT_76,
    LD_77,
    LD_78,
    LD_79,
    LD_7A,
    LD_7B,
    LD_7C,
    LD_7D,
    LD_7E,
    LD_7F,
    ADD_80,
    ADD_81,
    ADD_82,
    ADD_83,
    ADD_84,
    ADD_85,
    ADD_86,
    ADD_87,
    ADC_88,
    ADC_89,
    ADC_8A,
    ADC_8B,
    ADC_8C,
    ADC_8D,
    ADC_8E,
    ADC_8F,
    SUB_90,
    SUB_91,
    SUB_92,
    SUB_93,
    SUB_94,
    SUB_95,
    SUB_96,
    SUB_97,
    SBC_98,
    SBC_99,
    SBC_9A,
    SBC_9B,
    SBC_9C,
    SBC_9D,
    SBC_9E,
    SBC_9F,
    AND_A0,
    AND_A1,
    AND_A2,
    AND_A3,
    AND_A4,
    AND_A5,
    AND_A6,
    AND_A7,
    XOR_A8,
    XOR_A9,
    XOR_AA,
    XOR_AB,
    XOR_AC,
    XOR_AD,
    XOR_AE,
    XOR_AF,
    OR_B0,
    OR_B1,
    OR_B2,
    OR_B3,
    OR_B4,
    OR_B5,
    OR_B6,
    OR_B7,
    CP_B8,
    CP_B9,
    CP_BA,
    CP_BB,
    CP_BC,
    CP_BD,
    CP_BE,
    CP_BF,
    RET_C0,
    POP_C1,
    JP_C2,
    JP_C3,
    CALL_C4,
    PUSH_C5,
    ADD_C6,
    RST_C7,
    RET_C8,
    RET_C9,
    JP_CA,
    PREFIX_CB,
    CALL_CC,
    CALL_CD,
    ADC_CE,
    RST_CF,
    RET_D0,
    POP_D1,
    JP_D2,
    no_opcode,
    CALL_D4,
    PUSH_D5,
    SUB_D6,
    RST_D7,
    RET_D8,
    RETI_D9,
    JP_DA,
    no_opcode,
    CALL_DC,
    no_opcode,
    SBC_DE,
    RST_DF,
    LDH_E0,
    POP_E1,
    LD_E2,
    no_opcode,
    no_opcode,
    PUSH_E5,
    AND_E6,
    RST_E7,
    ADD_E8,
    JP_E9,
    LD_EA,
    no_opcode,
    no_opcode,
    no_opcode,
    XOR_EE,
    RST_EF,
    LDH_F0,
    POP_F1,
    LD_F2,
    DI_F3,
    no_opcode,
    PUSH_F5,
    OR_F6,
    RST_F7,
    LD_F8,
    LD_F9,
    LD_FA,
    EI_FB,
    no_opcode,
    no_opcode,
    CP_FE,
    RST_FF,
    RLC_100,
    RLC_101,
    RLC_102,
    RLC_103,
    RLC_104,
    RLC_105,
    RLC_106,
    RLC_107,
    RRC_108,
    RRC_109,
    RRC_10A,
    RRC_10B,
    RRC_10C,
    RRC_10D,
    RRC_10E,
    RRC_10F,
    RL_110,
    RL_111,
    RL_112,
    RL_113,
    RL_114,
    RL_115,
    RL_116,
    RL_117,
    RR_118,
    RR_119,
    RR_11A,
    RR_11B,
    RR_11C,
    RR_11D,
    RR_11E,
    RR_11F,
    SLA_120,
    SLA_121,
    SLA_122,
    SLA_123,
    SLA_124,
    SLA_125,
    SLA_126,
    SLA_127,
    SRA_128,
    SRA_129,
    SRA_12A,
    SRA_12B,
    SRA_12C,
    SRA_12D,
    SRA_12E,
    SRA_12F,
    SWAP_130,
    SWAP_131,
    SWAP_132,
    SWAP_133,
    SWAP_134,
    SWAP_135,
    SWAP_136,
    SWAP_137,
    SRL_138,
    SRL_139,
    SRL_13A,
    SRL_13B,
    SRL_13C,
    SRL_13D,
    SRL_13E,
    SRL_13F,
    BIT_140,
    BIT_141,
    BIT_142,
    BIT_143,
    BIT_144,
    BIT_145,
    BIT_146,
    BIT_147,
    BIT_148,
    BIT_149,
    BIT_14A,
    BIT_14B,
    BIT_14C,
    BIT_14D,
    BIT_14E,
    BIT_14F,
    BIT_150,
    BIT_151,
    BIT_152,
    BIT_153,
    BIT_154,
    BIT_155,
    BIT_156,
    BIT_157,
    BIT_158,
    BIT_159,
    BIT_15A,
    BIT_15B,
    BIT_15C,
    BIT_15D,
    BIT_15E,
    BIT_15F,
    BIT_160,
    BIT_161,
    BIT_162,
    BIT_163,
    BIT_164,
    BIT_165,
    BIT_166,
    BIT_167,
    BIT_168,
    BIT_169,
    BIT_16A,
    BIT_16B,
    BIT_16C,
    BIT_16D,
    BIT_16E,
    BIT_16F,
    BIT_170,
    BIT_171,
    BIT_172,
    BIT_173,
    BIT_174,
    BIT_175,
    BIT_176,
    BIT_177,
    BIT_178,
    BIT_179,
    BIT_17A,
    BIT_17B,
    BIT_17C,
    BIT_17D,
    BIT_17E,
    BIT_17F,
    RES_180,
    RES_181,
    RES_182,
    RES_183,
    RES_184,
    RES_185,
    RES_186,
    RES_187,
    RES_188,
    RES_189,
    RES_18A,
    RES_18B,
    RES_18C,
    RES_18D,
    RES_18E,
    RES_18F,
    RES_190,
    RES_191,
    RES_192,
    RES_193,
    RES_194,
    RES_195,
    RES_196,
    RES_197,
    RES_198,
    RES_199,
    RES_19A,
    RES_19B,
    RES_19C,
    RES_19D,
    RES_19E,
    RES_19F,
    RES_1A0,
    RES_1A1,
    RES_1A2,
    RES_1A3,
    RES_1A4,
    RES_1A5,
    RES_1A6,
    RES_1A7,
    RES_1A8,
    RES_1A9,
    RES_1AA,
    RES_1AB,
    RES_1AC,
    RES_1AD,
    RES_1AE,
    RES_1AF,
    RES_1B0,
    RES_1B1,
    RES_1B2,
    RES_1B3,
    RES_1B4,
    RES_1B5,
    RES_1B6,
    RES_1B7,
    RES_1B8,
    RES_1B9,
    RES_1BA,
    RES_1BB,
    RES_1BC,
    RES_1BD,
    RES_1BE,
    RES_1BF,
    SET_1C0,
    SET_1C1,
    SET_1C2,
    SET_1C3,
    SET_1C4,
    SET_1C5,
    SET_1C6,
    SET_1C7,
    SET_1C8,
    SET_1C9,
    SET_1CA,
    SET_1CB,
    SET_1CC,
    SET_1CD,
    SET_1CE,
    SET_1CF,
    SET_1D0,
    SET_1D1,
    SET_1D2,
    SET_1D3,
    SET_1D4,
    SET_1D5,
    SET_1D6,
    SET_1D7,
    SET_1D8,
    SET_1D9,
    SET_1DA,
    SET_1DB,
    SET_1DC,
    SET_1DD,
    SET_1DE,
    SET_1DF,
    SET_1E0,
    SET_1E1,
    SET_1E2,
    SET_1E3,
    SET_1E4,
    SET_1E5,
    SET_1E6,
    SET_1E7,
    SET_1E8,
    SET_1E9,
    SET_1EA,
    SET_1EB,
    SET_1EC,
    SET_1ED,
    SET_1EE,
    SET_1EF,
    SET_1F0,
    SET_1F1,
    SET_1F2,
    SET_1F3,
    SET_1F4,
    SET_1F5,
    SET_1F6,
    SET_1F7,
    SET_1F8,
    SET_1F9,
    SET_1FA,
    SET_1FB,
    SET_1FC,
    SET_1FD,
    SET_1FE,
    SET_1FF,

]


OPCODE_LENGTHS = array.array("B", [
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
    ])


CPU_COMMANDS = [
    "NOP",
    "LD BC,d16",
    "LD (BC),A",
    "INC BC",
    "INC B",
    "DEC B",
    "LD B,d8",
    "RLCA",
    "LD (a16),SP",
    "ADD HL,BC",
    "LD A,(BC)",
    "DEC BC",
    "INC C",
    "DEC C",
    "LD C,d8",
    "RRCA",
    "STOP 0",
    "LD DE,d16",
    "LD (DE),A",
    "INC DE",
    "INC D",
    "DEC D",
    "LD D,d8",
    "RLA",
    "JR r8",
    "ADD HL,DE",
    "LD A,(DE)",
    "DEC DE",
    "INC E",
    "DEC E",
    "LD E,d8",
    "RRA",
    "JR NZ,r8",
    "LD HL,d16",
    "LD (HL+),A",
    "INC HL",
    "INC H",
    "DEC H",
    "LD H,d8",
    "DAA",
    "JR Z,r8",
    "ADD HL,HL",
    "LD A,(HL+)",
    "DEC HL",
    "INC L",
    "DEC L",
    "LD L,d8",
    "CPL",
    "JR NC,r8",
    "LD SP,d16",
    "LD (HL-),A",
    "INC SP",
    "INC (HL)",
    "DEC (HL)",
    "LD (HL),d8",
    "SCF",
    "JR C,r8",
    "ADD HL,SP",
    "LD A,(HL-)",
    "DEC SP",
    "INC A",
    "DEC A",
    "LD A,d8",
    "CCF",
    "LD B,B",
    "LD B,C",
    "LD B,D",
    "LD B,E",
    "LD B,H",
    "LD B,L",
    "LD B,(HL)",
    "LD B,A",
    "LD C,B",
    "LD C,C",
    "LD C,D",
    "LD C,E",
    "LD C,H",
    "LD C,L",
    "LD C,(HL)",
    "LD C,A",
    "LD D,B",
    "LD D,C",
    "LD D,D",
    "LD D,E",
    "LD D,H",
    "LD D,L",
    "LD D,(HL)",
    "LD D,A",
    "LD E,B",
    "LD E,C",
    "LD E,D",
    "LD E,E",
    "LD E,H",
    "LD E,L",
    "LD E,(HL)",
    "LD E,A",
    "LD H,B",
    "LD H,C",
    "LD H,D",
    "LD H,E",
    "LD H,H",
    "LD H,L",
    "LD H,(HL)",
    "LD H,A",
    "LD L,B",
    "LD L,C",
    "LD L,D",
    "LD L,E",
    "LD L,H",
    "LD L,L",
    "LD L,(HL)",
    "LD L,A",
    "LD (HL),B",
    "LD (HL),C",
    "LD (HL),D",
    "LD (HL),E",
    "LD (HL),H",
    "LD (HL),L",
    "HALT",
    "LD (HL),A",
    "LD A,B",
    "LD A,C",
    "LD A,D",
    "LD A,E",
    "LD A,H",
    "LD A,L",
    "LD A,(HL)",
    "LD A,A",
    "ADD A,B",
    "ADD A,C",
    "ADD A,D",
    "ADD A,E",
    "ADD A,H",
    "ADD A,L",
    "ADD A,(HL)",
    "ADD A,A",
    "ADC A,B",
    "ADC A,C",
    "ADC A,D",
    "ADC A,E",
    "ADC A,H",
    "ADC A,L",
    "ADC A,(HL)",
    "ADC A,A",
    "SUB B",
    "SUB C",
    "SUB D",
    "SUB E",
    "SUB H",
    "SUB L",
    "SUB (HL)",
    "SUB A",
    "SBC A,B",
    "SBC A,C",
    "SBC A,D",
    "SBC A,E",
    "SBC A,H",
    "SBC A,L",
    "SBC A,(HL)",
    "SBC A,A",
    "AND B",
    "AND C",
    "AND D",
    "AND E",
    "AND H",
    "AND L",
    "AND (HL)",
    "AND A",
    "XOR B",
    "XOR C",
    "XOR D",
    "XOR E",
    "XOR H",
    "XOR L",
    "XOR (HL)",
    "XOR A",
    "OR B",
    "OR C",
    "OR D",
    "OR E",
    "OR H",
    "OR L",
    "OR (HL)",
    "OR A",
    "CP B",
    "CP C",
    "CP D",
    "CP E",
    "CP H",
    "CP L",
    "CP (HL)",
    "CP A",
    "RET NZ",
    "POP BC",
    "JP NZ,a16",
    "JP a16",
    "CALL NZ,a16",
    "PUSH BC",
    "ADD A,d8",
    "RST 00H",
    "RET Z",
    "RET",
    "JP Z,a16",
    "PREFIX CB",
    "CALL Z,a16",
    "CALL a16",
    "ADC A,d8",
    "RST 08H",
    "RET NC",
    "POP DE",
    "JP NC,a16",
    "",
    "CALL NC,a16",
    "PUSH DE",
    "SUB d8",
    "RST 10H",
    "RET C",
    "RETI",
    "JP C,a16",
    "",
    "CALL C,a16",
    "",
    "SBC A,d8",
    "RST 18H",
    "LDH (a8),A",
    "POP HL",
    "LD (C),A",
    "",
    "",
    "PUSH HL",
    "AND d8",
    "RST 20H",
    "ADD SP,r8",
    "JP (HL)",
    "LD (a16),A",
    "",
    "",
    "",
    "XOR d8",
    "RST 28H",
    "LDH A,(a8)",
    "POP AF",
    "LD A,(C)",
    "DI",
    "",
    "PUSH AF",
    "OR d8",
    "RST 30H",
    "LD HL,SP+r8",
    "LD SP,HL",
    "LD A,(a16)",
    "EI",
    "",
    "",
    "CP d8",
    "RST 38H",
    "RLC B",
    "RLC C",
    "RLC D",
    "RLC E",
    "RLC H",
    "RLC L",
    "RLC (HL)",
    "RLC A",
    "RRC B",
    "RRC C",
    "RRC D",
    "RRC E",
    "RRC H",
    "RRC L",
    "RRC (HL)",
    "RRC A",
    "RL B",
    "RL C",
    "RL D",
    "RL E",
    "RL H",
    "RL L",
    "RL (HL)",
    "RL A",
    "RR B",
    "RR C",
    "RR D",
    "RR E",
    "RR H",
    "RR L",
    "RR (HL)",
    "RR A",
    "SLA B",
    "SLA C",
    "SLA D",
    "SLA E",
    "SLA H",
    "SLA L",
    "SLA (HL)",
    "SLA A",
    "SRA B",
    "SRA C",
    "SRA D",
    "SRA E",
    "SRA H",
    "SRA L",
    "SRA (HL)",
    "SRA A",
    "SWAP B",
    "SWAP C",
    "SWAP D",
    "SWAP E",
    "SWAP H",
    "SWAP L",
    "SWAP (HL)",
    "SWAP A",
    "SRL B",
    "SRL C",
    "SRL D",
    "SRL E",
    "SRL H",
    "SRL L",
    "SRL (HL)",
    "SRL A",
    "BIT 0,B",
    "BIT 0,C",
    "BIT 0,D",
    "BIT 0,E",
    "BIT 0,H",
    "BIT 0,L",
    "BIT 0,(HL)",
    "BIT 0,A",
    "BIT 1,B",
    "BIT 1,C",
    "BIT 1,D",
    "BIT 1,E",
    "BIT 1,H",
    "BIT 1,L",
    "BIT 1,(HL)",
    "BIT 1,A",
    "BIT 2,B",
    "BIT 2,C",
    "BIT 2,D",
    "BIT 2,E",
    "BIT 2,H",
    "BIT 2,L",
    "BIT 2,(HL)",
    "BIT 2,A",
    "BIT 3,B",
    "BIT 3,C",
    "BIT 3,D",
    "BIT 3,E",
    "BIT 3,H",
    "BIT 3,L",
    "BIT 3,(HL)",
    "BIT 3,A",
    "BIT 4,B",
    "BIT 4,C",
    "BIT 4,D",
    "BIT 4,E",
    "BIT 4,H",
    "BIT 4,L",
    "BIT 4,(HL)",
    "BIT 4,A",
    "BIT 5,B",
    "BIT 5,C",
    "BIT 5,D",
    "BIT 5,E",
    "BIT 5,H",
    "BIT 5,L",
    "BIT 5,(HL)",
    "BIT 5,A",
    "BIT 6,B",
    "BIT 6,C",
    "BIT 6,D",
    "BIT 6,E",
    "BIT 6,H",
    "BIT 6,L",
    "BIT 6,(HL)",
    "BIT 6,A",
    "BIT 7,B",
    "BIT 7,C",
    "BIT 7,D",
    "BIT 7,E",
    "BIT 7,H",
    "BIT 7,L",
    "BIT 7,(HL)",
    "BIT 7,A",
    "RES 0,B",
    "RES 0,C",
    "RES 0,D",
    "RES 0,E",
    "RES 0,H",
    "RES 0,L",
    "RES 0,(HL)",
    "RES 0,A",
    "RES 1,B",
    "RES 1,C",
    "RES 1,D",
    "RES 1,E",
    "RES 1,H",
    "RES 1,L",
    "RES 1,(HL)",
    "RES 1,A",
    "RES 2,B",
    "RES 2,C",
    "RES 2,D",
    "RES 2,E",
    "RES 2,H",
    "RES 2,L",
    "RES 2,(HL)",
    "RES 2,A",
    "RES 3,B",
    "RES 3,C",
    "RES 3,D",
    "RES 3,E",
    "RES 3,H",
    "RES 3,L",
    "RES 3,(HL)",
    "RES 3,A",
    "RES 4,B",
    "RES 4,C",
    "RES 4,D",
    "RES 4,E",
    "RES 4,H",
    "RES 4,L",
    "RES 4,(HL)",
    "RES 4,A",
    "RES 5,B",
    "RES 5,C",
    "RES 5,D",
    "RES 5,E",
    "RES 5,H",
    "RES 5,L",
    "RES 5,(HL)",
    "RES 5,A",
    "RES 6,B",
    "RES 6,C",
    "RES 6,D",
    "RES 6,E",
    "RES 6,H",
    "RES 6,L",
    "RES 6,(HL)",
    "RES 6,A",
    "RES 7,B",
    "RES 7,C",
    "RES 7,D",
    "RES 7,E",
    "RES 7,H",
    "RES 7,L",
    "RES 7,(HL)",
    "RES 7,A",
    "SET 0,B",
    "SET 0,C",
    "SET 0,D",
    "SET 0,E",
    "SET 0,H",
    "SET 0,L",
    "SET 0,(HL)",
    "SET 0,A",
    "SET 1,B",
    "SET 1,C",
    "SET 1,D",
    "SET 1,E",
    "SET 1,H",
    "SET 1,L",
    "SET 1,(HL)",
    "SET 1,A",
    "SET 2,B",
    "SET 2,C",
    "SET 2,D",
    "SET 2,E",
    "SET 2,H",
    "SET 2,L",
    "SET 2,(HL)",
    "SET 2,A",
    "SET 3,B",
    "SET 3,C",
    "SET 3,D",
    "SET 3,E",
    "SET 3,H",
    "SET 3,L",
    "SET 3,(HL)",
    "SET 3,A",
    "SET 4,B",
    "SET 4,C",
    "SET 4,D",
    "SET 4,E",
    "SET 4,H",
    "SET 4,L",
    "SET 4,(HL)",
    "SET 4,A",
    "SET 5,B",
    "SET 5,C",
    "SET 5,D",
    "SET 5,E",
    "SET 5,H",
    "SET 5,L",
    "SET 5,(HL)",
    "SET 5,A",
    "SET 6,B",
    "SET 6,C",
    "SET 6,D",
    "SET 6,E",
    "SET 6,H",
    "SET 6,L",
    "SET 6,(HL)",
    "SET 6,A",
    "SET 7,B",
    "SET 7,C",
    "SET 7,D",
    "SET 7,E",
    "SET 7,H",
    "SET 7,L",
    "SET 7,(HL)",
    "SET 7,A",
    ]
