
cimport numpy
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
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char NOP_00(CPU.CPU) except -1 # 00 NOP
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_01(CPU.CPU, int v) except -1 # 01 LD BC,d16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_02(CPU.CPU) except -1 # 02 LD (BC),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_03(CPU.CPU) except -1 # 03 INC BC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_04(CPU.CPU) except -1 # 04 INC B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_05(CPU.CPU) except -1 # 05 DEC B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_06(CPU.CPU, int v) except -1 # 06 LD B,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLCA_07(CPU.CPU) except -1 # 07 RLCA
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_08(CPU.CPU, int v) except -1 # 08 LD (a16),SP
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_09(CPU.CPU) except -1 # 09 ADD HL,BC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_0a(CPU.CPU) except -1 # 0a LD A,(BC)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_0b(CPU.CPU) except -1 # 0b DEC BC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_0c(CPU.CPU) except -1 # 0c INC C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_0d(CPU.CPU) except -1 # 0d DEC C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_0e(CPU.CPU, int v) except -1 # 0e LD C,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRCA_0f(CPU.CPU) except -1 # 0f RRCA
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char STOP_10(CPU.CPU, int v) except -1 # 10 STOP 0
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_11(CPU.CPU, int v) except -1 # 11 LD DE,d16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_12(CPU.CPU) except -1 # 12 LD (DE),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_13(CPU.CPU) except -1 # 13 INC DE
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_14(CPU.CPU) except -1 # 14 INC D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_15(CPU.CPU) except -1 # 15 DEC D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_16(CPU.CPU, int v) except -1 # 16 LD D,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLA_17(CPU.CPU) except -1 # 17 RLA
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JR_18(CPU.CPU, int v) except -1 # 18 JR r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_19(CPU.CPU) except -1 # 19 ADD HL,DE
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_1a(CPU.CPU) except -1 # 1a LD A,(DE)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_1b(CPU.CPU) except -1 # 1b DEC DE
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_1c(CPU.CPU) except -1 # 1c INC E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_1d(CPU.CPU) except -1 # 1d DEC E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_1e(CPU.CPU, int v) except -1 # 1e LD E,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRA_1f(CPU.CPU) except -1 # 1f RRA
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JR_20(CPU.CPU, int v) except -1 # 20 JR NZ,r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_21(CPU.CPU, int v) except -1 # 21 LD HL,d16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_22(CPU.CPU) except -1 # 22 LD (HL+),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_23(CPU.CPU) except -1 # 23 INC HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_24(CPU.CPU) except -1 # 24 INC H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_25(CPU.CPU) except -1 # 25 DEC H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_26(CPU.CPU, int v) except -1 # 26 LD H,d8
@cython.locals(v=int, flag=uchar, t=int, corr=ushort)
cdef unsigned char DAA_27(CPU.CPU) except -1 # 27 DAA
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JR_28(CPU.CPU, int v) except -1 # 28 JR Z,r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_29(CPU.CPU) except -1 # 29 ADD HL,HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_2a(CPU.CPU) except -1 # 2a LD A,(HL+)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_2b(CPU.CPU) except -1 # 2b DEC HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_2c(CPU.CPU) except -1 # 2c INC L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_2d(CPU.CPU) except -1 # 2d DEC L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_2e(CPU.CPU, int v) except -1 # 2e LD L,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CPL_2f(CPU.CPU) except -1 # 2f CPL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JR_30(CPU.CPU, int v) except -1 # 30 JR NC,r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_31(CPU.CPU, int v) except -1 # 31 LD SP,d16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_32(CPU.CPU) except -1 # 32 LD (HL-),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_33(CPU.CPU) except -1 # 33 INC SP
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_34(CPU.CPU) except -1 # 34 INC (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_35(CPU.CPU) except -1 # 35 DEC (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_36(CPU.CPU, int v) except -1 # 36 LD (HL),d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SCF_37(CPU.CPU) except -1 # 37 SCF
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JR_38(CPU.CPU, int v) except -1 # 38 JR C,r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_39(CPU.CPU) except -1 # 39 ADD HL,SP
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_3a(CPU.CPU) except -1 # 3a LD A,(HL-)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_3b(CPU.CPU) except -1 # 3b DEC SP
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char INC_3c(CPU.CPU) except -1 # 3c INC A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DEC_3d(CPU.CPU) except -1 # 3d DEC A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_3e(CPU.CPU, int v) except -1 # 3e LD A,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CCF_3f(CPU.CPU) except -1 # 3f CCF
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_40(CPU.CPU) except -1 # 40 LD B,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_41(CPU.CPU) except -1 # 41 LD B,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_42(CPU.CPU) except -1 # 42 LD B,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_43(CPU.CPU) except -1 # 43 LD B,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_44(CPU.CPU) except -1 # 44 LD B,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_45(CPU.CPU) except -1 # 45 LD B,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_46(CPU.CPU) except -1 # 46 LD B,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_47(CPU.CPU) except -1 # 47 LD B,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_48(CPU.CPU) except -1 # 48 LD C,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_49(CPU.CPU) except -1 # 49 LD C,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4a(CPU.CPU) except -1 # 4a LD C,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4b(CPU.CPU) except -1 # 4b LD C,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4c(CPU.CPU) except -1 # 4c LD C,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4d(CPU.CPU) except -1 # 4d LD C,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4e(CPU.CPU) except -1 # 4e LD C,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_4f(CPU.CPU) except -1 # 4f LD C,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_50(CPU.CPU) except -1 # 50 LD D,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_51(CPU.CPU) except -1 # 51 LD D,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_52(CPU.CPU) except -1 # 52 LD D,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_53(CPU.CPU) except -1 # 53 LD D,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_54(CPU.CPU) except -1 # 54 LD D,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_55(CPU.CPU) except -1 # 55 LD D,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_56(CPU.CPU) except -1 # 56 LD D,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_57(CPU.CPU) except -1 # 57 LD D,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_58(CPU.CPU) except -1 # 58 LD E,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_59(CPU.CPU) except -1 # 59 LD E,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5a(CPU.CPU) except -1 # 5a LD E,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5b(CPU.CPU) except -1 # 5b LD E,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5c(CPU.CPU) except -1 # 5c LD E,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5d(CPU.CPU) except -1 # 5d LD E,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5e(CPU.CPU) except -1 # 5e LD E,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_5f(CPU.CPU) except -1 # 5f LD E,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_60(CPU.CPU) except -1 # 60 LD H,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_61(CPU.CPU) except -1 # 61 LD H,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_62(CPU.CPU) except -1 # 62 LD H,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_63(CPU.CPU) except -1 # 63 LD H,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_64(CPU.CPU) except -1 # 64 LD H,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_65(CPU.CPU) except -1 # 65 LD H,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_66(CPU.CPU) except -1 # 66 LD H,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_67(CPU.CPU) except -1 # 67 LD H,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_68(CPU.CPU) except -1 # 68 LD L,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_69(CPU.CPU) except -1 # 69 LD L,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6a(CPU.CPU) except -1 # 6a LD L,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6b(CPU.CPU) except -1 # 6b LD L,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6c(CPU.CPU) except -1 # 6c LD L,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6d(CPU.CPU) except -1 # 6d LD L,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6e(CPU.CPU) except -1 # 6e LD L,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_6f(CPU.CPU) except -1 # 6f LD L,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_70(CPU.CPU) except -1 # 70 LD (HL),B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_71(CPU.CPU) except -1 # 71 LD (HL),C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_72(CPU.CPU) except -1 # 72 LD (HL),D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_73(CPU.CPU) except -1 # 73 LD (HL),E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_74(CPU.CPU) except -1 # 74 LD (HL),H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_75(CPU.CPU) except -1 # 75 LD (HL),L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char HALT_76(CPU.CPU) except -1 # 76 HALT
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_77(CPU.CPU) except -1 # 77 LD (HL),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_78(CPU.CPU) except -1 # 78 LD A,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_79(CPU.CPU) except -1 # 79 LD A,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7a(CPU.CPU) except -1 # 7a LD A,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7b(CPU.CPU) except -1 # 7b LD A,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7c(CPU.CPU) except -1 # 7c LD A,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7d(CPU.CPU) except -1 # 7d LD A,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7e(CPU.CPU) except -1 # 7e LD A,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_7f(CPU.CPU) except -1 # 7f LD A,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_80(CPU.CPU) except -1 # 80 ADD A,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_81(CPU.CPU) except -1 # 81 ADD A,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_82(CPU.CPU) except -1 # 82 ADD A,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_83(CPU.CPU) except -1 # 83 ADD A,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_84(CPU.CPU) except -1 # 84 ADD A,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_85(CPU.CPU) except -1 # 85 ADD A,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_86(CPU.CPU) except -1 # 86 ADD A,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_87(CPU.CPU) except -1 # 87 ADD A,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_88(CPU.CPU) except -1 # 88 ADC A,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_89(CPU.CPU) except -1 # 89 ADC A,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8a(CPU.CPU) except -1 # 8a ADC A,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8b(CPU.CPU) except -1 # 8b ADC A,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8c(CPU.CPU) except -1 # 8c ADC A,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8d(CPU.CPU) except -1 # 8d ADC A,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8e(CPU.CPU) except -1 # 8e ADC A,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_8f(CPU.CPU) except -1 # 8f ADC A,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_90(CPU.CPU) except -1 # 90 SUB B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_91(CPU.CPU) except -1 # 91 SUB C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_92(CPU.CPU) except -1 # 92 SUB D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_93(CPU.CPU) except -1 # 93 SUB E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_94(CPU.CPU) except -1 # 94 SUB H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_95(CPU.CPU) except -1 # 95 SUB L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_96(CPU.CPU) except -1 # 96 SUB (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_97(CPU.CPU) except -1 # 97 SUB A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_98(CPU.CPU) except -1 # 98 SBC A,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_99(CPU.CPU) except -1 # 99 SBC A,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9a(CPU.CPU) except -1 # 9a SBC A,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9b(CPU.CPU) except -1 # 9b SBC A,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9c(CPU.CPU) except -1 # 9c SBC A,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9d(CPU.CPU) except -1 # 9d SBC A,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9e(CPU.CPU) except -1 # 9e SBC A,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_9f(CPU.CPU) except -1 # 9f SBC A,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a0(CPU.CPU) except -1 # a0 AND B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a1(CPU.CPU) except -1 # a1 AND C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a2(CPU.CPU) except -1 # a2 AND D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a3(CPU.CPU) except -1 # a3 AND E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a4(CPU.CPU) except -1 # a4 AND H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a5(CPU.CPU) except -1 # a5 AND L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a6(CPU.CPU) except -1 # a6 AND (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_a7(CPU.CPU) except -1 # a7 AND A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_a8(CPU.CPU) except -1 # a8 XOR B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_a9(CPU.CPU) except -1 # a9 XOR C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_aa(CPU.CPU) except -1 # aa XOR D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_ab(CPU.CPU) except -1 # ab XOR E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_ac(CPU.CPU) except -1 # ac XOR H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_ad(CPU.CPU) except -1 # ad XOR L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_ae(CPU.CPU) except -1 # ae XOR (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_af(CPU.CPU) except -1 # af XOR A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b0(CPU.CPU) except -1 # b0 OR B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b1(CPU.CPU) except -1 # b1 OR C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b2(CPU.CPU) except -1 # b2 OR D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b3(CPU.CPU) except -1 # b3 OR E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b4(CPU.CPU) except -1 # b4 OR H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b5(CPU.CPU) except -1 # b5 OR L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b6(CPU.CPU) except -1 # b6 OR (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_b7(CPU.CPU) except -1 # b7 OR A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_b8(CPU.CPU) except -1 # b8 CP B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_b9(CPU.CPU) except -1 # b9 CP C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_ba(CPU.CPU) except -1 # ba CP D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_bb(CPU.CPU) except -1 # bb CP E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_bc(CPU.CPU) except -1 # bc CP H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_bd(CPU.CPU) except -1 # bd CP L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_be(CPU.CPU) except -1 # be CP (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_bf(CPU.CPU) except -1 # bf CP A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_c0(CPU.CPU) except -1 # c0 RET NZ
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char POP_c1(CPU.CPU) except -1 # c1 POP BC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_c2(CPU.CPU, int v) except -1 # c2 JP NZ,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_c3(CPU.CPU, int v) except -1 # c3 JP a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_c4(CPU.CPU, int v) except -1 # c4 CALL NZ,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char PUSH_c5(CPU.CPU) except -1 # c5 PUSH BC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_c6(CPU.CPU, int v) except -1 # c6 ADD A,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_c7(CPU.CPU) except -1 # c7 RST 00H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_c8(CPU.CPU) except -1 # c8 RET Z
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_c9(CPU.CPU) except -1 # c9 RET
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_ca(CPU.CPU, int v) except -1 # ca JP Z,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CB_cb(CPU.CPU) except -1 # cb PREFIX CB
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_cc(CPU.CPU, int v) except -1 # cc CALL Z,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_cd(CPU.CPU, int v) except -1 # cd CALL a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADC_ce(CPU.CPU, int v) except -1 # ce ADC A,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_cf(CPU.CPU) except -1 # cf RST 08H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_d0(CPU.CPU) except -1 # d0 RET NC
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char POP_d1(CPU.CPU) except -1 # d1 POP DE
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_d2(CPU.CPU, int v) except -1 # d2 JP NC,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_d4(CPU.CPU, int v) except -1 # d4 CALL NC,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char PUSH_d5(CPU.CPU) except -1 # d5 PUSH DE
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SUB_d6(CPU.CPU, int v) except -1 # d6 SUB d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_d7(CPU.CPU) except -1 # d7 RST 10H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RET_d8(CPU.CPU) except -1 # d8 RET C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RETI_d9(CPU.CPU) except -1 # d9 RETI
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_da(CPU.CPU, int v) except -1 # da JP C,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CALL_dc(CPU.CPU, int v) except -1 # dc CALL C,a16
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SBC_de(CPU.CPU, int v) except -1 # de SBC A,d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_df(CPU.CPU) except -1 # df RST 18H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_e0(CPU.CPU, int v) except -1 # e0 LDH (a8),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char POP_e1(CPU.CPU) except -1 # e1 POP HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_e2(CPU.CPU) except -1 # e2 LD (C),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char PUSH_e5(CPU.CPU) except -1 # e5 PUSH HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char AND_e6(CPU.CPU, int v) except -1 # e6 AND d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_e7(CPU.CPU) except -1 # e7 RST 20H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char ADD_e8(CPU.CPU, int v) except -1 # e8 ADD SP,r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char JP_e9(CPU.CPU) except -1 # e9 JP (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_ea(CPU.CPU, int v) except -1 # ea LD (a16),A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char XOR_ee(CPU.CPU, int v) except -1 # ee XOR d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_ef(CPU.CPU) except -1 # ef RST 28H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_f0(CPU.CPU, int v) except -1 # f0 LDH A,(a8)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char POP_f1(CPU.CPU) except -1 # f1 POP AF
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_f2(CPU.CPU) except -1 # f2 LD A,(C)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char DI_f3(CPU.CPU) except -1 # f3 DI
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char PUSH_f5(CPU.CPU) except -1 # f5 PUSH AF
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char OR_f6(CPU.CPU, int v) except -1 # f6 OR d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_f7(CPU.CPU) except -1 # f7 RST 30H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_f8(CPU.CPU, int v) except -1 # f8 LD HL,SP+r8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_f9(CPU.CPU) except -1 # f9 LD SP,HL
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char LD_fa(CPU.CPU, int v) except -1 # fa LD A,(a16)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char EI_fb(CPU.CPU) except -1 # fb EI
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char CP_fe(CPU.CPU, int v) except -1 # fe CP d8
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RST_ff(CPU.CPU) except -1 # ff RST 38H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_100(CPU.CPU) except -1 # 100 RLC B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_101(CPU.CPU) except -1 # 101 RLC C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_102(CPU.CPU) except -1 # 102 RLC D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_103(CPU.CPU) except -1 # 103 RLC E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_104(CPU.CPU) except -1 # 104 RLC H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_105(CPU.CPU) except -1 # 105 RLC L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_106(CPU.CPU) except -1 # 106 RLC (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RLC_107(CPU.CPU) except -1 # 107 RLC A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_108(CPU.CPU) except -1 # 108 RRC B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_109(CPU.CPU) except -1 # 109 RRC C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10a(CPU.CPU) except -1 # 10a RRC D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10b(CPU.CPU) except -1 # 10b RRC E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10c(CPU.CPU) except -1 # 10c RRC H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10d(CPU.CPU) except -1 # 10d RRC L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10e(CPU.CPU) except -1 # 10e RRC (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RRC_10f(CPU.CPU) except -1 # 10f RRC A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_110(CPU.CPU) except -1 # 110 RL B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_111(CPU.CPU) except -1 # 111 RL C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_112(CPU.CPU) except -1 # 112 RL D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_113(CPU.CPU) except -1 # 113 RL E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_114(CPU.CPU) except -1 # 114 RL H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_115(CPU.CPU) except -1 # 115 RL L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_116(CPU.CPU) except -1 # 116 RL (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RL_117(CPU.CPU) except -1 # 117 RL A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_118(CPU.CPU) except -1 # 118 RR B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_119(CPU.CPU) except -1 # 119 RR C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11a(CPU.CPU) except -1 # 11a RR D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11b(CPU.CPU) except -1 # 11b RR E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11c(CPU.CPU) except -1 # 11c RR H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11d(CPU.CPU) except -1 # 11d RR L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11e(CPU.CPU) except -1 # 11e RR (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RR_11f(CPU.CPU) except -1 # 11f RR A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_120(CPU.CPU) except -1 # 120 SLA B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_121(CPU.CPU) except -1 # 121 SLA C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_122(CPU.CPU) except -1 # 122 SLA D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_123(CPU.CPU) except -1 # 123 SLA E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_124(CPU.CPU) except -1 # 124 SLA H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_125(CPU.CPU) except -1 # 125 SLA L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_126(CPU.CPU) except -1 # 126 SLA (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SLA_127(CPU.CPU) except -1 # 127 SLA A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_128(CPU.CPU) except -1 # 128 SRA B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_129(CPU.CPU) except -1 # 129 SRA C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12a(CPU.CPU) except -1 # 12a SRA D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12b(CPU.CPU) except -1 # 12b SRA E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12c(CPU.CPU) except -1 # 12c SRA H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12d(CPU.CPU) except -1 # 12d SRA L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12e(CPU.CPU) except -1 # 12e SRA (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRA_12f(CPU.CPU) except -1 # 12f SRA A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_130(CPU.CPU) except -1 # 130 SWAP B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_131(CPU.CPU) except -1 # 131 SWAP C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_132(CPU.CPU) except -1 # 132 SWAP D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_133(CPU.CPU) except -1 # 133 SWAP E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_134(CPU.CPU) except -1 # 134 SWAP H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_135(CPU.CPU) except -1 # 135 SWAP L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_136(CPU.CPU) except -1 # 136 SWAP (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SWAP_137(CPU.CPU) except -1 # 137 SWAP A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_138(CPU.CPU) except -1 # 138 SRL B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_139(CPU.CPU) except -1 # 139 SRL C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13a(CPU.CPU) except -1 # 13a SRL D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13b(CPU.CPU) except -1 # 13b SRL E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13c(CPU.CPU) except -1 # 13c SRL H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13d(CPU.CPU) except -1 # 13d SRL L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13e(CPU.CPU) except -1 # 13e SRL (HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SRL_13f(CPU.CPU) except -1 # 13f SRL A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_140(CPU.CPU) except -1 # 140 BIT 0,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_141(CPU.CPU) except -1 # 141 BIT 0,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_142(CPU.CPU) except -1 # 142 BIT 0,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_143(CPU.CPU) except -1 # 143 BIT 0,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_144(CPU.CPU) except -1 # 144 BIT 0,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_145(CPU.CPU) except -1 # 145 BIT 0,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_146(CPU.CPU) except -1 # 146 BIT 0,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_147(CPU.CPU) except -1 # 147 BIT 0,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_148(CPU.CPU) except -1 # 148 BIT 1,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_149(CPU.CPU) except -1 # 149 BIT 1,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14a(CPU.CPU) except -1 # 14a BIT 1,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14b(CPU.CPU) except -1 # 14b BIT 1,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14c(CPU.CPU) except -1 # 14c BIT 1,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14d(CPU.CPU) except -1 # 14d BIT 1,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14e(CPU.CPU) except -1 # 14e BIT 1,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_14f(CPU.CPU) except -1 # 14f BIT 1,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_150(CPU.CPU) except -1 # 150 BIT 2,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_151(CPU.CPU) except -1 # 151 BIT 2,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_152(CPU.CPU) except -1 # 152 BIT 2,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_153(CPU.CPU) except -1 # 153 BIT 2,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_154(CPU.CPU) except -1 # 154 BIT 2,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_155(CPU.CPU) except -1 # 155 BIT 2,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_156(CPU.CPU) except -1 # 156 BIT 2,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_157(CPU.CPU) except -1 # 157 BIT 2,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_158(CPU.CPU) except -1 # 158 BIT 3,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_159(CPU.CPU) except -1 # 159 BIT 3,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15a(CPU.CPU) except -1 # 15a BIT 3,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15b(CPU.CPU) except -1 # 15b BIT 3,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15c(CPU.CPU) except -1 # 15c BIT 3,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15d(CPU.CPU) except -1 # 15d BIT 3,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15e(CPU.CPU) except -1 # 15e BIT 3,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_15f(CPU.CPU) except -1 # 15f BIT 3,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_160(CPU.CPU) except -1 # 160 BIT 4,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_161(CPU.CPU) except -1 # 161 BIT 4,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_162(CPU.CPU) except -1 # 162 BIT 4,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_163(CPU.CPU) except -1 # 163 BIT 4,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_164(CPU.CPU) except -1 # 164 BIT 4,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_165(CPU.CPU) except -1 # 165 BIT 4,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_166(CPU.CPU) except -1 # 166 BIT 4,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_167(CPU.CPU) except -1 # 167 BIT 4,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_168(CPU.CPU) except -1 # 168 BIT 5,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_169(CPU.CPU) except -1 # 169 BIT 5,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16a(CPU.CPU) except -1 # 16a BIT 5,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16b(CPU.CPU) except -1 # 16b BIT 5,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16c(CPU.CPU) except -1 # 16c BIT 5,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16d(CPU.CPU) except -1 # 16d BIT 5,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16e(CPU.CPU) except -1 # 16e BIT 5,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_16f(CPU.CPU) except -1 # 16f BIT 5,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_170(CPU.CPU) except -1 # 170 BIT 6,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_171(CPU.CPU) except -1 # 171 BIT 6,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_172(CPU.CPU) except -1 # 172 BIT 6,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_173(CPU.CPU) except -1 # 173 BIT 6,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_174(CPU.CPU) except -1 # 174 BIT 6,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_175(CPU.CPU) except -1 # 175 BIT 6,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_176(CPU.CPU) except -1 # 176 BIT 6,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_177(CPU.CPU) except -1 # 177 BIT 6,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_178(CPU.CPU) except -1 # 178 BIT 7,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_179(CPU.CPU) except -1 # 179 BIT 7,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17a(CPU.CPU) except -1 # 17a BIT 7,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17b(CPU.CPU) except -1 # 17b BIT 7,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17c(CPU.CPU) except -1 # 17c BIT 7,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17d(CPU.CPU) except -1 # 17d BIT 7,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17e(CPU.CPU) except -1 # 17e BIT 7,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char BIT_17f(CPU.CPU) except -1 # 17f BIT 7,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_180(CPU.CPU) except -1 # 180 RES 0,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_181(CPU.CPU) except -1 # 181 RES 0,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_182(CPU.CPU) except -1 # 182 RES 0,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_183(CPU.CPU) except -1 # 183 RES 0,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_184(CPU.CPU) except -1 # 184 RES 0,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_185(CPU.CPU) except -1 # 185 RES 0,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_186(CPU.CPU) except -1 # 186 RES 0,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_187(CPU.CPU) except -1 # 187 RES 0,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_188(CPU.CPU) except -1 # 188 RES 1,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_189(CPU.CPU) except -1 # 189 RES 1,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18a(CPU.CPU) except -1 # 18a RES 1,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18b(CPU.CPU) except -1 # 18b RES 1,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18c(CPU.CPU) except -1 # 18c RES 1,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18d(CPU.CPU) except -1 # 18d RES 1,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18e(CPU.CPU) except -1 # 18e RES 1,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_18f(CPU.CPU) except -1 # 18f RES 1,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_190(CPU.CPU) except -1 # 190 RES 2,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_191(CPU.CPU) except -1 # 191 RES 2,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_192(CPU.CPU) except -1 # 192 RES 2,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_193(CPU.CPU) except -1 # 193 RES 2,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_194(CPU.CPU) except -1 # 194 RES 2,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_195(CPU.CPU) except -1 # 195 RES 2,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_196(CPU.CPU) except -1 # 196 RES 2,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_197(CPU.CPU) except -1 # 197 RES 2,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_198(CPU.CPU) except -1 # 198 RES 3,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_199(CPU.CPU) except -1 # 199 RES 3,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19a(CPU.CPU) except -1 # 19a RES 3,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19b(CPU.CPU) except -1 # 19b RES 3,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19c(CPU.CPU) except -1 # 19c RES 3,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19d(CPU.CPU) except -1 # 19d RES 3,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19e(CPU.CPU) except -1 # 19e RES 3,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_19f(CPU.CPU) except -1 # 19f RES 3,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a0(CPU.CPU) except -1 # 1a0 RES 4,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a1(CPU.CPU) except -1 # 1a1 RES 4,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a2(CPU.CPU) except -1 # 1a2 RES 4,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a3(CPU.CPU) except -1 # 1a3 RES 4,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a4(CPU.CPU) except -1 # 1a4 RES 4,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a5(CPU.CPU) except -1 # 1a5 RES 4,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a6(CPU.CPU) except -1 # 1a6 RES 4,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a7(CPU.CPU) except -1 # 1a7 RES 4,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a8(CPU.CPU) except -1 # 1a8 RES 5,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1a9(CPU.CPU) except -1 # 1a9 RES 5,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1aa(CPU.CPU) except -1 # 1aa RES 5,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1ab(CPU.CPU) except -1 # 1ab RES 5,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1ac(CPU.CPU) except -1 # 1ac RES 5,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1ad(CPU.CPU) except -1 # 1ad RES 5,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1ae(CPU.CPU) except -1 # 1ae RES 5,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1af(CPU.CPU) except -1 # 1af RES 5,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b0(CPU.CPU) except -1 # 1b0 RES 6,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b1(CPU.CPU) except -1 # 1b1 RES 6,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b2(CPU.CPU) except -1 # 1b2 RES 6,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b3(CPU.CPU) except -1 # 1b3 RES 6,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b4(CPU.CPU) except -1 # 1b4 RES 6,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b5(CPU.CPU) except -1 # 1b5 RES 6,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b6(CPU.CPU) except -1 # 1b6 RES 6,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b7(CPU.CPU) except -1 # 1b7 RES 6,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b8(CPU.CPU) except -1 # 1b8 RES 7,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1b9(CPU.CPU) except -1 # 1b9 RES 7,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1ba(CPU.CPU) except -1 # 1ba RES 7,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1bb(CPU.CPU) except -1 # 1bb RES 7,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1bc(CPU.CPU) except -1 # 1bc RES 7,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1bd(CPU.CPU) except -1 # 1bd RES 7,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1be(CPU.CPU) except -1 # 1be RES 7,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char RES_1bf(CPU.CPU) except -1 # 1bf RES 7,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c0(CPU.CPU) except -1 # 1c0 SET 0,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c1(CPU.CPU) except -1 # 1c1 SET 0,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c2(CPU.CPU) except -1 # 1c2 SET 0,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c3(CPU.CPU) except -1 # 1c3 SET 0,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c4(CPU.CPU) except -1 # 1c4 SET 0,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c5(CPU.CPU) except -1 # 1c5 SET 0,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c6(CPU.CPU) except -1 # 1c6 SET 0,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c7(CPU.CPU) except -1 # 1c7 SET 0,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c8(CPU.CPU) except -1 # 1c8 SET 1,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1c9(CPU.CPU) except -1 # 1c9 SET 1,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ca(CPU.CPU) except -1 # 1ca SET 1,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1cb(CPU.CPU) except -1 # 1cb SET 1,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1cc(CPU.CPU) except -1 # 1cc SET 1,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1cd(CPU.CPU) except -1 # 1cd SET 1,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ce(CPU.CPU) except -1 # 1ce SET 1,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1cf(CPU.CPU) except -1 # 1cf SET 1,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d0(CPU.CPU) except -1 # 1d0 SET 2,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d1(CPU.CPU) except -1 # 1d1 SET 2,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d2(CPU.CPU) except -1 # 1d2 SET 2,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d3(CPU.CPU) except -1 # 1d3 SET 2,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d4(CPU.CPU) except -1 # 1d4 SET 2,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d5(CPU.CPU) except -1 # 1d5 SET 2,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d6(CPU.CPU) except -1 # 1d6 SET 2,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d7(CPU.CPU) except -1 # 1d7 SET 2,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d8(CPU.CPU) except -1 # 1d8 SET 3,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1d9(CPU.CPU) except -1 # 1d9 SET 3,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1da(CPU.CPU) except -1 # 1da SET 3,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1db(CPU.CPU) except -1 # 1db SET 3,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1dc(CPU.CPU) except -1 # 1dc SET 3,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1dd(CPU.CPU) except -1 # 1dd SET 3,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1de(CPU.CPU) except -1 # 1de SET 3,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1df(CPU.CPU) except -1 # 1df SET 3,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e0(CPU.CPU) except -1 # 1e0 SET 4,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e1(CPU.CPU) except -1 # 1e1 SET 4,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e2(CPU.CPU) except -1 # 1e2 SET 4,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e3(CPU.CPU) except -1 # 1e3 SET 4,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e4(CPU.CPU) except -1 # 1e4 SET 4,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e5(CPU.CPU) except -1 # 1e5 SET 4,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e6(CPU.CPU) except -1 # 1e6 SET 4,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e7(CPU.CPU) except -1 # 1e7 SET 4,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e8(CPU.CPU) except -1 # 1e8 SET 5,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1e9(CPU.CPU) except -1 # 1e9 SET 5,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ea(CPU.CPU) except -1 # 1ea SET 5,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1eb(CPU.CPU) except -1 # 1eb SET 5,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ec(CPU.CPU) except -1 # 1ec SET 5,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ed(CPU.CPU) except -1 # 1ed SET 5,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ee(CPU.CPU) except -1 # 1ee SET 5,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ef(CPU.CPU) except -1 # 1ef SET 5,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f0(CPU.CPU) except -1 # 1f0 SET 6,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f1(CPU.CPU) except -1 # 1f1 SET 6,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f2(CPU.CPU) except -1 # 1f2 SET 6,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f3(CPU.CPU) except -1 # 1f3 SET 6,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f4(CPU.CPU) except -1 # 1f4 SET 6,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f5(CPU.CPU) except -1 # 1f5 SET 6,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f6(CPU.CPU) except -1 # 1f6 SET 6,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f7(CPU.CPU) except -1 # 1f7 SET 6,A
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f8(CPU.CPU) except -1 # 1f8 SET 7,B
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1f9(CPU.CPU) except -1 # 1f9 SET 7,C
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1fa(CPU.CPU) except -1 # 1fa SET 7,D
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1fb(CPU.CPU) except -1 # 1fb SET 7,E
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1fc(CPU.CPU) except -1 # 1fc SET 7,H
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1fd(CPU.CPU) except -1 # 1fd SET 7,L
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1fe(CPU.CPU) except -1 # 1fe SET 7,(HL)
@cython.locals(v=int, flag=uchar, t=int)
cdef unsigned char SET_1ff(CPU.CPU) except -1 # 1ff SET 7,A
