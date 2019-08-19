#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .constants import OAM_OFFSET, LCDC_OFFSET, LOW_TILEMAP
from .tile import Tile
from pyboy.lcd import LCDCRegister


class Sprite:
    def __init__(self, mb, index):
        self.mb = mb
        self.offset = index * 4

    @property
    def y(self):
        return self.mb.getitem(OAM_OFFSET + self.offset + 0)

    @property
    def x(self):
        return self.mb.getitem(OAM_OFFSET + self.offset + 1)

    @property
    def tile_index(self):
        """
        Doesn't return high/low because sprites always use low
        """
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

    def _get_lcdc_register(self):
        return LCDCRegister(self.mb.getitem(LCDC_OFFSET))

    @property
    def tiles(self):
        tile_index = self.tile_index
        LCDC = self._get_lcdc_register()
        if LCDC.sprite_height:
            return [Tile(self.mb, tile_index, False), Tile(self.mb, tile_index + 1, False)]
        else:
            return [Tile(self.mb, tile_index, False)]

    @property
    def on_screen(self):
        LCDC = self._get_lcdc_register()
        sprite_height = 16 if LCDC.sprite_height else 16
        return (0 < self.y < 144 + sprite_height and
                0 < self.x < 160 + 8)

def get_bit(val, bit):
    # return (val & (1 << bit)) >> bit
    return (val >> bit) & 1
