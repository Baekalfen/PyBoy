#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""
The Game Boy has two tile maps, which defines what is rendered on the screen.
"""

from pyboy.lcd import LCDCRegister

from .constants import HIGH_TILEMAP, LCDC_OFFSET, LOW_TILEDATA_LENGTH, LOW_TILEMAP
from .tile import Tile


class TileMap:
    def __init__(self, mb, window=False):
        """
        The Game Boy has two tile maps, which defines what is rendered on the screen. These are also referred to as
        "background" and "window".

        This object defines `__getitem__`, which means it can be accessed with the square brackets to get a tile
        identifier at a given coordinate.

        Example:
        ```
        >>> tilemap = pyboy.get_window_tile_map()
        >>> tile = tilemap[10,10]
        >>> print(tile)
        34
        >>> print(tile_map[0:10,10])
        [43, 54, 23, 23, 23, 54, 12, 54, 54, 23]
        >>> print(tile_map[0:10,0:4])
        [[43, 54, 23, 23, 23, 54, 12, 54, 54, 23],
         [43, 54, 43, 23, 23, 43, 12, 39, 54, 23],
         [43, 54, 23, 12, 87, 54, 12, 54, 21, 23],
         [43, 54, 23, 43, 23, 87, 12, 50, 54, 72]]
        ```
        """
        self.mb = mb

        LCDC = self._get_lcdc_register()

        if window:
            self.map_offset = HIGH_TILEMAP if LCDC.windowmap_select else LOW_TILEMAP
        else:
            self.map_offset = HIGH_TILEMAP if LCDC.backgroundmap_select else LOW_TILEMAP

        self.signed_tile_data = not bool(LCDC.tiledata_select)
        self._use_tile_objects = False

    def _get_lcdc_register(self):
        return LCDCRegister(self.mb.getitem(LCDC_OFFSET))

    @property
    def signed_tile_index(self):
        """
        The Game Boy uses both signed and unsigned tile indexes. Use this attribute to identify which is used. Read
        more about it in [Pan Docs: VRAM Tile Data](http://bgb.bircd.org/pandocs.htm#vramtiledata).

        Returns:
            bool: Whether this tile map uses signed tile indexes.
        """
        return self.signed_tile_data

    def get_tile_address(self, x, y):
        """
        Returns the memory address in the tilemap for the tile at the given coordinate. The address contains the index
        of tile which will be shown at this position. This should not be confused with the actual tile data of
        `pyboy.botsupport.tile.Tile.data_address`.

        This can be used as an global identifier for the specific location in a tile map.

        Be aware, that the tile index referenced at the memory address might change between calls to
        `pyboy.pyboy.PyBoy.tick`. And the tile data for the same tile index might also change to display something else
        on the screen.

        The index might also be a signed number. Depending on if it is signed or not, will change where the tile data
        is read from. Use `pyboy.botsupport.tilemap.TileMap.signed_tile_index` to test if the indexes are signed for
        this tile view. You can read how the indexes work in the
        [Pan Docs: VRAM Tile Data](http://bgb.bircd.org/pandocs.htm#vramtiledata).

        Args:
            x (int): X-coordinate in this tile map.
            y (int): Y-coordinate in this tile map.

        Returns:
            int: Address in the tile map to read a tile index.
        """

        if not 0 <= x < 32:
            raise IndexError("x is out of bounds. Value of 0 to 31 is allowed")
        if not 0 <= y < 32:
            raise IndexError("y is out of bounds. Value of 0 to 31 is allowed")
        return self.map_offset + 32*y + x

    def get_tile(self, x, y):
        """
        Provides a `pyboy.botsupport.tile.Tile`-object which allows for easy interpretation of the tile data. The
        object is agnostic to where it was found in the tilemap. I.e. equal `pyboy.botsupport.tile.Tile`-objects might
        be returned from two different coordinates in the tile map.

        Args:
            x (int): X-coordinate in this tile map.
            y (int): Y-coordinate in this tile map.

        Returns:
            `pyboy.botsupport.tile.Tile`: Tile object corresponding to the tile index at the given coordinate in the
            tile map.
        """
        return Tile(self.mb, index=(self.get_tile_index(x, y)[1], self.signed_tile_data))

    def get_tile_identifier(self, x, y):
        """
        Returns an identifier of the tile at the given coordinate in the tile map. The identifier can be used to
        quickly recognize what is on the screen through this tile view.

        This identifier unifies the otherwise complicated indexing system on the Game Boy into a single range of
        0-383 (both included).

        Use this instead of `pyboy.botsupport.tilemap.TileMap.get_tile_index`, if you want a simple way to identify
        tiles without researching the quirks of tile indexes used in the Game Boy.

        Returns:
            int: Tile identifier.
        """

        tile = self.mb.getitem(self.get_tile_address(x, y))
        if self.signed_tile_data:
            return ((tile ^ 0x80) - 128) + LOW_TILEDATA_LENGTH
        else:
            return tile

    def get_tile_index(self, x, y):
        """
        Returns the index of the tile at the given coordinate in the tile map.

        Consider using `pyboy.botsupport.tilemap.TileMap.get_tile_identifier` if you want a simple way to identify
        tiles in the tile map.

        You can read how the indexes work in the
        [Pan Docs: VRAM Tile Data](http://bgb.bircd.org/pandocs.htm#vramtiledata).

        Returns:
            tuple (bool, int): First value indicates if the index is signed. The second value is the index. Both are
                needed for comparison.
        """

        tile = self.mb.getitem(self.get_tile_address(x, y))
        if self.signed_tile_data:
            return (self.signed_tile_data, (tile ^ 0x80) - 128)
        else:
            return (self.signed_tile_data, tile)

    def get_tile_matrix(self):
        """
        Returns a matrix of 32x32 of the given tile map. Each element in the matrix, is the tile identifier to be shown
        on screen for each position.

        The identifier can be used to quickly identify what is on the screen through this tile view.

        You can read how the indexes work in the
        [Pan Docs: VRAM Tile Data](http://bgb.bircd.org/pandocs.htm#vramtiledata).

        Returns:
            list: Nested list creating a 32x32 matrix of tile identifiers.
        """
        return self[:, :]

    def __str__(self):
        adjust = 4
        _use_tile_objects = self._use_tile_objects
        self.use_tile_objects(False)
        return_data = (
                f"Tile Map Address: {self.map_offset:#0{6}x}, " +
                f"Signed Tile Data: {'Yes' if self.signed_tile_data else 'No'}\n" +
                " "*5 + "".join([f"{i: <4}" for i in range(32)]) + "\n" +
                "_"*(adjust*32+2) + "\n" +
                "\n".join(
                    [
                        f"{i: <3}| " + "".join([str(tile).ljust(adjust) for tile in line])
                        for i, line in enumerate(self.get_tile_matrix())
                    ]
                )
            )
        self.use_tile_objects(_use_tile_objects)
        return return_data

    def use_tile_objects(self, switch):
        """
        Used to change which object is returned when using the ``__getitem__`` method (i.e. `tilemap[0,0]`).

        Args:
            switch (bool): If True, accesses will return `pyboy.botsupport.tile.Tile`-object. If False, accesses will
                return an `int`.
        """
        self._use_tile_objects = switch

    def __getitem__(self, xy):
        x, y = xy

        if x == slice(None):
            x = slice(0, 32, 1)

        if y == slice(None):
            y = slice(0, 32, 1)

        x_slice = isinstance(x, slice) # Assume slice, otherwise int
        y_slice = isinstance(y, slice) # Assume slice, otherwise int
        assert x_slice or isinstance(x, int)
        assert y_slice or isinstance(y, int)

        if self._use_tile_objects:
            tile_fun = self.get_tile
        else:
            tile_fun = lambda x, y: self.get_tile_identifier(x, y)

        if x_slice and y_slice:
            return [[tile_fun(_x, _y) for _x in range(x.stop)[x]] for _y in range(y.stop)[y]]
        elif x_slice:
            return [tile_fun(_x, y) for _x in range(x.stop)[x]]
        elif y_slice:
            return [tile_fun(x, _y) for _y in range(y.stop)[y]]
        else:
            return tile_fun(x, y)
