#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

VRAM_OFFSET = 0x8000


class TileView:
    def __init__(self, mb, high_tile_data=False):
        self.mb = mb
        self.view_offset = 0x1C00 if high_tile_data else 0x1800
        self.high_tile_data = high_tile_data

    def get_tile(self, x, y):
        assert 0 <= x < 32
        assert 0 <= y < 32

        if self.high_tile_data:
            return self.mb.getitem(VRAM_OFFSET + self.view_offset + ((32*y + x) ^ 0x80) - 128)
        else:
            return self.mb.getitem(VRAM_OFFSET + self.view_offset + 32*y + x)
