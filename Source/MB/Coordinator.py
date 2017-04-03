# -*- encoding: utf-8 -*-
#
# Authors: Mads Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from MathUint8 import getBit

STAT = 0xFF41
LY = 0xFF44
LYC = 0xFF45

def calculateCycles(self, x):
    while x > 0:
        x -= self.cpu.tick()
    return x

def setSTATMode(self,mode):
    self[STAT] &= 0b11111100 # Clearing 2 LSB
    self[STAT] |= mode # Apply mode to LSB

    if self.cpu.testSTATFlag(mode+3) and mode != 3: # Mode "3" is not interruptable
        self.cpu.setInterruptFlag(self.cpu.LCDC)

def checkLYC(self, y):
    self[LY] = y
    if self[LYC] == y:
        self[STAT] |= 0b100 # Sets the LYC flag
        if getBit(self[STAT], 6) == 1:
            self.cpu.setInterruptFlag(self.cpu.LCDC)
    else:
        self[STAT] &= 0b11111011

def tickFrame(self):
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

