#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""
The Game Boy uses tiles as the building block for all graphics on the screen. This base-class is used both for
`pyboy.botsupport.sprite.Sprite` and `pyboy.botsupport.tilemap.TileMap`, when refering to graphics.
"""

import numpy as np
from PIL import Image

from .constants import LOW_TILEDATA, LOW_TILEDATA_LENGTH, VRAM_OFFSET


# TODO: Import from window_sdl2
def _getcolorcode(byte1, byte2, offset):
    """Convert 2 bytes into color code at a given offset.

    The colors are 2 bit and are found like this:

    Color of the first pixel is 0b10
    | Color of the second pixel is 0b01
    v v
    1 0 0 1 0 0 0 1 <- byte1
    0 1 1 1 1 1 0 0 <- byte2
    """
    return (((byte2 >> (offset)) & 0b1) << 1) + ((byte1 >> (offset)) & 0b1)


class Tile:
    def __init__(self, mb, identifier=None, index=None):
        """
        The Game Boy uses tiles as the building block for all graphics on the screen. This base-class is used for
        `pyboy.pyboy.PyBoy.get_tile`, `pyboy.botsupport.sprite.Sprite` and `pyboy.botsupport.tilemap.TileMap`, when
        refering to graphics.

        This class is not meant to be instantiated by developers reading this documentation, but it will be created
        internaly and returned by `pyboy.botsupport.sprite.Sprite.tiles` and
        `pyboy.botsupport.tilemap.TileMap.get_tile`.

        The data of this class is static, apart from the image data, which is loaded from the Game Boy's memory when
        needed. Be aware, that the graphics for the tile can change between each call to `pyboy.pyboy.PyBoy.tick`.
        """

        self.mb = mb

        if index is not None:
            assert isinstance(index, tuple), "Index parameters needs to be a tuple of (int:index, bool:signed)"
            index, signed = index
            assert isinstance(signed, bool), "signed is not instance of bool"
            if signed:
                assert -128 <= index <= 127, "index out of range"
            else:
                assert 0 <= index < LOW_TILEDATA_LENGTH, "index out of range"
            self._signed_tile_data = signed
            self._index = index
            # The offset is not HIGH_TILEDATA, as it start 128 tiles after LOW_TILEDATA. We need the middle of
            # the high tile data area -- i.e. 256 tiles of 16 bytes into LOW_TILEDATA.
            offset = LOW_TILEDATA + 16*LOW_TILEDATA_LENGTH if signed else LOW_TILEDATA
            self._data_address = offset + (16*index) # _OFFSET + self._index * 2
        elif identifier is not None:
            assert 0 <= identifier < 384, "Identifier out of range"
            self._signed_tile_data = identifier >= LOW_TILEDATA_LENGTH
            self._index = identifier
            if self._signed_tile_data:
                self._index -= LOW_TILEDATA_LENGTH
            self._data_address = LOW_TILEDATA + (16*identifier)
        else:
            raise Exception("No identifier or index specified")

    def get_identifier(self):
        """
        The Game Boy has a slightly complicated indexing system for tiles. Use this attribute instead to get a unified
        and easy way to compare and identify tiles. If you want to modify the state of the tilemap or tile data
        directly in the emulator, you'll need to look at `pyboy.botsupport.tile.Tile.get_index`.

        Returns:
            int: Unique identifier for the tile
        """
        return (self._data_address - LOW_TILEDATA) // 16
    identifier = property(get_identifier)

    def get_data_address(self):
        """
        The tile data is defined in a specific area of the Game Boy. This function returns the address of the tile data
        corresponding to the tile index. It is advised to use `pyboy.botsupport.tile.Tile.image` or one of the other
        `image`-functions if you want to view the tile.

        You can read how the data is read in the
        [Pan Docs: VRAM Tile Data](http://bgb.bircd.org/pandocs.htm#vramtiledata).

        Returns:
            int: address in VRAM where tile data starts
        """
        return self._data_address
    data_address = property(get_data_address)

    def get_index(self):
        """
        If you need to compare two tiles, consider using `pyboy.botsupport.tile.Tile.identifier` instead, or simply the
        equal operator: `tile1 == tile2`. The index returned here is mostly for use when interfacing directly with the
        Game Boy.

        Each tile of the Game Boy is referred to by an index. This function returns the tile index this object
        corresponds to. It also returns a bool which specify whether the index is signed (True) or not (False). Both
        the bool and the index are needed to correctly identify a tile.

        The signed indexes also uses another starting address than the unsigned indexes. Use the
        `pyboy.botsupport.tile.Tile.data_address` attribute if you want the address of the tile data.

        You can read how the indexes work in the
        [Pan Docs: VRAM Tile Data](http://bgb.bircd.org/pandocs.htm#vramtiledata).

        Returns:
            tuple (bool, int): First value indicates if the index is signed. The second value is the index.
            Both are needed for comparison.
        """
        return (self._signed_tile_data, self._index)
    index = property(get_index)

    def image(self):
        """
        Use this function to get an easy-to-use `PIL.Image` object of the tile. The image is 8x8 pixels in RGBA colors.

        Be aware, that the graphics for this tile can change between each call to `pyboy.pyboy.PyBoy.tick`.

        Returns:
            PIL.Image : Image of tile in 8x8 pixels and RGBA colors.
        """
        return Image.frombytes('RGBA', (8, 8), bytes(self.image_data()))

    def image_ndarray(self):
        """
        Use this function to get an easy-to-use `numpy.ndarray` object of the tile. The array has a shape of (8, 8, 4)
        and each value is of `numpy.uint8`. The values corresponds to and RGBA image of 8x8 pixels with each sub-color
        in a separate cell.

        Be aware, that the graphics for this tile can change between each call to `pyboy.pyboy.PyBoy.tick`.

        Returns:
            numpy.ndarray : Array of shape (8, 8, 4) with data type of `numpy.uint8`.
        """
        return np.asarray(self.image_data()).view(dtype=np.uint8).reshape(8, 8, 4)

    def image_data(self):
        """
        Use this function to get the raw tile data. The data is a `memoryview` corresponding to 8x8 pixels in RGBA
        colors.

        Be aware, that the graphics for this tile can change between each call to `pyboy.pyboy.PyBoy.tick`.

        Returns:
            memoryview : Image data of tile in 8x8 pixels and RGBA colors.
        """
        data = np.zeros((8, 8), dtype=np.uint32)

        for k in range(0, 16, 2): # 2 bytes for each line
            byte1 = self.mb.lcd.VRAM[self._data_address + k - VRAM_OFFSET]
            byte2 = self.mb.lcd.VRAM[self._data_address + k + 1 - VRAM_OFFSET]

            for x in range(8):
                colorcode = _getcolorcode(byte1, byte2, 7-x)
                data[k//2][x] = self.mb.lcd.BGP.getcolor(colorcode)

        return data

    # def highlight(self):
    #     """
    #     Not yet implemented. Will be used to highlight the tile when debug windows are enabled.
    #     """
    #     pass

    def __eq__(self, other):
        return self.identifier == other.identifier

    def __str__(self):
        high_low = 'H' if self._signed_tile_data else 'L'
        return f"Tile: {high_low}, {self.index}"
