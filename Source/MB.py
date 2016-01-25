# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from CPU import CPU
from RAM import RAM
from Cartridge import Cartridge
from LCD import LCD
from Interaction import Interaction
from time import time
from Timer import Timer
from CPU.flags import VBlank
import CoreDump

class Motherboard():
    def __init__(self, gameROMFile, bootROMFile, window):
        self.timer = Timer()
        self.interaction = Interaction()
        self.cartridge = Cartridge(gameROMFile)
        self.ram = RAM(bootROMFile, self.cartridge, self.interaction, self.timer, random=False)
        self.cpu = CPU(self.ram, self.timer)
        self.lcd = LCD(self.ram, window)

        CoreDump.RAM = self.ram
        CoreDump.CPU = self.cpu

    def calculateCycles(self, x):
        while x > 0:
            x -= self.cpu.tick()
        return x

    def setSTATMode(self,mode):
        self.cpu.ram[0xFF41] &= 0b11111100 # Clearing 2 LSB
        self.cpu.ram[0xFF41] |= mode # Apply mode to LSB

        if self.cpu.testSTATFlag(mode+3):
            self.cpu.setInterruptFlag(self.cpu.LCDC)

    def tick(self):
        # TODO: Refactor this by moving most of this logic to LCD (LCD is current part of host) and a central oscillator/timer (maybe refactor this file)

        # http://problemkaputt.de/pandocs.htm#lcdstatusregister
        # ---------------
        # The following are typical when the display is enabled:
        #   Mode 2  2_____2_____2_____2_____2_____2___________________2____
        #   Mode 3  _33____33____33____33____33____33__________________3___
        #   Mode 0  ___000___000___000___000___000___000________________000
        #   Mode 1  ____________________________________11111111111111_____

        # The Mode Flag goes through the values 0, 2, and 3 at a cycle of about 109uS.
        # 0 is present about 48.6uS, 2 about 19uS, and 3 about 41uS.
        # This is interrupted every 16.6ms by the VBlank (1).
        # The mode flag stays set at 1 for about 1.08 ms.

        # Mode 0 is present between 201-207 clks, 2 about 77-83 clks, and 3 about 169-175 clks.
        # A complete cycle through these states takes 456 clks. VBlank lasts 4560 clks.
        # A complete screen refresh occurs every 70224 clks.
        # ---------------

        # The CPU calculates instructions by 1.000.000 pr. second. That means, 1µs from the scheme above, is 1 instruction.
        # GBCPUman.pdf says: "The LY can take on any value between 0 through 153"
        # The modes 0, 2 and 3 takes 109µs.
        # 109µs * 153 = 16677 µs = 16.677ms ≈ 1/60 second = 16.667ms
        # 144 to 153 is the mode 1 phase. This is 9 times 109µs. This is off-by-one of the estimated 1.08ms mode 1 phase.
        # I can conclude, every line takes 109µs to render, this is done 144 (143?) times.
        # The following 10 * 109µs are waiting before restarting.


        ##################
        #
        # Timing the LCD
        #
        STAT = 0xFF41
        LY = 0xFF44
        LYC = 0xFF45

        # TODO: the 19, 41 and 49 ticks should correct for longer instructions
        # Iterate the 144 lines on screen
        for y in xrange(144):
            self.ram[LY] = y
            if self.ram[LYC] == y and self.cpu.testSTATFlag(self.cpu.LYCFlagEnable):
                #LYC interrupt
                if self.cpu.testSTATFlag(self.cpu.LYCFlag):
                    self.cpu.setInterruptFlag(self.cpu.LCDC)

            # Mode 2
            self.setSTATMode(2)
            self.calculateCycles(80)
            # Mode 3
            self.setSTATMode(3)
            self.calculateCycles(170)
            # Mode 0
            self.setSTATMode(0)
            self.calculateCycles(206)

            # 80 + 170 + 206 = 456 "A complete cycle through these states takes 456 clks"

        self.cpu.setInterruptFlag(self.cpu.VBlank)
        # Wait for next frame
        for y in xrange(144,154):
            self.ram[LY] = y
            if self.ram[LYC] == y and self.cpu.testSTATFlag(self.cpu.LYCFlagEnable):
                #LYC interrupt
                if self.cpu.testSTATFlag(self.cpu.LYCFlag):
                    self.cpu.setInterruptFlag(self.cpu.LCDC)

            # Mode 1
            self.setSTATMode(1)
            self.calculateCycles(456)

            # VBlank lasts 4560 clks.

        self.lcd.tick() # Refreshes the host display

    def loadCartridge(self, filename):
        self.cartridge = Cartridge(filename)

    def buttonEvent(self, key):
        self.interaction.keyEvent(key)
        self.cpu.setInterruptFlag(self.cpu.HightoLow)


if __name__ == "__main__":
    mb = Motherboard("pokemon_blue.gb", "DMG_ROM.bin", None)
    i = 0
    t = time()
    while i < 100:
        mb.tickFrame()
        i += 1
        t2 = t
        t = time()
        print ".", t - t2
