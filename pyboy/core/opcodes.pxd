
# THIS FILE IS AUTO-GENERATED!!!
# DO NOT MODIFY THIS FILE.
# CHANGES TO THE CODE SHOULD BE MADE IN 'opcodes_gen.py'.

from . cimport cpu
cimport cython
from libc.stdint cimport uint8_t, uint16_t, uint32_t


cdef uint16_t FLAGC, FLAGH, FLAGN, FLAGZ
cdef uint8_t[512] OPCODE_LENGTHS
@cython.locals(v=cython.int, a=cython.int, b=cython.int, pc=cython.ushort)
cdef int execute_opcode(cpu.CPU, uint16_t) noexcept

cdef uint8_t no_opcode(cpu.CPU) noexcept

@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t NOP_00(cpu.CPU) noexcept # 00 NOP
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_01(cpu.CPU, int v) noexcept # 01 LD BC,d16
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_02(cpu.CPU) noexcept # 02 LD (BC),A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t INC_03(cpu.CPU) noexcept # 03 INC BC
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t INC_04(cpu.CPU) noexcept # 04 INC B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t DEC_05(cpu.CPU) noexcept # 05 DEC B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_06(cpu.CPU, int v) noexcept # 06 LD B,d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RLCA_07(cpu.CPU) noexcept # 07 RLCA
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_08(cpu.CPU, int v) noexcept # 08 LD (a16),SP
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADD_09(cpu.CPU) noexcept # 09 ADD HL,BC
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_0A(cpu.CPU) noexcept # 0A LD A,(BC)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t DEC_0B(cpu.CPU) noexcept # 0B DEC BC
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t INC_0C(cpu.CPU) noexcept # 0C INC C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t DEC_0D(cpu.CPU) noexcept # 0D DEC C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_0E(cpu.CPU, int v) noexcept # 0E LD C,d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RRCA_0F(cpu.CPU) noexcept # 0F RRCA
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t STOP_10(cpu.CPU, int v) noexcept # 10 STOP 0
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_11(cpu.CPU, int v) noexcept # 11 LD DE,d16
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_12(cpu.CPU) noexcept # 12 LD (DE),A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t INC_13(cpu.CPU) noexcept # 13 INC DE
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t INC_14(cpu.CPU) noexcept # 14 INC D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t DEC_15(cpu.CPU) noexcept # 15 DEC D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_16(cpu.CPU, int v) noexcept # 16 LD D,d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RLA_17(cpu.CPU) noexcept # 17 RLA
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t JR_18(cpu.CPU, int v) noexcept # 18 JR r8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADD_19(cpu.CPU) noexcept # 19 ADD HL,DE
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_1A(cpu.CPU) noexcept # 1A LD A,(DE)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t DEC_1B(cpu.CPU) noexcept # 1B DEC DE
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t INC_1C(cpu.CPU) noexcept # 1C INC E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t DEC_1D(cpu.CPU) noexcept # 1D DEC E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_1E(cpu.CPU, int v) noexcept # 1E LD E,d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RRA_1F(cpu.CPU) noexcept # 1F RRA
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t JR_20(cpu.CPU, int v) noexcept # 20 JR NZ,r8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_21(cpu.CPU, int v) noexcept # 21 LD HL,d16
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_22(cpu.CPU) noexcept # 22 LD (HL+),A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t INC_23(cpu.CPU) noexcept # 23 INC HL
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t INC_24(cpu.CPU) noexcept # 24 INC H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t DEC_25(cpu.CPU) noexcept # 25 DEC H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_26(cpu.CPU, int v) noexcept # 26 LD H,d8
@cython.locals(v=int, flag=uint8_t, t=int, corr=ushort)
cdef uint8_t DAA_27(cpu.CPU) noexcept # 27 DAA
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t JR_28(cpu.CPU, int v) noexcept # 28 JR Z,r8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADD_29(cpu.CPU) noexcept # 29 ADD HL,HL
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_2A(cpu.CPU) noexcept # 2A LD A,(HL+)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t DEC_2B(cpu.CPU) noexcept # 2B DEC HL
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t INC_2C(cpu.CPU) noexcept # 2C INC L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t DEC_2D(cpu.CPU) noexcept # 2D DEC L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_2E(cpu.CPU, int v) noexcept # 2E LD L,d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CPL_2F(cpu.CPU) noexcept # 2F CPL
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t JR_30(cpu.CPU, int v) noexcept # 30 JR NC,r8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_31(cpu.CPU, int v) noexcept # 31 LD SP,d16
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_32(cpu.CPU) noexcept # 32 LD (HL-),A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t INC_33(cpu.CPU) noexcept # 33 INC SP
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t INC_34(cpu.CPU) noexcept # 34 INC (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t DEC_35(cpu.CPU) noexcept # 35 DEC (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_36(cpu.CPU, int v) noexcept # 36 LD (HL),d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SCF_37(cpu.CPU) noexcept # 37 SCF
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t JR_38(cpu.CPU, int v) noexcept # 38 JR C,r8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADD_39(cpu.CPU) noexcept # 39 ADD HL,SP
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_3A(cpu.CPU) noexcept # 3A LD A,(HL-)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t DEC_3B(cpu.CPU) noexcept # 3B DEC SP
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t INC_3C(cpu.CPU) noexcept # 3C INC A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t DEC_3D(cpu.CPU) noexcept # 3D DEC A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_3E(cpu.CPU, int v) noexcept # 3E LD A,d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CCF_3F(cpu.CPU) noexcept # 3F CCF
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_40(cpu.CPU) noexcept # 40 LD B,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_41(cpu.CPU) noexcept # 41 LD B,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_42(cpu.CPU) noexcept # 42 LD B,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_43(cpu.CPU) noexcept # 43 LD B,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_44(cpu.CPU) noexcept # 44 LD B,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_45(cpu.CPU) noexcept # 45 LD B,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_46(cpu.CPU) noexcept # 46 LD B,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_47(cpu.CPU) noexcept # 47 LD B,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_48(cpu.CPU) noexcept # 48 LD C,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_49(cpu.CPU) noexcept # 49 LD C,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_4A(cpu.CPU) noexcept # 4A LD C,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_4B(cpu.CPU) noexcept # 4B LD C,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_4C(cpu.CPU) noexcept # 4C LD C,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_4D(cpu.CPU) noexcept # 4D LD C,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_4E(cpu.CPU) noexcept # 4E LD C,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_4F(cpu.CPU) noexcept # 4F LD C,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_50(cpu.CPU) noexcept # 50 LD D,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_51(cpu.CPU) noexcept # 51 LD D,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_52(cpu.CPU) noexcept # 52 LD D,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_53(cpu.CPU) noexcept # 53 LD D,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_54(cpu.CPU) noexcept # 54 LD D,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_55(cpu.CPU) noexcept # 55 LD D,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_56(cpu.CPU) noexcept # 56 LD D,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_57(cpu.CPU) noexcept # 57 LD D,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_58(cpu.CPU) noexcept # 58 LD E,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_59(cpu.CPU) noexcept # 59 LD E,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_5A(cpu.CPU) noexcept # 5A LD E,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_5B(cpu.CPU) noexcept # 5B LD E,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_5C(cpu.CPU) noexcept # 5C LD E,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_5D(cpu.CPU) noexcept # 5D LD E,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_5E(cpu.CPU) noexcept # 5E LD E,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_5F(cpu.CPU) noexcept # 5F LD E,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_60(cpu.CPU) noexcept # 60 LD H,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_61(cpu.CPU) noexcept # 61 LD H,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_62(cpu.CPU) noexcept # 62 LD H,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_63(cpu.CPU) noexcept # 63 LD H,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_64(cpu.CPU) noexcept # 64 LD H,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_65(cpu.CPU) noexcept # 65 LD H,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_66(cpu.CPU) noexcept # 66 LD H,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_67(cpu.CPU) noexcept # 67 LD H,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_68(cpu.CPU) noexcept # 68 LD L,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_69(cpu.CPU) noexcept # 69 LD L,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_6A(cpu.CPU) noexcept # 6A LD L,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_6B(cpu.CPU) noexcept # 6B LD L,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_6C(cpu.CPU) noexcept # 6C LD L,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_6D(cpu.CPU) noexcept # 6D LD L,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_6E(cpu.CPU) noexcept # 6E LD L,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_6F(cpu.CPU) noexcept # 6F LD L,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_70(cpu.CPU) noexcept # 70 LD (HL),B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_71(cpu.CPU) noexcept # 71 LD (HL),C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_72(cpu.CPU) noexcept # 72 LD (HL),D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_73(cpu.CPU) noexcept # 73 LD (HL),E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_74(cpu.CPU) noexcept # 74 LD (HL),H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_75(cpu.CPU) noexcept # 75 LD (HL),L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t HALT_76(cpu.CPU) noexcept # 76 HALT
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_77(cpu.CPU) noexcept # 77 LD (HL),A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_78(cpu.CPU) noexcept # 78 LD A,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_79(cpu.CPU) noexcept # 79 LD A,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_7A(cpu.CPU) noexcept # 7A LD A,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_7B(cpu.CPU) noexcept # 7B LD A,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_7C(cpu.CPU) noexcept # 7C LD A,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_7D(cpu.CPU) noexcept # 7D LD A,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_7E(cpu.CPU) noexcept # 7E LD A,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_7F(cpu.CPU) noexcept # 7F LD A,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADD_80(cpu.CPU) noexcept # 80 ADD A,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADD_81(cpu.CPU) noexcept # 81 ADD A,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADD_82(cpu.CPU) noexcept # 82 ADD A,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADD_83(cpu.CPU) noexcept # 83 ADD A,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADD_84(cpu.CPU) noexcept # 84 ADD A,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADD_85(cpu.CPU) noexcept # 85 ADD A,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADD_86(cpu.CPU) noexcept # 86 ADD A,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADD_87(cpu.CPU) noexcept # 87 ADD A,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADC_88(cpu.CPU) noexcept # 88 ADC A,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADC_89(cpu.CPU) noexcept # 89 ADC A,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADC_8A(cpu.CPU) noexcept # 8A ADC A,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADC_8B(cpu.CPU) noexcept # 8B ADC A,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADC_8C(cpu.CPU) noexcept # 8C ADC A,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADC_8D(cpu.CPU) noexcept # 8D ADC A,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADC_8E(cpu.CPU) noexcept # 8E ADC A,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADC_8F(cpu.CPU) noexcept # 8F ADC A,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SUB_90(cpu.CPU) noexcept # 90 SUB B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SUB_91(cpu.CPU) noexcept # 91 SUB C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SUB_92(cpu.CPU) noexcept # 92 SUB D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SUB_93(cpu.CPU) noexcept # 93 SUB E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SUB_94(cpu.CPU) noexcept # 94 SUB H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SUB_95(cpu.CPU) noexcept # 95 SUB L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SUB_96(cpu.CPU) noexcept # 96 SUB (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SUB_97(cpu.CPU) noexcept # 97 SUB A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SBC_98(cpu.CPU) noexcept # 98 SBC A,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SBC_99(cpu.CPU) noexcept # 99 SBC A,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SBC_9A(cpu.CPU) noexcept # 9A SBC A,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SBC_9B(cpu.CPU) noexcept # 9B SBC A,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SBC_9C(cpu.CPU) noexcept # 9C SBC A,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SBC_9D(cpu.CPU) noexcept # 9D SBC A,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SBC_9E(cpu.CPU) noexcept # 9E SBC A,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SBC_9F(cpu.CPU) noexcept # 9F SBC A,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t AND_A0(cpu.CPU) noexcept # A0 AND B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t AND_A1(cpu.CPU) noexcept # A1 AND C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t AND_A2(cpu.CPU) noexcept # A2 AND D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t AND_A3(cpu.CPU) noexcept # A3 AND E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t AND_A4(cpu.CPU) noexcept # A4 AND H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t AND_A5(cpu.CPU) noexcept # A5 AND L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t AND_A6(cpu.CPU) noexcept # A6 AND (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t AND_A7(cpu.CPU) noexcept # A7 AND A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t XOR_A8(cpu.CPU) noexcept # A8 XOR B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t XOR_A9(cpu.CPU) noexcept # A9 XOR C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t XOR_AA(cpu.CPU) noexcept # AA XOR D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t XOR_AB(cpu.CPU) noexcept # AB XOR E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t XOR_AC(cpu.CPU) noexcept # AC XOR H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t XOR_AD(cpu.CPU) noexcept # AD XOR L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t XOR_AE(cpu.CPU) noexcept # AE XOR (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t XOR_AF(cpu.CPU) noexcept # AF XOR A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t OR_B0(cpu.CPU) noexcept # B0 OR B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t OR_B1(cpu.CPU) noexcept # B1 OR C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t OR_B2(cpu.CPU) noexcept # B2 OR D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t OR_B3(cpu.CPU) noexcept # B3 OR E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t OR_B4(cpu.CPU) noexcept # B4 OR H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t OR_B5(cpu.CPU) noexcept # B5 OR L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t OR_B6(cpu.CPU) noexcept # B6 OR (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t OR_B7(cpu.CPU) noexcept # B7 OR A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CP_B8(cpu.CPU) noexcept # B8 CP B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CP_B9(cpu.CPU) noexcept # B9 CP C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CP_BA(cpu.CPU) noexcept # BA CP D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CP_BB(cpu.CPU) noexcept # BB CP E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CP_BC(cpu.CPU) noexcept # BC CP H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CP_BD(cpu.CPU) noexcept # BD CP L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CP_BE(cpu.CPU) noexcept # BE CP (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CP_BF(cpu.CPU) noexcept # BF CP A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RET_C0(cpu.CPU) noexcept # C0 RET NZ
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t POP_C1(cpu.CPU) noexcept # C1 POP BC
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t JP_C2(cpu.CPU, int v) noexcept # C2 JP NZ,a16
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t JP_C3(cpu.CPU, int v) noexcept # C3 JP a16
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CALL_C4(cpu.CPU, int v) noexcept # C4 CALL NZ,a16
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t PUSH_C5(cpu.CPU) noexcept # C5 PUSH BC
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADD_C6(cpu.CPU, int v) noexcept # C6 ADD A,d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RST_C7(cpu.CPU) noexcept # C7 RST 00H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RET_C8(cpu.CPU) noexcept # C8 RET Z
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RET_C9(cpu.CPU) noexcept # C9 RET
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t JP_CA(cpu.CPU, int v) noexcept # CA JP Z,a16
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t PREFIX_CB(cpu.CPU) noexcept # CB PREFIX CB
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CALL_CC(cpu.CPU, int v) noexcept # CC CALL Z,a16
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CALL_CD(cpu.CPU, int v) noexcept # CD CALL a16
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADC_CE(cpu.CPU, int v) noexcept # CE ADC A,d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RST_CF(cpu.CPU) noexcept # CF RST 08H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RET_D0(cpu.CPU) noexcept # D0 RET NC
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t POP_D1(cpu.CPU) noexcept # D1 POP DE
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t JP_D2(cpu.CPU, int v) noexcept # D2 JP NC,a16
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CALL_D4(cpu.CPU, int v) noexcept # D4 CALL NC,a16
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t PUSH_D5(cpu.CPU) noexcept # D5 PUSH DE
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SUB_D6(cpu.CPU, int v) noexcept # D6 SUB d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RST_D7(cpu.CPU) noexcept # D7 RST 10H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RET_D8(cpu.CPU) noexcept # D8 RET C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RETI_D9(cpu.CPU) noexcept # D9 RETI
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t JP_DA(cpu.CPU, int v) noexcept # DA JP C,a16
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CALL_DC(cpu.CPU, int v) noexcept # DC CALL C,a16
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SBC_DE(cpu.CPU, int v) noexcept # DE SBC A,d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RST_DF(cpu.CPU) noexcept # DF RST 18H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LDH_E0(cpu.CPU, int v) noexcept # E0 LDH (a8),A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t POP_E1(cpu.CPU) noexcept # E1 POP HL
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_E2(cpu.CPU) noexcept # E2 LD (C),A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t PUSH_E5(cpu.CPU) noexcept # E5 PUSH HL
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t AND_E6(cpu.CPU, int v) noexcept # E6 AND d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RST_E7(cpu.CPU) noexcept # E7 RST 20H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t ADD_E8(cpu.CPU, int v) noexcept # E8 ADD SP,r8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t JP_E9(cpu.CPU) noexcept # E9 JP (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_EA(cpu.CPU, int v) noexcept # EA LD (a16),A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t XOR_EE(cpu.CPU, int v) noexcept # EE XOR d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RST_EF(cpu.CPU) noexcept # EF RST 28H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LDH_F0(cpu.CPU, int v) noexcept # F0 LDH A,(a8)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t POP_F1(cpu.CPU) noexcept # F1 POP AF
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_F2(cpu.CPU) noexcept # F2 LD A,(C)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t DI_F3(cpu.CPU) noexcept # F3 DI
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t PUSH_F5(cpu.CPU) noexcept # F5 PUSH AF
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t OR_F6(cpu.CPU, int v) noexcept # F6 OR d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RST_F7(cpu.CPU) noexcept # F7 RST 30H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_F8(cpu.CPU, int v) noexcept # F8 LD HL,SP+r8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_F9(cpu.CPU) noexcept # F9 LD SP,HL
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t LD_FA(cpu.CPU, int v) noexcept # FA LD A,(a16)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t EI_FB(cpu.CPU) noexcept # FB EI
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t CP_FE(cpu.CPU, int v) noexcept # FE CP d8
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RST_FF(cpu.CPU) noexcept # FF RST 38H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RLC_100(cpu.CPU) noexcept # 100 RLC B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RLC_101(cpu.CPU) noexcept # 101 RLC C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RLC_102(cpu.CPU) noexcept # 102 RLC D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RLC_103(cpu.CPU) noexcept # 103 RLC E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RLC_104(cpu.CPU) noexcept # 104 RLC H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RLC_105(cpu.CPU) noexcept # 105 RLC L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RLC_106(cpu.CPU) noexcept # 106 RLC (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RLC_107(cpu.CPU) noexcept # 107 RLC A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RRC_108(cpu.CPU) noexcept # 108 RRC B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RRC_109(cpu.CPU) noexcept # 109 RRC C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RRC_10A(cpu.CPU) noexcept # 10A RRC D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RRC_10B(cpu.CPU) noexcept # 10B RRC E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RRC_10C(cpu.CPU) noexcept # 10C RRC H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RRC_10D(cpu.CPU) noexcept # 10D RRC L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RRC_10E(cpu.CPU) noexcept # 10E RRC (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RRC_10F(cpu.CPU) noexcept # 10F RRC A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RL_110(cpu.CPU) noexcept # 110 RL B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RL_111(cpu.CPU) noexcept # 111 RL C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RL_112(cpu.CPU) noexcept # 112 RL D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RL_113(cpu.CPU) noexcept # 113 RL E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RL_114(cpu.CPU) noexcept # 114 RL H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RL_115(cpu.CPU) noexcept # 115 RL L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RL_116(cpu.CPU) noexcept # 116 RL (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RL_117(cpu.CPU) noexcept # 117 RL A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RR_118(cpu.CPU) noexcept # 118 RR B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RR_119(cpu.CPU) noexcept # 119 RR C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RR_11A(cpu.CPU) noexcept # 11A RR D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RR_11B(cpu.CPU) noexcept # 11B RR E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RR_11C(cpu.CPU) noexcept # 11C RR H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RR_11D(cpu.CPU) noexcept # 11D RR L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RR_11E(cpu.CPU) noexcept # 11E RR (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RR_11F(cpu.CPU) noexcept # 11F RR A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SLA_120(cpu.CPU) noexcept # 120 SLA B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SLA_121(cpu.CPU) noexcept # 121 SLA C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SLA_122(cpu.CPU) noexcept # 122 SLA D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SLA_123(cpu.CPU) noexcept # 123 SLA E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SLA_124(cpu.CPU) noexcept # 124 SLA H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SLA_125(cpu.CPU) noexcept # 125 SLA L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SLA_126(cpu.CPU) noexcept # 126 SLA (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SLA_127(cpu.CPU) noexcept # 127 SLA A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRA_128(cpu.CPU) noexcept # 128 SRA B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRA_129(cpu.CPU) noexcept # 129 SRA C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRA_12A(cpu.CPU) noexcept # 12A SRA D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRA_12B(cpu.CPU) noexcept # 12B SRA E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRA_12C(cpu.CPU) noexcept # 12C SRA H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRA_12D(cpu.CPU) noexcept # 12D SRA L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRA_12E(cpu.CPU) noexcept # 12E SRA (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRA_12F(cpu.CPU) noexcept # 12F SRA A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SWAP_130(cpu.CPU) noexcept # 130 SWAP B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SWAP_131(cpu.CPU) noexcept # 131 SWAP C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SWAP_132(cpu.CPU) noexcept # 132 SWAP D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SWAP_133(cpu.CPU) noexcept # 133 SWAP E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SWAP_134(cpu.CPU) noexcept # 134 SWAP H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SWAP_135(cpu.CPU) noexcept # 135 SWAP L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SWAP_136(cpu.CPU) noexcept # 136 SWAP (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SWAP_137(cpu.CPU) noexcept # 137 SWAP A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRL_138(cpu.CPU) noexcept # 138 SRL B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRL_139(cpu.CPU) noexcept # 139 SRL C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRL_13A(cpu.CPU) noexcept # 13A SRL D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRL_13B(cpu.CPU) noexcept # 13B SRL E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRL_13C(cpu.CPU) noexcept # 13C SRL H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRL_13D(cpu.CPU) noexcept # 13D SRL L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRL_13E(cpu.CPU) noexcept # 13E SRL (HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SRL_13F(cpu.CPU) noexcept # 13F SRL A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_140(cpu.CPU) noexcept # 140 BIT 0,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_141(cpu.CPU) noexcept # 141 BIT 0,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_142(cpu.CPU) noexcept # 142 BIT 0,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_143(cpu.CPU) noexcept # 143 BIT 0,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_144(cpu.CPU) noexcept # 144 BIT 0,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_145(cpu.CPU) noexcept # 145 BIT 0,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_146(cpu.CPU) noexcept # 146 BIT 0,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_147(cpu.CPU) noexcept # 147 BIT 0,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_148(cpu.CPU) noexcept # 148 BIT 1,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_149(cpu.CPU) noexcept # 149 BIT 1,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_14A(cpu.CPU) noexcept # 14A BIT 1,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_14B(cpu.CPU) noexcept # 14B BIT 1,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_14C(cpu.CPU) noexcept # 14C BIT 1,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_14D(cpu.CPU) noexcept # 14D BIT 1,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_14E(cpu.CPU) noexcept # 14E BIT 1,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_14F(cpu.CPU) noexcept # 14F BIT 1,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_150(cpu.CPU) noexcept # 150 BIT 2,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_151(cpu.CPU) noexcept # 151 BIT 2,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_152(cpu.CPU) noexcept # 152 BIT 2,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_153(cpu.CPU) noexcept # 153 BIT 2,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_154(cpu.CPU) noexcept # 154 BIT 2,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_155(cpu.CPU) noexcept # 155 BIT 2,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_156(cpu.CPU) noexcept # 156 BIT 2,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_157(cpu.CPU) noexcept # 157 BIT 2,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_158(cpu.CPU) noexcept # 158 BIT 3,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_159(cpu.CPU) noexcept # 159 BIT 3,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_15A(cpu.CPU) noexcept # 15A BIT 3,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_15B(cpu.CPU) noexcept # 15B BIT 3,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_15C(cpu.CPU) noexcept # 15C BIT 3,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_15D(cpu.CPU) noexcept # 15D BIT 3,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_15E(cpu.CPU) noexcept # 15E BIT 3,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_15F(cpu.CPU) noexcept # 15F BIT 3,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_160(cpu.CPU) noexcept # 160 BIT 4,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_161(cpu.CPU) noexcept # 161 BIT 4,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_162(cpu.CPU) noexcept # 162 BIT 4,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_163(cpu.CPU) noexcept # 163 BIT 4,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_164(cpu.CPU) noexcept # 164 BIT 4,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_165(cpu.CPU) noexcept # 165 BIT 4,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_166(cpu.CPU) noexcept # 166 BIT 4,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_167(cpu.CPU) noexcept # 167 BIT 4,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_168(cpu.CPU) noexcept # 168 BIT 5,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_169(cpu.CPU) noexcept # 169 BIT 5,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_16A(cpu.CPU) noexcept # 16A BIT 5,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_16B(cpu.CPU) noexcept # 16B BIT 5,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_16C(cpu.CPU) noexcept # 16C BIT 5,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_16D(cpu.CPU) noexcept # 16D BIT 5,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_16E(cpu.CPU) noexcept # 16E BIT 5,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_16F(cpu.CPU) noexcept # 16F BIT 5,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_170(cpu.CPU) noexcept # 170 BIT 6,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_171(cpu.CPU) noexcept # 171 BIT 6,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_172(cpu.CPU) noexcept # 172 BIT 6,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_173(cpu.CPU) noexcept # 173 BIT 6,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_174(cpu.CPU) noexcept # 174 BIT 6,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_175(cpu.CPU) noexcept # 175 BIT 6,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_176(cpu.CPU) noexcept # 176 BIT 6,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_177(cpu.CPU) noexcept # 177 BIT 6,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_178(cpu.CPU) noexcept # 178 BIT 7,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_179(cpu.CPU) noexcept # 179 BIT 7,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_17A(cpu.CPU) noexcept # 17A BIT 7,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_17B(cpu.CPU) noexcept # 17B BIT 7,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_17C(cpu.CPU) noexcept # 17C BIT 7,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_17D(cpu.CPU) noexcept # 17D BIT 7,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_17E(cpu.CPU) noexcept # 17E BIT 7,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t BIT_17F(cpu.CPU) noexcept # 17F BIT 7,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_180(cpu.CPU) noexcept # 180 RES 0,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_181(cpu.CPU) noexcept # 181 RES 0,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_182(cpu.CPU) noexcept # 182 RES 0,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_183(cpu.CPU) noexcept # 183 RES 0,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_184(cpu.CPU) noexcept # 184 RES 0,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_185(cpu.CPU) noexcept # 185 RES 0,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_186(cpu.CPU) noexcept # 186 RES 0,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_187(cpu.CPU) noexcept # 187 RES 0,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_188(cpu.CPU) noexcept # 188 RES 1,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_189(cpu.CPU) noexcept # 189 RES 1,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_18A(cpu.CPU) noexcept # 18A RES 1,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_18B(cpu.CPU) noexcept # 18B RES 1,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_18C(cpu.CPU) noexcept # 18C RES 1,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_18D(cpu.CPU) noexcept # 18D RES 1,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_18E(cpu.CPU) noexcept # 18E RES 1,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_18F(cpu.CPU) noexcept # 18F RES 1,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_190(cpu.CPU) noexcept # 190 RES 2,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_191(cpu.CPU) noexcept # 191 RES 2,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_192(cpu.CPU) noexcept # 192 RES 2,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_193(cpu.CPU) noexcept # 193 RES 2,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_194(cpu.CPU) noexcept # 194 RES 2,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_195(cpu.CPU) noexcept # 195 RES 2,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_196(cpu.CPU) noexcept # 196 RES 2,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_197(cpu.CPU) noexcept # 197 RES 2,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_198(cpu.CPU) noexcept # 198 RES 3,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_199(cpu.CPU) noexcept # 199 RES 3,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_19A(cpu.CPU) noexcept # 19A RES 3,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_19B(cpu.CPU) noexcept # 19B RES 3,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_19C(cpu.CPU) noexcept # 19C RES 3,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_19D(cpu.CPU) noexcept # 19D RES 3,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_19E(cpu.CPU) noexcept # 19E RES 3,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_19F(cpu.CPU) noexcept # 19F RES 3,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1A0(cpu.CPU) noexcept # 1A0 RES 4,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1A1(cpu.CPU) noexcept # 1A1 RES 4,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1A2(cpu.CPU) noexcept # 1A2 RES 4,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1A3(cpu.CPU) noexcept # 1A3 RES 4,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1A4(cpu.CPU) noexcept # 1A4 RES 4,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1A5(cpu.CPU) noexcept # 1A5 RES 4,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1A6(cpu.CPU) noexcept # 1A6 RES 4,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1A7(cpu.CPU) noexcept # 1A7 RES 4,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1A8(cpu.CPU) noexcept # 1A8 RES 5,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1A9(cpu.CPU) noexcept # 1A9 RES 5,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1AA(cpu.CPU) noexcept # 1AA RES 5,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1AB(cpu.CPU) noexcept # 1AB RES 5,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1AC(cpu.CPU) noexcept # 1AC RES 5,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1AD(cpu.CPU) noexcept # 1AD RES 5,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1AE(cpu.CPU) noexcept # 1AE RES 5,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1AF(cpu.CPU) noexcept # 1AF RES 5,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1B0(cpu.CPU) noexcept # 1B0 RES 6,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1B1(cpu.CPU) noexcept # 1B1 RES 6,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1B2(cpu.CPU) noexcept # 1B2 RES 6,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1B3(cpu.CPU) noexcept # 1B3 RES 6,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1B4(cpu.CPU) noexcept # 1B4 RES 6,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1B5(cpu.CPU) noexcept # 1B5 RES 6,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1B6(cpu.CPU) noexcept # 1B6 RES 6,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1B7(cpu.CPU) noexcept # 1B7 RES 6,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1B8(cpu.CPU) noexcept # 1B8 RES 7,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1B9(cpu.CPU) noexcept # 1B9 RES 7,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1BA(cpu.CPU) noexcept # 1BA RES 7,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1BB(cpu.CPU) noexcept # 1BB RES 7,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1BC(cpu.CPU) noexcept # 1BC RES 7,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1BD(cpu.CPU) noexcept # 1BD RES 7,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1BE(cpu.CPU) noexcept # 1BE RES 7,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t RES_1BF(cpu.CPU) noexcept # 1BF RES 7,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1C0(cpu.CPU) noexcept # 1C0 SET 0,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1C1(cpu.CPU) noexcept # 1C1 SET 0,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1C2(cpu.CPU) noexcept # 1C2 SET 0,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1C3(cpu.CPU) noexcept # 1C3 SET 0,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1C4(cpu.CPU) noexcept # 1C4 SET 0,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1C5(cpu.CPU) noexcept # 1C5 SET 0,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1C6(cpu.CPU) noexcept # 1C6 SET 0,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1C7(cpu.CPU) noexcept # 1C7 SET 0,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1C8(cpu.CPU) noexcept # 1C8 SET 1,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1C9(cpu.CPU) noexcept # 1C9 SET 1,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1CA(cpu.CPU) noexcept # 1CA SET 1,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1CB(cpu.CPU) noexcept # 1CB SET 1,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1CC(cpu.CPU) noexcept # 1CC SET 1,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1CD(cpu.CPU) noexcept # 1CD SET 1,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1CE(cpu.CPU) noexcept # 1CE SET 1,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1CF(cpu.CPU) noexcept # 1CF SET 1,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1D0(cpu.CPU) noexcept # 1D0 SET 2,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1D1(cpu.CPU) noexcept # 1D1 SET 2,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1D2(cpu.CPU) noexcept # 1D2 SET 2,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1D3(cpu.CPU) noexcept # 1D3 SET 2,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1D4(cpu.CPU) noexcept # 1D4 SET 2,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1D5(cpu.CPU) noexcept # 1D5 SET 2,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1D6(cpu.CPU) noexcept # 1D6 SET 2,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1D7(cpu.CPU) noexcept # 1D7 SET 2,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1D8(cpu.CPU) noexcept # 1D8 SET 3,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1D9(cpu.CPU) noexcept # 1D9 SET 3,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1DA(cpu.CPU) noexcept # 1DA SET 3,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1DB(cpu.CPU) noexcept # 1DB SET 3,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1DC(cpu.CPU) noexcept # 1DC SET 3,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1DD(cpu.CPU) noexcept # 1DD SET 3,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1DE(cpu.CPU) noexcept # 1DE SET 3,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1DF(cpu.CPU) noexcept # 1DF SET 3,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1E0(cpu.CPU) noexcept # 1E0 SET 4,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1E1(cpu.CPU) noexcept # 1E1 SET 4,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1E2(cpu.CPU) noexcept # 1E2 SET 4,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1E3(cpu.CPU) noexcept # 1E3 SET 4,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1E4(cpu.CPU) noexcept # 1E4 SET 4,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1E5(cpu.CPU) noexcept # 1E5 SET 4,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1E6(cpu.CPU) noexcept # 1E6 SET 4,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1E7(cpu.CPU) noexcept # 1E7 SET 4,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1E8(cpu.CPU) noexcept # 1E8 SET 5,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1E9(cpu.CPU) noexcept # 1E9 SET 5,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1EA(cpu.CPU) noexcept # 1EA SET 5,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1EB(cpu.CPU) noexcept # 1EB SET 5,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1EC(cpu.CPU) noexcept # 1EC SET 5,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1ED(cpu.CPU) noexcept # 1ED SET 5,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1EE(cpu.CPU) noexcept # 1EE SET 5,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1EF(cpu.CPU) noexcept # 1EF SET 5,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1F0(cpu.CPU) noexcept # 1F0 SET 6,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1F1(cpu.CPU) noexcept # 1F1 SET 6,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1F2(cpu.CPU) noexcept # 1F2 SET 6,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1F3(cpu.CPU) noexcept # 1F3 SET 6,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1F4(cpu.CPU) noexcept # 1F4 SET 6,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1F5(cpu.CPU) noexcept # 1F5 SET 6,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1F6(cpu.CPU) noexcept # 1F6 SET 6,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1F7(cpu.CPU) noexcept # 1F7 SET 6,A
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1F8(cpu.CPU) noexcept # 1F8 SET 7,B
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1F9(cpu.CPU) noexcept # 1F9 SET 7,C
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1FA(cpu.CPU) noexcept # 1FA SET 7,D
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1FB(cpu.CPU) noexcept # 1FB SET 7,E
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1FC(cpu.CPU) noexcept # 1FC SET 7,H
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1FD(cpu.CPU) noexcept # 1FD SET 7,L
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1FE(cpu.CPU) noexcept # 1FE SET 7,(HL)
@cython.locals(v=int, flag=uint8_t, t=int)
cdef uint8_t SET_1FF(cpu.CPU) noexcept # 1FF SET 7,A
