# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from registers import A, F, B, C, D, E, H, L, SP, PC
from MathUint8 import getBit
import CoreDump
from opcodeToName import CPU_COMMANDS, CPU_COMMANDS_EXT
from flags import flagZ, flagN, flagH, flagC # Only debugging
from Logger import logger
from Interrupts import InterruptVector, NoInterrupt
import numpy as np

class CPU():
    #  A, F, B, C, D, E, H, L, SP, PC, AF, BC, DE, HL, pointer, Flag
    from opcodes import opcodes
    from registers import reg, setReg, setAF, setBC, setDE, setHL, setPC, incPC, getAF, getBC, getDE, getHL
    from Interrupts import checkForInterrupts, testAndTriggerInterrupt
    from flags import VBlank, LCDC, TIMER, Serial, HightoLow, LYCFlag, LYCFlagEnable
    from flags import testFlag, setFlag, clearFlag
    from flags import testInterruptFlag, setInterruptFlag, clearInterruptFlag, testInterruptFlagEnabled
    from flags import testSTATFlag, setSTATFlag, clearSTATFlag, testSTATFlagEnabled
    from flags import testRAMRegisterFlag, setRAMRegisterFlag, clearRAMRegisterFlag, testRAMRegisterFlagEnabled
    from operations import CPU_EI, CPU_STOP, CPU_HALT, CPU_LDD, CPU_LDI, CPU_INC8, CPU_DEC8, CPU_INC16, CPU_DEC16, CPU_ADD8, CPU_ADD16, CPU_SUB8, CPU_ADC8, CPU_SBC8, CPU_AND8, CPU_XOR8, CPU_OR8, CPU_CP, CPU_RLC, CPU_RRC, CPU_RL, CPU_RR, CPU_DAA, CPU_RET, CPU_POP, CPU_PUSH, CPU_DI, CPU_EXT_SLA, CPU_EXT_SRA, CPU_EXT_SWAP, CPU_EXT_SRL, CPU_EXT_BIT, CPU_EXT_RES, CPU_EXT_SET, CPU_EXT_RLC, CPU_EXT_RRC, CPU_EXT_RL, CPU_EXT_RR

    def __init__(self, MB, profiling=False):
        self.mb = MB

        self.interruptMasterEnable = False

        self.breakAllow = True
        self.breakOn = False
        self.breakNext = None

        self.halted = False
        self.stopped = False

        self.debugCallStack = []

        self.reg[PC] = 0

        #debug
        self.oldPC = -1
        self.lala = False

        # Profiling
        self.profiling = profiling
        self.hitRate = np.zeros(shape=(512,), dtype=int)

    def executeInstruction(self, instruction):
        # '*' unpacks tuple into arguments
        success = instruction[0](*instruction[2])
        if success:
            return instruction[1][1]  # Select correct cycles for jumps
        else:
            return instruction[1][0]

    def fetchInstruction(self, pc):
        opcode = self.mb[pc]
        if opcode == 0xCB:  # Extension code
            pc += 1
            opcode = self.mb[pc]
            opcode += 0x100  # Internally shifting look-up table

        #Profiling
        if self.profiling:
            self.hitRate[opcode] += 1
        # if opcode == 0xf0:
        #     print "F0", hex(self.mb[pc+1])

        operation = opcodes.opcodes[opcode]

        # OPTIMIZE: Can this be improved?
        if operation[0] == 1:
            return (
                operation[2],
                operation[1],
                (self, pc+operation[0])
            )
        elif operation[0] == 2:
            # 8-bit immediate
            return (
                operation[2],
                operation[1],
                (self, self.mb[pc+1], pc+operation[0])
            )
        elif operation[0] == 3:
            # 16-bit immediate
            # Flips order of values due to big-endian
            return (
                operation[2],
                operation[1],
                (self, (self.mb[pc+2] << 8) + self.mb[pc+1], pc+operation[0])
            )
        else:
            raise CoreDump.CoreDump("Unexpected opcode length: %s" % operation[0])

    def tick(self):
        # "The interrupt will be acknowledged during opcode fetch period of each instruction."
        didInterrupt = self.checkForInterrupts()

        instruction = None
        if self.halted and didInterrupt:
            # GBCPUman.pdf page 20
            # WARNING: The instruction immediately following the HALT instruction is "skipped"
            # when interrupts are disabled (DI) on the GB,GBP, and SGB.
            self.halted = False
        instruction = self.fetchInstruction(self.reg[PC])

        if __debug__:
            # if self.reg[PC] == 0x50:
            # self.lala = True

            if self.lala and not self.halted:
                if (self.mb[self.reg[PC]]) == 0xCB:
                    self.logger(hex(self.reg[PC]+1)[2:], hex(self.mb[self.reg[PC]]))
                else:
                    self.logger(hex(self.reg[PC])[2:], hex(self.mb[self.reg[PC]]))

            if self.breakAllow and self.reg[PC] == self.breakNext:
                self.breakAllow = False
                self.breakOn = True

            if self.oldPC == self.reg[PC] and not self.halted:
                self.breakOn = True
                logger.info("PC DIDN'T CHANGE! Can't continue!")
                CoreDump.windowHandle.dump(self.mb.cartridge.filename+"_dump.bmp")
                raise Exception("Escape to main.py")
            self.oldPC = self.reg[PC]

            #TODO: Make better CoreDump print out. Where is 0xC000?
            #TODO: Make better opcode printing. Show arguments (check LDH/LDD)
            if self.breakOn:
                self.getDump(instruction)

                action = raw_input()
                if action == 'd':
                    CoreDump.CoreDump("Debug")
                elif action == 'r':
                    self.breakOn = False
                    self.breakAllow = False
                elif action[:2] == "0x":
                    logger.info("Breaking on next {}".format(hex(int(action,16)))) #Checking parser
                    self.breakNext = int(action,16)
                    self.breakOn = False
                    self.breakAllow = True
                elif action == 'ei':
                    self.interruptMasterEnable = True
                elif action == 'o':
                    targetPC = instruction[-1][-1]
                    logger.info("Stepping over for {}".format(hex(targetPC))) #Checking parser
                    self.breakNext = targetPC
                    self.breakOn = False
                    self.breakAllow = True
                else:
                    pass

        return self.executeInstruction(instruction)

    def error(self, message):
        raise CoreDump.CoreDump(message)

    def getDump(self, instruction = None):
        flags = ""
        if self.testFlag(flagZ):
            flags += " Z"
        if self.testFlag(flagH):
            flags += " H"
        if self.testFlag(flagC):
            flags += " C"
        if self.testFlag(flagN):
            flags += " N"

        logger.info("A:   0x%0.2X   F: 0x%0.2X" % (self.reg[A], self.reg[F]))
        logger.info("B:   0x%0.2X   C: 0x%0.2X" % (self.reg[B], self.reg[C]))
        logger.info("D:   0x%0.2X   E: 0x%0.2X" % (self.reg[D], self.reg[E]))
        logger.info("H:   0x%0.2X   L: 0x%0.2X" % (self.reg[H], self.reg[L]))
        logger.info("SP:  0x%0.4X   PC: 0x%0.4X"% (self.reg[SP], self.reg[PC]))
        # logger.info("0xC000", "0x%0.2X" % self.mb[0xc000])
        # logger.info("(HL-1)", "0x%0.2X" % self.mb[self.getHL()-1])
        logger.info("(HL) 0x%0.2X   (HL+1) 0x%0.2X" % (self.mb[self.getHL()],
            self.mb[self.getHL()+1]))
        logger.info("Timer: DIV %s, TIMA %s, TMA %s, TAC %s" % (self.mb[0xFF04], self.mb[0xFF05], self.mb[0xFF06],bin(self.mb[0xFF07])))

        if (self.mb[self.reg[PC]]) != 0xCB:
            l = self.opcodes[self.mb[self.reg[PC]]][0]
            logger.info("Op: 0x%0.2X" % self.mb[self.reg[PC]])
            logger.info("Name: " + str(CPU_COMMANDS[self.mb[self.reg[PC]]]))
            logger.info("Len:" + str(l))
            if instruction:
                logger.info(("val: 0x%0.2X" % instruction[2][1]) if not l == 1 else "")
        else:

            logger.info("CB op: 0x%0.2X  CB name: %s" % (self.mb[self.reg[PC]+1],
                   + str(CPU_COMMANDS_EXT[self.mb[self.reg[PC]+1]])))
        logger.info("Call Stack " + str(self.debugCallStack))
        logger.info("Active ROM and RAM bank " +
                str(self.mb.cartridge.ROMBankSelected) + ' ' +
                str(self.mb.cartridge.RAMBankSelected))
        logger.info("Master Interrupt" + str(self.interruptMasterEnable))
        logger.info("Enabled Interrupts")

        flags = ""
        if self.testInterruptFlagEnabled(self.VBlank):
            flags += "VBlank "
        if self.testInterruptFlagEnabled(self.LCDC):
            flags += "LCDC "
        if self.testInterruptFlagEnabled(self.TIMER):
            flags += "Timer "
        if self.testInterruptFlagEnabled(self.Serial):
            flags += "Serial "
        if self.testInterruptFlagEnabled(self.HightoLow):
            flags += "HightoLow "
	logger.info('{}'.format(flags))
        logger.info("Waiting Interrupts")
        flags = ""
        if self.testInterruptFlag(self.VBlank):
            flags += "VBlank "
        if self.testInterruptFlag(self.LCDC):
            flags += "LCDC "
        if self.testInterruptFlag(self.TIMER):
            flags += "Timer "
        if self.testInterruptFlag(self.Serial):
            flags += "Serial "
        if self.testInterruptFlag(self.HightoLow):
            flags += "HightoLow "
        if self.halted:
            flags += " **HALTED**"
        logger.info(flags)
