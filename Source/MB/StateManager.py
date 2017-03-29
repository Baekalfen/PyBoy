# -*- encoding: utf-8 -*-
#
# Authors: Mads Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


def saveState(self, filename = "state"):
    self.logger("Saving state...")
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

        f.write(chr(self.lcd.LCDC.value))
        self.logger("LCDC",self.lcd.LCDC.value)

        # # Save cartridge RAM
        # for n in self.ram.cartridge.RAMBanks:
        #     for m in n:
        #         f.write(chr(m))

    self.logger("State saved.")


def loadState(self, filename = "state"):
    self.logger("Loading state...")
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

        for n in xrange(len(self.ram.VRAM)):
            self.ram.VRAM[n] = ord(f.read(1))

        for n in xrange(len(self.ram.internalRAM0)):
            self.ram.internalRAM0[n] = ord(f.read(1))

        for n in xrange(len(self.ram.OAM)):
            self.ram.OAM[n] = ord(f.read(1))

        for n in xrange(len(self.ram.nonIOInternalRAM0)):
            self.ram.nonIOInternalRAM0[n] = ord(f.read(1))

        for n in xrange(len(self.ram.IOPorts)):
            self.ram.IOPorts[n] = ord(f.read(1))

        for n in xrange(len(self.ram.internalRAM1)):
            self.ram.internalRAM1[n] = ord(f.read(1))

        for n in xrange(len(self.ram.nonIOInternalRAM1)):
            self.ram.nonIOInternalRAM1[n] = ord(f.read(1))

        for n in xrange(len(self.ram.interruptRegister)):
            self.ram.interruptRegister[n] = ord(f.read(1))

        self.lcd.LCDC.set(ord(f.read(1)))
        self.logger("LCDC",self.lcd.LCDC.value)

        # # Loading RAMBanks to cartridge
        # for i in xrange(len(self.ram.cartridge.RAMBanks)):
        #     for j in xrange(len(self.ram.cartridge.RAMBanks[i])):
        #         self.ram.cartridge.RAMBanks[i][j] = ord(f.read(1))

    self.logger("State loaded.")
    self.lcd.refreshTileData()
