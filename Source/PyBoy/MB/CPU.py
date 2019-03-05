# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# from opcodes import opcodes
import opcodes
import CoreDump
from ..opcodeToName import CPU_COMMANDS, CPU_COMMANDS_EXT
# import flags
# from flags import flagZ, flagN, flagH, flagC
# from flags import VBlank, LCDC, TIMER, Serial, HightoLow
from ..Logger import logger
# from Interrupts import InterruptVector, NoInterrupt
import numpy as np


flagC, flagH, flagN, flagZ = range(4, 8)
VBlank, LCDC, TIMER, Serial, HightoLow = range(5)
IF_address = 0xFF0F
IE_address = 0xFFFF
NoInterrupt = 0
InterruptVector = 1

def setA(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self._A = x

def setF(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self._F = x

def setB(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self._B = x

def setC(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self._C = x

def setD(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self._D = x

def setE(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self._E = x

def setH(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self.HL &= 0x00FF
    self.HL |= x << 8

def setL(self, x):
    assert x <= 0xFF, "%0.2x" % x
    self.HL &= 0xFF00
    self.HL |= x

def setHL(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self._HL = x

def setSP(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self._SP = x

def setPC(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self._PC = x

def setAF(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self.A = x >> 8
    self.F = x & 0x00F0 # Lower nibble of F is always zero!

def setBC(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self.B = x >> 8
    self.C = x & 0x00FF

def setDE(self, x):
    assert x <= 0xFFFF, "%0.4x" % x
    self.D = x >> 8
    self.E = x & 0x00FF

def getA(self):
    return self._A
def getF(self):
    return self._F
def getB(self):
    return self._B
def getC(self):
    return self._C
def getD(self):
    return self._D
def getE(self):
    return self._E
def getH(self):
    return self._HL >> 8
def getL(self):
    return self._HL & 0xFF
def getHL(self):
    return self._HL
def getSP(self):
    return self._SP
def getPC(self):
    return self._PC
def getAF(self):
    return (self.A << 8) + self.F
def getBC(self):
    return (self.B << 8) + self.C
def getDE(self):
    return (self.D << 8) + self.E

class CPU(object): # 'object' is important for property!!!
    # from registers import A, F, B, C, D, E, HL, SP, PC
    # from registers import setH, setL, setAF, setBC, setDE
    # from Interrupts import checkForInterrupts, testAndTriggerInterrupt
    # from flags import testFlag, setFlag, clearFlag
    # from flags import testInterruptFlag, setInterruptFlag, clearInterruptFlag, testInterruptFlagEnabled, testRAMRegisterFlag



    ### CPU Flags

    def testFlag(self, flag):
        return (self.F & (1 << flag)) != 0

    def setFlag(self, flag, value=True):
        self.F = (self.F & (0xFF - (1 << flag)))
        if value:
            self.F = (self.F + (1 << flag))

    def clearFlag(self, flag):
        self.F = (self.F & (0xFF - (1 << flag)))


    ### Interrupt flags


    def testInterruptFlag(self, flag):
        return (self.mb[0xFF0F] & (1 << flag))


    def setInterruptFlag(self, flag):
        self.mb[0xFF0F] |= (1 << flag)


    def clearInterruptFlag(self, flag):
        self.mb[0xFF0F] &= (0xFF - (1 << flag))


    def testInterruptFlagEnabled(self, flag):
        return (self.mb[0xFFFF] & (1 << flag))



    def testRAMRegisterFlag(self, address, flag):
        return (self.mb[address] & (1 << flag))

    def setRAMRegisterFlag(self, address, flag, value=True):
        self.clearRAMRegisterFlag(address, flag)
        # self.mb[address] = (self.mb[address] & (0xFF - (1 << flag)))
        # if value:
        self.mb[address] = (self.mb[address] + (value << flag))

    def clearRAMRegisterFlag(self, address, flag):
        self.mb[address] = (self.mb[address] & (0xFF - (1 << flag)))

    def testRAMRegisterFlagEnabled(self, address, flag):
        return (self.mb[address] & (1 << flag))

    def checkForInterrupts(self):
        #GPCPUman.pdf p. 40 about priorities
        # If an interrupt occours, the PC is pushed to the stack.
        # It is up to the interrupt routine to return it.

        # 0xFF0F (IF_address) - Bit 0-4 Requested interrupts
        # 0xFFFF (IE_address) - Bit 0-4 Enabling interrupt vectors
        anyInterruptToHandle = ((self.mb[IF_address] & 0b11111) & (self.mb[IE_address] & 0b11111)) != 0

        # Better to make a long check, than run through 5 if statements
        if anyInterruptToHandle and self.interruptMasterEnable:

            return (
                self.testAndTriggerInterrupt(VBlank, 0x0040) or
                self.testAndTriggerInterrupt(LCDC, 0x0048) or
                self.testAndTriggerInterrupt(TIMER, 0x0050) or
                self.testAndTriggerInterrupt(Serial, 0x0058) or
                self.testAndTriggerInterrupt(HightoLow, 0x0060)
                )

        return NoInterrupt

    def testAndTriggerInterrupt(self, flag, vector):
        if self.testInterruptFlagEnabled(flag) and self.testInterruptFlag(flag):

            self.clearInterruptFlag(flag)
            self.interruptMasterEnable = False
            if self.halted:
                self.PC += 1 # Escape HALT on return
                # self.CPU_PUSH(self.PC+1)
            # else:
                # self.CPU_PUSH(self.PC)

            self.mb[self.SP-1] = self.PC >> 8 # High
            self.mb[self.SP-2] = self.PC & 0xFF # Low
            self.SP -= 2

            self.PC = vector

            return InterruptVector
        return NoInterrupt


    A = property(getA, setA)
    F = property(getF, setF)
    B = property(getB, setB)
    C = property(getC, setC)
    D = property(getD, setD)
    E = property(getE, setE)
    HL = property(getHL, setHL)
    SP = property(getSP, setSP)
    PC = property(getPC, setPC)

    H = property(getH, setH)
    L = property(getL, setL)
    AF = property(getAF, setAF) # Only used in StateManager
    BC = property(getBC, setBC)
    DE = property(getDE, setDE)

    fC = property(lambda s:bool(s.F & (1 << flagC)), None)
    fH = property(lambda s:bool(s.F & (1 << flagH)), None)
    fN = property(lambda s:bool(s.F & (1 << flagN)), None)
    fZ = property(lambda s:bool(s.F & (1 << flagZ)), None)
    fNC = property(lambda s:not bool(s.F & (1 << flagC)), None)
    fNZ = property(lambda s:not bool(s.F & (1 << flagZ)), None)

    def __init__(self, MB, profiling=False):
        self._A = 0
        self._F = 0
        self._B = 0
        self._C = 0
        self._D = 0
        self._E = 0
        self._HL = 0
        self._SP = 0
        self._PC = 0

        self.mb = MB

        self.interruptMasterEnable = False

        self.breakAllow = True
        self.breakOn = False
        self.breakNext = 0

        self.halted = False
        self.stopped = False

        self.debugCallStack = []

        # self.PC = 0

        #debug
        self.oldPC = -1
        self.lala = False

        # Profiling
        self.profiling = profiling
        if profiling:
            self.hitRate = np.zeros(shape=(512,), dtype=int)

    def fetchAndExecuteInstruction(self, pc):
        opcode = self.mb[pc]
        print("PC: 0x%0.2x, Opcode: 0x%0.2x" % (pc, opcode))
        print "%0.4x CB%0.2x AF:%0.4x BC:%0.4x DE%0.4x HL%0.4x SP%0.4x" % (self.PC, self.mb[self.PC+1], self.AF, self.BC, self.DE, self.HL, self.SP)
        if opcode == 0xCB:  # Extension code
            pc += 1
            opcode = self.mb[pc]
            opcode += 0x100  # Internally shifting look-up table

        #Profiling
        if self.profiling:
            self.hitRate[opcode] += 1

        return opcodes.executeOpcode(self, opcode)


    def tick(self):
        # "The interrupt will be acknowledged during opcode fetch period of each instruction."
        didInterrupt = self.checkForInterrupts()

        instruction = None
        if self.halted and didInterrupt:
            # GBCPUman.pdf page 20
            # WARNING: The instruction immediately following the HALT instruction is "skipped"
            # when interrupts are disabled (DI) on the GB,GBP, and SGB.
            self.halted = False
        elif self.halted:
            return -1
        # instruction = self.fetchInstruction(self.PC)
        # return self.executeInstruction(instruction)
        return self.fetchAndExecuteInstruction(self.PC)

        #if __debug__:
        #    if self.lala and not self.halted:
        #        if (self.mb[self.PC]) == 0xCB:
        #            print "%0.4x CB%0.2x AF:%0.4x BC:%0.4x DE%0.4x HL%0.4x SP%0.4x" % (self.PC, self.mb[self.PC+1], self.AF, self.BC, self.DE, self.HL, self.SP)
        #        else:
        #            print "%0.4x %0.2x AF:%0.4x BC:%0.4x DE%0.4x HL%0.4x SP%0.4x" % (self.PC, self.mb[self.PC], self.AF, self.BC, self.DE, self.HL, self.SP)

        #    if self.breakAllow and self.PC == self.breakNext and self.AF == 0x1f80:
        #        self.breakAllow = False
        #        self.breakOn = True

        #    if self.oldPC == self.PC and not self.halted:
        #        self.breakOn = True
        #        logger.info("PC DIDN'T CHANGE! Can't continue!")
        #        print self.getDump()
        #        # CoreDump.windowHandle.dump(self.mb.cartridge.filename+"_dump.bmp")
        #        raise Exception("Escape to main.py")
        #    self.oldPC = self.PC

        #    #TODO: Make better CoreDump print out. Where is 0xC000?
        #    #TODO: Make better opcode printing. Show arguments (check LDH/LDD)
        #    if self.breakOn:
        #        self.getDump(instruction)

        #        action = raw_input()
        #        if action == 'd':
        #            CoreDump.CoreDump("Debug")
        #        elif action == 'c':
        #            self.breakOn = False
        #            self.breakAllow = True
        #        elif action == 'r':
        #            self.breakOn = False
        #            self.breakAllow = False
        #        elif action[:2] == "0x":
        #            logger.info("Breaking on next {}".format(hex(int(action,16)))) #Checking parser
        #            self.breakNext = int(action,16)
        #            self.breakOn = False
        #            self.breakAllow = True
        #        elif action == 'ei':
        #            self.interruptMasterEnable = True
        #        elif action == 'o':
        #            targetPC = instruction[-1][-1]
        #            logger.info("Stepping over for {}".format(hex(targetPC))) #Checking parser
        #            self.breakNext = targetPC
        #            self.breakOn = False
        #            self.breakAllow = True
        #        else:
        #            pass

        #if __debug__:
        #    try:
        #        return self.executeInstruction(instruction)
        #    except:
        #        self.getDump(instruction)
        #        exit(1)
        #else:
        #    return self.executeInstruction(instruction)

    def getDump(self, instruction = None):
        pass
    #     flags = ""
    #     if self.testFlag(flagZ):
    #         flags += " Z"
    #     if self.testFlag(flagH):
    #         flags += " H"
    #     if self.testFlag(flagC):
    #         flags += " C"
    #     if self.testFlag(flagN):
    #         flags += " N"

    #     logger.info(flags)
    #     logger.info("A:   0x%0.2X   F: 0x%0.2X" % (self.A, self.F))
    #     logger.info("B:   0x%0.2X   C: 0x%0.2X" % (self.B, self.C))
    #     logger.info("D:   0x%0.2X   E: 0x%0.2X" % (self.D, self.E))
    #     logger.info("H:   0x%0.2X   L: 0x%0.2X" % (self.HL >> 8, self.HL & 0xFF))
    #     logger.info("SP:  0x%0.4X   PC: 0x%0.4X"% (self.SP, self.PC))
    #     # logger.info("0xC000", "0x%0.2X" % self.mb[0xc000])
    #     # logger.info("(HL-1)", "0x%0.2X" % self.mb[self.getHL()-1])
    #     logger.info("(HL) 0x%0.2X   (HL+1) 0x%0.2X" % (self.mb[self.HL], self.mb[self.HL+1]))
    #     logger.info("(SP) 0x%0.2X   (SP+1) 0x%0.2X" % (self.mb[self.SP], self.mb[self.SP+1]))
    #     logger.info(" ".join(map(lambda x: "%0.2x" % x, [self.mb[self.SP+x] for x in range(16)])))
    #     logger.info("Timer: DIV %s, TIMA %s, TMA %s, TAC %s" % (self.mb[0xFF04], self.mb[0xFF05], self.mb[0xFF06],bin(self.mb[0xFF07])))

    #     if (self.mb[self.PC]) != 0xCB:
    #         l = opcodes[self.mb[self.PC]][0]
    #         logger.info("Op: 0x%0.2X" % self.mb[self.PC])
    #         logger.info("Name: " + str(CPU_COMMANDS[self.mb[self.PC]]))
    #         logger.info("Len:" + str(l))
    #         if instruction:
    #             logger.info(("val: 0x%0.2X" % instruction[2][1]) if not l == 1 else "")
    #     else:

    #         logger.info("CB op: 0x%0.2X  CB name: %s" % (self.mb[self.PC+1], str(CPU_COMMANDS_EXT[self.mb[self.PC+1]])))
    #     logger.info("Call Stack " + str(self.debugCallStack))
    #     logger.info("Active ROM and RAM bank " +
    #             str(self.mb.cartridge.ROMBankSelected) + ' ' +
    #             str(self.mb.cartridge.RAMBankSelected))
    #     logger.info("Master Interrupt" + str(self.interruptMasterEnable))
    #     logger.info("Enabled Interrupts")

    #     flags = ""
    #     if self.testInterruptFlagEnabled(VBlank):
    #         flags += "VBlank "
    #     if self.testInterruptFlagEnabled(LCDC):
    #         flags += "LCDC "
    #     if self.testInterruptFlagEnabled(TIMER):
    #         flags += "Timer "
    #     if self.testInterruptFlagEnabled(Serial):
    #         flags += "Serial "
    #     if self.testInterruptFlagEnabled(HightoLow):
    #         flags += "HightoLow "
    #     logger.info(flags)
    #     logger.info("Waiting Interrupts")
    #     flags = ""
    #     if self.testInterruptFlag(VBlank):
    #         flags += "VBlank "
    #     if self.testInterruptFlag(LCDC):
    #         flags += "LCDC "
    #     if self.testInterruptFlag(TIMER):
    #         flags += "Timer "
    #     if self.testInterruptFlag(Serial):
    #         flags += "Serial "
    #     if self.testInterruptFlag(HightoLow):
    #         flags += "HightoLow "
    #     if self.halted:
    #         flags += " **HALTED**"
    #     logger.info(flags)
