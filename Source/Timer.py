# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
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
        self.dividers = [1024, 16, 64, 256] #4^(1+n) = 4<<2*n ???

    def tick(self,cycles):
        if self.TAC & 0b100 == 0: # Check if timer is enabled
            return False

        self.DIVcounter += cycles
        if self.DIVcounter >= 256:
            self.DIVcounter -= 256 # Keeps possible remainder
            self.DIV += 1
            self.DIV &= 0xFF

        TIMAOverFlow = False

        self.TIMAcounter += cycles
        divider = self.dividers[self.TAC & 0b11]
        if self.TIMAcounter >= divider:
            self.TIMAcounter -= divider # Keeps possible remainder
            self.TIMA += 1
            if self.TIMA > 0xFF:
                self.TIMA = self.TMA
                TIMAOverFlow = True # Send yes, to interrupt
            self.TIMA &= 0xFF

        return TIMAOverFlow

    def getDIV(self):
        return (self.counter/256) & 0xFF