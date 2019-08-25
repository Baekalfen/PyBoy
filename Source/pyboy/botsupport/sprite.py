#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""
This class presents an interface to the sprites held in the OAM data on the Game Boy.
"""

from .constants import OAM_OFFSET, LCDC_OFFSET
from .tile import Tile
from pyboy.lcd import LCDCRegister

class Sprite:
    def __init__(self, mb, index):
        """
        This class presents an interface to the sprites held in the OAM data on the Game Boy.

        The purpose is to make it easier to interpret events on the screen, in order to program a bot, or train an AI.

        Sprites are used on the Game Boy for enemy and player characters, as only sprites can have transparency, and can move at pixel-precision on the screen. The other method of graphics -- tile maps -- can only be placed in a grid-size of 8x8 pixels precision, and can have no transparency.

        By looking for specific tile indexes, you will be able to iterate through all sprites, and easy locate tile indexes corresponding to players, enemies, power-ups and so on.
        """
        self.mb = mb
        self.offset = index * 4

    @property
    def y(self):
        """
        The Y-coordinate on the screen to show the Sprite.

        Returns:
            int: Y-coordinate
        """
        return self.mb.getitem(OAM_OFFSET + self.offset + 0)

    @property
    def x(self):
        """
        The X-coordinate on the screen to show the Sprite.

        Returns:
            int: X-coordinate
        """
        return self.mb.getitem(OAM_OFFSET + self.offset + 1)

    @property
    def tile_index(self):
        """
        The index/identifier of the tile the sprite uses. To get a better representation, see the method `pyboy.botsupport.sprite.Sprite.tiles`.

        For double-height sprites, this will only give the index/identifier of the first tile. The second tile will always be the one immediately following the first (`tile_index + 1`).

        Returns:
            int: unsigned tile index
        """
        # Sprites can only use unsigned tile indexes in the lower tile data.
        return self.mb.getitem(OAM_OFFSET + self.offset + 2)
    tile_identifier = tile_index # Same as index, when there is no signed indexes

    @property
    def attr_obj_bg_priority(self):
        """
        To better understand this values, look in the [Pan Docs: VRAM Sprite Attribute Table (OAM)](http://bgb.bircd.org/pandocs.htm#vramspriteattributetableoam).

        Returns:
            bool: The state of the bit in the attributes lookup.
        """
        attr = self.mb.getitem(OAM_OFFSET + self.offset + 3)
        return _get_bit(attr, 7)

    @property
    def attr_y_flip(self):
        """
        To better understand this values, look in the [Pan Docs: VRAM Sprite Attribute Table (OAM)](http://bgb.bircd.org/pandocs.htm#vramspriteattributetableoam).

        Returns:
            bool: The state of the bit in the attributes lookup.
        """
        attr = self.mb.getitem(OAM_OFFSET + self.offset + 3)
        return _get_bit(attr, 6)

    @property
    def attr_x_flip(self):
        """
        To better understand this values, look in the [Pan Docs: VRAM Sprite Attribute Table (OAM)](http://bgb.bircd.org/pandocs.htm#vramspriteattributetableoam).

        Returns:
            bool: The state of the bit in the attributes lookup.
        """
        attr = self.mb.getitem(OAM_OFFSET + self.offset + 3)
        return _get_bit(attr, 5)

    @property
    def attr_palette_number(self):
        """
        To better understand this values, look in the [Pan Docs: VRAM Sprite Attribute Table (OAM)](http://bgb.bircd.org/pandocs.htm#vramspriteattributetableoam).

        Returns:
            bool: The state of the bit in the attributes lookup.
        """
        attr = self.mb.getitem(OAM_OFFSET + self.offset + 3)
        return _get_bit(attr, 4)

    def _get_lcdc_register(self):
        return LCDCRegister(self.mb.getitem(LCDC_OFFSET))

    @property
    def tiles(self):
        """
        The Game Boy support sprites of single-height (8x8 pixels) and double-height (8x16 pixels).

        In the single-height format, one tile is used. For double-height sprites, the Game Boy will also use the tile immidiately following the index given, and render it below the first.

        More information can be found in the [Pan Docs: VRAM Sprite Attribute Table (OAM)](http://bgb.bircd.org/pandocs.htm#vramspriteattributetableoam)

        Returns:
            list: A list of `pyboy.botsupport.tile.Tile` object(s) representing the graphics data for the sprite
        """
        tile_index = self.tile_index
        LCDC = self._get_lcdc_register()
        if LCDC.sprite_height:
            return [Tile(self.mb, index=(tile_index, False)), Tile(self.mb, index=(tile_index + 1, False))]
        else:
            return [Tile(self.mb, index=(tile_index, False))]

    @property
    def on_screen(self):
        """
        To disable sprites from being rendered on screen, developers will place the sprite outside the area of the screen. This is often a good way to determine if the sprite is inactive.

        This check doesn't take transparency into account, and will only check the sprites bounding-box of 8x8 or 8x16 pixels.

        Returns:
            bool: True if the sprite has at least one pixel on screen.
        """
        LCDC = self._get_lcdc_register()
        sprite_height = 16 if LCDC.sprite_height else 16
        return (0 < self.y < 144 + sprite_height and
                0 < self.x < 160 + 8)

    def __eq__(self, other):
        return self.offset == other.offset

    def __str__(self):
        return f"Sprite: (self.x, self.y), {self.tiles}"

def _get_bit(val, bit):
    # return (val & (1 << bit)) >> bit
    return (val >> bit) & 1
