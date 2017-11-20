# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

STAT = 0xFF41
LY = 0xFF44
LYC = 0xFF45

def setSTATMode(self,mode):
    self[STAT] &= 0b11111100 # Clearing 2 LSB
    self[STAT] |= mode # Apply mode to LSB

    if self.cpu.testRAMRegisterFlag(STAT,mode+3) and mode != 3: # Mode "3" is not interruptable
    # if self.cpu.testSTATFlag(mode+3) and mode != 3: # Mode "3" is not interruptable
        self.cpu.setInterruptFlag(self.cpu.LCDC)

def checkLYC(self, y):
    self[LY] = y
    if self[LYC] == y:
        self[STAT] |= 0b100 # Sets the LYC flag
        if self[STAT] & 0b01000000:
            self.cpu.setInterruptFlag(self.cpu.LCDC)
    else:
        self[STAT] &= 0b11111011

def calculateCycles(self, x):
    while x > 0:
        cycles = self.cpu.tick()

        # TODO: Benchmark whether 'if' and 'try/except' is better
        if cycles == -1: # CPU has HALTED
            # Fast-forward to next interrupt:
            # VBLANK and LCDC are covered by just returning.
            # Timer has to be determined.
            # As we are halted, we are guaranteed, that
            # our state cannot be altered by other factors
            # than time.
            # For HiToLo interrupt it is indistinguishable
            # whether it gets triggered mid-frame or by next
            # frame
            # Serial is not implemented, so this isn't a concern
            cycles = min(self.timer.cyclesToInterrupt(), x)

            # Profiling
            if self.cpu.profiling:
                self.cpu.hitRate[0x76] += cycles/4

        x -= cycles
        if self.timer.tick(cycles):
            self.cpu.setInterruptFlag(self.TIMER)

def tickFrame(self):
    lcdEnabled = self.lcd.LCDC.enabled
    if lcdEnabled:
        self.lcd.refreshTileDataAdaptive()

        if __debug__:
            self.MainWindow.refreshTileView1(self.lcd)
            self.MainWindow.refreshTileView2(self.lcd)
            self.MainWindow.refreshSpriteView(self.lcd)
            self.MainWindow.drawTileCacheView(self.lcd)
            self.MainWindow.drawTileView1ScreenPort(self.lcd)
            self.MainWindow.drawTileView2WindowPort(self.lcd)

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

            self.MainWindow.scanline(y, self.lcd.getViewPort(), self.lcd.getWindowPos()) # Just recording states of LCD registers

            # Mode 0
            self.setSTATMode(0)
            self.calculateCycles(206)

        self.cpu.setInterruptFlag(self.cpu.VBlank)

        self.MainWindow.renderScreen(self.lcd) # Actually render screen from scanline parameters

        # Wait for next frame
        for y in xrange(144,154):
            self.checkLYC(y)

            # Mode 1
            self.setSTATMode(1)
            self.calculateCycles(456)
    else:
        # https://www.reddit.com/r/EmuDev/comments/6r6gf3/gb_pokemon_gold_spews_unexpected_values_at_mbc/
        # TODO: What happens if LCD gets turned on/off mid-cycle?
        self.MainWindow.blankScreen()
        self.setSTATMode(0)
        self[LY] = 0

        for y in xrange(154):
            self.calculateCycles(456)


