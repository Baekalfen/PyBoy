
# THIS FILE IS AUTO-GENERATED!!!
# DO NOT MODIFY THIS FILE.
# CHANGES TO THE CODE SHOULD BE MADE IN 'generator.py'.

cimport cpu
cimport cython
from libc.stdint cimport uint8_t, uint16_t, uint32_t


cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef uint16_t FLAGC, FLAGH, FLAGN, FLAGZ
cdef uint8_t[512] OPCODE_LENGTHS
cdef uint16_t get_opcode_length(uint16_t)
@cython.locals(v=cython.int, a=cython.int, b=cython.int, pc=cython.ushort)
cdef int execute_opcode(cpu.CPU, uint16_t)

cdef unsigned char no_opcode(cpu.CPU) except -1
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char NOP_00(cpu.CPU) except -1 # 00 NOP
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_01(cpu.CPU, int v) except -1 # 01 LD BC,d16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_02(cpu.CPU) except -1 # 02 LD (BC),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_03(cpu.CPU) except -1 # 03 INC BC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_04(cpu.CPU) except -1 # 04 INC B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_05(cpu.CPU) except -1 # 05 DEC B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_06(cpu.CPU, int v) except -1 # 06 LD B,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLCA_07(cpu.CPU) except -1 # 07 RLCA
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_08(cpu.CPU, int v) except -1 # 08 LD (a16),SP
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_09(cpu.CPU) except -1 # 09 ADD HL,BC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_0A(cpu.CPU) except -1 # 0A LD A,(BC)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_0B(cpu.CPU) except -1 # 0B DEC BC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_0C(cpu.CPU) except -1 # 0C INC C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_0D(cpu.CPU) except -1 # 0D DEC C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_0E(cpu.CPU, int v) except -1 # 0E LD C,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRCA_0F(cpu.CPU) except -1 # 0F RRCA
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char STOP_10(cpu.CPU, int v) except -1 # 10 STOP 0
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_11(cpu.CPU, int v) except -1 # 11 LD DE,d16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_12(cpu.CPU) except -1 # 12 LD (DE),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_13(cpu.CPU) except -1 # 13 INC DE
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_14(cpu.CPU) except -1 # 14 INC D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_15(cpu.CPU) except -1 # 15 DEC D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_16(cpu.CPU, int v) except -1 # 16 LD D,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLA_17(cpu.CPU) except -1 # 17 RLA
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JR_18(cpu.CPU, int v) except -1 # 18 JR r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_19(cpu.CPU) except -1 # 19 ADD HL,DE
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_1A(cpu.CPU) except -1 # 1A LD A,(DE)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_1B(cpu.CPU) except -1 # 1B DEC DE
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_1C(cpu.CPU) except -1 # 1C INC E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_1D(cpu.CPU) except -1 # 1D DEC E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_1E(cpu.CPU, int v) except -1 # 1E LD E,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRA_1F(cpu.CPU) except -1 # 1F RRA
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JR_20(cpu.CPU, int v) except -1 # 20 JR NZ,r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_21(cpu.CPU, int v) except -1 # 21 LD HL,d16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_22(cpu.CPU) except -1 # 22 LD (HL+),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_23(cpu.CPU) except -1 # 23 INC HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_24(cpu.CPU) except -1 # 24 INC H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_25(cpu.CPU) except -1 # 25 DEC H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_26(cpu.CPU, int v) except -1 # 26 LD H,d8
@cython.locals(v=int, flag=uchar, t=int, corr=ushort)
cdef unsigned char DAA_27(cpu.CPU) except -1 # 27 DAA
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JR_28(cpu.CPU, int v) except -1 # 28 JR Z,r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_29(cpu.CPU) except -1 # 29 ADD HL,HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_2A(cpu.CPU) except -1 # 2A LD A,(HL+)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_2B(cpu.CPU) except -1 # 2B DEC HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_2C(cpu.CPU) except -1 # 2C INC L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_2D(cpu.CPU) except -1 # 2D DEC L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_2E(cpu.CPU, int v) except -1 # 2E LD L,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CPL_2F(cpu.CPU) except -1 # 2F CPL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JR_30(cpu.CPU, int v) except -1 # 30 JR NC,r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_31(cpu.CPU, int v) except -1 # 31 LD SP,d16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_32(cpu.CPU) except -1 # 32 LD (HL-),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_33(cpu.CPU) except -1 # 33 INC SP
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_34(cpu.CPU) except -1 # 34 INC (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_35(cpu.CPU) except -1 # 35 DEC (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_36(cpu.CPU, int v) except -1 # 36 LD (HL),d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SCF_37(cpu.CPU) except -1 # 37 SCF
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JR_38(cpu.CPU, int v) except -1 # 38 JR C,r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_39(cpu.CPU) except -1 # 39 ADD HL,SP
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_3A(cpu.CPU) except -1 # 3A LD A,(HL-)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_3B(cpu.CPU) except -1 # 3B DEC SP
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_3C(cpu.CPU) except -1 # 3C INC A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_3D(cpu.CPU) except -1 # 3D DEC A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_3E(cpu.CPU, int v) except -1 # 3E LD A,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CCF_3F(cpu.CPU) except -1 # 3F CCF
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_40(cpu.CPU) except -1 # 40 LD B,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_41(cpu.CPU) except -1 # 41 LD B,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_42(cpu.CPU) except -1 # 42 LD B,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_43(cpu.CPU) except -1 # 43 LD B,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_44(cpu.CPU) except -1 # 44 LD B,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_45(cpu.CPU) except -1 # 45 LD B,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_46(cpu.CPU) except -1 # 46 LD B,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_47(cpu.CPU) except -1 # 47 LD B,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_48(cpu.CPU) except -1 # 48 LD C,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_49(cpu.CPU) except -1 # 49 LD C,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4A(cpu.CPU) except -1 # 4A LD C,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4B(cpu.CPU) except -1 # 4B LD C,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4C(cpu.CPU) except -1 # 4C LD C,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4D(cpu.CPU) except -1 # 4D LD C,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4E(cpu.CPU) except -1 # 4E LD C,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4F(cpu.CPU) except -1 # 4F LD C,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_50(cpu.CPU) except -1 # 50 LD D,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_51(cpu.CPU) except -1 # 51 LD D,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_52(cpu.CPU) except -1 # 52 LD D,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_53(cpu.CPU) except -1 # 53 LD D,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_54(cpu.CPU) except -1 # 54 LD D,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_55(cpu.CPU) except -1 # 55 LD D,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_56(cpu.CPU) except -1 # 56 LD D,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_57(cpu.CPU) except -1 # 57 LD D,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_58(cpu.CPU) except -1 # 58 LD E,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_59(cpu.CPU) except -1 # 59 LD E,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5A(cpu.CPU) except -1 # 5A LD E,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5B(cpu.CPU) except -1 # 5B LD E,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5C(cpu.CPU) except -1 # 5C LD E,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5D(cpu.CPU) except -1 # 5D LD E,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5E(cpu.CPU) except -1 # 5E LD E,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5F(cpu.CPU) except -1 # 5F LD E,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_60(cpu.CPU) except -1 # 60 LD H,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_61(cpu.CPU) except -1 # 61 LD H,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_62(cpu.CPU) except -1 # 62 LD H,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_63(cpu.CPU) except -1 # 63 LD H,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_64(cpu.CPU) except -1 # 64 LD H,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_65(cpu.CPU) except -1 # 65 LD H,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_66(cpu.CPU) except -1 # 66 LD H,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_67(cpu.CPU) except -1 # 67 LD H,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_68(cpu.CPU) except -1 # 68 LD L,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_69(cpu.CPU) except -1 # 69 LD L,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6A(cpu.CPU) except -1 # 6A LD L,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6B(cpu.CPU) except -1 # 6B LD L,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6C(cpu.CPU) except -1 # 6C LD L,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6D(cpu.CPU) except -1 # 6D LD L,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6E(cpu.CPU) except -1 # 6E LD L,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6F(cpu.CPU) except -1 # 6F LD L,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_70(cpu.CPU) except -1 # 70 LD (HL),B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_71(cpu.CPU) except -1 # 71 LD (HL),C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_72(cpu.CPU) except -1 # 72 LD (HL),D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_73(cpu.CPU) except -1 # 73 LD (HL),E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_74(cpu.CPU) except -1 # 74 LD (HL),H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_75(cpu.CPU) except -1 # 75 LD (HL),L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char HALT_76(cpu.CPU) except -1 # 76 HALT
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_77(cpu.CPU) except -1 # 77 LD (HL),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_78(cpu.CPU) except -1 # 78 LD A,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_79(cpu.CPU) except -1 # 79 LD A,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7A(cpu.CPU) except -1 # 7A LD A,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7B(cpu.CPU) except -1 # 7B LD A,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7C(cpu.CPU) except -1 # 7C LD A,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7D(cpu.CPU) except -1 # 7D LD A,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7E(cpu.CPU) except -1 # 7E LD A,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7F(cpu.CPU) except -1 # 7F LD A,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_80(cpu.CPU) except -1 # 80 ADD A,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_81(cpu.CPU) except -1 # 81 ADD A,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_82(cpu.CPU) except -1 # 82 ADD A,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_83(cpu.CPU) except -1 # 83 ADD A,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_84(cpu.CPU) except -1 # 84 ADD A,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_85(cpu.CPU) except -1 # 85 ADD A,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_86(cpu.CPU) except -1 # 86 ADD A,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_87(cpu.CPU) except -1 # 87 ADD A,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_88(cpu.CPU) except -1 # 88 ADC A,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_89(cpu.CPU) except -1 # 89 ADC A,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8A(cpu.CPU) except -1 # 8A ADC A,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8B(cpu.CPU) except -1 # 8B ADC A,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8C(cpu.CPU) except -1 # 8C ADC A,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8D(cpu.CPU) except -1 # 8D ADC A,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8E(cpu.CPU) except -1 # 8E ADC A,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8F(cpu.CPU) except -1 # 8F ADC A,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_90(cpu.CPU) except -1 # 90 SUB B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_91(cpu.CPU) except -1 # 91 SUB C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_92(cpu.CPU) except -1 # 92 SUB D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_93(cpu.CPU) except -1 # 93 SUB E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_94(cpu.CPU) except -1 # 94 SUB H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_95(cpu.CPU) except -1 # 95 SUB L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_96(cpu.CPU) except -1 # 96 SUB (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_97(cpu.CPU) except -1 # 97 SUB A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_98(cpu.CPU) except -1 # 98 SBC A,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_99(cpu.CPU) except -1 # 99 SBC A,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9A(cpu.CPU) except -1 # 9A SBC A,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9B(cpu.CPU) except -1 # 9B SBC A,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9C(cpu.CPU) except -1 # 9C SBC A,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9D(cpu.CPU) except -1 # 9D SBC A,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9E(cpu.CPU) except -1 # 9E SBC A,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9F(cpu.CPU) except -1 # 9F SBC A,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_A0(cpu.CPU) except -1 # A0 AND B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_A1(cpu.CPU) except -1 # A1 AND C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_A2(cpu.CPU) except -1 # A2 AND D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_A3(cpu.CPU) except -1 # A3 AND E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_A4(cpu.CPU) except -1 # A4 AND H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_A5(cpu.CPU) except -1 # A5 AND L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_A6(cpu.CPU) except -1 # A6 AND (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_A7(cpu.CPU) except -1 # A7 AND A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_A8(cpu.CPU) except -1 # A8 XOR B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_A9(cpu.CPU) except -1 # A9 XOR C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_AA(cpu.CPU) except -1 # AA XOR D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_AB(cpu.CPU) except -1 # AB XOR E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_AC(cpu.CPU) except -1 # AC XOR H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_AD(cpu.CPU) except -1 # AD XOR L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_AE(cpu.CPU) except -1 # AE XOR (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_AF(cpu.CPU) except -1 # AF XOR A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_B0(cpu.CPU) except -1 # B0 OR B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_B1(cpu.CPU) except -1 # B1 OR C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_B2(cpu.CPU) except -1 # B2 OR D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_B3(cpu.CPU) except -1 # B3 OR E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_B4(cpu.CPU) except -1 # B4 OR H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_B5(cpu.CPU) except -1 # B5 OR L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_B6(cpu.CPU) except -1 # B6 OR (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_B7(cpu.CPU) except -1 # B7 OR A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_B8(cpu.CPU) except -1 # B8 CP B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_B9(cpu.CPU) except -1 # B9 CP C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_BA(cpu.CPU) except -1 # BA CP D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_BB(cpu.CPU) except -1 # BB CP E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_BC(cpu.CPU) except -1 # BC CP H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_BD(cpu.CPU) except -1 # BD CP L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_BE(cpu.CPU) except -1 # BE CP (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_BF(cpu.CPU) except -1 # BF CP A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_C0(cpu.CPU) except -1 # C0 RET NZ
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char POP_C1(cpu.CPU) except -1 # C1 POP BC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_C2(cpu.CPU, int v) except -1 # C2 JP NZ,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_C3(cpu.CPU, int v) except -1 # C3 JP a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_C4(cpu.CPU, int v) except -1 # C4 CALL NZ,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char PUSH_C5(cpu.CPU) except -1 # C5 PUSH BC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_C6(cpu.CPU, int v) except -1 # C6 ADD A,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_C7(cpu.CPU) except -1 # C7 RST 00H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_C8(cpu.CPU) except -1 # C8 RET Z
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_C9(cpu.CPU) except -1 # C9 RET
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_CA(cpu.CPU, int v) except -1 # CA JP Z,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char PREFIX_CB(cpu.CPU) except -1 # CB PREFIX CB
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_CC(cpu.CPU, int v) except -1 # CC CALL Z,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_CD(cpu.CPU, int v) except -1 # CD CALL a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_CE(cpu.CPU, int v) except -1 # CE ADC A,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_CF(cpu.CPU) except -1 # CF RST 08H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_D0(cpu.CPU) except -1 # D0 RET NC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char POP_D1(cpu.CPU) except -1 # D1 POP DE
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_D2(cpu.CPU, int v) except -1 # D2 JP NC,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_D4(cpu.CPU, int v) except -1 # D4 CALL NC,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char PUSH_D5(cpu.CPU) except -1 # D5 PUSH DE
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_D6(cpu.CPU, int v) except -1 # D6 SUB d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_D7(cpu.CPU) except -1 # D7 RST 10H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_D8(cpu.CPU) except -1 # D8 RET C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RETI_D9(cpu.CPU) except -1 # D9 RETI
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_DA(cpu.CPU, int v) except -1 # DA JP C,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_DC(cpu.CPU, int v) except -1 # DC CALL C,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_DE(cpu.CPU, int v) except -1 # DE SBC A,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_DF(cpu.CPU) except -1 # DF RST 18H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LDH_E0(cpu.CPU, int v) except -1 # E0 LDH (a8),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char POP_E1(cpu.CPU) except -1 # E1 POP HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_E2(cpu.CPU) except -1 # E2 LD (C),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char PUSH_E5(cpu.CPU) except -1 # E5 PUSH HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_E6(cpu.CPU, int v) except -1 # E6 AND d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_E7(cpu.CPU) except -1 # E7 RST 20H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_E8(cpu.CPU, int v) except -1 # E8 ADD SP,r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_E9(cpu.CPU) except -1 # E9 JP (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_EA(cpu.CPU, int v) except -1 # EA LD (a16),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_EE(cpu.CPU, int v) except -1 # EE XOR d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_EF(cpu.CPU) except -1 # EF RST 28H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LDH_F0(cpu.CPU, int v) except -1 # F0 LDH A,(a8)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char POP_F1(cpu.CPU) except -1 # F1 POP AF
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_F2(cpu.CPU) except -1 # F2 LD A,(C)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DI_F3(cpu.CPU) except -1 # F3 DI
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char PUSH_F5(cpu.CPU) except -1 # F5 PUSH AF
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_F6(cpu.CPU, int v) except -1 # F6 OR d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_F7(cpu.CPU) except -1 # F7 RST 30H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_F8(cpu.CPU, int v) except -1 # F8 LD HL,SP+r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_F9(cpu.CPU) except -1 # F9 LD SP,HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_FA(cpu.CPU, int v) except -1 # FA LD A,(a16)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char EI_FB(cpu.CPU) except -1 # FB EI
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_FE(cpu.CPU, int v) except -1 # FE CP d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_FF(cpu.CPU) except -1 # FF RST 38H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_100(cpu.CPU) except -1 # 100 RLC B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_101(cpu.CPU) except -1 # 101 RLC C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_102(cpu.CPU) except -1 # 102 RLC D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_103(cpu.CPU) except -1 # 103 RLC E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_104(cpu.CPU) except -1 # 104 RLC H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_105(cpu.CPU) except -1 # 105 RLC L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_106(cpu.CPU) except -1 # 106 RLC (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_107(cpu.CPU) except -1 # 107 RLC A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_108(cpu.CPU) except -1 # 108 RRC B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_109(cpu.CPU) except -1 # 109 RRC C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10A(cpu.CPU) except -1 # 10A RRC D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10B(cpu.CPU) except -1 # 10B RRC E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10C(cpu.CPU) except -1 # 10C RRC H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10D(cpu.CPU) except -1 # 10D RRC L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10E(cpu.CPU) except -1 # 10E RRC (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10F(cpu.CPU) except -1 # 10F RRC A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_110(cpu.CPU) except -1 # 110 RL B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_111(cpu.CPU) except -1 # 111 RL C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_112(cpu.CPU) except -1 # 112 RL D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_113(cpu.CPU) except -1 # 113 RL E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_114(cpu.CPU) except -1 # 114 RL H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_115(cpu.CPU) except -1 # 115 RL L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_116(cpu.CPU) except -1 # 116 RL (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_117(cpu.CPU) except -1 # 117 RL A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_118(cpu.CPU) except -1 # 118 RR B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_119(cpu.CPU) except -1 # 119 RR C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11A(cpu.CPU) except -1 # 11A RR D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11B(cpu.CPU) except -1 # 11B RR E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11C(cpu.CPU) except -1 # 11C RR H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11D(cpu.CPU) except -1 # 11D RR L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11E(cpu.CPU) except -1 # 11E RR (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11F(cpu.CPU) except -1 # 11F RR A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_120(cpu.CPU) except -1 # 120 SLA B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_121(cpu.CPU) except -1 # 121 SLA C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_122(cpu.CPU) except -1 # 122 SLA D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_123(cpu.CPU) except -1 # 123 SLA E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_124(cpu.CPU) except -1 # 124 SLA H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_125(cpu.CPU) except -1 # 125 SLA L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_126(cpu.CPU) except -1 # 126 SLA (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_127(cpu.CPU) except -1 # 127 SLA A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_128(cpu.CPU) except -1 # 128 SRA B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_129(cpu.CPU) except -1 # 129 SRA C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12A(cpu.CPU) except -1 # 12A SRA D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12B(cpu.CPU) except -1 # 12B SRA E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12C(cpu.CPU) except -1 # 12C SRA H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12D(cpu.CPU) except -1 # 12D SRA L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12E(cpu.CPU) except -1 # 12E SRA (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12F(cpu.CPU) except -1 # 12F SRA A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_130(cpu.CPU) except -1 # 130 SWAP B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_131(cpu.CPU) except -1 # 131 SWAP C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_132(cpu.CPU) except -1 # 132 SWAP D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_133(cpu.CPU) except -1 # 133 SWAP E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_134(cpu.CPU) except -1 # 134 SWAP H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_135(cpu.CPU) except -1 # 135 SWAP L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_136(cpu.CPU) except -1 # 136 SWAP (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_137(cpu.CPU) except -1 # 137 SWAP A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_138(cpu.CPU) except -1 # 138 SRL B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_139(cpu.CPU) except -1 # 139 SRL C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13A(cpu.CPU) except -1 # 13A SRL D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13B(cpu.CPU) except -1 # 13B SRL E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13C(cpu.CPU) except -1 # 13C SRL H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13D(cpu.CPU) except -1 # 13D SRL L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13E(cpu.CPU) except -1 # 13E SRL (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13F(cpu.CPU) except -1 # 13F SRL A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_140(cpu.CPU) except -1 # 140 BIT 0,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_141(cpu.CPU) except -1 # 141 BIT 0,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_142(cpu.CPU) except -1 # 142 BIT 0,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_143(cpu.CPU) except -1 # 143 BIT 0,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_144(cpu.CPU) except -1 # 144 BIT 0,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_145(cpu.CPU) except -1 # 145 BIT 0,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_146(cpu.CPU) except -1 # 146 BIT 0,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_147(cpu.CPU) except -1 # 147 BIT 0,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_148(cpu.CPU) except -1 # 148 BIT 1,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_149(cpu.CPU) except -1 # 149 BIT 1,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14A(cpu.CPU) except -1 # 14A BIT 1,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14B(cpu.CPU) except -1 # 14B BIT 1,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14C(cpu.CPU) except -1 # 14C BIT 1,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14D(cpu.CPU) except -1 # 14D BIT 1,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14E(cpu.CPU) except -1 # 14E BIT 1,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14F(cpu.CPU) except -1 # 14F BIT 1,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_150(cpu.CPU) except -1 # 150 BIT 2,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_151(cpu.CPU) except -1 # 151 BIT 2,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_152(cpu.CPU) except -1 # 152 BIT 2,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_153(cpu.CPU) except -1 # 153 BIT 2,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_154(cpu.CPU) except -1 # 154 BIT 2,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_155(cpu.CPU) except -1 # 155 BIT 2,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_156(cpu.CPU) except -1 # 156 BIT 2,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_157(cpu.CPU) except -1 # 157 BIT 2,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_158(cpu.CPU) except -1 # 158 BIT 3,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_159(cpu.CPU) except -1 # 159 BIT 3,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15A(cpu.CPU) except -1 # 15A BIT 3,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15B(cpu.CPU) except -1 # 15B BIT 3,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15C(cpu.CPU) except -1 # 15C BIT 3,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15D(cpu.CPU) except -1 # 15D BIT 3,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15E(cpu.CPU) except -1 # 15E BIT 3,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15F(cpu.CPU) except -1 # 15F BIT 3,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_160(cpu.CPU) except -1 # 160 BIT 4,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_161(cpu.CPU) except -1 # 161 BIT 4,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_162(cpu.CPU) except -1 # 162 BIT 4,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_163(cpu.CPU) except -1 # 163 BIT 4,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_164(cpu.CPU) except -1 # 164 BIT 4,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_165(cpu.CPU) except -1 # 165 BIT 4,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_166(cpu.CPU) except -1 # 166 BIT 4,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_167(cpu.CPU) except -1 # 167 BIT 4,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_168(cpu.CPU) except -1 # 168 BIT 5,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_169(cpu.CPU) except -1 # 169 BIT 5,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16A(cpu.CPU) except -1 # 16A BIT 5,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16B(cpu.CPU) except -1 # 16B BIT 5,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16C(cpu.CPU) except -1 # 16C BIT 5,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16D(cpu.CPU) except -1 # 16D BIT 5,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16E(cpu.CPU) except -1 # 16E BIT 5,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16F(cpu.CPU) except -1 # 16F BIT 5,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_170(cpu.CPU) except -1 # 170 BIT 6,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_171(cpu.CPU) except -1 # 171 BIT 6,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_172(cpu.CPU) except -1 # 172 BIT 6,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_173(cpu.CPU) except -1 # 173 BIT 6,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_174(cpu.CPU) except -1 # 174 BIT 6,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_175(cpu.CPU) except -1 # 175 BIT 6,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_176(cpu.CPU) except -1 # 176 BIT 6,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_177(cpu.CPU) except -1 # 177 BIT 6,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_178(cpu.CPU) except -1 # 178 BIT 7,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_179(cpu.CPU) except -1 # 179 BIT 7,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17A(cpu.CPU) except -1 # 17A BIT 7,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17B(cpu.CPU) except -1 # 17B BIT 7,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17C(cpu.CPU) except -1 # 17C BIT 7,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17D(cpu.CPU) except -1 # 17D BIT 7,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17E(cpu.CPU) except -1 # 17E BIT 7,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17F(cpu.CPU) except -1 # 17F BIT 7,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_180(cpu.CPU) except -1 # 180 RES 0,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_181(cpu.CPU) except -1 # 181 RES 0,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_182(cpu.CPU) except -1 # 182 RES 0,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_183(cpu.CPU) except -1 # 183 RES 0,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_184(cpu.CPU) except -1 # 184 RES 0,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_185(cpu.CPU) except -1 # 185 RES 0,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_186(cpu.CPU) except -1 # 186 RES 0,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_187(cpu.CPU) except -1 # 187 RES 0,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_188(cpu.CPU) except -1 # 188 RES 1,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_189(cpu.CPU) except -1 # 189 RES 1,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18A(cpu.CPU) except -1 # 18A RES 1,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18B(cpu.CPU) except -1 # 18B RES 1,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18C(cpu.CPU) except -1 # 18C RES 1,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18D(cpu.CPU) except -1 # 18D RES 1,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18E(cpu.CPU) except -1 # 18E RES 1,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18F(cpu.CPU) except -1 # 18F RES 1,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_190(cpu.CPU) except -1 # 190 RES 2,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_191(cpu.CPU) except -1 # 191 RES 2,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_192(cpu.CPU) except -1 # 192 RES 2,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_193(cpu.CPU) except -1 # 193 RES 2,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_194(cpu.CPU) except -1 # 194 RES 2,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_195(cpu.CPU) except -1 # 195 RES 2,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_196(cpu.CPU) except -1 # 196 RES 2,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_197(cpu.CPU) except -1 # 197 RES 2,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_198(cpu.CPU) except -1 # 198 RES 3,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_199(cpu.CPU) except -1 # 199 RES 3,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19A(cpu.CPU) except -1 # 19A RES 3,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19B(cpu.CPU) except -1 # 19B RES 3,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19C(cpu.CPU) except -1 # 19C RES 3,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19D(cpu.CPU) except -1 # 19D RES 3,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19E(cpu.CPU) except -1 # 19E RES 3,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19F(cpu.CPU) except -1 # 19F RES 3,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1A0(cpu.CPU) except -1 # 1A0 RES 4,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1A1(cpu.CPU) except -1 # 1A1 RES 4,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1A2(cpu.CPU) except -1 # 1A2 RES 4,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1A3(cpu.CPU) except -1 # 1A3 RES 4,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1A4(cpu.CPU) except -1 # 1A4 RES 4,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1A5(cpu.CPU) except -1 # 1A5 RES 4,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1A6(cpu.CPU) except -1 # 1A6 RES 4,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1A7(cpu.CPU) except -1 # 1A7 RES 4,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1A8(cpu.CPU) except -1 # 1A8 RES 5,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1A9(cpu.CPU) except -1 # 1A9 RES 5,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1AA(cpu.CPU) except -1 # 1AA RES 5,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1AB(cpu.CPU) except -1 # 1AB RES 5,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1AC(cpu.CPU) except -1 # 1AC RES 5,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1AD(cpu.CPU) except -1 # 1AD RES 5,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1AE(cpu.CPU) except -1 # 1AE RES 5,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1AF(cpu.CPU) except -1 # 1AF RES 5,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1B0(cpu.CPU) except -1 # 1B0 RES 6,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1B1(cpu.CPU) except -1 # 1B1 RES 6,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1B2(cpu.CPU) except -1 # 1B2 RES 6,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1B3(cpu.CPU) except -1 # 1B3 RES 6,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1B4(cpu.CPU) except -1 # 1B4 RES 6,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1B5(cpu.CPU) except -1 # 1B5 RES 6,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1B6(cpu.CPU) except -1 # 1B6 RES 6,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1B7(cpu.CPU) except -1 # 1B7 RES 6,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1B8(cpu.CPU) except -1 # 1B8 RES 7,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1B9(cpu.CPU) except -1 # 1B9 RES 7,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1BA(cpu.CPU) except -1 # 1BA RES 7,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1BB(cpu.CPU) except -1 # 1BB RES 7,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1BC(cpu.CPU) except -1 # 1BC RES 7,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1BD(cpu.CPU) except -1 # 1BD RES 7,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1BE(cpu.CPU) except -1 # 1BE RES 7,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1BF(cpu.CPU) except -1 # 1BF RES 7,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1C0(cpu.CPU) except -1 # 1C0 SET 0,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1C1(cpu.CPU) except -1 # 1C1 SET 0,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1C2(cpu.CPU) except -1 # 1C2 SET 0,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1C3(cpu.CPU) except -1 # 1C3 SET 0,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1C4(cpu.CPU) except -1 # 1C4 SET 0,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1C5(cpu.CPU) except -1 # 1C5 SET 0,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1C6(cpu.CPU) except -1 # 1C6 SET 0,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1C7(cpu.CPU) except -1 # 1C7 SET 0,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1C8(cpu.CPU) except -1 # 1C8 SET 1,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1C9(cpu.CPU) except -1 # 1C9 SET 1,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1CA(cpu.CPU) except -1 # 1CA SET 1,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1CB(cpu.CPU) except -1 # 1CB SET 1,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1CC(cpu.CPU) except -1 # 1CC SET 1,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1CD(cpu.CPU) except -1 # 1CD SET 1,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1CE(cpu.CPU) except -1 # 1CE SET 1,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1CF(cpu.CPU) except -1 # 1CF SET 1,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1D0(cpu.CPU) except -1 # 1D0 SET 2,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1D1(cpu.CPU) except -1 # 1D1 SET 2,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1D2(cpu.CPU) except -1 # 1D2 SET 2,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1D3(cpu.CPU) except -1 # 1D3 SET 2,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1D4(cpu.CPU) except -1 # 1D4 SET 2,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1D5(cpu.CPU) except -1 # 1D5 SET 2,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1D6(cpu.CPU) except -1 # 1D6 SET 2,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1D7(cpu.CPU) except -1 # 1D7 SET 2,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1D8(cpu.CPU) except -1 # 1D8 SET 3,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1D9(cpu.CPU) except -1 # 1D9 SET 3,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1DA(cpu.CPU) except -1 # 1DA SET 3,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1DB(cpu.CPU) except -1 # 1DB SET 3,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1DC(cpu.CPU) except -1 # 1DC SET 3,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1DD(cpu.CPU) except -1 # 1DD SET 3,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1DE(cpu.CPU) except -1 # 1DE SET 3,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1DF(cpu.CPU) except -1 # 1DF SET 3,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1E0(cpu.CPU) except -1 # 1E0 SET 4,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1E1(cpu.CPU) except -1 # 1E1 SET 4,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1E2(cpu.CPU) except -1 # 1E2 SET 4,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1E3(cpu.CPU) except -1 # 1E3 SET 4,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1E4(cpu.CPU) except -1 # 1E4 SET 4,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1E5(cpu.CPU) except -1 # 1E5 SET 4,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1E6(cpu.CPU) except -1 # 1E6 SET 4,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1E7(cpu.CPU) except -1 # 1E7 SET 4,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1E8(cpu.CPU) except -1 # 1E8 SET 5,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1E9(cpu.CPU) except -1 # 1E9 SET 5,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1EA(cpu.CPU) except -1 # 1EA SET 5,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1EB(cpu.CPU) except -1 # 1EB SET 5,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1EC(cpu.CPU) except -1 # 1EC SET 5,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ED(cpu.CPU) except -1 # 1ED SET 5,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1EE(cpu.CPU) except -1 # 1EE SET 5,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1EF(cpu.CPU) except -1 # 1EF SET 5,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1F0(cpu.CPU) except -1 # 1F0 SET 6,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1F1(cpu.CPU) except -1 # 1F1 SET 6,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1F2(cpu.CPU) except -1 # 1F2 SET 6,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1F3(cpu.CPU) except -1 # 1F3 SET 6,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1F4(cpu.CPU) except -1 # 1F4 SET 6,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1F5(cpu.CPU) except -1 # 1F5 SET 6,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1F6(cpu.CPU) except -1 # 1F6 SET 6,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1F7(cpu.CPU) except -1 # 1F7 SET 6,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1F8(cpu.CPU) except -1 # 1F8 SET 7,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1F9(cpu.CPU) except -1 # 1F9 SET 7,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1FA(cpu.CPU) except -1 # 1FA SET 7,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1FB(cpu.CPU) except -1 # 1FB SET 7,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1FC(cpu.CPU) except -1 # 1FC SET 7,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1FD(cpu.CPU) except -1 # 1FD SET 7,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1FE(cpu.CPU) except -1 # 1FE SET 7,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1FF(cpu.CPU) except -1 # 1FF SET 7,A
