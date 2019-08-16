#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .tile import Tile

VRAM_OFFSET = 0x8000


class TileMap:
    def __init__(self, mb, high_tile_data=False):
        self.mb = mb
        self.map_offset = 0x1C00 if high_tile_data else 0x1800
        self.high_tile_data = high_tile_data

    def get_tile(self, x, y):
        """
        Returns the tile-index of the tile at the given coordinate in the tile map.
        """

        assert 0 <= x < 32
        assert 0 <= y < 32

        tile = self.mb.getitem(VRAM_OFFSET + self.map_offset + 32*y + x)
        if self.high_tile_data:
            return (tile ^ 0x80) - 128
        else:
            return tile
            # return Tile(self.lcd.VRAM(self.map_offset + ((32*y + x) ^ 0x80) - 128))
        # else:
            # return Tile(self.lcd.VRAM(self.map_offset + 32*y + x))

    # Get only the tiles within the current display map
    # def get_tile_matrix_map(self):
    #     pass

    def get_tile_matrix(self):
        return self[:,:]

    def __str__(self):
        adjust = 4
        return (
                " "*5 + "".join([f"{i: <4}" for i in range(32)]) + "\n" +
                "_"*(adjust*32+2) + "\n" +
                "\n".join([f"{i: <3}| " + "".join([str(tile).ljust(adjust) for tile in line]) for i,line in enumerate(self.get_tile_matrix())])
            )

    def __getitem__(self, xy):
        x, y = xy

        if x == slice(None):
            x = slice(0,32,1)

        if y == slice(None):
            y = slice(0,32,1)

        x_slice = isinstance(x, slice) # Assume slice, otherwise int
        y_slice = isinstance(y, slice) # Assume slice, otherwise int

        if x_slice and y_slice:
            return [[self.get_tile(_x, _y) for _x in range(x.stop)[x]] for _y in range(y.stop)[y]]
        elif x_slice:
            return [self.get_tile(_x, y) for _x in range(x.stop)[x]]
        elif y_slice:
            return [self.get_tile(x, _y) for _y in range(y.stop)[y]]
        else:
            return self.get_tile(x, y)

