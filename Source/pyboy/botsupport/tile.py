#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import numpy as np
from PIL import Image
from .constants import HIGH_TILEDATA, LOW_TILEDATA, VRAM_OFFSET

# TODO: Import from window_sdl2
def getcolorcode(byte1, byte2, offset):
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
    def __init__(self, mb, index, high):
        """
        The data of tile is static, apart from the image data, which is loaded from the Game Boy's memory when needed. Be aware, that the graphics for this tile can change between each call to `pyboy.PyBoy.tick`.
        """

        self.mb = mb
        self.high_tile_data = high
        self._index = index
        offset = LOW_TILEDATA if high else HIGH_TILEDATA # It's supposed to be negated
        self._data_address = offset + (16*index) # _OFFSET + self._index * 2

    def get_data_address(self):
        return self._data_address
    data_address = property(get_data_address)

    def get_index(self):
        return (self.high_tile_data, self._index)
    index = property(get_index)

    def image(self):
        return Image.frombytes('RGBA', (8,8), bytes(self.image_data()))

    def image_ndarray(self):
        return np.asarray(self.image_data())

    def image_data(self):
        data = np.zeros((8,8), dtype=np.uint32)

        for k in range(0, 16, 2): # 2 bytes for each line
            byte1 = self.mb.lcd.VRAM[self._data_address + k - VRAM_OFFSET]
            byte2 = self.mb.lcd.VRAM[self._data_address + k + 1 - VRAM_OFFSET]

            for x in range(8):
                colorcode = getcolorcode(byte1, byte2, 7-x)
                data[k//2][x] = self.mb.lcd.BGP.getcolor(colorcode)

        return data

    def highlight(self):
        # Highlight in debug window
        pass

    def __str__(self):
        high_low = 'H' if self.high_tile_data else 'L'
        return f"{high_low}{self.index}"

