# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys
# # import pyximport; pyximport.install()

from ..Logger import logger
import Timer
import CPU
from .. import RAM, BootROM, LCD, Interaction, CoreDump
from .. import Cartridge
# # from CPU.flags import VBlank, TIMER, HightoLow, LCDC
# VBlank, LCDC, TIMER, Serial, HightoLow = range(5)

# STAT = 0xFF41
# LY = 0xFF44
# LYC = 0xFF45

class Motherboard():
    def __init__(self, gameROMFile, bootROMFile, window, profiling = False, debugger = None):
        if bootROMFile is not None:
            logger.info("Boot-ROM file provided")

        if profiling:
            logger.info("Profiling enabled")

        self.debugger = debugger
        self.MainWindow = window
        self.timer = Timer.Timer()
        self.interaction = Interaction.Interaction()
        self.cartridge = Cartridge.Cartridge.Cartridge(gameROMFile)
        self.bootROM = BootROM.BootROM(bootROMFile)
        self.ram = RAM.RAM(random=False)
        self.cpu = CPU.CPU(self, profiling)
        self.lcd = LCD.LCD(self)
        self.bootROMEnabled = True

        if "loadState" in sys.argv:
            self.loadState(str(self.cartridge.filename) + ".state")

        self.cartridge.loadRAM()
        if self.cartridge.rtcEnabled:
            self.cartridge.rtc.load(self.cartridge.filename)

        CoreDump.RAM = self.ram
        CoreDump.CPU = self.cpu

    def buttonEvent(self, key):
        self.interaction.keyEvent(key)
        self.cpu.setInterruptFlag(HightoLow)

    def stop(self, save):
        if save:
            self.cartridge.saveRAM()
            if self.cartridge.rtcEnabled:
                self.cartridge.rtc.save(self.cartridge.filename)


    #########################
    ## Coordinator

    def setSTATMode(self, mode):
        self[STAT] &= 0b11111100 # Clearing 2 LSB
        self[STAT] |= mode # Apply mode to LSB

        if self.cpu.testRAMRegisterFlag(STAT,mode+3) and mode != 3: # Mode "3" is not interruptable
        # if self.cpu.testSTATFlag(mode+3) and mode != 3: # Mode "3" is not interruptable
            self.cpu.setInterruptFlag(LCDC)

    def checkLYC(self, y):
        self[LY] = y
        if self[LYC] == y:
            self[STAT] |= 0b100 # Sets the LYC flag
            if self[STAT] & 0b01000000:
                self.cpu.setInterruptFlag(LCDC)
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
                self.cpu.setInterruptFlag(TIMER)

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

            self.cpu.setInterruptFlag(VBlank)

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


    ########################
    ## MemoryManager

    def __len__(self):
        return 0xFFFF

    def __getitem__(self, i):
        return self.get(i)

    def get(self, i):
        if 0x0000 <= i < 0x4000:  # 16kB ROM bank #0
            if i <= 0xFF and self.bootROMEnabled:
                return self.bootROM[i]
            else:
                return self.cartridge[i]
        elif 0x4000 <= i < 0x8000:  # 16kB switchable ROM bank
            return self.cartridge[i]
        elif 0x8000 <= i < 0xA000:  # 8kB Video RAM
            return self.lcd.VRAM[i - 0x8000]
        elif 0xA000 <= i < 0xC000:  # 8kB switchable RAM bank
            return self.cartridge[i]
        elif 0xC000 <= i < 0xE000:  # 8kB Internal RAM
            return self.ram.internalRAM0[i - 0xC000]
        elif 0xE000 <= i < 0xFE00:  # Echo of 8kB Internal RAM
            # Redirect to internal RAM
            return self[i - 0x2000]
        elif 0xFE00 <= i < 0xFEA0:  # Sprite Attrib Memory (OAM)
            return self.lcd.OAM[i - 0xFE00]
        elif 0xFEA0 <= i < 0xFF00:  # Empty but unusable for I/O
            return self.ram.nonIOInternalRAM0[i - 0xFEA0]
        elif 0xFF00 <= i < 0xFF4C:  # I/O ports
            if i == 0xFF04:
                return self.timer.DIV
            elif i == 0xFF05:
                return self.timer.TIMA
            elif i == 0xFF06:
                return self.timer.TMA
            elif i == 0xFF07:
                return self.timer.TAC
            elif i == 0xFF40:
                return self.lcd.LCDC.value
            elif i == 0xFF47:
                return self.lcd.BGP.value
            elif i == 0xFF48:
                return self.lcd.OBP0.value
            elif i == 0xFF49:
                return self.lcd.OBP1.value
            else:
                return self.ram.IOPorts[i - 0xFF00]
        elif 0xFF4C <= i < 0xFF80:  # Empty but unusable for I/O
            return self.ram.nonIOInternalRAM1[i - 0xFF4C]
        elif 0xFF80 <= i < 0xFFFF:  # Internal RAM
            return self.ram.internalRAM1[i-0xFF80]
        elif i == 0xFFFF:  # Interrupt Enable Register
            return self.ram.interruptRegister[0]
        else:
            raise Exception("Memory access violation. Tried to read: %s" % hex(i))

    def __setitem__(self,i,value):
        self.set(i,value)

    def set(self,i,value):
        if i == 0xFF01:
            print chr(value),
        assert value < 0x100, "Memory write error! Can't write %s to %s" % (hex(value),hex(i))
                # CoreDump.CoreDump("Memory write error! Can't write %s to %s" % (hex(value),hex(i))),\

        if 0x0000 <= i < 0x4000:  # 16kB ROM bank #0
            self.cartridge[i] = value #Doesn't change the data. This is for MBC commands
        elif 0x4000 <= i < 0x8000:  # 16kB switchable ROM bank
            self.cartridge[i] = value #Doesn't change the data. This is for MBC commands
        elif 0x8000 <= i < 0xA000:  # 8kB Video RAM
            self.lcd.VRAM[i - 0x8000] = value
            if i < 0x9800: # Is within tile data -- not tile maps
                self.lcd.tilesChanged.add(i & 0xFFF0) # Mask out the byte of the tile
        elif 0xA000 <= i < 0xC000:  # 8kB switchable RAM bank
            self.cartridge[i] = value
        elif 0xC000 <= i < 0xE000:  # 8kB Internal RAM
            self.ram.internalRAM0[i - 0xC000] = value
        elif 0xE000 <= i < 0xFE00:  # Echo of 8kB Internal RAM
            # Redirect to internal RAM
            self[i - 0x2000] = value
        elif 0xFE00 <= i < 0xFEA0:  # Sprite Attrib Memory (OAM)
            self.lcd.OAM[i - 0xFE00] = value
        elif 0xFEA0 <= i < 0xFF00:  # Empty but unusable for I/O
            self.ram.nonIOInternalRAM0[i - 0xFEA0] = value
        elif 0xFF00 <= i < 0xFF4C:  # I/O ports
            if i == 0xFF00:
                self.ram.IOPorts[i - 0xFF00] = self.interaction.pull(value)
            elif i == 0xFF04:
                self.timer.DIV = 0
            elif i == 0xFF05:
                self.timer.TIMA = value
            elif i == 0xFF06:
                self.timer.TMA = value
            elif i == 0xFF07:
                self.timer.TAC = value & 0b11
            elif i == 0xFF40:
                self.lcd.LCDC.set(value)
            elif i == 0xFF46:
                self.transferDMAtoOAM(value)
            elif i == 0xFF47:
                self.lcd.BGP.set(value)
            elif i == 0xFF48:
                self.lcd.OBP0.set(value)
            elif i == 0xFF49:
                self.lcd.OBP1.set(value)
            else:
                self.ram.IOPorts[i - 0xFF00] = value
        elif 0xFF4C <= i < 0xFF80:  # Empty but unusable for I/O
            if self.bootROMEnabled and i == 0xFF50 and value == 1:
                self.bootROMEnabled = False
            self.ram.nonIOInternalRAM1[i - 0xFF4C] = value
        elif 0xFF80 <= i < 0xFFFF:  # Internal RAM
            self.ram.internalRAM1[i-0xFF80] = value
        elif i == 0xFFFF:  # Interrupt Enable Register
            self.ram.interruptRegister[0] = value
        else:
            raise Exception("Memory access violation. Tried to write: %s" % hex(i))

    def transferDMAtoOAM(self,src,dst=0xFE00):
        # http://problemkaputt.de/pandocs.htm#lcdoamdmatransfers
        # TODO: Add timing delay of 160µs and disallow access to RAM!
        offset = src * 0x100
        for n in xrange(0x00,0xA0):
            self.__setitem__(dst + n, self.__getitem__(n + offset))






    ##########################
    # Statemanager
    def saveState(self, filename):
        logger.info("Saving state...")
        with open(filename, "wb") as f:
            for n in [self.cpu.AF, self.cpu.BC, self.cpu.DE, self.cpu.HL, self.cpu.SP, self.cpu.PC]:
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
            self.cpu.oldPC = -1

            self.cpu.AF, self.cpu.BC, self.cpu.DE,\
            self.cpu.HL, self.cpu.SP, self.cpu.PC = [ord(f.read(1)) | (ord(f.read(1))<<8) for _ in xrange(6)]

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

