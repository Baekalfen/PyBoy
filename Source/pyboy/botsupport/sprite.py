#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .tile import Tile
from pyboy.lcd import LCDCRegister

OAM_OFFSET = 0x8000
LCDC_OFFSET = 0xFF40


class Sprite:
    def __init__(self, lcd, index):
        self.lcd = lcd
        # self.index = index
        self.mem_index = index * 4

        # We save it, to keep contistency
        self.sprite_height = self.lcd.LCDC.sprite_height

    # Legacy support -- use properties
    def get_y(self):
        return self.lcd.OAM(self.mem_index + 0)

    # Legacy support -- use properties
    def get_x(self):
        return self.lcd.OAM(self.mem_index + 1)

    # Legacy support -- use properties
    def get_tile(self):
        return self.tile_index()

    @property
    def tile_index(self):
        return self.lcd.OAM(self.mem_index + 2)

    # Legacy support -- use properties
    def get_attributes(self):
        attr = self.lcd.OAM(self.mem_index + 3)
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

    def is_on_screen(self):
        sprite_height = 16 if self.lcd.LCDC.sprite_height else 16
        return (0 < self.y < 144 + sprite_height and
                0 < self.x < 160 + 8)

    @property
    def tiles(self):
        tile_index = self.get_tile()
        if self.sprite_height:
            return [Tile(self.lcd, tile_index), Tile(self.lcd, tile_index + 1)]
        else:
            return [Tile(self.lcd, tile_index)]

    x = property(get_x)
    y = property(get_y)
    attributes = property(get_attributes)

def get_bit(val, bit):
    # return (val & (1 << bit)) >> bit
    return (val >> bit) & 1
