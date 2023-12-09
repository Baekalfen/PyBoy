#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
"""
The Game Boy uses tiles as the building block for all graphics on the screen. This base-class is used both for
`pyboy.api.sprite.Sprite` and `pyboy.api.tilemap.TileMap`, when refering to graphics.
"""

import numpy as np

import pyboy
from pyboy import utils

from .constants import LOW_TILEDATA, TILES, TILES_CGB, VRAM_OFFSET

logger = pyboy.logging.get_logger(__name__)

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False


class Tile:
    def __init__(self, mb, identifier):
        """
        The Game Boy uses tiles as the building block for all graphics on the screen. This base-class is used for
        `pyboy.tile`, `pyboy.api.sprite.Sprite` and `pyboy.api.tilemap.TileMap`, when refering to graphics.

        This class is not meant to be instantiated by developers reading this documentation, but it will be created
        internally and returned by `pyboy.api.sprite.Sprite.tiles` and
        `pyboy.api.tilemap.TileMap.tile`.

        The data of this class is static, apart from the image data, which is loaded from the Game Boy's memory when
        needed. Beware that the graphics for the tile can change between each call to `pyboy.PyBoy.tick`.
        """
        self.mb = mb

        if self.mb.cgb:
            assert 0 <= identifier < TILES_CGB, "Identifier out of range"
        else:
            assert 0 <= identifier < TILES, "Identifier out of range"

        self.data_address = LOW_TILEDATA + (16 * (identifier%TILES))
        """
        The tile data is defined in a specific area of the Game Boy. This function returns the address of the tile data
        corresponding to the tile identifier. It is advised to use `pyboy.api.tile.Tile.image` or one of the
        other `image`-functions if you want to view the tile.

        You can read how the data is read in the
        [Pan Docs: VRAM Tile Data](http://bgb.bircd.org/pandocs.htm#vramtiledata).

        Returns
        -------
        int:
            address in VRAM where tile data starts
        """

        if identifier < TILES:
            self.vram_bank = 0
        else:
            self.vram_bank = 1

        self.tile_identifier = identifier
        """
        The Game Boy has a slightly complicated indexing system for tiles. This identifier unifies the otherwise
        complicated indexing system on the Game Boy into a single range of 0-383 (both included) or 0-767 for Game Boy
        Color.

        Returns
        -------
        int:
            Unique identifier for the tile
        """

        self.shape = (8, 8)
        """
        Tiles are always 8x8 pixels.

        Returns
        -------
        (int, int):
            The width and height of the tile.
        """

        self.raw_buffer_format = self.mb.lcd.renderer.color_format
        """
        Returns the color format of the raw screen buffer.

        Returns
        -------
        str:
            Color format of the raw screen buffer. E.g. 'RGBX'.
        """

    def image(self):
        """
        Use this function to get an `PIL.Image` object of the tile. The image is 8x8 pixels. The format or "mode" might change at any time.

        Be aware, that the graphics for this tile can change between each call to `pyboy.PyBoy.tick`.

        Returns
        -------
        PIL.Image :
            Image of tile in 8x8 pixels and RGBA colors.
        """
        if Image is None:
            logger.error(f"{__name__}: Missing dependency \"Pillow\".")
            return None

        if cythonmode:
            return Image.fromarray(self._image_data().base, mode="RGBX")
        else:
            return Image.frombytes("RGBX", (8, 8), self._image_data())

    def image_ndarray(self):
        """
        Use this function to get an `numpy.ndarray` object of the tile. The array has a shape of (8, 8, 4)
        and each value is of `numpy.uint8`. The values corresponds to an image of 8x8 pixels with each sub-color
        in a separate cell. The format is given by `pyboy.api.tile.Tile.raw_buffer_format`.

        Be aware, that the graphics for this tile can change between each call to `pyboy.PyBoy.tick`.

        Returns
        -------
        numpy.ndarray :
            Array of shape (8, 8, 4) with data type of `numpy.uint8`.
        """
        # The data is laid out as (X, red, green, blue), where X is currently always zero, but this is not guarenteed
        # across versions of PyBoy.
        return np.asarray(self._image_data()).view(dtype=np.uint8).reshape(8, 8, 4)

    def _image_data(self):
        """
        Use this function to get the raw tile data. The data is a `memoryview` corresponding to 8x8 pixels in RGBA
        colors.

        Be aware, that the graphics for this tile can change between each call to `pyboy.PyBoy.tick`.

        Returns
        -------
        memoryview :
            Image data of tile in 8x8 pixels and RGB colors.
        """
        self.data = np.zeros((8, 8), dtype=np.uint32)
        for k in range(0, 16, 2): # 2 bytes for each line
            if self.vram_bank == 0:
                byte1 = self.mb.lcd.VRAM0[self.data_address + k - VRAM_OFFSET]
                byte2 = self.mb.lcd.VRAM0[self.data_address + k + 1 - VRAM_OFFSET]
            else:
                byte1 = self.mb.lcd.VRAM1[self.data_address + k - VRAM_OFFSET]
                byte2 = self.mb.lcd.VRAM1[self.data_address + k + 1 - VRAM_OFFSET]

            for x in range(8):
                colorcode = utils.color_code(byte1, byte2, 7 - x)
                alpha_mask = 0x00FFFFFF
                self.data[k // 2][x] = self.mb.lcd.BGP.getcolor(colorcode) & alpha_mask
        return self.data

    def __eq__(self, other):
        return self.data_address == other.data_address and self.vram_bank == other.vram_bank

    def __repr__(self):
        return f"Tile: {self.tile_identifier}"
