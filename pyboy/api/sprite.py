#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
"""
This class presents an interface to the sprites held in the OAM data on the Game Boy.
"""

from pyboy.core.lcd import LCDCRegister
from pyboy.utils import PyBoyOutOfBoundsException

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
        using `pyboy.sprite_by_tile_identifier` and feed it to your bot or AI.
        """
        if not (0 <= sprite_index < SPRITES):
            raise PyBoyOutOfBoundsException(f"Sprite index of {sprite_index} is out of range (0-{SPRITES})")
        self.mb = mb
        self._offset = sprite_index * 4

        self._sprite_index = sprite_index
        """
        The index of the sprite itself. Beware, that this only represents the index or a "slot" in OAM memory.
        Many games will change the image data of the sprite in the "slot" several times per second.

        Returns
        -------
        int:
            unsigned tile index
        """

        # Documentation states the y coordinate needs to be subtracted by 16
        self.y = self.mb.getitem(OAM_OFFSET + self._offset + 0) - 16
        """
        The Y-coordinate on the screen to show the Sprite. The (x,y) coordinate points to the top-left corner of the sprite.

        Returns
        -------
        int:
            Y-coordinate
        """

        # Documentation states the x coordinate needs to be subtracted by 8
        self.x = self.mb.getitem(OAM_OFFSET + self._offset + 1) - 8
        """
        The X-coordinate on the screen to show the Sprite. The (x,y) coordinate points to the top-left corner of the sprite.

        Returns
        -------
        int:
            X-coordinate
        """

        # Sprites can only use unsigned tile indexes in the lower tile data.
        self.tile_identifier = self.mb.getitem(OAM_OFFSET + self._offset + 2)
        """
        The identifier of the tile the sprite uses. To get a better representation, see the method
        `pyboy.api.sprite.Sprite.tiles`.

        For double-height sprites, this will only give the identifier of the first tile. The second tile will
        always be the one immediately following the first (`tile_identifier + 1`).

        Returns
        -------
        int:
            unsigned tile index
        """

        attr = self.mb.getitem(OAM_OFFSET + self._offset + 3)
        self.attr_obj_bg_priority = _bit(attr, 7)
        """
        To better understand this values, look in the [Pan Docs: VRAM Sprite Attribute Table
        (OAM)](https://gbdev.io/pandocs/OAM.html).

        Returns
        -------
        bool:
            The state of the bit in the attributes lookup.
        """

        self.attr_y_flip = _bit(attr, 6)
        """
        To better understand this values, look in the [Pan Docs: VRAM Sprite Attribute Table
        (OAM)](https://gbdev.io/pandocs/OAM.html).

        Returns
        -------
        bool:
            The state of the bit in the attributes lookup.
        """

        self.attr_x_flip = _bit(attr, 5)
        """
        To better understand this values, look in the [Pan Docs: VRAM Sprite Attribute Table
        (OAM)](https://gbdev.io/pandocs/OAM.html).

        Returns
        -------
        bool:
            The state of the bit in the attributes lookup.
        """

        self.attr_palette_number = 0
        """
        To better understand this values, look in the [Pan Docs: VRAM Sprite Attribute Table
        (OAM)](https://gbdev.io/pandocs/OAM.html).

        Returns
        -------
        int:
            The state of the bit(s) in the attributes lookup.
        """

        self.attr_cgb_bank_number = 0
        """
        To better understand this values, look in the [Pan Docs: VRAM Sprite Attribute Table
        (OAM)](https://gbdev.io/pandocs/OAM.html).

        Returns
        -------
        bool:
            The state of the bit in the attributes lookup.
        """

        if self.mb.cgb:
            self.attr_palette_number = attr & 0b111
            self.attr_cgb_bank_number = _bit(attr, 3)
        else:
            self.attr_palette_number = _bit(attr, 4)

        LCDC = LCDCRegister(self.mb.getitem(LCDC_OFFSET))
        sprite_height = 16 if LCDC.sprite_height else 8
        self.shape = (8, sprite_height)
        """
        Sprites can be set to be 8x8 or 8x16 pixels (16 pixels tall). This is defined globally for the rendering
        hardware, so it's either all sprites using 8x16 pixels, or all sprites using 8x8 pixels.

        Returns
        -------
        (int, int):
            The width and height of the sprite.
        """

        self.tiles = [Tile(self.mb, self.tile_identifier)]
        """
        The Game Boy support sprites of single-height (8x8 pixels) and double-height (8x16 pixels).

        In the single-height format, one tile is used. For double-height sprites, the Game Boy will also use the tile
        immediately following the identifier given, and render it below the first.

        More information can be found in the [Pan Docs: VRAM Sprite Attribute Table
        (OAM)](https://gbdev.io/pandocs/OAM.html)

        Returns
        -------
        list:
            A list of `pyboy.api.tile.Tile` object(s) representing the graphics data for the sprite
        """
        if sprite_height == 16:
            self.tiles += [Tile(self.mb, self.tile_identifier + 1)]

        self.on_screen = -sprite_height < self.y < 144 and -8 < self.x < 160
        """
        To disable sprites from being rendered on screen, developers will place the sprite outside the area of the
        screen. This is often a good way to determine if the sprite is inactive.

        This check doesn't take transparency into account, and will only check the sprite's bounding-box of 8x8 or 8x16
        pixels.

        Returns
        -------
        bool:
            True if the sprite has at least one pixel on screen.
        """

    def __eq__(self, other):
        return self._offset == other._offset

    def __repr__(self):
        tiles = ", ".join([str(t) for t in self.tiles])
        return f"Sprite [{self._sprite_index}]: Position: ({self.x}, {self.y}), Shape: {self.shape}, Tiles: ({tiles}), On screen: {self.on_screen}"


def _bit(val, bit):
    # return (val & (1 << bit)) >> bit
    return (val >> bit) & 1
