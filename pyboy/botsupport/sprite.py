#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""
This class presents an interface to the sprites held in the OAM data on the Game Boy.
"""

from pyboy.core.lcd import LCDCRegister

from .constants import LCDC_OFFSET, OAM_OFFSET, SPRITES
from .tile import Tile


class Sprite:
    def __init__(self, mb, sprite_index):
        """
        This class presents an interface to the sprites held in the OAM data on the Game Boy.

        The purpose is to make it easier to interpret events on the screen, in order to program a bot, or train an AI.

        Sprites are used on the Game Boy for enemy and player characters, as only sprites can have transparency, and can
        move at pixel-precision on the screen. The other method of graphics -- tile maps -- can only be placed in a
        grid-size of 8x8 pixels precision, and can have no transparency.

        Sprites on the Game Boy are tightly associated with tiles. The sprites can be seen as "upgraded" tiles, as the
        image data still refers back to one (or two) tiles. The tile that a sprite will show, can change between each
        call to `pyboy.PyBoy.tick`, so make sure to verify the `Sprite.tile_identifier` hasn't changed.

        By knowing the tile identifiers of players, enemies, power-ups and so on, you'll be able to search for them
        using `pyboy.PyBoy.get_sprite_by_tile_identifier` and feed it to your bot or AI.
        """
        assert 0 <= sprite_index < SPRITES, f"Sprite index of {sprite_index} is out of range (0-{SPRITES})"
        self.mb = mb
        self._offset = sprite_index * 4

    @property
    def sprite_index(self):
        """
        The index of the sprite itself. Beware, that this only represents the index or a "slot" in OAM memory.
        Many games will change the image data of the sprite in the "slot" several times per second.

        Returns:
            int: unsigned tile index
        """
        return self._offset // 4

    @property
    def y(self):
        """
        The Y-coordinate on the screen to show the Sprite. The (x,y) coordinate points to the top-left corner of the sprite.

        Returns:
            int: Y-coordinate
        """
        # Documentation states the y coordinate needs to be subtracted by 16
        return self.mb.getitem(OAM_OFFSET + self._offset + 0) - 16

    @property
    def x(self):
        """
        The X-coordinate on the screen to show the Sprite. The (x,y) coordinate points to the top-left corner of the sprite.

        Returns:
            int: X-coordinate
        """
        # Documentation states the x coordinate needs to be subtracted by 8
        return self.mb.getitem(OAM_OFFSET + self._offset + 1) - 8

    @property
    def tile_identifier(self):
        """
        The identifier of the tile the sprite uses. To get a better representation, see the method
        `pyboy.botsupport.sprite.Sprite.tiles`.

        For double-height sprites, this will only give the identifier of the first tile. The second tile will
        always be the one immediately following the first (`tile_identifier + 1`).

        Returns:
            int: unsigned tile index
        """
        # Sprites can only use unsigned tile indexes in the lower tile data.
        return self.mb.getitem(OAM_OFFSET + self._offset + 2)

    @property
    def attr_obj_bg_priority(self):
        """
        To better understand this values, look in the [Pan Docs: VRAM Sprite Attribute Table
        (OAM)](http://bgb.bircd.org/pandocs.htm#vramspriteattributetableoam).

        Returns:
            bool: The state of the bit in the attributes lookup.
        """
        attr = self.mb.getitem(OAM_OFFSET + self._offset + 3)
        return _get_bit(attr, 7)

    @property
    def attr_y_flip(self):
        """
        To better understand this values, look in the [Pan Docs: VRAM Sprite Attribute Table
        (OAM)](http://bgb.bircd.org/pandocs.htm#vramspriteattributetableoam).

        Returns:
            bool: The state of the bit in the attributes lookup.
        """
        attr = self.mb.getitem(OAM_OFFSET + self._offset + 3)
        return _get_bit(attr, 6)

    @property
    def attr_x_flip(self):
        """
        To better understand this values, look in the [Pan Docs: VRAM Sprite Attribute Table
        (OAM)](http://bgb.bircd.org/pandocs.htm#vramspriteattributetableoam).

        Returns:
            bool: The state of the bit in the attributes lookup.
        """
        attr = self.mb.getitem(OAM_OFFSET + self._offset + 3)
        return _get_bit(attr, 5)

    @property
    def attr_palette_number(self):
        """
        To better understand this values, look in the [Pan Docs: VRAM Sprite Attribute Table
        (OAM)](http://bgb.bircd.org/pandocs.htm#vramspriteattributetableoam).

        Returns:
            bool: The state of the bit in the attributes lookup.
        """
        attr = self.mb.getitem(OAM_OFFSET + self._offset + 3)
        return _get_bit(attr, 4)

    def _get_lcdc_register(self):
        return LCDCRegister(self.mb.getitem(LCDC_OFFSET))

    @property
    def tiles(self):
        """
        The Game Boy support sprites of single-height (8x8 pixels) and double-height (8x16 pixels).

        In the single-height format, one tile is used. For double-height sprites, the Game Boy will also use the tile
        immediately following the identifier given, and render it below the first.

        More information can be found in the [Pan Docs: VRAM Sprite Attribute Table
        (OAM)](http://bgb.bircd.org/pandocs.htm#vramspriteattributetableoam)

        Returns:
            list: A list of `pyboy.botsupport.tile.Tile` object(s) representing the graphics data for the sprite
        """
        _, sprite_height = self.shape
        if sprite_height == 16:
            return [Tile(self.mb, self.tile_identifier), Tile(self.mb, self.tile_identifier+1)]
        else:
            return [Tile(self.mb, self.tile_identifier)]

    @property
    def on_screen(self):
        """
        To disable sprites from being rendered on screen, developers will place the sprite outside the area of the
        screen. This is often a good way to determine if the sprite is inactive.

        This check doesn't take transparency into account, and will only check the sprite's bounding-box of 8x8 or 8x16
        pixels.

        Returns:
            bool: True if the sprite has at least one pixel on screen.
        """
        _, sprite_height = self.shape
        return (-sprite_height < self.y < 144 and -8 < self.x < 160)

    @property
    def shape(self):
        """
        Sprites can be set to be 8x8 or 8x16 pixels (16 pixels tall). This is defined globally for the rendering
        hardware, so it's either all sprites using 8x16 pixels, or all sprites using 8x8 pixels.

        Returns:
            (int, int): The width and height of the sprite.
        """
        LCDC = self._get_lcdc_register()
        sprite_height = 16 if LCDC.sprite_height else 8
        return (8, sprite_height)

    def __eq__(self, other):
        return self._offset == other._offset

    def __repr__(self):
        tiles = ', '.join([str(t) for t in self.tiles])
        return f"Sprite [{self.sprite_index}]: Position: ({self.x}, {self.y}), Shape: {self.shape}, Tiles: ({tiles}), On screen: {self.on_screen}"


def _get_bit(val, bit):
    # return (val & (1 << bit)) >> bit
    return (val >> bit) & 1
