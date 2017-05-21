# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


def __getitem__(self, i):
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
        raise CoreDump.CoreDump("Memory access violation. Tried to read: %s" % hex(i))

def __setitem__(self,i,value):
    assert value < 0x100, "Memory write error! Can't write %s to %s" % (hex(value),hex(i))
            # CoreDump.CoreDump("Memory write error! Can't write %s to %s" % (hex(value),hex(i))),\

    if 0x0000 <= i < 0x4000:  # 16kB ROM bank #0
        self.cartridge[i] = value #Doesn't change the data. This is for MBC commands
    elif 0x4000 <= i < 0x8000:  # 16kB switchable ROM bank
        self.cartridge[i] = value #Doesn't change the data. This is for MBC commands
    elif 0x8000 <= i < 0xA000:  # 8kB Video RAM
        if i < 0x9800: # Is within tile data -- not tile maps
            self.lcd.tilesChanged.add(i & 0xFFF0) # Mask out the byte of the tile
        self.lcd.VRAM[i - 0x8000] = value
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
        raise CoreDump.CoreDump("Memory access violation. Tried to write: %s" % hex(i))

def transferDMAtoOAM(self,src,dst=0xFE00):
    # http://problemkaputt.de/pandocs.htm#lcdoamdmatransfers
    # TODO: Add timing delay of 160µs and disallow access to RAM!
    offset = src * 0x100
    for n in xrange(0x00,0xA0):
        self.__setitem__(0xFE00 + n, self.__getitem__(n + offset))

