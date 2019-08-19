#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .tile import Tile
from .constants import HIGH_TILEMAP, LOW_TILEMAP, LCDC_OFFSET
from pyboy.lcd import LCDCRegister


class TileMap:
    def __init__(self, mb, window=False):
        """
        The Game Boy has two tile maps, which defines what is rendered on the screen. These are also referred to as "background" and "window".

        """
        self.mb = mb

        LCDC = self._get_lcdc_register()

        if window:
            self.map_offset = HIGH_TILEMAP if LCDC.windowmap_select else LOW_TILEMAP
        else:
            self.map_offset = HIGH_TILEMAP if LCDC.backgroundmap_select else LOW_TILEMAP

        self.high_tile_data = bool(LCDC.tiledata_select)
        # self.map_offset = HIGH_TILEMAP if self.high_tile_data else LOW_TILEMAP
        self._use_tile_objects = False

    def _get_lcdc_register(self):
        return LCDCRegister(self.mb.getitem(LCDC_OFFSET))

    def get_tile_address(self, x, y):
        """
        Returns the memory address for a tile at the given coordinate in the tile map.

        This can be used as an global identifier for the specific location of a tile in a tile map.

        Be aware, that the tile referenced at the memory address might change to display something else on the screen.
        """

        if not 0 <= x < 32:
            raise IndexError("x is out of bounds. Value of 0 to 31 is allowed")
        if not 0 <= y < 32:
            raise IndexError("y is out of bounds. Value of 0 to 31 is allowed")
        return self.map_offset + 32*y + x

    def get_tile(self, x, y):
        """
        Returns a `pyboy.botsupport.Tile` object of the tile at the given coordinate in the tile map.
        """
        return Tile(self.mb, self.get_tile_index(x,y)[1], self.high_tile_data)

    def get_tile_index(self, x, y):
        """
        Returns the index of the tile at the given coordinate in the tile map.

        This can be used to identify tiles
        """

        tile = self.mb.getitem(self.get_tile_address(x,y))
        if self.high_tile_data:
            return (self.high_tile_data, (tile ^ 0x80) - 128)
        else:
            return (self.high_tile_data, tile)

    def get_tile_matrix(self):
        """
        Returns a matrix of 32x32 of the given tile map. Each element in the matrix, is an object of `pyboy.botsupport.Tile`.
        """
        return self[:,:]

    def __str__(self):
        adjust = 4
        return (
                f"Tile Map Address: {self.map_offset:#0{6}x}, High Tile Data: {'Yes' if self.high_tile_data else 'No'}" +
                " "*5 + "".join([f"{i: <4}" for i in range(32)]) + "\n" +
                "_"*(adjust*32+2) + "\n" +
                "\n".join([f"{i: <3}| " + "".join([str(tile.index).ljust(adjust) for tile in line]) for i,line in enumerate(self.get_tile_matrix())])
            )

    def use_tile_objects(self, v):
        self._use_tile_objects = v

    def __getitem__(self, xy):
        x, y = xy

        if x == slice(None):
            x = slice(0,32,1)

        if y == slice(None):
            y = slice(0,32,1)

        x_slice = isinstance(x, slice) # Assume slice, otherwise int
        y_slice = isinstance(y, slice) # Assume slice, otherwise int
        assert x_slice or isinstance(x, int)
        assert y_slice or isinstance(y, int)

        if self._use_tile_objects:
            tile_fun = self.get_tile
        else:
            tile_fun = lambda x,y: self.get_tile_index(x,y)[1]

        if x_slice and y_slice:
            return [[tile_fun(_x, _y) for _x in range(x.stop)[x]] for _y in range(y.stop)[y]]
        elif x_slice:
            return [tile_fun(_x, y) for _x in range(x.stop)[x]]
        elif y_slice:
            return [tile_fun(x, _y) for _y in range(y.stop)[y]]
        else:
            return tile_fun(x, y)

