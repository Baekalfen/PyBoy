
# THIS FILE IS AUTO-GENERATED!!!
# DO NOT MODIFY THIS FILE.
# CHANGES TO THE CODE SHOULD BE MADE IN 'opcodes_gen.py'.

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

def NOP_00(cpu): # 00 NOP
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_01(cpu, v): # 01 LD BC,d16
    cpu.B = v >> 8
    cpu.C = v & 0x00FF
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    cpu.cycles += 12


def LD_02(cpu): # 02 LD (BC),A
    cpu.mb.setitem(((cpu.B << 8) + cpu.C), cpu.A)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def INC_03(cpu): # 03 INC BC
    t = ((cpu.B << 8) + cpu.C) + 1
    # No flag operations
    t &= 0xFFFF
    cpu.B = t >> 8
    cpu.C = t & 0x00FF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 4


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
    cpu.cycles += 4


def LD_06(cpu, v): # 06 LD B,d8
    cpu.B = v
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 4


def LD_08(cpu, v): # 08 LD (a16),SP
    cpu.mb.setitem(v, cpu.SP & 0xFF)
    cpu.mb.setitem(v+1, cpu.SP >> 8)
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    cpu.cycles += 20


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
    cpu.cycles += 8


def LD_0A(cpu): # 0A LD A,(BC)
    cpu.A = cpu.mb.getitem(((cpu.B << 8) + cpu.C))
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def DEC_0B(cpu): # 0B DEC BC
    t = ((cpu.B << 8) + cpu.C) - 1
    # No flag operations
    t &= 0xFFFF
    cpu.B = t >> 8
    cpu.C = t & 0x00FF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 4


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
    cpu.cycles += 4


def LD_0E(cpu, v): # 0E LD C,d8
    cpu.C = v
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 4


def STOP_10(cpu, v): # 10 STOP 0
    if cpu.mb.cgb:
        cpu.mb.switch_speed()
        cpu.mb.setitem(0xFF04, 0)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_11(cpu, v): # 11 LD DE,d16
    cpu.D = v >> 8
    cpu.E = v & 0x00FF
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    cpu.cycles += 12


def LD_12(cpu): # 12 LD (DE),A
    cpu.mb.setitem(((cpu.D << 8) + cpu.E), cpu.A)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def INC_13(cpu): # 13 INC DE
    t = ((cpu.D << 8) + cpu.E) + 1
    # No flag operations
    t &= 0xFFFF
    cpu.D = t >> 8
    cpu.E = t & 0x00FF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 4


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
    cpu.cycles += 4


def LD_16(cpu, v): # 16 LD D,d8
    cpu.D = v
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 4


def JR_18(cpu, v): # 18 JR r8
    cpu.PC += 2 + ((v ^ 0x80) - 0x80)
    cpu.PC &= 0xFFFF
    cpu.cycles += 12


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
    cpu.cycles += 8


def LD_1A(cpu): # 1A LD A,(DE)
    cpu.A = cpu.mb.getitem(((cpu.D << 8) + cpu.E))
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def DEC_1B(cpu): # 1B DEC DE
    t = ((cpu.D << 8) + cpu.E) - 1
    # No flag operations
    t &= 0xFFFF
    cpu.D = t >> 8
    cpu.E = t & 0x00FF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 4


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
    cpu.cycles += 4


def LD_1E(cpu, v): # 1E LD E,d8
    cpu.E = v
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 4


def JR_20(cpu, v): # 20 JR NZ,r8
    cpu.PC += 2
    if ((cpu.F & (1 << FLAGZ)) == 0):
        cpu.PC += ((v ^ 0x80) - 0x80)
        cpu.PC &= 0xFFFF
        cpu.cycles += 12
    else:
        cpu.PC &= 0xFFFF
        cpu.cycles += 8


def LD_21(cpu, v): # 21 LD HL,d16
    cpu.HL = v
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    cpu.cycles += 12


def LD_22(cpu): # 22 LD (HL+),A
    cpu.mb.setitem(cpu.HL, cpu.A)
    cpu.HL += 1
    cpu.HL &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def INC_23(cpu): # 23 INC HL
    t = cpu.HL + 1
    # No flag operations
    t &= 0xFFFF
    cpu.HL = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 4


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
    cpu.cycles += 4


def LD_26(cpu, v): # 26 LD H,d8
    cpu.HL = (cpu.HL & 0x00FF) | (v << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 4


def JR_28(cpu, v): # 28 JR Z,r8
    cpu.PC += 2
    if ((cpu.F & (1 << FLAGZ)) != 0):
        cpu.PC += ((v ^ 0x80) - 0x80)
        cpu.PC &= 0xFFFF
        cpu.cycles += 12
    else:
        cpu.PC &= 0xFFFF
        cpu.cycles += 8


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
    cpu.cycles += 8


def LD_2A(cpu): # 2A LD A,(HL+)
    cpu.A = cpu.mb.getitem(cpu.HL)
    cpu.HL += 1
    cpu.HL &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def DEC_2B(cpu): # 2B DEC HL
    t = cpu.HL - 1
    # No flag operations
    t &= 0xFFFF
    cpu.HL = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 4


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
    cpu.cycles += 4


def LD_2E(cpu, v): # 2E LD L,d8
    cpu.HL = (cpu.HL & 0xFF00) | (v & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def CPL_2F(cpu): # 2F CPL
    cpu.A = (~cpu.A) & 0xFF
    flag = 0b01100000
    cpu.F &= 0b10010000
    cpu.F |= flag
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def JR_30(cpu, v): # 30 JR NC,r8
    cpu.PC += 2
    if ((cpu.F & (1 << FLAGC)) == 0):
        cpu.PC += ((v ^ 0x80) - 0x80)
        cpu.PC &= 0xFFFF
        cpu.cycles += 12
    else:
        cpu.PC &= 0xFFFF
        cpu.cycles += 8


def LD_31(cpu, v): # 31 LD SP,d16
    cpu.SP = v
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    cpu.cycles += 12


def LD_32(cpu): # 32 LD (HL-),A
    cpu.mb.setitem(cpu.HL, cpu.A)
    cpu.HL -= 1
    cpu.HL &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def INC_33(cpu): # 33 INC SP
    t = cpu.SP + 1
    # No flag operations
    t &= 0xFFFF
    cpu.SP = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def INC_34(cpu): # 34 INC (HL)
    t = cpu.mb.getitem(cpu.HL) + 1
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.mb.getitem(cpu.HL) & 0xF) + (1 & 0xF)) > 0xF) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def DEC_35(cpu): # 35 DEC (HL)
    t = cpu.mb.getitem(cpu.HL) - 1
    flag = 0b01000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (((cpu.mb.getitem(cpu.HL) & 0xF) - (1 & 0xF)) < 0) << FLAGH
    cpu.F &= 0b00010000
    cpu.F |= flag
    t &= 0xFF
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_36(cpu, v): # 36 LD (HL),d8
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, v)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SCF_37(cpu): # 37 SCF
    flag = 0b00010000
    cpu.F &= 0b10000000
    cpu.F |= flag
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def JR_38(cpu, v): # 38 JR C,r8
    cpu.PC += 2
    if ((cpu.F & (1 << FLAGC)) != 0):
        cpu.PC += ((v ^ 0x80) - 0x80)
        cpu.PC &= 0xFFFF
        cpu.cycles += 12
    else:
        cpu.PC &= 0xFFFF
        cpu.cycles += 8


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
    cpu.cycles += 8


def LD_3A(cpu): # 3A LD A,(HL-)
    cpu.A = cpu.mb.getitem(cpu.HL)
    cpu.HL -= 1
    cpu.HL &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def DEC_3B(cpu): # 3B DEC SP
    t = cpu.SP - 1
    # No flag operations
    t &= 0xFFFF
    cpu.SP = t
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 4


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
    cpu.cycles += 4


def LD_3E(cpu, v): # 3E LD A,d8
    cpu.A = v
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def CCF_3F(cpu): # 3F CCF
    flag = (cpu.F & 0b00010000) ^ 0b00010000
    cpu.F &= 0b10000000
    cpu.F |= flag
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_40(cpu): # 40 LD B,B
    cpu.B = cpu.B
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_41(cpu): # 41 LD B,C
    cpu.B = cpu.C
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_42(cpu): # 42 LD B,D
    cpu.B = cpu.D
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_43(cpu): # 43 LD B,E
    cpu.B = cpu.E
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_44(cpu): # 44 LD B,H
    cpu.B = (cpu.HL >> 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_45(cpu): # 45 LD B,L
    cpu.B = (cpu.HL & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_46(cpu): # 46 LD B,(HL)
    cpu.B = cpu.mb.getitem(cpu.HL)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_47(cpu): # 47 LD B,A
    cpu.B = cpu.A
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_48(cpu): # 48 LD C,B
    cpu.C = cpu.B
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_49(cpu): # 49 LD C,C
    cpu.C = cpu.C
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_4A(cpu): # 4A LD C,D
    cpu.C = cpu.D
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_4B(cpu): # 4B LD C,E
    cpu.C = cpu.E
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_4C(cpu): # 4C LD C,H
    cpu.C = (cpu.HL >> 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_4D(cpu): # 4D LD C,L
    cpu.C = (cpu.HL & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_4E(cpu): # 4E LD C,(HL)
    cpu.C = cpu.mb.getitem(cpu.HL)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_4F(cpu): # 4F LD C,A
    cpu.C = cpu.A
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_50(cpu): # 50 LD D,B
    cpu.D = cpu.B
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_51(cpu): # 51 LD D,C
    cpu.D = cpu.C
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_52(cpu): # 52 LD D,D
    cpu.D = cpu.D
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_53(cpu): # 53 LD D,E
    cpu.D = cpu.E
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_54(cpu): # 54 LD D,H
    cpu.D = (cpu.HL >> 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_55(cpu): # 55 LD D,L
    cpu.D = (cpu.HL & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_56(cpu): # 56 LD D,(HL)
    cpu.D = cpu.mb.getitem(cpu.HL)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_57(cpu): # 57 LD D,A
    cpu.D = cpu.A
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_58(cpu): # 58 LD E,B
    cpu.E = cpu.B
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_59(cpu): # 59 LD E,C
    cpu.E = cpu.C
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_5A(cpu): # 5A LD E,D
    cpu.E = cpu.D
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_5B(cpu): # 5B LD E,E
    cpu.E = cpu.E
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_5C(cpu): # 5C LD E,H
    cpu.E = (cpu.HL >> 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_5D(cpu): # 5D LD E,L
    cpu.E = (cpu.HL & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_5E(cpu): # 5E LD E,(HL)
    cpu.E = cpu.mb.getitem(cpu.HL)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_5F(cpu): # 5F LD E,A
    cpu.E = cpu.A
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_60(cpu): # 60 LD H,B
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.B << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_61(cpu): # 61 LD H,C
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.C << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_62(cpu): # 62 LD H,D
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.D << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_63(cpu): # 63 LD H,E
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.E << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_64(cpu): # 64 LD H,H
    cpu.HL = (cpu.HL & 0x00FF) | ((cpu.HL >> 8) << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_65(cpu): # 65 LD H,L
    cpu.HL = (cpu.HL & 0x00FF) | ((cpu.HL & 0xFF) << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_66(cpu): # 66 LD H,(HL)
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.mb.getitem(cpu.HL) << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_67(cpu): # 67 LD H,A
    cpu.HL = (cpu.HL & 0x00FF) | (cpu.A << 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_68(cpu): # 68 LD L,B
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.B & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_69(cpu): # 69 LD L,C
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.C & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_6A(cpu): # 6A LD L,D
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.D & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_6B(cpu): # 6B LD L,E
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.E & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_6C(cpu): # 6C LD L,H
    cpu.HL = (cpu.HL & 0xFF00) | ((cpu.HL >> 8) & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_6D(cpu): # 6D LD L,L
    cpu.HL = (cpu.HL & 0xFF00) | ((cpu.HL & 0xFF) & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_6E(cpu): # 6E LD L,(HL)
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.mb.getitem(cpu.HL) & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_6F(cpu): # 6F LD L,A
    cpu.HL = (cpu.HL & 0xFF00) | (cpu.A & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_70(cpu): # 70 LD (HL),B
    cpu.mb.setitem(cpu.HL, cpu.B)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_71(cpu): # 71 LD (HL),C
    cpu.mb.setitem(cpu.HL, cpu.C)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_72(cpu): # 72 LD (HL),D
    cpu.mb.setitem(cpu.HL, cpu.D)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_73(cpu): # 73 LD (HL),E
    cpu.mb.setitem(cpu.HL, cpu.E)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_74(cpu): # 74 LD (HL),H
    cpu.mb.setitem(cpu.HL, (cpu.HL >> 8))
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_75(cpu): # 75 LD (HL),L
    cpu.mb.setitem(cpu.HL, (cpu.HL & 0xFF))
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def HALT_76(cpu): # 76 HALT
    cpu.halted = True
    cpu.bail = True
    cpu.cycles += 4


def LD_77(cpu): # 77 LD (HL),A
    cpu.mb.setitem(cpu.HL, cpu.A)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_78(cpu): # 78 LD A,B
    cpu.A = cpu.B
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_79(cpu): # 79 LD A,C
    cpu.A = cpu.C
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_7A(cpu): # 7A LD A,D
    cpu.A = cpu.D
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_7B(cpu): # 7B LD A,E
    cpu.A = cpu.E
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_7C(cpu): # 7C LD A,H
    cpu.A = (cpu.HL >> 8)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_7D(cpu): # 7D LD A,L
    cpu.A = (cpu.HL & 0xFF)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def LD_7E(cpu): # 7E LD A,(HL)
    cpu.A = cpu.mb.getitem(cpu.HL)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_7F(cpu): # 7F LD A,A
    cpu.A = cpu.A
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 8


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 8


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 8


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 8


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 8


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 8


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 8


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 4


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
    cpu.cycles += 8


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
    cpu.cycles += 4


def RET_C0(cpu): # C0 RET NZ
    if ((cpu.F & (1 << FLAGZ)) == 0):
        cpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High
        cpu.PC |= cpu.mb.getitem(cpu.SP) # Low
        cpu.SP += 2
        cpu.SP &= 0xFFFF
        cpu.cycles += 20
    else:
        cpu.PC += 1
        cpu.PC &= 0xFFFF
        cpu.cycles += 8


def POP_C1(cpu): # C1 POP BC
    cpu.B = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) # High
    cpu.C = cpu.mb.getitem(cpu.SP) # Low
    cpu.SP += 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 12


def JP_C2(cpu, v): # C2 JP NZ,a16
    if ((cpu.F & (1 << FLAGZ)) == 0):
        cpu.PC = v
        cpu.cycles += 16
    else:
        cpu.PC += 3
        cpu.PC &= 0xFFFF
        cpu.cycles += 12


def JP_C3(cpu, v): # C3 JP a16
    cpu.PC = v
    cpu.cycles += 16


def CALL_C4(cpu, v): # C4 CALL NZ,a16
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    if ((cpu.F & (1 << FLAGZ)) == 0):
        cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
        cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
        cpu.SP -= 2
        cpu.SP &= 0xFFFF
        cpu.PC = v
        cpu.cycles += 24
    else:
        cpu.cycles += 12


def PUSH_C5(cpu): # C5 PUSH BC
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.B) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.C) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 16


def ADD_C6(cpu, v): # C6 ADD A,d8
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
    cpu.cycles += 8


def RST_C7(cpu): # C7 RST 00H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 0
    cpu.cycles += 16


def RET_C8(cpu): # C8 RET Z
    if ((cpu.F & (1 << FLAGZ)) != 0):
        cpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High
        cpu.PC |= cpu.mb.getitem(cpu.SP) # Low
        cpu.SP += 2
        cpu.SP &= 0xFFFF
        cpu.cycles += 20
    else:
        cpu.PC += 1
        cpu.PC &= 0xFFFF
        cpu.cycles += 8


def RET_C9(cpu): # C9 RET
    cpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High
    cpu.PC |= cpu.mb.getitem(cpu.SP) # Low
    cpu.SP += 2
    cpu.SP &= 0xFFFF
    cpu.cycles += 16


def JP_CA(cpu, v): # CA JP Z,a16
    if ((cpu.F & (1 << FLAGZ)) != 0):
        cpu.PC = v
        cpu.cycles += 16
    else:
        cpu.PC += 3
        cpu.PC &= 0xFFFF
        cpu.cycles += 12


def PREFIX_CB(cpu): # CB PREFIX CB
    logger.critical('CB cannot be called!')
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def CALL_CC(cpu, v): # CC CALL Z,a16
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    if ((cpu.F & (1 << FLAGZ)) != 0):
        cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
        cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
        cpu.SP -= 2
        cpu.SP &= 0xFFFF
        cpu.PC = v
        cpu.cycles += 24
    else:
        cpu.cycles += 12


def CALL_CD(cpu, v): # CD CALL a16
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = v
    cpu.cycles += 24


def ADC_CE(cpu, v): # CE ADC A,d8
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
    cpu.cycles += 8


def RST_CF(cpu): # CF RST 08H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 8
    cpu.cycles += 16


def RET_D0(cpu): # D0 RET NC
    if ((cpu.F & (1 << FLAGC)) == 0):
        cpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High
        cpu.PC |= cpu.mb.getitem(cpu.SP) # Low
        cpu.SP += 2
        cpu.SP &= 0xFFFF
        cpu.cycles += 20
    else:
        cpu.PC += 1
        cpu.PC &= 0xFFFF
        cpu.cycles += 8


def POP_D1(cpu): # D1 POP DE
    cpu.D = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) # High
    cpu.E = cpu.mb.getitem(cpu.SP) # Low
    cpu.SP += 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 12


def JP_D2(cpu, v): # D2 JP NC,a16
    if ((cpu.F & (1 << FLAGC)) == 0):
        cpu.PC = v
        cpu.cycles += 16
    else:
        cpu.PC += 3
        cpu.PC &= 0xFFFF
        cpu.cycles += 12


def CALL_D4(cpu, v): # D4 CALL NC,a16
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    if ((cpu.F & (1 << FLAGC)) == 0):
        cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
        cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
        cpu.SP -= 2
        cpu.SP &= 0xFFFF
        cpu.PC = v
        cpu.cycles += 24
    else:
        cpu.cycles += 12


def PUSH_D5(cpu): # D5 PUSH DE
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.D) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.E) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 16


def SUB_D6(cpu, v): # D6 SUB d8
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
    cpu.cycles += 8


def RST_D7(cpu): # D7 RST 10H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 16
    cpu.cycles += 16


def RET_D8(cpu): # D8 RET C
    if ((cpu.F & (1 << FLAGC)) != 0):
        cpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High
        cpu.PC |= cpu.mb.getitem(cpu.SP) # Low
        cpu.SP += 2
        cpu.SP &= 0xFFFF
        cpu.cycles += 20
    else:
        cpu.PC += 1
        cpu.PC &= 0xFFFF
        cpu.cycles += 8


def RETI_D9(cpu): # D9 RETI
    cpu.interrupt_master_enable = True
    cpu.bail = (cpu.interrupts_flag_register & 0b11111) & (cpu.interrupts_enabled_register & 0b11111)
    cpu.PC = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8 # High
    cpu.PC |= cpu.mb.getitem(cpu.SP) # Low
    cpu.SP += 2
    cpu.SP &= 0xFFFF
    cpu.cycles += 16


def JP_DA(cpu, v): # DA JP C,a16
    if ((cpu.F & (1 << FLAGC)) != 0):
        cpu.PC = v
        cpu.cycles += 16
    else:
        cpu.PC += 3
        cpu.PC &= 0xFFFF
        cpu.cycles += 12


def CALL_DC(cpu, v): # DC CALL C,a16
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    if ((cpu.F & (1 << FLAGC)) != 0):
        cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
        cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
        cpu.SP -= 2
        cpu.SP &= 0xFFFF
        cpu.PC = v
        cpu.cycles += 24
    else:
        cpu.cycles += 12


def SBC_DE(cpu, v): # DE SBC A,d8
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
    cpu.cycles += 8


def RST_DF(cpu): # DF RST 18H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 24
    cpu.cycles += 16


def LDH_E0(cpu, v): # E0 LDH (a8),A
    cpu.cycles += 4
    cpu.mb.setitem(v + 0xFF00, cpu.A)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def POP_E1(cpu): # E1 POP HL
    cpu.HL = (cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) << 8) + cpu.mb.getitem(cpu.SP) # High
    cpu.SP += 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 12


def LD_E2(cpu): # E2 LD (C),A
    cpu.mb.setitem(0xFF00 + cpu.C, cpu.A)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def PUSH_E5(cpu): # E5 PUSH HL
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.HL >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.HL & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 16


def AND_E6(cpu, v): # E6 AND d8
    t = cpu.A & v
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RST_E7(cpu): # E7 RST 20H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 32
    cpu.cycles += 16


def ADD_E8(cpu, v): # E8 ADD SP,r8
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
    cpu.cycles += 16


def JP_E9(cpu): # E9 JP (HL)
    cpu.PC = cpu.HL
    cpu.cycles += 4


def LD_EA(cpu, v): # EA LD (a16),A
    cpu.cycles += 8
    cpu.mb.setitem(v, cpu.A)
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def XOR_EE(cpu, v): # EE XOR d8
    t = cpu.A ^ v
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RST_EF(cpu): # EF RST 28H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 40
    cpu.cycles += 16


def LDH_F0(cpu, v): # F0 LDH A,(a8)
    cpu.cycles += 4
    cpu.A = cpu.mb.getitem(v + 0xFF00)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def POP_F1(cpu): # F1 POP AF
    cpu.A = cpu.mb.getitem((cpu.SP + 1) & 0xFFFF) # High
    cpu.F = cpu.mb.getitem(cpu.SP) & 0xF0 & 0xF0 # Low
    cpu.SP += 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 12


def LD_F2(cpu): # F2 LD A,(C)
    cpu.A = cpu.mb.getitem(0xFF00 + cpu.C)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def DI_F3(cpu): # F3 DI
    cpu.interrupt_master_enable = False
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def PUSH_F5(cpu): # F5 PUSH AF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.A) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.F & 0xF0) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 16


def OR_F6(cpu, v): # F6 OR d8
    t = cpu.A | v
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RST_F7(cpu): # F7 RST 30H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 48
    cpu.cycles += 16


def LD_F8(cpu, v): # F8 LD HL,SP+r8
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
    cpu.cycles += 12


def LD_F9(cpu): # F9 LD SP,HL
    cpu.SP = cpu.HL
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def LD_FA(cpu, v): # FA LD A,(a16)
    cpu.cycles += 8
    cpu.A = cpu.mb.getitem(v)
    cpu.PC += 3
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def EI_FB(cpu): # FB EI
    cpu.interrupt_master_enable = True
    cpu.bail = (cpu.interrupts_flag_register & 0b11111) & (cpu.interrupts_enabled_register & 0b11111)
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.cycles += 4


def CP_FE(cpu, v): # FE CP d8
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
    cpu.cycles += 8


def RST_FF(cpu): # FF RST 38H
    cpu.PC += 1
    cpu.PC &= 0xFFFF
    cpu.mb.setitem((cpu.SP-1) & 0xFFFF, cpu.PC >> 8) # High
    cpu.mb.setitem((cpu.SP-2) & 0xFFFF, cpu.PC & 0xFF) # Low
    cpu.SP -= 2
    cpu.SP &= 0xFFFF
    cpu.PC = 56
    cpu.cycles += 16


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


def RLC_106(cpu): # 106 RLC (HL)
    cpu.cycles += 4
    t = (cpu.mb.getitem(cpu.HL) << 1) + (cpu.mb.getitem(cpu.HL) >> 7)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


def RRC_10E(cpu): # 10E RRC (HL)
    cpu.cycles += 4
    t = (cpu.mb.getitem(cpu.HL) >> 1) + ((cpu.mb.getitem(cpu.HL) & 1) << 7) + ((cpu.mb.getitem(cpu.HL) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


def RL_116(cpu): # 116 RL (HL)
    cpu.cycles += 4
    t = (cpu.mb.getitem(cpu.HL) << 1) + ((cpu.F & (1 << FLAGC)) != 0)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


def RR_11E(cpu): # 11E RR (HL)
    cpu.cycles += 4
    t = (cpu.mb.getitem(cpu.HL) >> 1) + (((cpu.F & (1 << FLAGC)) != 0) << 7) + ((cpu.mb.getitem(cpu.HL) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


def SLA_126(cpu): # 126 SLA (HL)
    cpu.cycles += 4
    t = (cpu.mb.getitem(cpu.HL) << 1)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


def SRA_12E(cpu): # 12E SRA (HL)
    cpu.cycles += 4
    t = ((cpu.mb.getitem(cpu.HL) >> 1) | (cpu.mb.getitem(cpu.HL) & 0x80)) + ((cpu.mb.getitem(cpu.HL) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


def SWAP_136(cpu): # 136 SWAP (HL)
    cpu.cycles += 4
    t = ((cpu.mb.getitem(cpu.HL) & 0xF0) >> 4) | ((cpu.mb.getitem(cpu.HL) & 0x0F) << 4)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


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
    cpu.cycles += 8


def SRL_13E(cpu): # 13E SRL (HL)
    cpu.cycles += 4
    t = (cpu.mb.getitem(cpu.HL) >> 1) + ((cpu.mb.getitem(cpu.HL) & 1) << 8)
    flag = 0b00000000
    flag += ((t & 0xFF) == 0) << FLAGZ
    flag += (t > 0xFF) << FLAGC
    cpu.F &= 0b00000000
    cpu.F |= flag
    t &= 0xFF
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


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
    cpu.cycles += 8


def BIT_140(cpu): # 140 BIT 0,B
    t = cpu.B & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_141(cpu): # 141 BIT 0,C
    t = cpu.C & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_142(cpu): # 142 BIT 0,D
    t = cpu.D & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_143(cpu): # 143 BIT 0,E
    t = cpu.E & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_144(cpu): # 144 BIT 0,H
    t = (cpu.HL >> 8) & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_145(cpu): # 145 BIT 0,L
    t = (cpu.HL & 0xFF) & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_146(cpu): # 146 BIT 0,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_147(cpu): # 147 BIT 0,A
    t = cpu.A & (1 << 0)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_148(cpu): # 148 BIT 1,B
    t = cpu.B & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_149(cpu): # 149 BIT 1,C
    t = cpu.C & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_14A(cpu): # 14A BIT 1,D
    t = cpu.D & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_14B(cpu): # 14B BIT 1,E
    t = cpu.E & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_14C(cpu): # 14C BIT 1,H
    t = (cpu.HL >> 8) & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_14D(cpu): # 14D BIT 1,L
    t = (cpu.HL & 0xFF) & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_14E(cpu): # 14E BIT 1,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_14F(cpu): # 14F BIT 1,A
    t = cpu.A & (1 << 1)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_150(cpu): # 150 BIT 2,B
    t = cpu.B & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_151(cpu): # 151 BIT 2,C
    t = cpu.C & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_152(cpu): # 152 BIT 2,D
    t = cpu.D & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_153(cpu): # 153 BIT 2,E
    t = cpu.E & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_154(cpu): # 154 BIT 2,H
    t = (cpu.HL >> 8) & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_155(cpu): # 155 BIT 2,L
    t = (cpu.HL & 0xFF) & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_156(cpu): # 156 BIT 2,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_157(cpu): # 157 BIT 2,A
    t = cpu.A & (1 << 2)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_158(cpu): # 158 BIT 3,B
    t = cpu.B & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_159(cpu): # 159 BIT 3,C
    t = cpu.C & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_15A(cpu): # 15A BIT 3,D
    t = cpu.D & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_15B(cpu): # 15B BIT 3,E
    t = cpu.E & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_15C(cpu): # 15C BIT 3,H
    t = (cpu.HL >> 8) & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_15D(cpu): # 15D BIT 3,L
    t = (cpu.HL & 0xFF) & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_15E(cpu): # 15E BIT 3,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_15F(cpu): # 15F BIT 3,A
    t = cpu.A & (1 << 3)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_160(cpu): # 160 BIT 4,B
    t = cpu.B & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_161(cpu): # 161 BIT 4,C
    t = cpu.C & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_162(cpu): # 162 BIT 4,D
    t = cpu.D & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_163(cpu): # 163 BIT 4,E
    t = cpu.E & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_164(cpu): # 164 BIT 4,H
    t = (cpu.HL >> 8) & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_165(cpu): # 165 BIT 4,L
    t = (cpu.HL & 0xFF) & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_166(cpu): # 166 BIT 4,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_167(cpu): # 167 BIT 4,A
    t = cpu.A & (1 << 4)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_168(cpu): # 168 BIT 5,B
    t = cpu.B & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_169(cpu): # 169 BIT 5,C
    t = cpu.C & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_16A(cpu): # 16A BIT 5,D
    t = cpu.D & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_16B(cpu): # 16B BIT 5,E
    t = cpu.E & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_16C(cpu): # 16C BIT 5,H
    t = (cpu.HL >> 8) & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_16D(cpu): # 16D BIT 5,L
    t = (cpu.HL & 0xFF) & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_16E(cpu): # 16E BIT 5,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_16F(cpu): # 16F BIT 5,A
    t = cpu.A & (1 << 5)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_170(cpu): # 170 BIT 6,B
    t = cpu.B & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_171(cpu): # 171 BIT 6,C
    t = cpu.C & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_172(cpu): # 172 BIT 6,D
    t = cpu.D & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_173(cpu): # 173 BIT 6,E
    t = cpu.E & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_174(cpu): # 174 BIT 6,H
    t = (cpu.HL >> 8) & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_175(cpu): # 175 BIT 6,L
    t = (cpu.HL & 0xFF) & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_176(cpu): # 176 BIT 6,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_177(cpu): # 177 BIT 6,A
    t = cpu.A & (1 << 6)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_178(cpu): # 178 BIT 7,B
    t = cpu.B & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_179(cpu): # 179 BIT 7,C
    t = cpu.C & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_17A(cpu): # 17A BIT 7,D
    t = cpu.D & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_17B(cpu): # 17B BIT 7,E
    t = cpu.E & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_17C(cpu): # 17C BIT 7,H
    t = (cpu.HL >> 8) & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_17D(cpu): # 17D BIT 7,L
    t = (cpu.HL & 0xFF) & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_17E(cpu): # 17E BIT 7,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def BIT_17F(cpu): # 17F BIT 7,A
    t = cpu.A & (1 << 7)
    flag = 0b00100000
    flag += ((t & 0xFF) == 0) << FLAGZ
    cpu.F &= 0b00010000
    cpu.F |= flag
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_180(cpu): # 180 RES 0,B
    t = cpu.B & ~(1 << 0)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_181(cpu): # 181 RES 0,C
    t = cpu.C & ~(1 << 0)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_182(cpu): # 182 RES 0,D
    t = cpu.D & ~(1 << 0)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_183(cpu): # 183 RES 0,E
    t = cpu.E & ~(1 << 0)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_184(cpu): # 184 RES 0,H
    t = (cpu.HL >> 8) & ~(1 << 0)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_185(cpu): # 185 RES 0,L
    t = (cpu.HL & 0xFF) & ~(1 << 0)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_186(cpu): # 186 RES 0,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 0)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_187(cpu): # 187 RES 0,A
    t = cpu.A & ~(1 << 0)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_188(cpu): # 188 RES 1,B
    t = cpu.B & ~(1 << 1)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_189(cpu): # 189 RES 1,C
    t = cpu.C & ~(1 << 1)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_18A(cpu): # 18A RES 1,D
    t = cpu.D & ~(1 << 1)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_18B(cpu): # 18B RES 1,E
    t = cpu.E & ~(1 << 1)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_18C(cpu): # 18C RES 1,H
    t = (cpu.HL >> 8) & ~(1 << 1)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_18D(cpu): # 18D RES 1,L
    t = (cpu.HL & 0xFF) & ~(1 << 1)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_18E(cpu): # 18E RES 1,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 1)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_18F(cpu): # 18F RES 1,A
    t = cpu.A & ~(1 << 1)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_190(cpu): # 190 RES 2,B
    t = cpu.B & ~(1 << 2)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_191(cpu): # 191 RES 2,C
    t = cpu.C & ~(1 << 2)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_192(cpu): # 192 RES 2,D
    t = cpu.D & ~(1 << 2)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_193(cpu): # 193 RES 2,E
    t = cpu.E & ~(1 << 2)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_194(cpu): # 194 RES 2,H
    t = (cpu.HL >> 8) & ~(1 << 2)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_195(cpu): # 195 RES 2,L
    t = (cpu.HL & 0xFF) & ~(1 << 2)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_196(cpu): # 196 RES 2,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 2)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_197(cpu): # 197 RES 2,A
    t = cpu.A & ~(1 << 2)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_198(cpu): # 198 RES 3,B
    t = cpu.B & ~(1 << 3)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_199(cpu): # 199 RES 3,C
    t = cpu.C & ~(1 << 3)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_19A(cpu): # 19A RES 3,D
    t = cpu.D & ~(1 << 3)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_19B(cpu): # 19B RES 3,E
    t = cpu.E & ~(1 << 3)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_19C(cpu): # 19C RES 3,H
    t = (cpu.HL >> 8) & ~(1 << 3)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_19D(cpu): # 19D RES 3,L
    t = (cpu.HL & 0xFF) & ~(1 << 3)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_19E(cpu): # 19E RES 3,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 3)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_19F(cpu): # 19F RES 3,A
    t = cpu.A & ~(1 << 3)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1A0(cpu): # 1A0 RES 4,B
    t = cpu.B & ~(1 << 4)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1A1(cpu): # 1A1 RES 4,C
    t = cpu.C & ~(1 << 4)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1A2(cpu): # 1A2 RES 4,D
    t = cpu.D & ~(1 << 4)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1A3(cpu): # 1A3 RES 4,E
    t = cpu.E & ~(1 << 4)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1A4(cpu): # 1A4 RES 4,H
    t = (cpu.HL >> 8) & ~(1 << 4)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1A5(cpu): # 1A5 RES 4,L
    t = (cpu.HL & 0xFF) & ~(1 << 4)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1A6(cpu): # 1A6 RES 4,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 4)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1A7(cpu): # 1A7 RES 4,A
    t = cpu.A & ~(1 << 4)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1A8(cpu): # 1A8 RES 5,B
    t = cpu.B & ~(1 << 5)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1A9(cpu): # 1A9 RES 5,C
    t = cpu.C & ~(1 << 5)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1AA(cpu): # 1AA RES 5,D
    t = cpu.D & ~(1 << 5)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1AB(cpu): # 1AB RES 5,E
    t = cpu.E & ~(1 << 5)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1AC(cpu): # 1AC RES 5,H
    t = (cpu.HL >> 8) & ~(1 << 5)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1AD(cpu): # 1AD RES 5,L
    t = (cpu.HL & 0xFF) & ~(1 << 5)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1AE(cpu): # 1AE RES 5,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 5)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1AF(cpu): # 1AF RES 5,A
    t = cpu.A & ~(1 << 5)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1B0(cpu): # 1B0 RES 6,B
    t = cpu.B & ~(1 << 6)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1B1(cpu): # 1B1 RES 6,C
    t = cpu.C & ~(1 << 6)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1B2(cpu): # 1B2 RES 6,D
    t = cpu.D & ~(1 << 6)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1B3(cpu): # 1B3 RES 6,E
    t = cpu.E & ~(1 << 6)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1B4(cpu): # 1B4 RES 6,H
    t = (cpu.HL >> 8) & ~(1 << 6)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1B5(cpu): # 1B5 RES 6,L
    t = (cpu.HL & 0xFF) & ~(1 << 6)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1B6(cpu): # 1B6 RES 6,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 6)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1B7(cpu): # 1B7 RES 6,A
    t = cpu.A & ~(1 << 6)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1B8(cpu): # 1B8 RES 7,B
    t = cpu.B & ~(1 << 7)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1B9(cpu): # 1B9 RES 7,C
    t = cpu.C & ~(1 << 7)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1BA(cpu): # 1BA RES 7,D
    t = cpu.D & ~(1 << 7)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1BB(cpu): # 1BB RES 7,E
    t = cpu.E & ~(1 << 7)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1BC(cpu): # 1BC RES 7,H
    t = (cpu.HL >> 8) & ~(1 << 7)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1BD(cpu): # 1BD RES 7,L
    t = (cpu.HL & 0xFF) & ~(1 << 7)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1BE(cpu): # 1BE RES 7,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) & ~(1 << 7)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def RES_1BF(cpu): # 1BF RES 7,A
    t = cpu.A & ~(1 << 7)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1C0(cpu): # 1C0 SET 0,B
    t = cpu.B | (1 << 0)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1C1(cpu): # 1C1 SET 0,C
    t = cpu.C | (1 << 0)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1C2(cpu): # 1C2 SET 0,D
    t = cpu.D | (1 << 0)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1C3(cpu): # 1C3 SET 0,E
    t = cpu.E | (1 << 0)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1C4(cpu): # 1C4 SET 0,H
    t = (cpu.HL >> 8) | (1 << 0)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1C5(cpu): # 1C5 SET 0,L
    t = (cpu.HL & 0xFF) | (1 << 0)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1C6(cpu): # 1C6 SET 0,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) | (1 << 0)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1C7(cpu): # 1C7 SET 0,A
    t = cpu.A | (1 << 0)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1C8(cpu): # 1C8 SET 1,B
    t = cpu.B | (1 << 1)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1C9(cpu): # 1C9 SET 1,C
    t = cpu.C | (1 << 1)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1CA(cpu): # 1CA SET 1,D
    t = cpu.D | (1 << 1)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1CB(cpu): # 1CB SET 1,E
    t = cpu.E | (1 << 1)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1CC(cpu): # 1CC SET 1,H
    t = (cpu.HL >> 8) | (1 << 1)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1CD(cpu): # 1CD SET 1,L
    t = (cpu.HL & 0xFF) | (1 << 1)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1CE(cpu): # 1CE SET 1,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) | (1 << 1)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1CF(cpu): # 1CF SET 1,A
    t = cpu.A | (1 << 1)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1D0(cpu): # 1D0 SET 2,B
    t = cpu.B | (1 << 2)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1D1(cpu): # 1D1 SET 2,C
    t = cpu.C | (1 << 2)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1D2(cpu): # 1D2 SET 2,D
    t = cpu.D | (1 << 2)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1D3(cpu): # 1D3 SET 2,E
    t = cpu.E | (1 << 2)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1D4(cpu): # 1D4 SET 2,H
    t = (cpu.HL >> 8) | (1 << 2)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1D5(cpu): # 1D5 SET 2,L
    t = (cpu.HL & 0xFF) | (1 << 2)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1D6(cpu): # 1D6 SET 2,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) | (1 << 2)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1D7(cpu): # 1D7 SET 2,A
    t = cpu.A | (1 << 2)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1D8(cpu): # 1D8 SET 3,B
    t = cpu.B | (1 << 3)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1D9(cpu): # 1D9 SET 3,C
    t = cpu.C | (1 << 3)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1DA(cpu): # 1DA SET 3,D
    t = cpu.D | (1 << 3)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1DB(cpu): # 1DB SET 3,E
    t = cpu.E | (1 << 3)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1DC(cpu): # 1DC SET 3,H
    t = (cpu.HL >> 8) | (1 << 3)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1DD(cpu): # 1DD SET 3,L
    t = (cpu.HL & 0xFF) | (1 << 3)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1DE(cpu): # 1DE SET 3,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) | (1 << 3)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1DF(cpu): # 1DF SET 3,A
    t = cpu.A | (1 << 3)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1E0(cpu): # 1E0 SET 4,B
    t = cpu.B | (1 << 4)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1E1(cpu): # 1E1 SET 4,C
    t = cpu.C | (1 << 4)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1E2(cpu): # 1E2 SET 4,D
    t = cpu.D | (1 << 4)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1E3(cpu): # 1E3 SET 4,E
    t = cpu.E | (1 << 4)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1E4(cpu): # 1E4 SET 4,H
    t = (cpu.HL >> 8) | (1 << 4)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1E5(cpu): # 1E5 SET 4,L
    t = (cpu.HL & 0xFF) | (1 << 4)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1E6(cpu): # 1E6 SET 4,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) | (1 << 4)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1E7(cpu): # 1E7 SET 4,A
    t = cpu.A | (1 << 4)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1E8(cpu): # 1E8 SET 5,B
    t = cpu.B | (1 << 5)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1E9(cpu): # 1E9 SET 5,C
    t = cpu.C | (1 << 5)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1EA(cpu): # 1EA SET 5,D
    t = cpu.D | (1 << 5)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1EB(cpu): # 1EB SET 5,E
    t = cpu.E | (1 << 5)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1EC(cpu): # 1EC SET 5,H
    t = (cpu.HL >> 8) | (1 << 5)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1ED(cpu): # 1ED SET 5,L
    t = (cpu.HL & 0xFF) | (1 << 5)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1EE(cpu): # 1EE SET 5,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) | (1 << 5)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1EF(cpu): # 1EF SET 5,A
    t = cpu.A | (1 << 5)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1F0(cpu): # 1F0 SET 6,B
    t = cpu.B | (1 << 6)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1F1(cpu): # 1F1 SET 6,C
    t = cpu.C | (1 << 6)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1F2(cpu): # 1F2 SET 6,D
    t = cpu.D | (1 << 6)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1F3(cpu): # 1F3 SET 6,E
    t = cpu.E | (1 << 6)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1F4(cpu): # 1F4 SET 6,H
    t = (cpu.HL >> 8) | (1 << 6)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1F5(cpu): # 1F5 SET 6,L
    t = (cpu.HL & 0xFF) | (1 << 6)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1F6(cpu): # 1F6 SET 6,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) | (1 << 6)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1F7(cpu): # 1F7 SET 6,A
    t = cpu.A | (1 << 6)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1F8(cpu): # 1F8 SET 7,B
    t = cpu.B | (1 << 7)
    cpu.B = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1F9(cpu): # 1F9 SET 7,C
    t = cpu.C | (1 << 7)
    cpu.C = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1FA(cpu): # 1FA SET 7,D
    t = cpu.D | (1 << 7)
    cpu.D = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1FB(cpu): # 1FB SET 7,E
    t = cpu.E | (1 << 7)
    cpu.E = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1FC(cpu): # 1FC SET 7,H
    t = (cpu.HL >> 8) | (1 << 7)
    cpu.HL = (cpu.HL & 0x00FF) | (t << 8)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1FD(cpu): # 1FD SET 7,L
    t = (cpu.HL & 0xFF) | (1 << 7)
    cpu.HL = (cpu.HL & 0xFF00) | (t & 0xFF)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1FE(cpu): # 1FE SET 7,(HL)
    cpu.cycles += 4
    t = cpu.mb.getitem(cpu.HL) | (1 << 7)
    cpu.cycles += 4
    cpu.mb.setitem(cpu.HL, t)
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def SET_1FF(cpu): # 1FF SET 7,A
    t = cpu.A | (1 << 7)
    cpu.A = t
    cpu.PC += 2
    cpu.PC &= 0xFFFF
    cpu.cycles += 8


def no_opcode(cpu):
    return 0



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
    elif opcode == 0x0A:
        return LD_0A(cpu)
    elif opcode == 0x0B:
        return DEC_0B(cpu)
    elif opcode == 0x0C:
        return INC_0C(cpu)
    elif opcode == 0x0D:
        return DEC_0D(cpu)
    elif opcode == 0x0E:
        return LD_0E(cpu, v)
    elif opcode == 0x0F:
        return RRCA_0F(cpu)
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
    elif opcode == 0x1A:
        return LD_1A(cpu)
    elif opcode == 0x1B:
        return DEC_1B(cpu)
    elif opcode == 0x1C:
        return INC_1C(cpu)
    elif opcode == 0x1D:
        return DEC_1D(cpu)
    elif opcode == 0x1E:
        return LD_1E(cpu, v)
    elif opcode == 0x1F:
        return RRA_1F(cpu)
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
    elif opcode == 0x2A:
        return LD_2A(cpu)
    elif opcode == 0x2B:
        return DEC_2B(cpu)
    elif opcode == 0x2C:
        return INC_2C(cpu)
    elif opcode == 0x2D:
        return DEC_2D(cpu)
    elif opcode == 0x2E:
        return LD_2E(cpu, v)
    elif opcode == 0x2F:
        return CPL_2F(cpu)
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
    elif opcode == 0x3A:
        return LD_3A(cpu)
    elif opcode == 0x3B:
        return DEC_3B(cpu)
    elif opcode == 0x3C:
        return INC_3C(cpu)
    elif opcode == 0x3D:
        return DEC_3D(cpu)
    elif opcode == 0x3E:
        return LD_3E(cpu, v)
    elif opcode == 0x3F:
        return CCF_3F(cpu)
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
    elif opcode == 0x4A:
        return LD_4A(cpu)
    elif opcode == 0x4B:
        return LD_4B(cpu)
    elif opcode == 0x4C:
        return LD_4C(cpu)
    elif opcode == 0x4D:
        return LD_4D(cpu)
    elif opcode == 0x4E:
        return LD_4E(cpu)
    elif opcode == 0x4F:
        return LD_4F(cpu)
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
    elif opcode == 0x5A:
        return LD_5A(cpu)
    elif opcode == 0x5B:
        return LD_5B(cpu)
    elif opcode == 0x5C:
        return LD_5C(cpu)
    elif opcode == 0x5D:
        return LD_5D(cpu)
    elif opcode == 0x5E:
        return LD_5E(cpu)
    elif opcode == 0x5F:
        return LD_5F(cpu)
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
    elif opcode == 0x6A:
        return LD_6A(cpu)
    elif opcode == 0x6B:
        return LD_6B(cpu)
    elif opcode == 0x6C:
        return LD_6C(cpu)
    elif opcode == 0x6D:
        return LD_6D(cpu)
    elif opcode == 0x6E:
        return LD_6E(cpu)
    elif opcode == 0x6F:
        return LD_6F(cpu)
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
    elif opcode == 0x7A:
        return LD_7A(cpu)
    elif opcode == 0x7B:
        return LD_7B(cpu)
    elif opcode == 0x7C:
        return LD_7C(cpu)
    elif opcode == 0x7D:
        return LD_7D(cpu)
    elif opcode == 0x7E:
        return LD_7E(cpu)
    elif opcode == 0x7F:
        return LD_7F(cpu)
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
    elif opcode == 0x8A:
        return ADC_8A(cpu)
    elif opcode == 0x8B:
        return ADC_8B(cpu)
    elif opcode == 0x8C:
        return ADC_8C(cpu)
    elif opcode == 0x8D:
        return ADC_8D(cpu)
    elif opcode == 0x8E:
        return ADC_8E(cpu)
    elif opcode == 0x8F:
        return ADC_8F(cpu)
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
    elif opcode == 0x9A:
        return SBC_9A(cpu)
    elif opcode == 0x9B:
        return SBC_9B(cpu)
    elif opcode == 0x9C:
        return SBC_9C(cpu)
    elif opcode == 0x9D:
        return SBC_9D(cpu)
    elif opcode == 0x9E:
        return SBC_9E(cpu)
    elif opcode == 0x9F:
        return SBC_9F(cpu)
    elif opcode == 0xA0:
        return AND_A0(cpu)
    elif opcode == 0xA1:
        return AND_A1(cpu)
    elif opcode == 0xA2:
        return AND_A2(cpu)
    elif opcode == 0xA3:
        return AND_A3(cpu)
    elif opcode == 0xA4:
        return AND_A4(cpu)
    elif opcode == 0xA5:
        return AND_A5(cpu)
    elif opcode == 0xA6:
        return AND_A6(cpu)
    elif opcode == 0xA7:
        return AND_A7(cpu)
    elif opcode == 0xA8:
        return XOR_A8(cpu)
    elif opcode == 0xA9:
        return XOR_A9(cpu)
    elif opcode == 0xAA:
        return XOR_AA(cpu)
    elif opcode == 0xAB:
        return XOR_AB(cpu)
    elif opcode == 0xAC:
        return XOR_AC(cpu)
    elif opcode == 0xAD:
        return XOR_AD(cpu)
    elif opcode == 0xAE:
        return XOR_AE(cpu)
    elif opcode == 0xAF:
        return XOR_AF(cpu)
    elif opcode == 0xB0:
        return OR_B0(cpu)
    elif opcode == 0xB1:
        return OR_B1(cpu)
    elif opcode == 0xB2:
        return OR_B2(cpu)
    elif opcode == 0xB3:
        return OR_B3(cpu)
    elif opcode == 0xB4:
        return OR_B4(cpu)
    elif opcode == 0xB5:
        return OR_B5(cpu)
    elif opcode == 0xB6:
        return OR_B6(cpu)
    elif opcode == 0xB7:
        return OR_B7(cpu)
    elif opcode == 0xB8:
        return CP_B8(cpu)
    elif opcode == 0xB9:
        return CP_B9(cpu)
    elif opcode == 0xBA:
        return CP_BA(cpu)
    elif opcode == 0xBB:
        return CP_BB(cpu)
    elif opcode == 0xBC:
        return CP_BC(cpu)
    elif opcode == 0xBD:
        return CP_BD(cpu)
    elif opcode == 0xBE:
        return CP_BE(cpu)
    elif opcode == 0xBF:
        return CP_BF(cpu)
    elif opcode == 0xC0:
        return RET_C0(cpu)
    elif opcode == 0xC1:
        return POP_C1(cpu)
    elif opcode == 0xC2:
        return JP_C2(cpu, v)
    elif opcode == 0xC3:
        return JP_C3(cpu, v)
    elif opcode == 0xC4:
        return CALL_C4(cpu, v)
    elif opcode == 0xC5:
        return PUSH_C5(cpu)
    elif opcode == 0xC6:
        return ADD_C6(cpu, v)
    elif opcode == 0xC7:
        return RST_C7(cpu)
    elif opcode == 0xC8:
        return RET_C8(cpu)
    elif opcode == 0xC9:
        return RET_C9(cpu)
    elif opcode == 0xCA:
        return JP_CA(cpu, v)
    elif opcode == 0xCB:
        return PREFIX_CB(cpu)
    elif opcode == 0xCC:
        return CALL_CC(cpu, v)
    elif opcode == 0xCD:
        return CALL_CD(cpu, v)
    elif opcode == 0xCE:
        return ADC_CE(cpu, v)
    elif opcode == 0xCF:
        return RST_CF(cpu)
    elif opcode == 0xD0:
        return RET_D0(cpu)
    elif opcode == 0xD1:
        return POP_D1(cpu)
    elif opcode == 0xD2:
        return JP_D2(cpu, v)
    elif opcode == 0xD3:
        return no_opcode(cpu)
    elif opcode == 0xD4:
        return CALL_D4(cpu, v)
    elif opcode == 0xD5:
        return PUSH_D5(cpu)
    elif opcode == 0xD6:
        return SUB_D6(cpu, v)
    elif opcode == 0xD7:
        return RST_D7(cpu)
    elif opcode == 0xD8:
        return RET_D8(cpu)
    elif opcode == 0xD9:
        return RETI_D9(cpu)
    elif opcode == 0xDA:
        return JP_DA(cpu, v)
    elif opcode == 0xDB:
        return BRK(cpu)
    elif opcode == 0xDC:
        return CALL_DC(cpu, v)
    elif opcode == 0xDD:
        return no_opcode(cpu)
    elif opcode == 0xDE:
        return SBC_DE(cpu, v)
    elif opcode == 0xDF:
        return RST_DF(cpu)
    elif opcode == 0xE0:
        return LDH_E0(cpu, v)
    elif opcode == 0xE1:
        return POP_E1(cpu)
    elif opcode == 0xE2:
        return LD_E2(cpu)
    elif opcode == 0xE3:
        return no_opcode(cpu)
    elif opcode == 0xE4:
        return no_opcode(cpu)
    elif opcode == 0xE5:
        return PUSH_E5(cpu)
    elif opcode == 0xE6:
        return AND_E6(cpu, v)
    elif opcode == 0xE7:
        return RST_E7(cpu)
    elif opcode == 0xE8:
        return ADD_E8(cpu, v)
    elif opcode == 0xE9:
        return JP_E9(cpu)
    elif opcode == 0xEA:
        return LD_EA(cpu, v)
    elif opcode == 0xEB:
        return no_opcode(cpu)
    elif opcode == 0xEC:
        return no_opcode(cpu)
    elif opcode == 0xED:
        return no_opcode(cpu)
    elif opcode == 0xEE:
        return XOR_EE(cpu, v)
    elif opcode == 0xEF:
        return RST_EF(cpu)
    elif opcode == 0xF0:
        return LDH_F0(cpu, v)
    elif opcode == 0xF1:
        return POP_F1(cpu)
    elif opcode == 0xF2:
        return LD_F2(cpu)
    elif opcode == 0xF3:
        return DI_F3(cpu)
    elif opcode == 0xF4:
        return no_opcode(cpu)
    elif opcode == 0xF5:
        return PUSH_F5(cpu)
    elif opcode == 0xF6:
        return OR_F6(cpu, v)
    elif opcode == 0xF7:
        return RST_F7(cpu)
    elif opcode == 0xF8:
        return LD_F8(cpu, v)
    elif opcode == 0xF9:
        return LD_F9(cpu)
    elif opcode == 0xFA:
        return LD_FA(cpu, v)
    elif opcode == 0xFB:
        return EI_FB(cpu)
    elif opcode == 0xFC:
        return no_opcode(cpu)
    elif opcode == 0xFD:
        return no_opcode(cpu)
    elif opcode == 0xFE:
        return CP_FE(cpu, v)
    elif opcode == 0xFF:
        return RST_FF(cpu)
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
    elif opcode == 0x10A:
        return RRC_10A(cpu)
    elif opcode == 0x10B:
        return RRC_10B(cpu)
    elif opcode == 0x10C:
        return RRC_10C(cpu)
    elif opcode == 0x10D:
        return RRC_10D(cpu)
    elif opcode == 0x10E:
        return RRC_10E(cpu)
    elif opcode == 0x10F:
        return RRC_10F(cpu)
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
    elif opcode == 0x11A:
        return RR_11A(cpu)
    elif opcode == 0x11B:
        return RR_11B(cpu)
    elif opcode == 0x11C:
        return RR_11C(cpu)
    elif opcode == 0x11D:
        return RR_11D(cpu)
    elif opcode == 0x11E:
        return RR_11E(cpu)
    elif opcode == 0x11F:
        return RR_11F(cpu)
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
    elif opcode == 0x12A:
        return SRA_12A(cpu)
    elif opcode == 0x12B:
        return SRA_12B(cpu)
    elif opcode == 0x12C:
        return SRA_12C(cpu)
    elif opcode == 0x12D:
        return SRA_12D(cpu)
    elif opcode == 0x12E:
        return SRA_12E(cpu)
    elif opcode == 0x12F:
        return SRA_12F(cpu)
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
    elif opcode == 0x13A:
        return SRL_13A(cpu)
    elif opcode == 0x13B:
        return SRL_13B(cpu)
    elif opcode == 0x13C:
        return SRL_13C(cpu)
    elif opcode == 0x13D:
        return SRL_13D(cpu)
    elif opcode == 0x13E:
        return SRL_13E(cpu)
    elif opcode == 0x13F:
        return SRL_13F(cpu)
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
    elif opcode == 0x14A:
        return BIT_14A(cpu)
    elif opcode == 0x14B:
        return BIT_14B(cpu)
    elif opcode == 0x14C:
        return BIT_14C(cpu)
    elif opcode == 0x14D:
        return BIT_14D(cpu)
    elif opcode == 0x14E:
        return BIT_14E(cpu)
    elif opcode == 0x14F:
        return BIT_14F(cpu)
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
    elif opcode == 0x15A:
        return BIT_15A(cpu)
    elif opcode == 0x15B:
        return BIT_15B(cpu)
    elif opcode == 0x15C:
        return BIT_15C(cpu)
    elif opcode == 0x15D:
        return BIT_15D(cpu)
    elif opcode == 0x15E:
        return BIT_15E(cpu)
    elif opcode == 0x15F:
        return BIT_15F(cpu)
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
    elif opcode == 0x16A:
        return BIT_16A(cpu)
    elif opcode == 0x16B:
        return BIT_16B(cpu)
    elif opcode == 0x16C:
        return BIT_16C(cpu)
    elif opcode == 0x16D:
        return BIT_16D(cpu)
    elif opcode == 0x16E:
        return BIT_16E(cpu)
    elif opcode == 0x16F:
        return BIT_16F(cpu)
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
    elif opcode == 0x17A:
        return BIT_17A(cpu)
    elif opcode == 0x17B:
        return BIT_17B(cpu)
    elif opcode == 0x17C:
        return BIT_17C(cpu)
    elif opcode == 0x17D:
        return BIT_17D(cpu)
    elif opcode == 0x17E:
        return BIT_17E(cpu)
    elif opcode == 0x17F:
        return BIT_17F(cpu)
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
    elif opcode == 0x18A:
        return RES_18A(cpu)
    elif opcode == 0x18B:
        return RES_18B(cpu)
    elif opcode == 0x18C:
        return RES_18C(cpu)
    elif opcode == 0x18D:
        return RES_18D(cpu)
    elif opcode == 0x18E:
        return RES_18E(cpu)
    elif opcode == 0x18F:
        return RES_18F(cpu)
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
    elif opcode == 0x19A:
        return RES_19A(cpu)
    elif opcode == 0x19B:
        return RES_19B(cpu)
    elif opcode == 0x19C:
        return RES_19C(cpu)
    elif opcode == 0x19D:
        return RES_19D(cpu)
    elif opcode == 0x19E:
        return RES_19E(cpu)
    elif opcode == 0x19F:
        return RES_19F(cpu)
    elif opcode == 0x1A0:
        return RES_1A0(cpu)
    elif opcode == 0x1A1:
        return RES_1A1(cpu)
    elif opcode == 0x1A2:
        return RES_1A2(cpu)
    elif opcode == 0x1A3:
        return RES_1A3(cpu)
    elif opcode == 0x1A4:
        return RES_1A4(cpu)
    elif opcode == 0x1A5:
        return RES_1A5(cpu)
    elif opcode == 0x1A6:
        return RES_1A6(cpu)
    elif opcode == 0x1A7:
        return RES_1A7(cpu)
    elif opcode == 0x1A8:
        return RES_1A8(cpu)
    elif opcode == 0x1A9:
        return RES_1A9(cpu)
    elif opcode == 0x1AA:
        return RES_1AA(cpu)
    elif opcode == 0x1AB:
        return RES_1AB(cpu)
    elif opcode == 0x1AC:
        return RES_1AC(cpu)
    elif opcode == 0x1AD:
        return RES_1AD(cpu)
    elif opcode == 0x1AE:
        return RES_1AE(cpu)
    elif opcode == 0x1AF:
        return RES_1AF(cpu)
    elif opcode == 0x1B0:
        return RES_1B0(cpu)
    elif opcode == 0x1B1:
        return RES_1B1(cpu)
    elif opcode == 0x1B2:
        return RES_1B2(cpu)
    elif opcode == 0x1B3:
        return RES_1B3(cpu)
    elif opcode == 0x1B4:
        return RES_1B4(cpu)
    elif opcode == 0x1B5:
        return RES_1B5(cpu)
    elif opcode == 0x1B6:
        return RES_1B6(cpu)
    elif opcode == 0x1B7:
        return RES_1B7(cpu)
    elif opcode == 0x1B8:
        return RES_1B8(cpu)
    elif opcode == 0x1B9:
        return RES_1B9(cpu)
    elif opcode == 0x1BA:
        return RES_1BA(cpu)
    elif opcode == 0x1BB:
        return RES_1BB(cpu)
    elif opcode == 0x1BC:
        return RES_1BC(cpu)
    elif opcode == 0x1BD:
        return RES_1BD(cpu)
    elif opcode == 0x1BE:
        return RES_1BE(cpu)
    elif opcode == 0x1BF:
        return RES_1BF(cpu)
    elif opcode == 0x1C0:
        return SET_1C0(cpu)
    elif opcode == 0x1C1:
        return SET_1C1(cpu)
    elif opcode == 0x1C2:
        return SET_1C2(cpu)
    elif opcode == 0x1C3:
        return SET_1C3(cpu)
    elif opcode == 0x1C4:
        return SET_1C4(cpu)
    elif opcode == 0x1C5:
        return SET_1C5(cpu)
    elif opcode == 0x1C6:
        return SET_1C6(cpu)
    elif opcode == 0x1C7:
        return SET_1C7(cpu)
    elif opcode == 0x1C8:
        return SET_1C8(cpu)
    elif opcode == 0x1C9:
        return SET_1C9(cpu)
    elif opcode == 0x1CA:
        return SET_1CA(cpu)
    elif opcode == 0x1CB:
        return SET_1CB(cpu)
    elif opcode == 0x1CC:
        return SET_1CC(cpu)
    elif opcode == 0x1CD:
        return SET_1CD(cpu)
    elif opcode == 0x1CE:
        return SET_1CE(cpu)
    elif opcode == 0x1CF:
        return SET_1CF(cpu)
    elif opcode == 0x1D0:
        return SET_1D0(cpu)
    elif opcode == 0x1D1:
        return SET_1D1(cpu)
    elif opcode == 0x1D2:
        return SET_1D2(cpu)
    elif opcode == 0x1D3:
        return SET_1D3(cpu)
    elif opcode == 0x1D4:
        return SET_1D4(cpu)
    elif opcode == 0x1D5:
        return SET_1D5(cpu)
    elif opcode == 0x1D6:
        return SET_1D6(cpu)
    elif opcode == 0x1D7:
        return SET_1D7(cpu)
    elif opcode == 0x1D8:
        return SET_1D8(cpu)
    elif opcode == 0x1D9:
        return SET_1D9(cpu)
    elif opcode == 0x1DA:
        return SET_1DA(cpu)
    elif opcode == 0x1DB:
        return SET_1DB(cpu)
    elif opcode == 0x1DC:
        return SET_1DC(cpu)
    elif opcode == 0x1DD:
        return SET_1DD(cpu)
    elif opcode == 0x1DE:
        return SET_1DE(cpu)
    elif opcode == 0x1DF:
        return SET_1DF(cpu)
    elif opcode == 0x1E0:
        return SET_1E0(cpu)
    elif opcode == 0x1E1:
        return SET_1E1(cpu)
    elif opcode == 0x1E2:
        return SET_1E2(cpu)
    elif opcode == 0x1E3:
        return SET_1E3(cpu)
    elif opcode == 0x1E4:
        return SET_1E4(cpu)
    elif opcode == 0x1E5:
        return SET_1E5(cpu)
    elif opcode == 0x1E6:
        return SET_1E6(cpu)
    elif opcode == 0x1E7:
        return SET_1E7(cpu)
    elif opcode == 0x1E8:
        return SET_1E8(cpu)
    elif opcode == 0x1E9:
        return SET_1E9(cpu)
    elif opcode == 0x1EA:
        return SET_1EA(cpu)
    elif opcode == 0x1EB:
        return SET_1EB(cpu)
    elif opcode == 0x1EC:
        return SET_1EC(cpu)
    elif opcode == 0x1ED:
        return SET_1ED(cpu)
    elif opcode == 0x1EE:
        return SET_1EE(cpu)
    elif opcode == 0x1EF:
        return SET_1EF(cpu)
    elif opcode == 0x1F0:
        return SET_1F0(cpu)
    elif opcode == 0x1F1:
        return SET_1F1(cpu)
    elif opcode == 0x1F2:
        return SET_1F2(cpu)
    elif opcode == 0x1F3:
        return SET_1F3(cpu)
    elif opcode == 0x1F4:
        return SET_1F4(cpu)
    elif opcode == 0x1F5:
        return SET_1F5(cpu)
    elif opcode == 0x1F6:
        return SET_1F6(cpu)
    elif opcode == 0x1F7:
        return SET_1F7(cpu)
    elif opcode == 0x1F8:
        return SET_1F8(cpu)
    elif opcode == 0x1F9:
        return SET_1F9(cpu)
    elif opcode == 0x1FA:
        return SET_1FA(cpu)
    elif opcode == 0x1FB:
        return SET_1FB(cpu)
    elif opcode == 0x1FC:
        return SET_1FC(cpu)
    elif opcode == 0x1FD:
        return SET_1FD(cpu)
    elif opcode == 0x1FE:
        return SET_1FE(cpu)
    elif opcode == 0x1FF:
        return SET_1FF(cpu)


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
    1, 1, 3, 0, 3, 1, 2, 1, 1, 1, 3, 1, 3, 0, 2, 1,
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
    "Breakpoint/Illegal opcode",
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
