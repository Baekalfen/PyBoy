# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from flags import VBlank, LCDC, TIMER, Serial, HightoLow
from registers import PC

def checkForInterrupts(self):
    #GPCPUman.pdf p. 40 about priorities
    # If an interrupt occours, the PC is pushed to the stack.
    # It is up to the interrupt routine to return it.

    if self.interruptMasterEnable:
        # flags = self.ram[0xFF0F]

        # 0xFF0F (IF) - Bit 0-4 Showing an interrupt occoured
        # 0xFFFF (IE) - Bit 0-4 Enabling the same interrupts
        # "When an interrupt is used, a '0' should be stored in the IF register before the IE register is set"

        #NOTE: Previous versions checked if IF was set, not IE. This made an infinite loop in the boot ROM (logo scrolling).
        if self.testInterruptFlagEnabled(VBlank) and self.testInterruptFlag(VBlank): # Vertical Blank
            # print "Vertical Blank Interrupt"
            self.clearInterruptFlag(VBlank)
            self.interruptMasterEnableLatch = False
            self.CPU_PUSH(self.reg[PC])
            self.reg[PC] = 0x0040
            return True
        elif self.testInterruptFlagEnabled(LCDC) and self.testInterruptFlag(LCDC): # LCDC Status
            # print "LCDC Status Interrupt"
            self.clearInterruptFlag(LCDC)
            self.interruptMasterEnableLatch = False
            self.CPU_PUSH(self.reg[PC])
            self.reg[PC] = 0x0048
            return True
        elif self.testInterruptFlagEnabled(TIMER) and self.testInterruptFlag(TIMER): # TIMER Overflow
            # print "TIMER Overflow Interrupt"
            self.clearInterruptFlag(TIMER)
            self.interruptMasterEnableLatch = False
            self.CPU_PUSH(self.reg[PC])
            self.reg[PC] = 0x0050
            return True
        elif self.testInterruptFlagEnabled(Serial) and self.testInterruptFlag(Serial): # Serial Transfer
            print "Serial Transfer Interrupt"
            self.clearInterruptFlag(Serial)
            self.interruptMasterEnableLatch = False
            self.CPU_PUSH(self.reg[PC])
            self.reg[PC] = 0x0058
            return True
        elif self.testInterruptFlagEnabled(HightoLow) and self.testInterruptFlag(HightoLow): # High-to-low P10-P13
            # print "High-to-low P10-P13 Interrupt"
            self.clearInterruptFlag(HightoLow)
            self.interruptMasterEnableLatch = False
            self.CPU_PUSH(self.reg[PC])
            self.reg[PC] = 0x0060
            return True


    return (self.testInterruptFlag(VBlank) or
            self.testInterruptFlag(LCDC) or
            self.testInterruptFlag(TIMER) or
            self.testInterruptFlag(Serial) or
            self.testInterruptFlag(HightoLow))