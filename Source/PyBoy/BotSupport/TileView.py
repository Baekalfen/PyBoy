# -*- encoding: utf-8 -*-
#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

class TileView():
    def __init__(self, lcd, high_tile_data=False):
        self.VRAM = lcd.VRAM
        self.view_offset = 0x1C00 if high_tile_data else 0x1800
        self.high_tile_data = high_tile_data

    def get_tile(self, x, y):
        assert 0 <= x < 32
        assert 0 <= y < 32
        if self.high_tile_data:
            return (self.VRAM[self.view_offset+x+y*32] ^ 0x80) - 128
        else:
            return self.VRAM[self.view_offset+x+y*32]



