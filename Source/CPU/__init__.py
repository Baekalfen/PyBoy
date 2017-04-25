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
from Interrupts import InterruptVector, NonEnabledInterrupt, NoInterrupt

from GbLogger import gblogger


class CPU():
    #  A, F, B, C, D, E, H, L, SP, PC, AF, BC, DE, HL, pointer, Flag
    from opcodes import opcodes
    from registers import reg, setReg, setAF, setBC, setDE, setHL, setPC, incPC, getAF, getBC, getDE, getHL
    from Interrupts import checkForInterrupts
    from flags import VBlank, LCDC, TIMER, Serial, HightoLow, LYCFlag, LYCFlagEnable
    from flags import testFlag, setFlag, clearFlag
    from flags import testInterruptFlag, setInterruptFlag, clearInterruptFlag, testInterruptFlagEnabled
    from flags import testSTATFlag, setSTATFlag, clearSTATFlag, testSTATFlagEnabled
    from flags import testRAMRegisterFlag, setRAMRegisterFlag, clearRAMRegisterFlag, testRAMRegisterFlagEnabled
    from operations import CPU_EI, CPU_STOP, CPU_HALT, CPU_LDD, CPU_LDI, CPU_INC8, CPU_DEC8, CPU_INC16, CPU_DEC16, CPU_ADD8, CPU_ADD16, CPU_SUB8, CPU_ADC8, CPU_SBC8, CPU_AND8, CPU_XOR8, CPU_OR8, CPU_CP, CPU_RLC, CPU_RRC, CPU_RL, CPU_RR, CPU_DAA, CPU_RET, CPU_POP, CPU_PUSH, CPU_DI, CPU_EXT_SLA, CPU_EXT_SRA, CPU_EXT_SWAP, CPU_EXT_SRL, CPU_EXT_BIT, CPU_EXT_RES, CPU_EXT_SET, CPU_EXT_RLC, CPU_EXT_RRC, CPU_EXT_RL, CPU_EXT_RR

    def __init__(self, MB):
        self.mb = MB

        self.interruptMasterEnable = False
        self.interruptMasterEnableLatch = False

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

    def executeInstruction(self, instruction):
        self.interruptMasterEnable = self.interruptMasterEnableLatch

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

        operation = opcodes.opcodes[opcode]

        # #OPTIMIZE: Can this be improved?
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
        # InterruptVector, NonEnabledInterrupt, NoInterrupt
        if self.halted and didInterrupt:
            self.halted = False
            # GBCPUman.pdf page 20
            # WARNING: The instruction immediately following the HALT instruction is "skipped"
            # when interrupts are disabled (DI) on the GB,GBP, and SGB.

            if didInterrupt == NonEnabledInterrupt:
                self.reg[PC] += 1  # +1 to escape HALT, when interrupt didn't

            instruction = self.fetchInstruction(self.reg[PC])

        elif self.halted and not didInterrupt:
            operation = opcodes.opcodes[0x00] #Fetch NOP to still run timers and such
            instruction = (operation[2], operation[1], (self, self.reg[PC]))
            self.oldPC = -1 # Avoid detection of being stuck
        else:
            instruction = self.fetchInstruction(self.reg[PC])

        #     self.lala = True

        if self.lala and not self.halted:
            if (self.mb[self.reg[PC]]) == 0xCB:
                gblogger.info(hex(self.reg[PC]+1)[2:])
            else:
                gblogger.info(hex(self.reg[PC])[2:])

        if __debug__:

            if self.breakAllow and self.reg[PC] == self.breakNext:
                self.breakAllow = False
                self.breakOn = True

            if self.oldPC == self.reg[PC]:# and self.reg[PC] != 0x40: #Ignore VBLANK interrupt
                self.breakOn = True
                gblogger.info("PC DIDN'T CHANGE! Can't continue!")
                CoreDump.windowHandle.dump(self.mb.cartridge.filename+"_dump.bmp")
                raise Exception("Escape to main.py")
            self.oldPC = self.reg[PC]

            if self.breakOn:
                self.getDump(instruction)

                action = raw_input()
                if action == 'd':
                    CoreDump.CoreDump("Debug")
                elif action == 'r':
                    self.breakOn = False
                    self.breakAllow = False
                elif action[:2] == "0x":
                    gblogger.info("Breaking on next", hex(int(action,16)), "\n") #Checking parser
                    self.breakNext = int(action,16)
                    self.breakOn = False
                    self.breakAllow = True
                elif action == 'o':
                    targetPC = instruction[-1][-1]
                    gblogger.info("Stepping over for", hex(targetPC), "\n") #Checking parser
                    self.breakNext = targetPC
                    self.breakOn = False
                    self.breakAllow = True
                else:
                    pass

        #TODO: Make better CoreDump print out. Where is 0xC000?
        #TODO: Make better opcode printing. Show arguments (check LDH/LDD)

        cycles = self.executeInstruction(instruction)

        if self.mb.timer.tick(cycles):
            self.setInterruptFlag(self.TIMER)

        return cycles

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

        gblogger.info("A:   0x%0.2X   F: 0x%0.2X" % (self.reg[A], self.reg[F]))
        gblogger.info("B:   0x%0.2X   C: 0x%0.2X" % (self.reg[B], self.reg[C]))
        gblogger.info("D:   0x%0.2X   E: 0x%0.2X" % (self.reg[D], self.reg[E]))
        gblogger.info("H:   0x%0.2X   L: 0x%0.2X" % (self.reg[H], self.reg[L]))
        gblogger.info("SP:  0x%0.4X   PC: 0x%0.4X"% (self.reg[SP], self.reg[PC]))
        # gblogger.info("0xC000", "0x%0.2X" % self.mb[0xc000])
        # gblogger.info("(HL-1)", "0x%0.2X" % self.mb[self.getHL()-1])
        gblogger.info("(HL) 0x%0.2X   (HL+1) 0x%0.2X" % (self.mb[self.getHL()],
            self.mb[self.getHL()+1]))
        gblogger.info("Timer: DIV %s, TIMA %s, TMA %s, TAC %s" % (self.mb[0xFF04], self.mb[0xFF05], self.mb[0xFF06],bin(self.mb[0xFF07])))

        if (self.mb[self.reg[PC]]) != 0xCB:
            l = self.opcodes[self.mb[self.reg[PC]]][0]
            gblogger.info("Op: 0x%0.2X" % self.mb[self.reg[PC]])
            gblogger.info("Name: " + str(CPU_COMMANDS[self.mb[self.reg[PC]]]))
            gblogger.info("Len:" + str(l))
            if instruction:
                gblogger.info(("val: 0x%0.2X" % instruction[2][1]) if not l == 1 else "")
        else:
            gblogger.info("CB op: 0x%0.2X  CB name: %s" % (self.mb[self.reg[PC]+1],
                   + str(CPU_COMMANDS_EXT[self.mb[self.reg[PC]+1]])))
        gblogger.info("Call Stack " + str(self.debugCallStack))
        gblogger.info("Active ROM and RAM bank " +
                str(self.mb.cartridge.ROMBankSelected) + ' ' +
                str(self.mb.cartridge.RAMBankSelected))
        gblogger.info("Master Interrupt" + str(self.interruptMasterEnable) + ' '
                +str(self.interruptMasterEnableLatch))
        gblogger.info("Enabled Interrupts",)
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
        gblogger.info(flags)
        gblogger.info("Waiting Interrupts")
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
        gblogger.info(flags)
