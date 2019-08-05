#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

class Tile:
    def __init__(self, lcd, index):
        self.lcd = lcd
        self._index = index

    @property
    def address(self):
        return 0

    @property
    def index(self):
        return self._index

    @property
    def image_data(self):
        return ...

    def show(self):
        # Use imgcat or PIL to show the tile.
        pass

    def __str__(self):
        return f"Tile: {self.address:#0{6}x}"

