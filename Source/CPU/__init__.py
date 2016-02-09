# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# http://stackoverflow.com/questions/9638446/is-there-any-python-equivalent-to-partial-classes

from registers import A, F, B, C, D, E, H, L, SP, PC
from MathUint8 import getBit
import CoreDump
import warnings
from opcodeToName import CPU_COMMANDS, CPU_COMMANDS_EXT
from flags import flagZ, flagN, flagH, flagC # Only debugging
from Interrupts import InterruptVector, NonEnabledInterrupt, NoInterrupt


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

    def __init__(self, ram, timer, debugger=None):
        self.debugger = debugger
        self.timer = timer
        self.ram = ram
        self.interruptMasterEnable = False
        self.interruptMasterEnableLatch = False

        self.breakAllow = True
        self.breakOn = False
        self.breakNext = None

        self.breakNext = 0x2024
        # 0x1C9  Zeroing some internal RAM?
        # 0x1CC  Escaping?
        # 0x01D8 Zeroing TileView 2
        # 0x01DB Zeroing some of upper internal RAM (0xFEFF to 0xFE00?)
        # 0x01E2 Zeroing some of upper internal RAM (0xFFFE to 0xFF7E?)
        # 0x0221 Changing bank


        # Between 0x0221 and 0x0243, alot of random LD's - Why?

        # What happens at 0x47F2?
        # It's called from 0x0243

        # What happens at 0x7C3?
        # It's called from 0x0252

        self.halted = False
        self.stopped = False

        self.debugCallStack = []

        # Program Counter (PC) is not assumed initialized to 0
        self.reg[PC] = 0
        # if __debug__:
        #     self.reg[PC] = 0xFC # Disable boot-ROM

        #debug
        self.oldPC = -1
        self.lala = False

    def split16to8(self, variable):
        return ((variable & 0xFF00) >> 8, variable & 0x00FF)

    def combine8to16(self, a, b):
        return (a.getInt() << 8) + b.getInt()

    def executeInstruction(self, instruction):
        self.interruptMasterEnable = self.interruptMasterEnableLatch

        # '*' unpacks tuple into arguments
        success = instruction[0](*instruction[2])
        # assert (type(success) is bool or success is None), "Check opcodes"
        if success:
            return instruction[1][1]  # Select correct cycles for jumps
        else:
            return instruction[1][0]

    def fetchInstruction(self, pc):
        opcode = self.ram[pc]
        # if __debug__:
        #     print "opcode:", hex(opcode), "\tPC:", hex(self.reg[PC])
        if opcode == 0xCB:  # Extension code
            pc += 1
            opcode = self.ram[pc]
            # if __debug__:
            #     print "Shifted opcode:", hex(opcode)
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
                (self, self.ram[pc+1], pc+operation[0])
            )
        elif operation[0] == 3:
            # 16-bit immediate
            # Flips order of values due to big-endian
            return (
                operation[2],
                operation[1],
                (self, (self.ram[pc+2] << 8) +
                 self.ram[pc+1], pc+operation[0])
            )
        else:
            raise CoreDump.CoreDump("Unexpected opcode length: %s" % operation[0])

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

        print "A:", "0x%0.2X" % self.reg[A], "F:", "0x%0.2X" % self.reg[F],flags
        print "B:", "0x%0.2X" % self.reg[B], "C:", "0x%0.2X" % self.reg[C]
        print "D:", "0x%0.2X" % self.reg[D], "E:", "0x%0.2X" % self.reg[E]
        print "H:", "0x%0.2X" % self.reg[H], "L:", "0x%0.2X" % self.reg[L]
        print "SP:", "0x%0.4X" % self.reg[SP], "PC:", "0x%0.4X" % self.reg[PC]
        # print "0xC000", "0x%0.2X" % self.ram[0xc000]
        # print "(HL-1)", "0x%0.2X" % self.ram[self.getHL()-1]
        print "(HL)", "0x%0.2X" % self.ram[self.getHL()], "(HL+1)", "0x%0.2X" % self.ram[self.getHL()+1]
        print "Timer: DIV %s, TIMA %s, TMA %s, TAC %s" % (self.ram[0xFF04], self.ram[0xFF05], self.ram[0xFF06],bin(self.ram[0xFF07]))
        

        if (self.ram[self.reg[PC]]) != 0xCB:
            l = self.opcodes[self.ram[self.reg[PC]]][0]
            print "Op:", "0x%0.2X" % self.ram[self.reg[PC]], "Name:", CPU_COMMANDS[self.ram[self.reg[PC]]], "Len:", l, ("val:", "0x%0.2X" % instruction[2][1]) if not l == 1 else ""
        else:
            print "CB op:", "0x%0.2X" % self.ram[self.reg[PC]+1], "CB name:", CPU_COMMANDS_EXT[self.ram[self.reg[PC]+1]]
        print "Call Stack", self.debugCallStack
        print "Active ROM and RAM bank", self.ram.cartridge.ROMBankSelected , self.ram.cartridge.RAMBankSelected
        print "Master Interrupt",self.interruptMasterEnable, self.interruptMasterEnableLatch
        print "Enabled Interrupts",
        flags = ""
        if self.testInterruptFlagEnabled(self.VBlank):
            flags += " VBlank"
        if self.testInterruptFlagEnabled(self.LCDC):
            flags += " LCDC"
        if self.testInterruptFlagEnabled(self.TIMER):
            flags += " Timer"
        if self.testInterruptFlagEnabled(self.Serial):
            flags += " Serial"
        if self.testInterruptFlagEnabled(self.HightoLow):
            flags += " HightoLow"
        print flags
        print "Waiting Interrupts",
        flags = ""
        if self.testInterruptFlag(self.VBlank):
            flags += " VBlank"
        if self.testInterruptFlag(self.LCDC):
            flags += " LCDC"
        if self.testInterruptFlag(self.TIMER):
            flags += " Timer"
        if self.testInterruptFlag(self.Serial):
            flags += " Serial"
        if self.testInterruptFlag(self.HightoLow):
            flags += " HightoLow"
        if self.halted:
            flags += "\nHALTED"
        print flags

    def tick(self):
        # "The interrupt will be acknowledged during opcode fetch period of each instruction."
        didInterrupt = self.checkForInterrupts()

        # if self.reg[PC] == 0x2880 or self.reg[PC] == 0x2882:
        #     print "LY", hex(self.ram[0xFF44]), didInterrupt
        # if self.halted:
        #     exit()

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

        # if not self.ram.bootROMEnabled:
        #     if self.reg[PC] == 0x7c:
        #         self.breakOn = True
        #     if (self.ram[self.reg[PC]]) != 0xCB:
        #         l = self.opcodes[self.ram[self.reg[PC]]][0]
        #         print "Op:", "0x%0.2X" % self.ram[self.reg[PC]], "Name:", CPU_COMMANDS[self.ram[self.reg[PC]]], "Len:", l, ("val:", "0x%0.2X" % instruction[2][1]) if not l == 1 else ""
        #     else:
        #         print "CB op:", "0x%0.2X" % self.ram[self.reg[PC]+1], "CB name:", CPU_COMMANDS_EXT[self.ram[self.reg[PC]+1]]

            
        # if self.reg[PC] == 0x100:
        #     self.lala = True

        if self.lala and not self.halted:
            if (self.ram[self.reg[PC]]) == 0xCB:
                print hex(self.reg[PC]+1)[2:]
            else:
                print hex(self.reg[PC])[2:]        

        if __debug__:
            # if self.reg[PC] == 0x48 and not self.ram.bootROMEnabled and self.ram[0xFF45] != 0:
            #     self.breakOn = True

            if self.breakAllow and self.reg[PC] == self.breakNext:
                # self.breakNext = None
                self.breakAllow = False
                self.breakOn = True

            if self.oldPC == self.reg[PC]:# and self.reg[PC] != 0x40: #Ignore VBLANK interrupt
                self.breakOn = True
                print "PC DIDN'T CHANGE! Can't continue!"
                CoreDump.windowHandle.dump(self.ram.cartridge.filename+"_dump.bmp")
                raise Exception("Escape to main.py")
            self.oldPC = self.reg[PC]

            if self.breakOn:
                self.getDump(instruction)

                if self.reg[PC] == 0xc325:
                    print self.testFlag(flagZ),"\n"

                action = raw_input()
                if action == 'd':
                    CoreDump.CoreDump("Debug")
                elif action == 'r':
                    self.breakOn = False
                    self.breakAllow = False
                elif action[:2] == "0x":
                    print "Breaking on next", hex(int(action,16)), "\n" #Checking parser
                    self.breakNext = int(action,16)
                    self.breakOn = False
                    self.breakAllow = True
                else:
                    pass

        #TODO: Make better CoreDump print out. Where is 0xC000?
        #TODO: Make better opcode printing. Show arguments (check LDH/LDD)

        cycles = self.executeInstruction(instruction)

        if self.timer.tick(cycles):
            self.setInterruptFlag(self.TIMER)
        
        return cycles

    def error(self, message):
        raise CoreDump.CoreDump(message)
