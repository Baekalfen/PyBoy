# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from Logger import logger

def saveState(self, filename):
    logger.info("Saving state...")
    with open(filename, "wb") as f:
        for n in self.cpu.reg[:-2]:
            f.write(chr(n))

        for n in self.cpu.reg[-2:]:
            f.write(chr(n&0xFF))
            f.write(chr((n&0xFF00)>>8))

        f.write(chr(self.cpu.interruptMasterEnable))
        f.write(chr(self.cpu.halted))
        f.write(chr(self.cpu.stopped))
        f.write(chr(self.bootROMEnabled))

        f.write(bytearray([chr(n) for n in self.lcd.VRAM]))
        f.write(bytearray([chr(n) for n in self.ram.internalRAM0]))
        f.write(bytearray([chr(n) for n in self.lcd.OAM]))
        f.write(bytearray([chr(n) for n in self.ram.nonIOInternalRAM0]))
        f.write(bytearray([chr(n) for n in self.ram.IOPorts]))
        f.write(bytearray([chr(n) for n in self.ram.internalRAM1]))
        f.write(bytearray([chr(n) for n in self.ram.nonIOInternalRAM1]))
        f.write(bytearray([chr(n) for n in self.ram.interruptRegister]))

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

    logger.info("State saved.")


def loadState(self, filename):
    logger.info("Loading state...")
    with open(filename, "rb") as f:
        self.cpu.oldPC = None

        self.cpu.reg[:-2] = [ord(f.read(1)) for _ in xrange(len(self.cpu.reg)-2)]
        self.cpu.reg[-2:] = [ord(f.read(1)) + (ord(f.read(1))<<8) for _ in xrange(2)]

        self.cpu.interruptMasterEnable = ord(f.read(1))
        self.cpu.halted = ord(f.read(1))
        self.cpu.stopped = ord(f.read(1))
        self.bootROMEnabled = ord(f.read(1))

        self.lcd.VRAM[:]              = [ord(f.read(1)) for _ in self.lcd.VRAM]
        self.ram.internalRAM0[:]      = [ord(f.read(1)) for _ in self.ram.internalRAM0]
        self.lcd.OAM[:]               = [ord(f.read(1)) for _ in self.lcd.OAM]
        self.ram.nonIOInternalRAM0[:] = [ord(f.read(1)) for _ in self.ram.nonIOInternalRAM0]
        self.ram.IOPorts[:]           = [ord(f.read(1)) for _ in self.ram.IOPorts]
        self.ram.internalRAM1[:]      = [ord(f.read(1)) for _ in self.ram.internalRAM1]
        self.ram.nonIOInternalRAM1[:] = [ord(f.read(1)) for _ in self.ram.nonIOInternalRAM1]
        self.ram.interruptRegister[:] = [ord(f.read(1)) for _ in self.ram.interruptRegister]

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

    logger.info("State loaded.")

    self.lcd.clearCache = True
    self.lcd.refreshTileDataAdaptive()
