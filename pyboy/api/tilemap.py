#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
"""
The Game Boy has two tile maps, which defines what is rendered on the screen.
"""

import numpy as np

from pyboy.core.lcd import LCDCRegister

from .constants import HIGH_TILEMAP, LCDC_OFFSET, LOW_TILEDATA_NTILES, LOW_TILEMAP
from .tile import Tile


class TileMap:
    def __init__(self, pyboy, mb, select):
        """
        The Game Boy has two tile maps, which defines what is rendered on the screen. These are also referred to as
        "background" and "window".

        Use `pyboy.tilemap_background` and
        `pyboy.tilemap_window` to instantiate this object.

        This object defines `__getitem__`, which means it can be accessed with the square brackets to get a tile
        identifier at a given coordinate.

        Example:
        ```
        >>> pyboy.tilemap_window[8,8]
        1
        >>> pyboy.tilemap_window[7:12,8]
        [0, 1, 0, 1, 0]
        >>> pyboy.tilemap_window[7:12,8:11]
        [[0, 1, 0, 1, 0], [0, 2, 3, 4, 5], [0, 0, 6, 0, 0]]

        ```

        Each element in the matrix, is the tile identifier of the tile to be shown on screen for each position. If you
        need the entire 32x32 tile map, you can use the shortcut: `tilemap[:,:]`.
        """
        self.pyboy = pyboy
        self.mb = mb
        self._select = select
        self._use_tile_objects = False
        self.frame_count_update = 0
        self.__refresh_lcdc()

        self.shape = (32, 32)
        """
        Tile maps are always 32x32 tiles.

        Returns
        -------
        (int, int):
            The width and height of the tile map.
        """

    def _refresh_lcdc(self):
        if self.frame_count_update == self.pyboy.frame_count:
            return 0
        self.__refresh_lcdc()

    def __refresh_lcdc(self):
        """
        The tile data and view that is showed on the background and window respectively can change dynamically. If you
        believe it has changed, you can use this method to update the tilemap from the LCDC register.
        """
        LCDC = LCDCRegister(self.mb.getitem(LCDC_OFFSET))
        if self._select == "WINDOW":
            self.map_offset = HIGH_TILEMAP if LCDC.windowmap_select else LOW_TILEMAP
            self.signed_tile_data = not bool(LCDC.tiledata_select)
        elif self._select == "BACKGROUND":
            self.map_offset = HIGH_TILEMAP if LCDC.backgroundmap_select else LOW_TILEMAP
            self.signed_tile_data = not bool(LCDC.tiledata_select)
        else:
            raise KeyError(f"Invalid tilemap selected: {self._select}")

    def search_for_identifiers(self, identifiers):
        """
        Provided a list of tile identifiers, this function will find all occurrences of these in the tilemap and return
        the coordinates where each identifier is found.

        Example:
        ```
        >>> pyboy.tilemap_window.search_for_identifiers([5,3])
        [[[9, 11]], [[9, 9], [9, 12]]]

        ```

        Meaning, that tile identifier `43` is found at the positions: (0,0), (2,4), and (8,7), while tile identifier
        `123`was not found anywhere.

        Args:
            identifiers (list): List of tile identifiers (int)

        Returns
        -------
        list:
            list of matches for every tile identifier in the input
        """
        # TODO: Crude implementation
        tilemap_identifiers = np.asarray(self[:, :], dtype=np.uint32)
        matches = []
        for i in identifiers:
            matches.append([[int(y) for y in x] for x in np.argwhere(tilemap_identifiers == i)])
        return matches

    def _tile_address(self, column, row):
        """
        Returns the memory address in the tilemap for the tile at the given coordinate. The address contains the index
        of tile which will be shown at this position. This should not be confused with the actual tile data of
        `pyboy.api.tile.Tile.data_address`.

        This can be used as an global identifier for the specific location in a tile map.

        Be aware, that the tile index referenced at the memory address might change between calls to
        `pyboy.PyBoy.tick`. And the tile data for the same tile index might also change to display something else
        on the screen.

        The index might also be a signed number. Depending on if it is signed or not, will change where the tile data
        is read from. Use `pyboy.api.tilemap.TileMap.signed_tile_index` to test if the indexes are signed for
        this tile view. You can read how the indexes work in the
        [Pan Docs: VRAM Tile Data](https://gbdev.io/pandocs/Tile_Data.html).

        Args:
            column (int): Column in this tile map.
            row (int): Row in this tile map.

        Returns
        -------
        int:
            Address in the tile map to read a tile index.
        """
        if not 0 <= column < 32:
            raise IndexError("column is out of bounds. Value of 0 to 31 is allowed")
        if not 0 <= row < 32:
            raise IndexError("row is out of bounds. Value of 0 to 31 is allowed")
        return self.map_offset + 32 * row + column

    def tile(self, column, row):
        """
        Provides a `pyboy.api.tile.Tile`-object which allows for easy interpretation of the tile data. The
        object is agnostic to where it was found in the tilemap. I.e. equal `pyboy.api.tile.Tile`-objects might
        be returned from two different coordinates in the tile map if they are shown different places on the screen.

        Args:
            column (int): Column in this tile map.
            row (int): Row in this tile map.

        Returns
        -------
        `pyboy.api.tile.Tile`:
            Tile object corresponding to the tile index at the given coordinate in the
            tile map.
        """
        return Tile(self.mb, self.tile_identifier(column, row))

    def tile_identifier(self, column, row):
        """
        Returns an identifier (integer) of the tile at the given coordinate in the tile map. The identifier can be used
        to quickly recognize what is on the screen through this tile view.

        This identifier unifies the otherwise complicated indexing system on the Game Boy into a single range of
        0-383 (both included).

        You can read how the indexes work in the
        [Pan Docs: VRAM Tile Data](https://gbdev.io/pandocs/Tile_Data.html).

        Args:
            column (int): Column in this tile map.
            row (int): Row in this tile map.

        Returns
        -------
        int:
            Tile identifier.
        """
        self._refresh_lcdc()
        tile = self.mb.getitem(self._tile_address(column, row))
        if self.signed_tile_data:
            return ((tile ^ 0x80) - 128) + LOW_TILEDATA_NTILES
        else:
            return tile

    def __repr__(self):
        self._refresh_lcdc()
        adjust = 4
        _use_tile_objects = self._use_tile_objects
        self.use_tile_objects(False)

        return_data = (
            f"Tile Map Address: {self.map_offset:#0{6}x}, "
            + f"Signed Tile Data: {'Yes' if self.signed_tile_data else 'No'}\n"
            + " " * 5
            + "".join([f"{i: <4}" for i in range(32)])
            + "\n"
            + "_" * (adjust * 32 + 2)
            + "\n"
            + "\n".join(
                [
                    f"{i: <3}| " + "".join([str(tile).ljust(adjust) for tile in line])
                    for i, line in enumerate(self[:, :])
                ]
            )
        )
        self.use_tile_objects(_use_tile_objects)
        return return_data

    def use_tile_objects(self, switch):
        """
        Used to change which object is returned when using the ``__getitem__`` method (i.e. `tilemap[0,0]`).

        Args:
            switch (bool): If True, accesses will return `pyboy.api.tile.Tile`-object. If False, accesses will
                return an `int`.
        """
        self._use_tile_objects = switch

    def _fix_slice(self, addr):
        if addr.step is None:
            step = 1
        else:
            step = addr.step

        if addr.start is None:
            start = 0
        else:
            start = addr.start

        if addr.stop is None:
            stop = 32
        else:
            stop = addr.stop

        if step < 0:
            raise ValueError("Reversed ranges are unsupported")
        elif start > stop:
            raise ValueError("Invalid range")
        return start, stop, step

    def __getitem__(self, xy):
        if isinstance(xy, (int, slice)):
            x = xy
            y = slice(None)
        else:
            x, y = xy

        x_slice = isinstance(x, slice)
        y_slice = isinstance(y, slice)
        if x_slice:
            x = self._fix_slice(x)
        else:
            assert isinstance(x, int)

        if y_slice:
            y = self._fix_slice(y)
        else:
            assert isinstance(y, int)

        if self._use_tile_objects:
            tile_fun = self.tile
        else:
            tile_fun = lambda x, y: self.tile_identifier(x, y)

        if x_slice and y_slice:
            return [[tile_fun(_x, _y) for _x in range(*x)] for _y in range(*y)]
        elif x_slice:
            return [tile_fun(_x, y) for _x in range(*x)]
        elif y_slice:
            return [tile_fun(x, _y) for _y in range(*y)]
        else:
            return tile_fun(x, y)
