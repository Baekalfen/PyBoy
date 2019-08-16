#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .tile import Tile
from pyboy.lcd import LCDCRegister

OAM_OFFSET = 0x8000
LCDC_OFFSET = 0xFF40


class Sprite:
    def __init__(self, mb, index):
        self.mb = mb
        # self.index = index
        self.offset = index * 4

    @property
    def y(self):
        return self.mb.getitem(OAM_OFFSET + self.offset + 0)

    @property
    def x(self):
        return self.mb.getitem(OAM_OFFSET + self.offset + 1)

    @property
    def tile(self):
        return self.mb.getitem(OAM_OFFSET + self.offset + 2)

    @property
    def attributes(self):
        attr = self.mb.getitem(OAM_OFFSET + self.offset + 3)
        return {
            "OBJ-to-BG Priority": get_bit(attr, 7),
            "Y flip": get_bit(attr, 6),
            "X flip": get_bit(attr, 5),
            # non-CGB only
            "Palette number": get_bit(attr, 4),
            # CGB only
            # "Tile VRAM-bank": get_bit(attr, 3),
            # "Palette number": val & 0b11,
        }

    @property
    def tiles(self):
        tile_index = self.get_tile()
        if self.sprite_height:
            return [Tile(self.mb.lcd, tile_index), Tile(self.mb.lcd, tile_index + 1)]
        else:
            return [Tile(self.mb.lcd, tile_index)]

    @property
    def on_screen(self):
        LCDC_mem = self.mb.getitem(LCDC_OFFSET)
        LCDC = LCDCRegister(LCDC_mem)
        sprite_height = 16 if LCDC.sprite_height else 16
        return (0 < self.y < 144 + sprite_height and
                0 < self.x < 160 + 8)

def get_bit(val, bit):
    # return (val & (1 << bit)) >> bit
    return (val >> bit) & 1
