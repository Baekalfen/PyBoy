# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


# http://problemkaputt.de/pandocs.htm#gameboytechnicaldata
# Unless the oscillator frequency is multiplied or divided before it gets to the CPU,
# it must be running at 4.194304MHz (or if the CPU has an internal oscillator).
#
# http://problemkaputt.de/pandocs.htm#timeranddividerregisters
# Depending on the TAC register, the timer can run at one of four frequencies
# 00:   4096 Hz (OSC/1024)
# 01: 262144 Hz (OSC/16)
# 10:  65536 Hz (OSC/64)
# 11:  16384 Hz (OSC/256)


class Timer():
    def __init__(self):
        self.DIV = 0 # Always showing self.counter with mode 3 divider
        self.TIMA = 0 # Can be set from RAM 0xFF05
        self.DIVcounter = 0
        self.TIMAcounter = 0
        self.TMA = 0
        self.TAC = 0
        self.dividers = [1024, 16, 64, 256]

    def tick(self,cycles):
        self.DIVcounter += cycles
        self.DIV += (self.DIVcounter >> 8) # Add the overflown bits to DIV
        self.DIVcounter &= 0xFF # Remove the overflown bits
        self.DIV &= 0xFF

        if self.TAC & 0b100 == 0: # Check if timer is not enabled
            return False


        self.TIMAcounter += cycles
        divider = self.dividers[self.TAC & 0b11]

        if self.TIMAcounter >= divider:
            self.TIMAcounter -= divider # Keeps possible remainder
            self.TIMA += 1

            if self.TIMA > 0xFF:
                self.TIMA = self.TMA
                self.TIMA &= 0xFF
                return True

        return False

    def cyclesToInterrupt(self):
        if self.TAC & 0b100 == 0: # Check if timer is not enabled
            return 2**16 # Large enough, that 'calculateCycles' will choose 'x'

        divider = self.dividers[self.TAC & 0b11]

        cyclesLeft = ((0x100 - self.TIMA) * divider) - self.TIMAcounter

        return cyclesLeft
