#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import array


VIDEO_RAM = 8 * 1024  # 8KB
OBJECT_ATTRIBUTE_MEMORY = 0xA0

LCDC, STAT, SCY, SCX, LY, LYC, DMA, BGP, OBP0, OBP1, WY, WX = range(0xFF40, 0xFF4C)

# LCDC bit descriptions
(BACKGROUND_ENABLE, SPRITE_ENABLE, SPRITE_SIZE, BACKGROUNDMAP_SELECT,
 TILEDATA_SELELECT, WINDOW_ENABLE, WINDOWMAP_SELECT, LCD_ENABLE) = range(8)

# STAT bit descriptions
# MODEFLAG0, MODEFLAG1, COINCIDENCE, MODE00, MODE01, MODE10, LYC_LY = range(7)

ROWS, COLS = 144, 160


class LCD():
    def __init__(self, colorPalette):
        self.VRAM = array.array('B', [0]*VIDEO_RAM)
        self.OAM = array.array('B', [0]*OBJECT_ATTRIBUTE_MEMORY)

        self.LCDC = LCDCRegister(0)
        # self.STAT = 0x00
        self.SCY = 0x00
        self.SCX = 0x00
        # self.LY = 0x00
        # self.LYC = 0x00
        # self.DMA = 0x00
        self.BGP = PaletteRegister(0xFC, colorPalette)
        self.OBP0 = PaletteRegister(0xFF, colorPalette)
        self.OBP1 = PaletteRegister(0xFF, colorPalette)
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

    def get_windowpos(self):
        return (self.WX-7, self.WY)

    def get_viewport(self):
        return (self.SCX, self.SCY)


class PaletteRegister():
    def __init__(self, value, colorpalette):
        self.colorpalette = colorpalette
        self.value = 0
        self.set(value)

    def set(self, value):
        # Pokemon Blue continously sets this without changing the value
        if self.value == value:
            return False

        self.value = value
        self.lookup = [0] * 4
        for x in range(4):
            self.lookup[x] = self.colorpalette[(value >> x*2) & 0b11]
        return True

    def get_color(self, i):
        return self.lookup[i]


class LCDCRegister():
    def __init__(self, value):
        self.set(value)

    def set(self, value):
        self.value = value

        # No need to convert to bool. Any non-zero value is true.
        self.lcd_enable = value & (1 << 7)
        self.windowmap_select = value & (1 << 6)
        self.window_enable = value & (1 << 5)
        self.tiledata_select = value & (1 << 4)
        self.backgroundmap_select = value & (1 << 3)
        self.sprite_size = value & (1 << 2)
        self.sprite_enable = value & (1 << 1)
        self.background_enable = value & (1 << 0)
