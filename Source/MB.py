# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from CPU import CPU
from RAM import RAM
from RAM import VIDEO_RAM, INTERNAL_RAM_0, OBJECT_ATTRIBUTE_MEMORY, NON_IO_INTERNAL_RAM0, IO_PORTS, NON_IO_INTERNAL_RAM1, INTERNAL_RAM_1, INTERRUPT_ENABLE_REGISTER
from Cartridge import Cartridge
from LCD import LCD
from Interaction import Interaction
import time
from Timer import Timer
from CPU.flags import VBlank
import CoreDump
from MathUint8 import getBit

STAT = 0xFF41
LY = 0xFF44
LYC = 0xFF45

class Motherboard():
    def __init__(self, gameROMFile, bootROMFile, window):
        self.timer = Timer()
        self.interaction = Interaction()
        self.cartridge = Cartridge(gameROMFile)
        self.ram = RAM(bootROMFile, self.cartridge, self.interaction, self.timer, random=False)
        self.cpu = CPU(self.ram, self.timer)
        self.lcd = LCD(self.ram, window)

        # WARNING: Cyclic reference
        self.ram.lcd = self.lcd

        CoreDump.RAM = self.ram
        CoreDump.CPU = self.cpu

    def saveState(self, filename = "state"):
        print "Saving state..."
        with open(filename, "w") as f:
            for n in self.cpu.reg[:-2]:
                f.write(chr(n))

            for n in self.cpu.reg[-2:]:
                f.write(chr(n&0xFF))
                f.write(chr((n&0xFF00)>>8))

            f.write(chr(self.cpu.interruptMasterEnable))
            f.write(chr(self.cpu.interruptMasterEnableLatch))
            f.write(chr(self.cpu.halted))
            f.write(chr(self.cpu.stopped))
            f.write(chr(self.ram.bootROMEnabled))

            # Save debug vars

            for n in self.ram.VRAM:
                f.write(chr(n))

            for n in self.ram.internalRAM0:
                f.write(chr(n))

            for n in self.ram.OAM:
                f.write(chr(n))

            for n in self.ram.nonIOInternalRAM0:
                f.write(chr(n))

            for n in self.ram.IOPorts:
                f.write(chr(n))

            for n in self.ram.internalRAM1:
                f.write(chr(n))

            for n in self.ram.nonIOInternalRAM1:
                f.write(chr(n))

            for n in self.ram.interruptRegister:
                f.write(chr(n))

            f.write(chr(self.lcd.LCDC))
            print "LCDC",self.lcd.LCDC
            
            # # Save cartridge RAM
            # for n in self.ram.cartridge.RAMBanks:
            #     for m in n:
            #         f.write(chr(m))

        print "State saved."


    def loadState(self, filename = "state"):
        print "Loading state..."
        with open(filename, "r") as f:
            self.cpu.oldPC = None

            for n in xrange(len(self.cpu.reg)-2):
                self.cpu.reg[n] = ord(f.read(1))

            for n in xrange(len(self.cpu.reg)-2,len(self.cpu.reg)):
                self.cpu.reg[n] = ord(f.read(1))
                self.cpu.reg[n] += ord(f.read(1)) << 8

            self.cpu.interruptMasterEnable = ord(f.read(1))
            self.cpu.interruptMasterEnableLatch = ord(f.read(1))
            self.cpu.halted = ord(f.read(1))
            self.cpu.stopped = ord(f.read(1))
            self.ram.bootROMEnabled = ord(f.read(1))

            for n in xrange(VIDEO_RAM):
                self.ram.VRAM[n] = ord(f.read(1))

            for n in xrange(INTERNAL_RAM_0):
                self.ram.internalRAM0[n] = ord(f.read(1))

            for n in xrange(OBJECT_ATTRIBUTE_MEMORY):
                self.ram.OAM[n] = ord(f.read(1))

            for n in xrange(NON_IO_INTERNAL_RAM0):
                self.ram.nonIOInternalRAM0[n] = ord(f.read(1))

            for n in xrange(IO_PORTS):
                self.ram.IOPorts[n] = ord(f.read(1))

            for n in xrange(INTERNAL_RAM_1):
                self.ram.internalRAM1[n] = ord(f.read(1))

            for n in xrange(NON_IO_INTERNAL_RAM1):
                self.ram.nonIOInternalRAM1[n] = ord(f.read(1))

            for n in xrange(INTERRUPT_ENABLE_REGISTER):
                self.ram.interruptRegister[n] = ord(f.read(1))

            self.lcd.setLCDC(ord(f.read(1)))
            print "LCDC",self.lcd.LCDC

            # # Loading RAMBanks to cartridge
            # for i in xrange(len(self.ram.cartridge.RAMBanks)):
            #     for j in xrange(len(self.ram.cartridge.RAMBanks[i])):
            #         self.ram.cartridge.RAMBanks[i][j] = ord(f.read(1))

        print "State loaded."
        self.lcd.refreshTileData()

    def calculateCycles(self, x):
        while x > 0:
            x -= self.cpu.tick()
        return x

    def setSTATMode(self,mode):
        self.ram[STAT] &= 0b11111100 # Clearing 2 LSB
        self.ram[STAT] |= mode # Apply mode to LSB

        if self.cpu.testSTATFlag(mode+3) and mode != 3: # Mode "3" is not interruptable
            self.cpu.setInterruptFlag(self.cpu.LCDC)

    def checkLYC(self, y):
        self.ram[LY] = y
        if self.ram[LYC] == y:
            self.ram[STAT] |= 0b100 # Sets the LYC flag
            if getBit(self.ram[STAT], 6) == 1:
                self.cpu.setInterruptFlag(self.cpu.LCDC)
        else:
            self.ram[STAT] &= 0b11111011

    def tickFrame(self):
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

        # t = time.time()
        # TODO: the 19, 41 and 49 ticks should correct for longer instructions
        # Iterate the 144 lines on screen
        for y in xrange(144):
            self.checkLYC(y)

            # Mode 2
            self.setSTATMode(2)
            self.calculateCycles(80)
            # Mode 3
            self.setSTATMode(3)
            self.calculateCycles(170)
            
            self.lcd.scanline(y)

            # Mode 0
            self.setSTATMode(0)
            self.calculateCycles(206)

            # 80 + 170 + 206 = 456 "A complete cycle through these states takes 456 clks"
        # return t - time.time()

    def tickVblank(self):
        # t = time.time()
        self.cpu.setInterruptFlag(self.cpu.VBlank)
        # Wait for next frame
        for y in xrange(144,154):
            self.checkLYC(y)

            # Mode 1
            self.setSTATMode(1)
            self.calculateCycles(456)

            # VBlank lasts 4560 clks.

        # self.lcd.tick() # Refreshes the host display
        # return t-time.time()

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
