# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from flags import VBlank, LCDC, TIMER, Serial, HightoLow
from registers import PC

from GbLogger import gblogger

# Order important. NoInterrupt evaluates to False in if statements
NoInterrupt, InterruptVector = range(0,2)

def checkForInterrupts(self):
    #GPCPUman.pdf p. 40 about priorities
    # If an interrupt occours, the PC is pushed to the stack.
    # It is up to the interrupt routine to return it.

    requestedInterrupts = self.mb[0xFF0F] & 0b11111
    anyInterruptToHandle = (requestedInterrupts & (self.mb[0xFFFF] & 0b11111)) != 0

    # Better to make a long check, than run through 5 if statements
    if anyInterruptToHandle and self.interruptMasterEnable:
        # flags = self.mb[0xFF0F]

        # 0xFF0F (IF) - Bit 0-4 Showing an interrupt occoured
        # 0xFFFF (IE) - Bit 0-4 Enabling the same interrupts
        # "When an interrupt is used, a '0' should be stored in the IF register before the IE register is set"

        #NOTE: Previous versions checked if IF was set, not IE. This made an infinite loop in the boot ROM (logo scrolling).
        if self.testInterruptFlagEnabled(VBlank) and self.testInterruptFlag(VBlank): # Vertical Blank
            # gblogger.info("Vertical Blank Interrupt")
            # gblogger.info("Interrupt enable", bin(self.mb[0xFFFF]))
            self.clearInterruptFlag(VBlank)
            self.interruptMasterEnableLatch = False
            self.CPU_PUSH(self.reg[PC])
            self.reg[PC] = 0x0040
            return InterruptVector
        elif self.testInterruptFlagEnabled(LCDC) and self.testInterruptFlag(LCDC): # LCDC Status
            # gblogger.info("LCDC Status Interrupt")
            self.clearInterruptFlag(LCDC)
            self.interruptMasterEnableLatch = False
            self.CPU_PUSH(self.reg[PC])
            self.reg[PC] = 0x0048
            return InterruptVector
        elif self.testInterruptFlagEnabled(TIMER) and self.testInterruptFlag(TIMER): # TIMER Overflow
            # gblogger.info("TIMER Overflow Interrupt")
            self.clearInterruptFlag(TIMER)
            self.interruptMasterEnableLatch = False
            self.CPU_PUSH(self.reg[PC])
            self.reg[PC] = 0x0050
            return InterruptVector
        elif self.testInterruptFlagEnabled(Serial) and self.testInterruptFlag(Serial): # Serial Transfer
            gblogger.info("Serial Transfer Interrupt")
            self.clearInterruptFlag(Serial)
            self.interruptMasterEnableLatch = False
            self.CPU_PUSH(self.reg[PC])
            self.reg[PC] = 0x0058
            return InterruptVector
        elif self.testInterruptFlagEnabled(HightoLow) and self.testInterruptFlag(HightoLow): # High-to-low P10-P13
            self.clearInterruptFlag(HightoLow)
            self.interruptMasterEnableLatch = False
            self.CPU_PUSH(self.reg[PC])
            self.reg[PC] = 0x0060
            return InterruptVector


    # Check if both enable and trigger flags are enabled for any interrupts
    return NoInterrupt
