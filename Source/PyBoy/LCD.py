# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from . import CoreDump
from .RAM import allocateRAM, VIDEO_RAM, OBJECT_ATTRIBUTE_MEMORY


LCDC, STAT, SCY, SCX, LY, LYC, DMA, BGPalette, OBP0, OBP1, WY, WX = range(0xFF40, 0xFF4C)

# STAT bit descriptions
# ModeFlag0, ModeFlag1, Coincidence, Mode00, Mode01, Mode10, LYC_LY = range(7)

class LCD():
    def __init__(self, MB, color_palette):
        self.mb = MB
        self.color_palette = color_palette

        self.VRAM = allocateRAM(VIDEO_RAM)
        self.OAM = allocateRAM(OBJECT_ATTRIBUTE_MEMORY)
        self.LCDC = LCDCRegister(0)
        self.BGP = PaletteRegister(0xFC, color_palette)
        self.OBP0 = PaletteRegister(0xFF, color_palette)
        self.OBP1 = PaletteRegister(0xFF, color_palette)
        # self.STAT = 0x00
        # self.SCY = 0x00
        # self.SCX = 0x00
        # self.LY = 0x00
        # self.LYC = 0x00
        # self.DMA = 0x00
        # self.WY = 0x00
        # self.WX = 0x00

    def get_window_pos(self):
        return self.mb[WX]-7, self.mb[WY]

    def get_view_port(self):
        return self.mb[SCX], self.mb[SCY]


class PaletteRegister():
    def __init__(self, value, color_palette):
        self.value = None
        self.set(value)
        self.color_palette = color_palette

    def set(self, value):
        if self.value == value: # Pokemon Blue continously sets this without changing the value
            return False

        self.value = value
        self.lookup = [(value >> x) & 0b11 for x in xrange(0,8,2)]
        return True

    def get_color(self, i):
        return self.color_palette[self.lookup[i]]

    def get_code(self, i):
        return self.lookup[i]

class LCDCRegister():
    def __init__(self, value):
        self.set(value)

    def set(self, value):
        self.value = value

        # No need to convert to bool. Any non-zero value is evaluated as True
        self.enabled             = value & (1 << 7)
        self.window_map_select     = value & (1 << 6)
        self.window_enabled       = value & (1 << 5)
        self.tile_select          = value & (1 << 4)
        self.background_map_select = value & (1 << 3)
        self.sprite_size          = value & (1 << 2)
        self.sprite_enable        = value & (1 << 1)
        self.background_enable    = value & (1 << 0)

