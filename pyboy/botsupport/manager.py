#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
from . import constants as _constants
from . import screen as _screen
from . import sprite as _sprite
from . import tile as _tile
from . import tilemap as _tilemap

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False


class BotSupportManager:
    def __init__(self, pyboy, mb):
        if not cythonmode:
            self.pyboy = pyboy
            self.mb = mb

    def __cinit__(self, pyboy, mb):
        self.pyboy = pyboy
        self.mb = mb

    def screen(self):
        """
        Use this method to get a `pyboy.botsupport.screen.Screen` object. This can be used to get the screen buffer in
        a variety of formats.

        It's also here you can find the screen position (SCX, SCY, WX, WY) for each scan line in the screen buffer. See
        `pyboy.botsupport.screen.Screen.tilemap_position` for more information.

        Returns
        -------
        `pyboy.botsupport.screen.Screen`:
            A Screen object with helper functions for reading the screen buffer.
        """
        return _screen.Screen(self.mb)

    def sprite(self, sprite_index):
        """
        Provides a `pyboy.botsupport.sprite.Sprite` object, which makes the OAM data more presentable. The given index
        corresponds to index of the sprite in the "Object Attribute Memory" (OAM).

        The Game Boy supports 40 sprites in total. Read more details about it, in the [Pan
        Docs](http://bgb.bircd.org/pandocs.htm).

        Args:
            index (int): Sprite index from 0 to 39.
        Returns
        -------
        `pyboy.botsupport.sprite.Sprite`:
            Sprite corresponding to the given index.
        """
        return _sprite.Sprite(self.mb, sprite_index)

    def sprite_by_tile_identifier(self, tile_identifiers, on_screen=True):
        """
        Provided a list of tile identifiers, this function will find all occurrences of sprites using the tile
        identifiers and return the sprite indexes where each identifier is found. Use the sprite indexes in the
        `pyboy.botsupport.BotSupportManager.sprite` function to get a `pyboy.botsupport.sprite.Sprite` object.

        Example:
        ```
        >>> print(pyboy.botsupport_manager().sprite_by_tile_identifier([43, 123]))
        [[0, 2, 4], []]
        ```

        Meaning, that tile identifier `43` is found at the sprite indexes: 0, 2, and 4, while tile identifier
        `123` was not found anywhere.

        Args:
            identifiers (list): List of tile identifiers (int)
            on_screen (bool): Require that the matched sprite is on screen

        Returns
        -------
        list:
            list of sprite matches for every tile identifier in the input
        """

        matches = []
        for i in tile_identifiers:
            match = []
            for s in range(_constants.SPRITES):
                sprite = _sprite.Sprite(self.mb, s)
                for t in sprite.tiles:
                    if t.tile_identifier == i and (not on_screen or (on_screen and sprite.on_screen)):
                        match.append(s)
            matches.append(match)
        return matches

    def tile(self, identifier):
        """
        The Game Boy can have 384 tiles loaded in memory at once. Use this method to get a
        `pyboy.botsupport.tile.Tile`-object for given identifier.

        The identifier is a PyBoy construct, which unifies two different scopes of indexes in the Game Boy hardware. See
        the `pyboy.botsupport.tile.Tile` object for more information.

        Returns
        -------
        `pyboy.botsupport.tile.Tile`:
            A Tile object for the given identifier.
        """
        return _tile.Tile(self.mb, identifier=identifier)

    def tilemap_background(self):
        """
        The Game Boy uses two tile maps at the same time to draw graphics on the screen. This method will provide one
        for the _background_ tiles. The game chooses whether it wants to use the low or the high tilemap.

        Read more details about it, in the [Pan Docs](http://bgb.bircd.org/pandocs.htm#vrambackgroundmaps).

        Returns
        -------
        `pyboy.botsupport.tilemap.TileMap`:
            A TileMap object for the tile map.
        """
        return _tilemap.TileMap(self.mb, "BACKGROUND")

    def tilemap_window(self):
        """
        The Game Boy uses two tile maps at the same time to draw graphics on the screen. This method will provide one
        for the _window_ tiles. The game chooses whether it wants to use the low or the high tilemap.

        Read more details about it, in the [Pan Docs](http://bgb.bircd.org/pandocs.htm#vrambackgroundmaps).

        Returns
        -------
        `pyboy.botsupport.tilemap.TileMap`:
            A TileMap object for the tile map.
        """
        return _tilemap.TileMap(self.mb, "WINDOW")
