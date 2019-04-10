#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


cimport cpu
cimport cython
from libc.stdint cimport uint8_t, uint16_t, uint32_t


cdef (int, int) _dummy_declaration
cdef (int, int, int, int) _dummy_declaration2

cdef uint16_t flagC, flagH, flagN, flagZ
cdef uint8_t[512] opcodeLengths
cdef uint16_t getOpcodeLength(uint16_t)
@cython.locals(v=cython.int, a=cython.int, b=cython.int, pc=cython.ushort)
cdef int executeOpcode(cpu.CPU, uint16_t)


cdef unsigned char NOOPCODE(cpu.CPU) except -1
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
cdef unsigned char LD_0a(cpu.CPU) except -1 # 0a LD A,(BC)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_0b(cpu.CPU) except -1 # 0b DEC BC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_0c(cpu.CPU) except -1 # 0c INC C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_0d(cpu.CPU) except -1 # 0d DEC C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_0e(cpu.CPU, int v) except -1 # 0e LD C,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRCA_0f(cpu.CPU) except -1 # 0f RRCA
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
cdef unsigned char LD_1a(cpu.CPU) except -1 # 1a LD A,(DE)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_1b(cpu.CPU) except -1 # 1b DEC DE
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_1c(cpu.CPU) except -1 # 1c INC E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_1d(cpu.CPU) except -1 # 1d DEC E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_1e(cpu.CPU, int v) except -1 # 1e LD E,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRA_1f(cpu.CPU) except -1 # 1f RRA
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
cdef unsigned char LD_2a(cpu.CPU) except -1 # 2a LD A,(HL+)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_2b(cpu.CPU) except -1 # 2b DEC HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_2c(cpu.CPU) except -1 # 2c INC L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_2d(cpu.CPU) except -1 # 2d DEC L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_2e(cpu.CPU, int v) except -1 # 2e LD L,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CPL_2f(cpu.CPU) except -1 # 2f CPL
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
cdef unsigned char LD_3a(cpu.CPU) except -1 # 3a LD A,(HL-)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_3b(cpu.CPU) except -1 # 3b DEC SP
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_3c(cpu.CPU) except -1 # 3c INC A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_3d(cpu.CPU) except -1 # 3d DEC A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_3e(cpu.CPU, int v) except -1 # 3e LD A,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CCF_3f(cpu.CPU) except -1 # 3f CCF
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
cdef unsigned char LD_4a(cpu.CPU) except -1 # 4a LD C,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4b(cpu.CPU) except -1 # 4b LD C,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4c(cpu.CPU) except -1 # 4c LD C,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4d(cpu.CPU) except -1 # 4d LD C,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4e(cpu.CPU) except -1 # 4e LD C,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4f(cpu.CPU) except -1 # 4f LD C,A
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
cdef unsigned char LD_5a(cpu.CPU) except -1 # 5a LD E,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5b(cpu.CPU) except -1 # 5b LD E,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5c(cpu.CPU) except -1 # 5c LD E,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5d(cpu.CPU) except -1 # 5d LD E,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5e(cpu.CPU) except -1 # 5e LD E,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5f(cpu.CPU) except -1 # 5f LD E,A
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
cdef unsigned char LD_6a(cpu.CPU) except -1 # 6a LD L,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6b(cpu.CPU) except -1 # 6b LD L,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6c(cpu.CPU) except -1 # 6c LD L,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6d(cpu.CPU) except -1 # 6d LD L,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6e(cpu.CPU) except -1 # 6e LD L,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6f(cpu.CPU) except -1 # 6f LD L,A
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
cdef unsigned char LD_7a(cpu.CPU) except -1 # 7a LD A,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7b(cpu.CPU) except -1 # 7b LD A,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7c(cpu.CPU) except -1 # 7c LD A,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7d(cpu.CPU) except -1 # 7d LD A,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7e(cpu.CPU) except -1 # 7e LD A,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7f(cpu.CPU) except -1 # 7f LD A,A
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
cdef unsigned char ADC_8a(cpu.CPU) except -1 # 8a ADC A,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8b(cpu.CPU) except -1 # 8b ADC A,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8c(cpu.CPU) except -1 # 8c ADC A,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8d(cpu.CPU) except -1 # 8d ADC A,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8e(cpu.CPU) except -1 # 8e ADC A,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8f(cpu.CPU) except -1 # 8f ADC A,A
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
cdef unsigned char SBC_9a(cpu.CPU) except -1 # 9a SBC A,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9b(cpu.CPU) except -1 # 9b SBC A,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9c(cpu.CPU) except -1 # 9c SBC A,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9d(cpu.CPU) except -1 # 9d SBC A,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9e(cpu.CPU) except -1 # 9e SBC A,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9f(cpu.CPU) except -1 # 9f SBC A,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a0(cpu.CPU) except -1 # a0 AND B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a1(cpu.CPU) except -1 # a1 AND C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a2(cpu.CPU) except -1 # a2 AND D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a3(cpu.CPU) except -1 # a3 AND E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a4(cpu.CPU) except -1 # a4 AND H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a5(cpu.CPU) except -1 # a5 AND L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a6(cpu.CPU) except -1 # a6 AND (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a7(cpu.CPU) except -1 # a7 AND A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_a8(cpu.CPU) except -1 # a8 XOR B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_a9(cpu.CPU) except -1 # a9 XOR C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_aa(cpu.CPU) except -1 # aa XOR D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_ab(cpu.CPU) except -1 # ab XOR E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_ac(cpu.CPU) except -1 # ac XOR H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_ad(cpu.CPU) except -1 # ad XOR L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_ae(cpu.CPU) except -1 # ae XOR (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_af(cpu.CPU) except -1 # af XOR A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b0(cpu.CPU) except -1 # b0 OR B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b1(cpu.CPU) except -1 # b1 OR C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b2(cpu.CPU) except -1 # b2 OR D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b3(cpu.CPU) except -1 # b3 OR E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b4(cpu.CPU) except -1 # b4 OR H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b5(cpu.CPU) except -1 # b5 OR L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b6(cpu.CPU) except -1 # b6 OR (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b7(cpu.CPU) except -1 # b7 OR A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_b8(cpu.CPU) except -1 # b8 CP B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_b9(cpu.CPU) except -1 # b9 CP C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_ba(cpu.CPU) except -1 # ba CP D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_bb(cpu.CPU) except -1 # bb CP E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_bc(cpu.CPU) except -1 # bc CP H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_bd(cpu.CPU) except -1 # bd CP L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_be(cpu.CPU) except -1 # be CP (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_bf(cpu.CPU) except -1 # bf CP A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_c0(cpu.CPU) except -1 # c0 RET NZ
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char POP_c1(cpu.CPU) except -1 # c1 POP BC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_c2(cpu.CPU, int v) except -1 # c2 JP NZ,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_c3(cpu.CPU, int v) except -1 # c3 JP a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_c4(cpu.CPU, int v) except -1 # c4 CALL NZ,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char PUSH_c5(cpu.CPU) except -1 # c5 PUSH BC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_c6(cpu.CPU, int v) except -1 # c6 ADD A,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_c7(cpu.CPU) except -1 # c7 RST 00H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_c8(cpu.CPU) except -1 # c8 RET Z
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_c9(cpu.CPU) except -1 # c9 RET
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_ca(cpu.CPU, int v) except -1 # ca JP Z,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CB_cb(cpu.CPU) except -1 # cb PREFIX CB
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_cc(cpu.CPU, int v) except -1 # cc CALL Z,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_cd(cpu.CPU, int v) except -1 # cd CALL a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_ce(cpu.CPU, int v) except -1 # ce ADC A,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_cf(cpu.CPU) except -1 # cf RST 08H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_d0(cpu.CPU) except -1 # d0 RET NC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char POP_d1(cpu.CPU) except -1 # d1 POP DE
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_d2(cpu.CPU, int v) except -1 # d2 JP NC,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_d4(cpu.CPU, int v) except -1 # d4 CALL NC,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char PUSH_d5(cpu.CPU) except -1 # d5 PUSH DE
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_d6(cpu.CPU, int v) except -1 # d6 SUB d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_d7(cpu.CPU) except -1 # d7 RST 10H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_d8(cpu.CPU) except -1 # d8 RET C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RETI_d9(cpu.CPU) except -1 # d9 RETI
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_da(cpu.CPU, int v) except -1 # da JP C,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_dc(cpu.CPU, int v) except -1 # dc CALL C,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_de(cpu.CPU, int v) except -1 # de SBC A,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_df(cpu.CPU) except -1 # df RST 18H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_e0(cpu.CPU, int v) except -1 # e0 LDH (a8),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char POP_e1(cpu.CPU) except -1 # e1 POP HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_e2(cpu.CPU) except -1 # e2 LD (C),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char PUSH_e5(cpu.CPU) except -1 # e5 PUSH HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_e6(cpu.CPU, int v) except -1 # e6 AND d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_e7(cpu.CPU) except -1 # e7 RST 20H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_e8(cpu.CPU, int v) except -1 # e8 ADD SP,r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_e9(cpu.CPU) except -1 # e9 JP (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_ea(cpu.CPU, int v) except -1 # ea LD (a16),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_ee(cpu.CPU, int v) except -1 # ee XOR d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_ef(cpu.CPU) except -1 # ef RST 28H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_f0(cpu.CPU, int v) except -1 # f0 LDH A,(a8)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char POP_f1(cpu.CPU) except -1 # f1 POP AF
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_f2(cpu.CPU) except -1 # f2 LD A,(C)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DI_f3(cpu.CPU) except -1 # f3 DI
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char PUSH_f5(cpu.CPU) except -1 # f5 PUSH AF
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_f6(cpu.CPU, int v) except -1 # f6 OR d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_f7(cpu.CPU) except -1 # f7 RST 30H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_f8(cpu.CPU, int v) except -1 # f8 LD HL,SP+r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_f9(cpu.CPU) except -1 # f9 LD SP,HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_fa(cpu.CPU, int v) except -1 # fa LD A,(a16)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char EI_fb(cpu.CPU) except -1 # fb EI
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_fe(cpu.CPU, int v) except -1 # fe CP d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_ff(cpu.CPU) except -1 # ff RST 38H
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
cdef unsigned char RRC_10a(cpu.CPU) except -1 # 10a RRC D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10b(cpu.CPU) except -1 # 10b RRC E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10c(cpu.CPU) except -1 # 10c RRC H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10d(cpu.CPU) except -1 # 10d RRC L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10e(cpu.CPU) except -1 # 10e RRC (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10f(cpu.CPU) except -1 # 10f RRC A
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
cdef unsigned char RR_11a(cpu.CPU) except -1 # 11a RR D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11b(cpu.CPU) except -1 # 11b RR E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11c(cpu.CPU) except -1 # 11c RR H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11d(cpu.CPU) except -1 # 11d RR L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11e(cpu.CPU) except -1 # 11e RR (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11f(cpu.CPU) except -1 # 11f RR A
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
cdef unsigned char SRA_12a(cpu.CPU) except -1 # 12a SRA D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12b(cpu.CPU) except -1 # 12b SRA E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12c(cpu.CPU) except -1 # 12c SRA H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12d(cpu.CPU) except -1 # 12d SRA L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12e(cpu.CPU) except -1 # 12e SRA (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12f(cpu.CPU) except -1 # 12f SRA A
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
cdef unsigned char SRL_13a(cpu.CPU) except -1 # 13a SRL D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13b(cpu.CPU) except -1 # 13b SRL E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13c(cpu.CPU) except -1 # 13c SRL H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13d(cpu.CPU) except -1 # 13d SRL L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13e(cpu.CPU) except -1 # 13e SRL (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13f(cpu.CPU) except -1 # 13f SRL A
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
cdef unsigned char BIT_14a(cpu.CPU) except -1 # 14a BIT 1,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14b(cpu.CPU) except -1 # 14b BIT 1,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14c(cpu.CPU) except -1 # 14c BIT 1,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14d(cpu.CPU) except -1 # 14d BIT 1,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14e(cpu.CPU) except -1 # 14e BIT 1,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14f(cpu.CPU) except -1 # 14f BIT 1,A
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
cdef unsigned char BIT_15a(cpu.CPU) except -1 # 15a BIT 3,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15b(cpu.CPU) except -1 # 15b BIT 3,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15c(cpu.CPU) except -1 # 15c BIT 3,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15d(cpu.CPU) except -1 # 15d BIT 3,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15e(cpu.CPU) except -1 # 15e BIT 3,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15f(cpu.CPU) except -1 # 15f BIT 3,A
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
cdef unsigned char BIT_16a(cpu.CPU) except -1 # 16a BIT 5,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16b(cpu.CPU) except -1 # 16b BIT 5,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16c(cpu.CPU) except -1 # 16c BIT 5,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16d(cpu.CPU) except -1 # 16d BIT 5,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16e(cpu.CPU) except -1 # 16e BIT 5,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16f(cpu.CPU) except -1 # 16f BIT 5,A
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
cdef unsigned char BIT_17a(cpu.CPU) except -1 # 17a BIT 7,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17b(cpu.CPU) except -1 # 17b BIT 7,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17c(cpu.CPU) except -1 # 17c BIT 7,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17d(cpu.CPU) except -1 # 17d BIT 7,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17e(cpu.CPU) except -1 # 17e BIT 7,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17f(cpu.CPU) except -1 # 17f BIT 7,A
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
cdef unsigned char RES_18a(cpu.CPU) except -1 # 18a RES 1,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18b(cpu.CPU) except -1 # 18b RES 1,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18c(cpu.CPU) except -1 # 18c RES 1,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18d(cpu.CPU) except -1 # 18d RES 1,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18e(cpu.CPU) except -1 # 18e RES 1,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18f(cpu.CPU) except -1 # 18f RES 1,A
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
cdef unsigned char RES_19a(cpu.CPU) except -1 # 19a RES 3,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19b(cpu.CPU) except -1 # 19b RES 3,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19c(cpu.CPU) except -1 # 19c RES 3,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19d(cpu.CPU) except -1 # 19d RES 3,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19e(cpu.CPU) except -1 # 19e RES 3,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19f(cpu.CPU) except -1 # 19f RES 3,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a0(cpu.CPU) except -1 # 1a0 RES 4,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a1(cpu.CPU) except -1 # 1a1 RES 4,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a2(cpu.CPU) except -1 # 1a2 RES 4,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a3(cpu.CPU) except -1 # 1a3 RES 4,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a4(cpu.CPU) except -1 # 1a4 RES 4,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a5(cpu.CPU) except -1 # 1a5 RES 4,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a6(cpu.CPU) except -1 # 1a6 RES 4,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a7(cpu.CPU) except -1 # 1a7 RES 4,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a8(cpu.CPU) except -1 # 1a8 RES 5,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a9(cpu.CPU) except -1 # 1a9 RES 5,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1aa(cpu.CPU) except -1 # 1aa RES 5,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1ab(cpu.CPU) except -1 # 1ab RES 5,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1ac(cpu.CPU) except -1 # 1ac RES 5,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1ad(cpu.CPU) except -1 # 1ad RES 5,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1ae(cpu.CPU) except -1 # 1ae RES 5,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1af(cpu.CPU) except -1 # 1af RES 5,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b0(cpu.CPU) except -1 # 1b0 RES 6,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b1(cpu.CPU) except -1 # 1b1 RES 6,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b2(cpu.CPU) except -1 # 1b2 RES 6,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b3(cpu.CPU) except -1 # 1b3 RES 6,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b4(cpu.CPU) except -1 # 1b4 RES 6,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b5(cpu.CPU) except -1 # 1b5 RES 6,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b6(cpu.CPU) except -1 # 1b6 RES 6,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b7(cpu.CPU) except -1 # 1b7 RES 6,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b8(cpu.CPU) except -1 # 1b8 RES 7,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b9(cpu.CPU) except -1 # 1b9 RES 7,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1ba(cpu.CPU) except -1 # 1ba RES 7,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1bb(cpu.CPU) except -1 # 1bb RES 7,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1bc(cpu.CPU) except -1 # 1bc RES 7,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1bd(cpu.CPU) except -1 # 1bd RES 7,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1be(cpu.CPU) except -1 # 1be RES 7,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1bf(cpu.CPU) except -1 # 1bf RES 7,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c0(cpu.CPU) except -1 # 1c0 SET 0,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c1(cpu.CPU) except -1 # 1c1 SET 0,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c2(cpu.CPU) except -1 # 1c2 SET 0,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c3(cpu.CPU) except -1 # 1c3 SET 0,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c4(cpu.CPU) except -1 # 1c4 SET 0,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c5(cpu.CPU) except -1 # 1c5 SET 0,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c6(cpu.CPU) except -1 # 1c6 SET 0,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c7(cpu.CPU) except -1 # 1c7 SET 0,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c8(cpu.CPU) except -1 # 1c8 SET 1,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c9(cpu.CPU) except -1 # 1c9 SET 1,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ca(cpu.CPU) except -1 # 1ca SET 1,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1cb(cpu.CPU) except -1 # 1cb SET 1,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1cc(cpu.CPU) except -1 # 1cc SET 1,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1cd(cpu.CPU) except -1 # 1cd SET 1,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ce(cpu.CPU) except -1 # 1ce SET 1,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1cf(cpu.CPU) except -1 # 1cf SET 1,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d0(cpu.CPU) except -1 # 1d0 SET 2,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d1(cpu.CPU) except -1 # 1d1 SET 2,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d2(cpu.CPU) except -1 # 1d2 SET 2,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d3(cpu.CPU) except -1 # 1d3 SET 2,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d4(cpu.CPU) except -1 # 1d4 SET 2,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d5(cpu.CPU) except -1 # 1d5 SET 2,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d6(cpu.CPU) except -1 # 1d6 SET 2,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d7(cpu.CPU) except -1 # 1d7 SET 2,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d8(cpu.CPU) except -1 # 1d8 SET 3,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d9(cpu.CPU) except -1 # 1d9 SET 3,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1da(cpu.CPU) except -1 # 1da SET 3,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1db(cpu.CPU) except -1 # 1db SET 3,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1dc(cpu.CPU) except -1 # 1dc SET 3,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1dd(cpu.CPU) except -1 # 1dd SET 3,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1de(cpu.CPU) except -1 # 1de SET 3,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1df(cpu.CPU) except -1 # 1df SET 3,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e0(cpu.CPU) except -1 # 1e0 SET 4,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e1(cpu.CPU) except -1 # 1e1 SET 4,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e2(cpu.CPU) except -1 # 1e2 SET 4,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e3(cpu.CPU) except -1 # 1e3 SET 4,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e4(cpu.CPU) except -1 # 1e4 SET 4,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e5(cpu.CPU) except -1 # 1e5 SET 4,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e6(cpu.CPU) except -1 # 1e6 SET 4,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e7(cpu.CPU) except -1 # 1e7 SET 4,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e8(cpu.CPU) except -1 # 1e8 SET 5,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e9(cpu.CPU) except -1 # 1e9 SET 5,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ea(cpu.CPU) except -1 # 1ea SET 5,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1eb(cpu.CPU) except -1 # 1eb SET 5,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ec(cpu.CPU) except -1 # 1ec SET 5,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ed(cpu.CPU) except -1 # 1ed SET 5,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ee(cpu.CPU) except -1 # 1ee SET 5,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ef(cpu.CPU) except -1 # 1ef SET 5,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f0(cpu.CPU) except -1 # 1f0 SET 6,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f1(cpu.CPU) except -1 # 1f1 SET 6,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f2(cpu.CPU) except -1 # 1f2 SET 6,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f3(cpu.CPU) except -1 # 1f3 SET 6,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f4(cpu.CPU) except -1 # 1f4 SET 6,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f5(cpu.CPU) except -1 # 1f5 SET 6,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f6(cpu.CPU) except -1 # 1f6 SET 6,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f7(cpu.CPU) except -1 # 1f7 SET 6,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f8(cpu.CPU) except -1 # 1f8 SET 7,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f9(cpu.CPU) except -1 # 1f9 SET 7,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1fa(cpu.CPU) except -1 # 1fa SET 7,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1fb(cpu.CPU) except -1 # 1fb SET 7,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1fc(cpu.CPU) except -1 # 1fc SET 7,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1fd(cpu.CPU) except -1 # 1fd SET 7,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1fe(cpu.CPU) except -1 # 1fe SET 7,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ff(cpu.CPU) except -1 # 1ff SET 7,A
