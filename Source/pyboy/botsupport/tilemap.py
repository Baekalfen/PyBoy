#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .tile import Tile

VRAM_OFFSET = 0x8000


class TileView:
    def __init__(self, lcd, high_tile_data=False):
        self.lcd = lcd
        self.view_offset = 0x1C00 if high_tile_data else 0x1800
        self.high_tile_data = high_tile_data

    def get_tile(self, x, y):
        """
        Returns the tile-index of the tile at the given coordinate in the tile map.
        """

        assert 0 <= x < 32
        assert 0 <= y < 32

        if self.high_tile_data:
            return Tile(self.lcd.VRAM(self.view_offset + ((32*y + x) ^ 0x80) - 128))
        else:
            return Tile(self.lcd.VRAM(self.view_offset + 32*y + x))


    # Get only the tiles within the current display view
    # def get_view(self):
    #     pass
