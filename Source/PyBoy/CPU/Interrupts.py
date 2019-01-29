# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .flags import VBlank, LCDC, TIMER, Serial, HightoLow

# Order important. NoInterrupt evaluates to False in if statements
NoInterrupt, InterruptVector = range(0,2)
IF = 0xFF0F
IE = 0xFFFF

def checkForInterrupts(self):
    #GPCPUman.pdf p. 40 about priorities
    # If an interrupt occours, the PC is pushed to the stack.
    # It is up to the interrupt routine to return it.

    # 0xFF0F (IF) - Bit 0-4 Requested interrupts
    # 0xFFFF (IE) - Bit 0-4 Enabling interrupt vectors
    anyInterruptToHandle = ((self.mb[IF] & 0b11111) & (self.mb[IE] & 0b11111))

    # Better to make a long check, than run through 5 if statements
    # TODO: Implement a interruptMasterEnable latch! The interrupt doesn't take effect on the very next instruction after IE
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
