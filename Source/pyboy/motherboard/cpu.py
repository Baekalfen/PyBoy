#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import array
from . import opcodes


flagC, flagH, flagN, flagZ = range(4, 8)
VBlank, LCDC, TIMER, Serial, HightoLow = range(5)
IF_address = 0xFF0F
IE_address = 0xFFFF


class CPU():
    def setBC(self, x):
        assert x <= 0xFFFF, "%0.4x" % x
        self.B = x >> 8
        self.C = x & 0x00FF

    def setDE(self, x):
        assert x <= 0xFFFF, "%0.4x" % x
        self.D = x >> 8
        self.E = x & 0x00FF

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
    def setInterruptFlag(self, flag):
        self.mb.setitem(IF_address, self.mb.getitem(IF_address) | (1 << flag))

    def testRAMRegisterFlag(self, address, flag):
        v = self.mb.getitem(address)
        return (v & (1 << flag))

    def setRAMRegisterFlag(self, address, flag, value=True):
        self.clearRAMRegisterFlag(address, flag)
        # self.mb.setitem(address, (self.mb.getitem(address) & (0xFF - (1 << flag))))
        # if value:
        self.mb.setitem(address, (self.mb.getitem(address) + (value << flag)))

    def clearRAMRegisterFlag(self, address, flag):
        self.mb.setitem(address, (self.mb.getitem(address) & (0xFF - (1 << flag))))

    def testRAMRegisterFlagEnabled(self, address, flag):
        v = self.mb.getitem(address)
        return (v & (1 << flag))

    def testInterrupt(self, if_v, ie_v, flag):
        intr_flag_enabled = (ie_v & (1 << flag))
        intr_flag = (if_v & (1 << flag))

        if intr_flag_enabled and intr_flag:

            # Clear interrupt flag
            self.mb.setitem(0xFF0F, self.mb.getitem(0xFF0F) & (0xFF - (1 << flag)))

            self.interruptMasterEnable = False
            if self.halted:
                self.PC += 1 # Escape HALT on return
                # self.CPU_PUSH(self.PC+1)
            # else:
                # self.CPU_PUSH(self.PC)

            self.mb.setitem(self.SP-1, self.PC >> 8) # High
            self.mb.setitem(self.SP-2, self.PC & 0xFF) # Low
            self.SP -= 2

            # self.PC = vector

            return True
        return False

    def checkForInterrupts(self):
        #GPCPUman.pdf p. 40 about priorities
        # If an interrupt occours, the PC is pushed to the stack.
        # It is up to the interrupt routine to return it.
        if not self.interruptMasterEnable:
            return False

        # 0xFF0F (IF_address) - Bit 0-4 Requested interrupts
        if_v = self.mb.getitem(IF_address)
        # 0xFFFF (IE_address) - Bit 0-4 Enabling interrupt vectors
        ie_v = self.mb.getitem(IE_address)

        # Better to make a long check, than run through 5 if statements
        if ((if_v & 0b11111) & (ie_v & 0b11111)) != 0:
            if self.testInterrupt(if_v, ie_v, VBlank):
                self.PC = 0x0040
                return True
            elif self.testInterrupt(if_v, ie_v, LCDC):
                self.PC = 0x0048
                return True
            elif self.testInterrupt(if_v, ie_v, TIMER):
                self.PC = 0x0050
                return True
            elif self.testInterrupt(if_v, ie_v, Serial):
                self.PC = 0x0058
                return True
            elif self.testInterrupt(if_v, ie_v, HightoLow):
                self.PC = 0x0060
                return True
            # flags_vectors = [(VBlank, 0x0040), (LCDC, 0x0048), (TIMER, 0x0050), (Serial, 0x0058), (HightoLow, 0x0060)]
            # for flag, vector in flags_vectors:

        return False


    def fC(self):
        return (self.F & (1 << flagC)) != 0

    def fH(self):
        return (self.F & (1 << flagH)) != 0

    def fN(self):
        return (self.F & (1 << flagN)) != 0

    def fZ(self):
        return (self.F & (1 << flagZ)) != 0

    def fNC(self):
        return (self.F & (1 << flagC)) == 0

    def fNZ(self):
        return (self.F & (1 << flagZ)) == 0

    def __init__(self, MB, profiling=False):
        self.A = 0
        self.F = 0
        self.B = 0
        self.C = 0
        self.D = 0
        self.E = 0
        self.HL = 0
        self.SP = 0
        self.PC = 0

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
            self.hitRate = array.array('L', [0] * 512)

    def saveState(self, f):
        for n in [self.A, self.F, self.B, self.C, self.D, self.E]:
            f.write((n & 0xFF).to_bytes(1, 'little'))

        for n in [self.HL, self.SP, self.PC]:
            f.write((n & 0xFF).to_bytes(1, 'little'))
            f.write(((n & 0xFF00) >> 8).to_bytes(1, 'little'))

        f.write(self.interruptMasterEnable.to_bytes(1, 'little'))
        f.write(self.halted.to_bytes(1, 'little'))
        f.write(self.stopped.to_bytes(1, 'little'))

    def loadState(self, f):
        self.oldPC = -1

        self.A, self.F, self.B,\
        self.C, self.D, self.E  = [ord(f.read(1)) for _ in range(6)]

        self.HL, self.SP, self.PC = [ord(f.read(1)) | (ord(f.read(1))<<8) for _ in range(3)]

        self.interruptMasterEnable = ord(f.read(1))
        self.halted = ord(f.read(1))
        self.stopped = ord(f.read(1))

    def fetchAndExecuteInstruction(self, pc):
        opcode = self.mb.getitem(pc)
        # print("PC: 0x%0.2x, Opcode: 0x%0.2x" % (pc, opcode))
        # print "%0.4x CB%0.2x AF:%0.4x BC:%0.4x DE%0.4x HL%0.4x SP%0.4x" % (self.PC, self.mb.getitem(self.PC+1), self.AF, self.BC, self.DE, self.HL, self.SP)
        if opcode == 0xCB:  # Extension code
            pc += 1
            opcode = self.mb.getitem(pc)
            opcode += 0x100  # Internally shifting look-up table

        #Profiling
        if self.profiling:
            self.hitRate[opcode] += 1

        return opcodes.executeOpcode(self, opcode)


    def tick(self):
        # "The interrupt will be acknowledged during opcode fetch period of each instruction."
        didInterrupt = self.checkForInterrupts()

        # instruction = None
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
        #        if (self.mb.getitem(self.PC)) == 0xCB:
        #            print "%0.4x CB%0.2x AF:%0.4x BC:%0.4x DE%0.4x HL%0.4x SP%0.4x" % (self.PC, self.mb.getitem(self.PC+1), self.AF, self.BC, self.DE, self.HL, self.SP)
        #        else:
        #            print "%0.4x %0.2x AF:%0.4x BC:%0.4x DE%0.4x HL%0.4x SP%0.4x" % (self.PC, self.mb.getitem(self.PC), self.AF, self.BC, self.DE, self.HL, self.SP)

        #    if self.breakAllow and self.PC == self.breakNext and self.AF == 0x1f80:
        #        self.breakAllow = False
        #        self.breakOn = True

        #    if self.oldPC == self.PC and not self.halted:
        #        self.breakOn = True
        #        logger.info("PC DIDN'T CHANGE! Can't continue!")
        #        print self.getDump()
        #        raise Exception("Escape to main.py")
        #    self.oldPC = self.PC

        #    #TODO: Make better opcode printing. Show arguments (check LDH/LDD)
        #    if self.breakOn:
        #        self.getDump(instruction)

        #        action = raw_input()
        #        if action == 'd':
        #           pass
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
    #     # logger.info("0xC000", "0x%0.2X" % self.mb.getitem(0xc000))
    #     # logger.info("(HL-1)", "0x%0.2X" % self.mb.getitem(self.getHL()-1))
    #     logger.info("(HL) 0x%0.2X   (HL+1) 0x%0.2X" % (self.mb.getitem(self.HL), self.mb.getitem(self.HL+1)))
    #     logger.info("(SP) 0x%0.2X   (SP+1) 0x%0.2X" % (self.mb.getitem(self.SP), self.mb.getitem(self.SP+1)))
    #     logger.info(" ".join(map(lambda x: "%0.2x" % x, [self.mb.getitem(self.SP+x) for x in range(16)])))
    #     logger.info("Timer: DIV %s, TIMA %s, TMA %s, TAC %s" % (self.mb.getitem(0xFF04), self.mb.getitem(0xFF05), self.mb.getitem(0xFF06),bin(self.mb.getitem(0xFF07))))

    #     if (self.mb.getitem(self.PC)) != 0xCB:
    #         l = opcodes[self.mb.getitem(self.PC)][0]
    #         logger.info("Op: 0x%0.2X" % self.mb.getitem(self.PC))
    #         logger.info("Name: " + str(CPU_COMMANDS[self.mb.getitem(self.PC)]))
    #         logger.info("Len:" + str(l))
    #         if instruction:
    #             logger.info(("val: 0x%0.2X" % instruction[2][1]) if not l == 1 else "")
    #     else:

    #         logger.info("CB op: 0x%0.2X  CB name: %s" % (self.mb.getitem(self.PC+1), str(CPU_COMMANDS_EXT[self.mb.getitem(self.PC+1)])))
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
