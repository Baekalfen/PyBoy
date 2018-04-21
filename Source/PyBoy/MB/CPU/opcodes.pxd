cdef short NOP_00(self) # 00 NOP
cdef short LD_01(self, int v) # 01 LD BC,d16
cdef short LD_02(self) # 02 LD (BC),A
cdef short INC_03(self) # 03 INC BC
cdef short INC_04(self) # 04 INC B
cdef short DEC_05(self) # 05 DEC B
cdef short LD_06(self, int v) # 06 LD B,d8
cdef short RLCA_07(self) # 07 RLCA
cdef short LD_08(self, int v) # 08 LD (a16),SP
cdef short ADD_09(self) # 09 ADD HL,BC
cdef short LD_0a(self) # 0a LD A,(BC)
cdef short DEC_0b(self) # 0b DEC BC
cdef short INC_0c(self) # 0c INC C
cdef short DEC_0d(self) # 0d DEC C
cdef short LD_0e(self, int v) # 0e LD C,d8
cdef short RRCA_0f(self) # 0f RRCA
cdef short STOP_10(self, int v) # 10 STOP 0
cdef short LD_11(self, int v) # 11 LD DE,d16
cdef short LD_12(self) # 12 LD (DE),A
cdef short INC_13(self) # 13 INC DE
cdef short INC_14(self) # 14 INC D
cdef short DEC_15(self) # 15 DEC D
cdef short LD_16(self, int v) # 16 LD D,d8
cdef short RLA_17(self) # 17 RLA
cdef short JR_18(self, int v) # 18 JR r8
cdef short ADD_19(self) # 19 ADD HL,DE
cdef short LD_1a(self) # 1a LD A,(DE)
cdef short DEC_1b(self) # 1b DEC DE
cdef short INC_1c(self) # 1c INC E
cdef short DEC_1d(self) # 1d DEC E
cdef short LD_1e(self, int v) # 1e LD E,d8
cdef short RRA_1f(self) # 1f RRA
cdef short JR_20(self, int v) # 20 JR NZ,r8
cdef short LD_21(self, int v) # 21 LD HL,d16
cdef short LD_22(self) # 22 LD (HL+),A
cdef short INC_23(self) # 23 INC HL
cdef short INC_24(self) # 24 INC H
cdef short DEC_25(self) # 25 DEC H
cdef short LD_26(self, int v) # 26 LD H,d8
cdef short DAA_27(self) # 27 DAA
cdef short JR_28(self, int v) # 28 JR Z,r8
cdef short ADD_29(self) # 29 ADD HL,HL
cdef short LD_2a(self) # 2a LD A,(HL+)
cdef short DEC_2b(self) # 2b DEC HL
cdef short INC_2c(self) # 2c INC L
cdef short DEC_2d(self) # 2d DEC L
cdef short LD_2e(self, int v) # 2e LD L,d8
cdef short CPL_2f(self) # 2f CPL
cdef short JR_30(self, int v) # 30 JR NC,r8
cdef short LD_31(self, int v) # 31 LD SP,d16
cdef short LD_32(self) # 32 LD (HL-),A
cdef short INC_33(self) # 33 INC SP
cdef short INC_34(self) # 34 INC (HL)
cdef short DEC_35(self) # 35 DEC (HL)
cdef short LD_36(self, int v) # 36 LD (HL),d8
cdef short SCF_37(self) # 37 SCF
cdef short JR_38(self, int v) # 38 JR C,r8
cdef short ADD_39(self) # 39 ADD HL,SP
cdef short LD_3a(self) # 3a LD A,(HL-)
cdef short DEC_3b(self) # 3b DEC SP
cdef short INC_3c(self) # 3c INC A
cdef short DEC_3d(self) # 3d DEC A
cdef short LD_3e(self, int v) # 3e LD A,d8
cdef short CCF_3f(self) # 3f CCF
cdef short LD_40(self) # 40 LD B,B
cdef short LD_41(self) # 41 LD B,C
cdef short LD_42(self) # 42 LD B,D
cdef short LD_43(self) # 43 LD B,E
cdef short LD_44(self) # 44 LD B,H
cdef short LD_45(self) # 45 LD B,L
cdef short LD_46(self) # 46 LD B,(HL)
cdef short LD_47(self) # 47 LD B,A
cdef short LD_48(self) # 48 LD C,B
cdef short LD_49(self) # 49 LD C,C
cdef short LD_4a(self) # 4a LD C,D
cdef short LD_4b(self) # 4b LD C,E
cdef short LD_4c(self) # 4c LD C,H
cdef short LD_4d(self) # 4d LD C,L
cdef short LD_4e(self) # 4e LD C,(HL)
cdef short LD_4f(self) # 4f LD C,A
cdef short LD_50(self) # 50 LD D,B
cdef short LD_51(self) # 51 LD D,C
cdef short LD_52(self) # 52 LD D,D
cdef short LD_53(self) # 53 LD D,E
cdef short LD_54(self) # 54 LD D,H
cdef short LD_55(self) # 55 LD D,L
cdef short LD_56(self) # 56 LD D,(HL)
cdef short LD_57(self) # 57 LD D,A
cdef short LD_58(self) # 58 LD E,B
cdef short LD_59(self) # 59 LD E,C
cdef short LD_5a(self) # 5a LD E,D
cdef short LD_5b(self) # 5b LD E,E
cdef short LD_5c(self) # 5c LD E,H
cdef short LD_5d(self) # 5d LD E,L
cdef short LD_5e(self) # 5e LD E,(HL)
cdef short LD_5f(self) # 5f LD E,A
cdef short LD_60(self) # 60 LD H,B
cdef short LD_61(self) # 61 LD H,C
cdef short LD_62(self) # 62 LD H,D
cdef short LD_63(self) # 63 LD H,E
cdef short LD_64(self) # 64 LD H,H
cdef short LD_65(self) # 65 LD H,L
cdef short LD_66(self) # 66 LD H,(HL)
cdef short LD_67(self) # 67 LD H,A
cdef short LD_68(self) # 68 LD L,B
cdef short LD_69(self) # 69 LD L,C
cdef short LD_6a(self) # 6a LD L,D
cdef short LD_6b(self) # 6b LD L,E
cdef short LD_6c(self) # 6c LD L,H
cdef short LD_6d(self) # 6d LD L,L
cdef short LD_6e(self) # 6e LD L,(HL)
cdef short LD_6f(self) # 6f LD L,A
cdef short LD_70(self) # 70 LD (HL),B
cdef short LD_71(self) # 71 LD (HL),C
cdef short LD_72(self) # 72 LD (HL),D
cdef short LD_73(self) # 73 LD (HL),E
cdef short LD_74(self) # 74 LD (HL),H
cdef short LD_75(self) # 75 LD (HL),L
cdef short HALT_76(self) # 76 HALT
cdef short LD_77(self) # 77 LD (HL),A
cdef short LD_78(self) # 78 LD A,B
cdef short LD_79(self) # 79 LD A,C
cdef short LD_7a(self) # 7a LD A,D
cdef short LD_7b(self) # 7b LD A,E
cdef short LD_7c(self) # 7c LD A,H
cdef short LD_7d(self) # 7d LD A,L
cdef short LD_7e(self) # 7e LD A,(HL)
cdef short LD_7f(self) # 7f LD A,A
cdef short ADD_80(self) # 80 ADD A,B
cdef short ADD_81(self) # 81 ADD A,C
cdef short ADD_82(self) # 82 ADD A,D
cdef short ADD_83(self) # 83 ADD A,E
cdef short ADD_84(self) # 84 ADD A,H
cdef short ADD_85(self) # 85 ADD A,L
cdef short ADD_86(self) # 86 ADD A,(HL)
cdef short ADD_87(self) # 87 ADD A,A
cdef short ADC_88(self) # 88 ADC A,B
cdef short ADC_89(self) # 89 ADC A,C
cdef short ADC_8a(self) # 8a ADC A,D
cdef short ADC_8b(self) # 8b ADC A,E
cdef short ADC_8c(self) # 8c ADC A,H
cdef short ADC_8d(self) # 8d ADC A,L
cdef short ADC_8e(self) # 8e ADC A,(HL)
cdef short ADC_8f(self) # 8f ADC A,A
cdef short SUB_90(self) # 90 SUB B
cdef short SUB_91(self) # 91 SUB C
cdef short SUB_92(self) # 92 SUB D
cdef short SUB_93(self) # 93 SUB E
cdef short SUB_94(self) # 94 SUB H
cdef short SUB_95(self) # 95 SUB L
cdef short SUB_96(self) # 96 SUB (HL)
cdef short SUB_97(self) # 97 SUB A
cdef short SBC_98(self) # 98 SBC A,B
cdef short SBC_99(self) # 99 SBC A,C
cdef short SBC_9a(self) # 9a SBC A,D
cdef short SBC_9b(self) # 9b SBC A,E
cdef short SBC_9c(self) # 9c SBC A,H
cdef short SBC_9d(self) # 9d SBC A,L
cdef short SBC_9e(self) # 9e SBC A,(HL)
cdef short SBC_9f(self) # 9f SBC A,A
cdef short AND_a0(self) # a0 AND B
cdef short AND_a1(self) # a1 AND C
cdef short AND_a2(self) # a2 AND D
cdef short AND_a3(self) # a3 AND E
cdef short AND_a4(self) # a4 AND H
cdef short AND_a5(self) # a5 AND L
cdef short AND_a6(self) # a6 AND (HL)
cdef short AND_a7(self) # a7 AND A
cdef short XOR_a8(self) # a8 XOR B
cdef short XOR_a9(self) # a9 XOR C
cdef short XOR_aa(self) # aa XOR D
cdef short XOR_ab(self) # ab XOR E
cdef short XOR_ac(self) # ac XOR H
cdef short XOR_ad(self) # ad XOR L
cdef short XOR_ae(self) # ae XOR (HL)
cdef short XOR_af(self) # af XOR A
cdef short OR_b0(self) # b0 OR B
cdef short OR_b1(self) # b1 OR C
cdef short OR_b2(self) # b2 OR D
cdef short OR_b3(self) # b3 OR E
cdef short OR_b4(self) # b4 OR H
cdef short OR_b5(self) # b5 OR L
cdef short OR_b6(self) # b6 OR (HL)
cdef short OR_b7(self) # b7 OR A
cdef short CP_b8(self) # b8 CP B
cdef short CP_b9(self) # b9 CP C
cdef short CP_ba(self) # ba CP D
cdef short CP_bb(self) # bb CP E
cdef short CP_bc(self) # bc CP H
cdef short CP_bd(self) # bd CP L
cdef short CP_be(self) # be CP (HL)
cdef short CP_bf(self) # bf CP A
cdef short RET_c0(self) # c0 RET NZ
cdef short POP_c1(self) # c1 POP BC
cdef short JP_c2(self, int v) # c2 JP NZ,a16
cdef short JP_c3(self, int v) # c3 JP a16
cdef short CALL_c4(self, int v) # c4 CALL NZ,a16
cdef short PUSH_c5(self) # c5 PUSH BC
cdef short ADD_c6(self, int v) # c6 ADD A,d8
cdef short RST_c7(self) # c7 RST 00H
cdef short RET_c8(self) # c8 RET Z
cdef short RET_c9(self) # c9 RET
cdef short JP_ca(self, int v) # ca JP Z,a16
cdef short CB_cb(self) # cb PREFIX CB
cdef short CALL_cc(self, int v) # cc CALL Z,a16
cdef short CALL_cd(self, int v) # cd CALL a16
cdef short ADC_ce(self, int v) # ce ADC A,d8
cdef short RST_cf(self) # cf RST 08H
cdef short RET_d0(self) # d0 RET NC
cdef short POP_d1(self) # d1 POP DE
cdef short JP_d2(self, int v) # d2 JP NC,a16
cdef short CALL_d4(self, int v) # d4 CALL NC,a16
cdef short PUSH_d5(self) # d5 PUSH DE
cdef short SUB_d6(self, int v) # d6 SUB d8
cdef short RST_d7(self) # d7 RST 10H
cdef short RET_d8(self) # d8 RET C
cdef short RETI_d9(self) # d9 RETI
cdef short JP_da(self, int v) # da JP C,a16
cdef short CALL_dc(self, int v) # dc CALL C,a16
cdef short SBC_de(self, int v) # de SBC A,d8
cdef short RST_df(self) # df RST 18H
cdef short LD_e0(self, int v) # e0 LDH (a8),A
cdef short POP_e1(self) # e1 POP HL
cdef short LD_e2(self) # e2 LD (C),A
cdef short PUSH_e5(self) # e5 PUSH HL
cdef short AND_e6(self, int v) # e6 AND d8
cdef short RST_e7(self) # e7 RST 20H
cdef short ADD_e8(self, int v) # e8 ADD SP,r8
cdef short JP_e9(self) # e9 JP (HL)
cdef short LD_ea(self, int v) # ea LD (a16),A
cdef short XOR_ee(self, int v) # ee XOR d8
cdef short RST_ef(self) # ef RST 28H
cdef short LD_f0(self, int v) # f0 LDH A,(a8)
cdef short POP_f1(self) # f1 POP AF
cdef short LD_f2(self) # f2 LD A,(C)
cdef short DI_f3(self) # f3 DI
cdef short PUSH_f5(self) # f5 PUSH AF
cdef short OR_f6(self, int v) # f6 OR d8
cdef short RST_f7(self) # f7 RST 30H
cdef short LD_f8(self, int v) # f8 LD HL,SP+r8
cdef short LD_f9(self) # f9 LD SP,HL
cdef short LD_fa(self, int v) # fa LD A,(a16)
cdef short EI_fb(self) # fb EI
cdef short CP_fe(self, int v) # fe CP d8
cdef short RST_ff(self) # ff RST 38H
cdef short RLC_100(self) # 100 RLC B
cdef short RLC_101(self) # 101 RLC C
cdef short RLC_102(self) # 102 RLC D
cdef short RLC_103(self) # 103 RLC E
cdef short RLC_104(self) # 104 RLC H
cdef short RLC_105(self) # 105 RLC L
cdef short RLC_106(self) # 106 RLC (HL)
cdef short RLC_107(self) # 107 RLC A
cdef short RRC_108(self) # 108 RRC B
cdef short RRC_109(self) # 109 RRC C
cdef short RRC_10a(self) # 10a RRC D
cdef short RRC_10b(self) # 10b RRC E
cdef short RRC_10c(self) # 10c RRC H
cdef short RRC_10d(self) # 10d RRC L
cdef short RRC_10e(self) # 10e RRC (HL)
cdef short RRC_10f(self) # 10f RRC A
cdef short RL_110(self) # 110 RL B
cdef short RL_111(self) # 111 RL C
cdef short RL_112(self) # 112 RL D
cdef short RL_113(self) # 113 RL E
cdef short RL_114(self) # 114 RL H
cdef short RL_115(self) # 115 RL L
cdef short RL_116(self) # 116 RL (HL)
cdef short RL_117(self) # 117 RL A
cdef short RR_118(self) # 118 RR B
cdef short RR_119(self) # 119 RR C
cdef short RR_11a(self) # 11a RR D
cdef short RR_11b(self) # 11b RR E
cdef short RR_11c(self) # 11c RR H
cdef short RR_11d(self) # 11d RR L
cdef short RR_11e(self) # 11e RR (HL)
cdef short RR_11f(self) # 11f RR A
cdef short SLA_120(self) # 120 SLA B
cdef short SLA_121(self) # 121 SLA C
cdef short SLA_122(self) # 122 SLA D
cdef short SLA_123(self) # 123 SLA E
cdef short SLA_124(self) # 124 SLA H
cdef short SLA_125(self) # 125 SLA L
cdef short SLA_126(self) # 126 SLA (HL)
cdef short SLA_127(self) # 127 SLA A
cdef short SRA_128(self) # 128 SRA B
cdef short SRA_129(self) # 129 SRA C
cdef short SRA_12a(self) # 12a SRA D
cdef short SRA_12b(self) # 12b SRA E
cdef short SRA_12c(self) # 12c SRA H
cdef short SRA_12d(self) # 12d SRA L
cdef short SRA_12e(self) # 12e SRA (HL)
cdef short SRA_12f(self) # 12f SRA A
cdef short SWAP_130(self) # 130 SWAP B
cdef short SWAP_131(self) # 131 SWAP C
cdef short SWAP_132(self) # 132 SWAP D
cdef short SWAP_133(self) # 133 SWAP E
cdef short SWAP_134(self) # 134 SWAP H
cdef short SWAP_135(self) # 135 SWAP L
cdef short SWAP_136(self) # 136 SWAP (HL)
cdef short SWAP_137(self) # 137 SWAP A
cdef short SRL_138(self) # 138 SRL B
cdef short SRL_139(self) # 139 SRL C
cdef short SRL_13a(self) # 13a SRL D
cdef short SRL_13b(self) # 13b SRL E
cdef short SRL_13c(self) # 13c SRL H
cdef short SRL_13d(self) # 13d SRL L
cdef short SRL_13e(self) # 13e SRL (HL)
cdef short SRL_13f(self) # 13f SRL A
cdef short BIT_140(self) # 140 BIT 0,B
cdef short BIT_141(self) # 141 BIT 0,C
cdef short BIT_142(self) # 142 BIT 0,D
cdef short BIT_143(self) # 143 BIT 0,E
cdef short BIT_144(self) # 144 BIT 0,H
cdef short BIT_145(self) # 145 BIT 0,L
cdef short BIT_146(self) # 146 BIT 0,(HL)
cdef short BIT_147(self) # 147 BIT 0,A
cdef short BIT_148(self) # 148 BIT 1,B
cdef short BIT_149(self) # 149 BIT 1,C
cdef short BIT_14a(self) # 14a BIT 1,D
cdef short BIT_14b(self) # 14b BIT 1,E
cdef short BIT_14c(self) # 14c BIT 1,H
cdef short BIT_14d(self) # 14d BIT 1,L
cdef short BIT_14e(self) # 14e BIT 1,(HL)
cdef short BIT_14f(self) # 14f BIT 1,A
cdef short BIT_150(self) # 150 BIT 2,B
cdef short BIT_151(self) # 151 BIT 2,C
cdef short BIT_152(self) # 152 BIT 2,D
cdef short BIT_153(self) # 153 BIT 2,E
cdef short BIT_154(self) # 154 BIT 2,H
cdef short BIT_155(self) # 155 BIT 2,L
cdef short BIT_156(self) # 156 BIT 2,(HL)
cdef short BIT_157(self) # 157 BIT 2,A
cdef short BIT_158(self) # 158 BIT 3,B
cdef short BIT_159(self) # 159 BIT 3,C
cdef short BIT_15a(self) # 15a BIT 3,D
cdef short BIT_15b(self) # 15b BIT 3,E
cdef short BIT_15c(self) # 15c BIT 3,H
cdef short BIT_15d(self) # 15d BIT 3,L
cdef short BIT_15e(self) # 15e BIT 3,(HL)
cdef short BIT_15f(self) # 15f BIT 3,A
cdef short BIT_160(self) # 160 BIT 4,B
cdef short BIT_161(self) # 161 BIT 4,C
cdef short BIT_162(self) # 162 BIT 4,D
cdef short BIT_163(self) # 163 BIT 4,E
cdef short BIT_164(self) # 164 BIT 4,H
cdef short BIT_165(self) # 165 BIT 4,L
cdef short BIT_166(self) # 166 BIT 4,(HL)
cdef short BIT_167(self) # 167 BIT 4,A
cdef short BIT_168(self) # 168 BIT 5,B
cdef short BIT_169(self) # 169 BIT 5,C
cdef short BIT_16a(self) # 16a BIT 5,D
cdef short BIT_16b(self) # 16b BIT 5,E
cdef short BIT_16c(self) # 16c BIT 5,H
cdef short BIT_16d(self) # 16d BIT 5,L
cdef short BIT_16e(self) # 16e BIT 5,(HL)
cdef short BIT_16f(self) # 16f BIT 5,A
cdef short BIT_170(self) # 170 BIT 6,B
cdef short BIT_171(self) # 171 BIT 6,C
cdef short BIT_172(self) # 172 BIT 6,D
cdef short BIT_173(self) # 173 BIT 6,E
cdef short BIT_174(self) # 174 BIT 6,H
cdef short BIT_175(self) # 175 BIT 6,L
cdef short BIT_176(self) # 176 BIT 6,(HL)
cdef short BIT_177(self) # 177 BIT 6,A
cdef short BIT_178(self) # 178 BIT 7,B
cdef short BIT_179(self) # 179 BIT 7,C
cdef short BIT_17a(self) # 17a BIT 7,D
cdef short BIT_17b(self) # 17b BIT 7,E
cdef short BIT_17c(self) # 17c BIT 7,H
cdef short BIT_17d(self) # 17d BIT 7,L
cdef short BIT_17e(self) # 17e BIT 7,(HL)
cdef short BIT_17f(self) # 17f BIT 7,A
cdef short RES_180(self) # 180 RES 0,B
cdef short RES_181(self) # 181 RES 0,C
cdef short RES_182(self) # 182 RES 0,D
cdef short RES_183(self) # 183 RES 0,E
cdef short RES_184(self) # 184 RES 0,H
cdef short RES_185(self) # 185 RES 0,L
cdef short RES_186(self) # 186 RES 0,(HL)
cdef short RES_187(self) # 187 RES 0,A
cdef short RES_188(self) # 188 RES 1,B
cdef short RES_189(self) # 189 RES 1,C
cdef short RES_18a(self) # 18a RES 1,D
cdef short RES_18b(self) # 18b RES 1,E
cdef short RES_18c(self) # 18c RES 1,H
cdef short RES_18d(self) # 18d RES 1,L
cdef short RES_18e(self) # 18e RES 1,(HL)
cdef short RES_18f(self) # 18f RES 1,A
cdef short RES_190(self) # 190 RES 2,B
cdef short RES_191(self) # 191 RES 2,C
cdef short RES_192(self) # 192 RES 2,D
cdef short RES_193(self) # 193 RES 2,E
cdef short RES_194(self) # 194 RES 2,H
cdef short RES_195(self) # 195 RES 2,L
cdef short RES_196(self) # 196 RES 2,(HL)
cdef short RES_197(self) # 197 RES 2,A
cdef short RES_198(self) # 198 RES 3,B
cdef short RES_199(self) # 199 RES 3,C
cdef short RES_19a(self) # 19a RES 3,D
cdef short RES_19b(self) # 19b RES 3,E
cdef short RES_19c(self) # 19c RES 3,H
cdef short RES_19d(self) # 19d RES 3,L
cdef short RES_19e(self) # 19e RES 3,(HL)
cdef short RES_19f(self) # 19f RES 3,A
cdef short RES_1a0(self) # 1a0 RES 4,B
cdef short RES_1a1(self) # 1a1 RES 4,C
cdef short RES_1a2(self) # 1a2 RES 4,D
cdef short RES_1a3(self) # 1a3 RES 4,E
cdef short RES_1a4(self) # 1a4 RES 4,H
cdef short RES_1a5(self) # 1a5 RES 4,L
cdef short RES_1a6(self) # 1a6 RES 4,(HL)
cdef short RES_1a7(self) # 1a7 RES 4,A
cdef short RES_1a8(self) # 1a8 RES 5,B
cdef short RES_1a9(self) # 1a9 RES 5,C
cdef short RES_1aa(self) # 1aa RES 5,D
cdef short RES_1ab(self) # 1ab RES 5,E
cdef short RES_1ac(self) # 1ac RES 5,H
cdef short RES_1ad(self) # 1ad RES 5,L
cdef short RES_1ae(self) # 1ae RES 5,(HL)
cdef short RES_1af(self) # 1af RES 5,A
cdef short RES_1b0(self) # 1b0 RES 6,B
cdef short RES_1b1(self) # 1b1 RES 6,C
cdef short RES_1b2(self) # 1b2 RES 6,D
cdef short RES_1b3(self) # 1b3 RES 6,E
cdef short RES_1b4(self) # 1b4 RES 6,H
cdef short RES_1b5(self) # 1b5 RES 6,L
cdef short RES_1b6(self) # 1b6 RES 6,(HL)
cdef short RES_1b7(self) # 1b7 RES 6,A
cdef short RES_1b8(self) # 1b8 RES 7,B
cdef short RES_1b9(self) # 1b9 RES 7,C
cdef short RES_1ba(self) # 1ba RES 7,D
cdef short RES_1bb(self) # 1bb RES 7,E
cdef short RES_1bc(self) # 1bc RES 7,H
cdef short RES_1bd(self) # 1bd RES 7,L
cdef short RES_1be(self) # 1be RES 7,(HL)
cdef short RES_1bf(self) # 1bf RES 7,A
cdef short SET_1c0(self) # 1c0 SET 0,B
cdef short SET_1c1(self) # 1c1 SET 0,C
cdef short SET_1c2(self) # 1c2 SET 0,D
cdef short SET_1c3(self) # 1c3 SET 0,E
cdef short SET_1c4(self) # 1c4 SET 0,H
cdef short SET_1c5(self) # 1c5 SET 0,L
cdef short SET_1c6(self) # 1c6 SET 0,(HL)
cdef short SET_1c7(self) # 1c7 SET 0,A
cdef short SET_1c8(self) # 1c8 SET 1,B
cdef short SET_1c9(self) # 1c9 SET 1,C
cdef short SET_1ca(self) # 1ca SET 1,D
cdef short SET_1cb(self) # 1cb SET 1,E
cdef short SET_1cc(self) # 1cc SET 1,H
cdef short SET_1cd(self) # 1cd SET 1,L
cdef short SET_1ce(self) # 1ce SET 1,(HL)
cdef short SET_1cf(self) # 1cf SET 1,A
cdef short SET_1d0(self) # 1d0 SET 2,B
cdef short SET_1d1(self) # 1d1 SET 2,C
cdef short SET_1d2(self) # 1d2 SET 2,D
cdef short SET_1d3(self) # 1d3 SET 2,E
cdef short SET_1d4(self) # 1d4 SET 2,H
cdef short SET_1d5(self) # 1d5 SET 2,L
cdef short SET_1d6(self) # 1d6 SET 2,(HL)
cdef short SET_1d7(self) # 1d7 SET 2,A
cdef short SET_1d8(self) # 1d8 SET 3,B
cdef short SET_1d9(self) # 1d9 SET 3,C
cdef short SET_1da(self) # 1da SET 3,D
cdef short SET_1db(self) # 1db SET 3,E
cdef short SET_1dc(self) # 1dc SET 3,H
cdef short SET_1dd(self) # 1dd SET 3,L
cdef short SET_1de(self) # 1de SET 3,(HL)
cdef short SET_1df(self) # 1df SET 3,A
cdef short SET_1e0(self) # 1e0 SET 4,B
cdef short SET_1e1(self) # 1e1 SET 4,C
cdef short SET_1e2(self) # 1e2 SET 4,D
cdef short SET_1e3(self) # 1e3 SET 4,E
cdef short SET_1e4(self) # 1e4 SET 4,H
cdef short SET_1e5(self) # 1e5 SET 4,L
cdef short SET_1e6(self) # 1e6 SET 4,(HL)
cdef short SET_1e7(self) # 1e7 SET 4,A
cdef short SET_1e8(self) # 1e8 SET 5,B
cdef short SET_1e9(self) # 1e9 SET 5,C
cdef short SET_1ea(self) # 1ea SET 5,D
cdef short SET_1eb(self) # 1eb SET 5,E
cdef short SET_1ec(self) # 1ec SET 5,H
cdef short SET_1ed(self) # 1ed SET 5,L
cdef short SET_1ee(self) # 1ee SET 5,(HL)
cdef short SET_1ef(self) # 1ef SET 5,A
cdef short SET_1f0(self) # 1f0 SET 6,B
cdef short SET_1f1(self) # 1f1 SET 6,C
cdef short SET_1f2(self) # 1f2 SET 6,D
cdef short SET_1f3(self) # 1f3 SET 6,E
cdef short SET_1f4(self) # 1f4 SET 6,H
cdef short SET_1f5(self) # 1f5 SET 6,L
cdef short SET_1f6(self) # 1f6 SET 6,(HL)
cdef short SET_1f7(self) # 1f7 SET 6,A
cdef short SET_1f8(self) # 1f8 SET 7,B
cdef short SET_1f9(self) # 1f9 SET 7,C
cdef short SET_1fa(self) # 1fa SET 7,D
cdef short SET_1fb(self) # 1fb SET 7,E
cdef short SET_1fc(self) # 1fc SET 7,H
cdef short SET_1fd(self) # 1fd SET 7,L
cdef short SET_1fe(self) # 1fe SET 7,(HL)
cdef short SET_1ff(self) # 1ff SET 7,A
