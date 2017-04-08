# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


def saveState(self, filename):
    self.logger("Saving state...")
    with open(filename, "wb") as f:
        for n in self.cpu.reg[:-2]:
            f.write(chr(n))

        for n in self.cpu.reg[-2:]:
            f.write(chr(n&0xFF))
            f.write(chr((n&0xFF00)>>8))

        f.write(chr(self.cpu.interruptMasterEnable))
        f.write(chr(self.cpu.interruptMasterEnableLatch))
        f.write(chr(self.cpu.halted))
        f.write(chr(self.cpu.stopped))
        f.write(chr(self.bootROMEnabled))

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
        f.write(chr(self.lcd.BGP.value))
        f.write(chr(self.lcd.OBP0.value))
        f.write(chr(self.lcd.OBP1.value))


        f.write(chr(self.cartridge.ROMBankSelected))
        f.write(chr(self.cartridge.RAMBankSelected))
        f.write(chr(self.cartridge.RAMBankEnabled))
        f.write(chr(self.cartridge.memoryModel))
        self.cartridge.saveRAM(filename)
        if self.cartridge.rtcEnabled:
            self.cartridge.rtc.save(filename + ".rtc")

    self.logger("State saved.")


def loadState(self, filename):
    self.logger("Loading state...")
    with open(filename, "rb") as f:
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
        self.bootROMEnabled = ord(f.read(1))

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
        self.lcd.BGP.set(ord(f.read(1)))
        self.lcd.OBP0.set(ord(f.read(1)))
        self.lcd.OBP1.set(ord(f.read(1)))



        self.cartridge.ROMBankSelected = ord(f.read(1))
        self.cartridge.RAMBankSelected = ord(f.read(1))
        self.cartridge.RAMBankEnabled = ord(f.read(1))
        self.cartridge.memoryModel = ord(f.read(1))
        self.cartridge.loadRAM(filename)
        if self.cartridge.rtcEnabled:
            self.cartridge.rtc.load(filename + ".rtc")

    self.logger("State loaded.")

    self.lcd.clearCache = True
    self.lcd.refreshTileDataAdaptive()
