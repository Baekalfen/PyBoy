#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import array


VIDEO_RAM = 8 * 1024 # 8KB
OBJECT_ATTRIBUTE_MEMORY = 0xA0
LCDC, STAT, SCY, SCX, LY, LYC, DMA, BGP, OBP0, OBP1, WY, WX = range(0xFF40, 0xFF4C)
ROWS, COLS = 144, 160


class LCD:
    def __init__(self, color_palette):
        self.VRAM = array.array('B', [0] * VIDEO_RAM)
        self.OAM = array.array('B', [0] * OBJECT_ATTRIBUTE_MEMORY)

        self.LCDC = LCDCRegister(0)
        # self.STAT = 0x00
        self.SCY = 0x00
        self.SCX = 0x00
        # self.LY = 0x00
        # self.LYC = 0x00
        # self.DMA = 0x00
        self.BGP = PaletteRegister(0xFC, color_palette)
        self.OBP0 = PaletteRegister(0xFF, color_palette)
        self.OBP1 = PaletteRegister(0xFF, color_palette)
        self.WY = 0x00
        self.WX = 0x00

    def save_state(self, f):
        for n in range(VIDEO_RAM):
            f.write(self.VRAM[n].to_bytes(1, 'little'))

        for n in range(OBJECT_ATTRIBUTE_MEMORY):
            f.write(self.OAM[n].to_bytes(1, 'little'))

        f.write(self.LCDC.value.to_bytes(1, 'little'))
        f.write(self.BGP.value.to_bytes(1, 'little'))
        f.write(self.OBP0.value.to_bytes(1, 'little'))
        f.write(self.OBP1.value.to_bytes(1, 'little'))

        f.write(self.SCY.to_bytes(1, 'little'))
        f.write(self.SCX.to_bytes(1, 'little'))
        f.write(self.WY.to_bytes(1, 'little'))
        f.write(self.WX.to_bytes(1, 'little'))

    def load_state(self, f):
        for n in range(VIDEO_RAM):
            self.VRAM[n] = ord(f.read(1))

        for n in range(OBJECT_ATTRIBUTE_MEMORY):
            self.OAM[n] = ord(f.read(1))

        self.LCDC.set(ord(f.read(1)))
        self.BGP.set(ord(f.read(1)))
        self.OBP0.set(ord(f.read(1)))
        self.OBP1.set(ord(f.read(1)))

        self.SCY = ord(f.read(1))
        self.SCX = ord(f.read(1))
        self.WY = ord(f.read(1))
        self.WX = ord(f.read(1))

    def getwindowpos(self):
        return (self.WX - 7, self.WY)

    def getviewport(self):
        return (self.SCX, self.SCY)


class PaletteRegister:
    def __init__(self, value, color_palette):
        self.color_palette = color_palette
        self.value = 0
        self.set(value)

    def set(self, value):
        # Pokemon Blue continously sets this without changing the value
        if self.value == value:
            return False

        self.value = value
        self.lookup = [0] * 4
        for x in range(4):
            self.lookup[x] = self.color_palette[(value >> x * 2) & 0b11]
        return True

    def getcolor(self, i):
        return self.lookup[i]


class LCDCRegister:
    def __init__(self, value):
        self.set(value)

    def set(self, value):
        self.value = value

        # No need to convert to bool. Any non-zero value is true.
        self.lcd_enable           = value & (1 << 7)
        self.windowmap_select     = value & (1 << 6)
        self.window_enable        = value & (1 << 5)
        self.tiledata_select      = value & (1 << 4)
        self.backgroundmap_select = value & (1 << 3)
        self.sprite_height        = value & (1 << 2)
        self.sprite_enable        = value & (1 << 1)
        self.background_enable    = value & (1 << 0)
