#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
__pdoc__ = {
    "GameWrapperPokemonGen1.cartridge_title": False,
    "GameWrapperPokemonGen1.post_tick": False,
}

import numpy as np

import pyboy
from pyboy.utils import _bcd_to_dec, bcd_to_dec

from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)

# Set of addresses for information on pokemon
# Based on the following link: https://datacrystal.tcrf.net/wiki/Pok%C3%A9mon_Red_and_Blue/RAM_map
ADDR_TITLE_SCREEN = 0x1FC3
ADDR_NUMBER_OF_POKEMON = 0xD163 # In party

#Item related values
ADDR_TOTAL_ITEMS = 0xD53A
ADDR_BADGES = 0xD356 # Currently requires conversion (each bit is an independent switch and represents a badge)

# Game Time
ADDR_HOURS = 0xDA40
ADDR_MINUTES = 0xDA42
ADDR_SECONDS = 0xDA44

# Battle mode - May remove this due to not knowing exactly what it does.
ADDR_BATTLE = 0xD057


class GameWrapperPokemonGen1(PyBoyGameWrapper):
    """
    This class wraps Pokemon Red/Blue, and provides basic access for AIs.

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """

    cartridge_title = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, game_area_section=(0, 0, 20, 18), game_area_follow_scxy=True, **kwargs)
        self.sprite_offset = 0

    def enabled(self):
        return (self.pyboy.cartridge_title == "POKEMON RED") or (self.pyboy.cartridge_title == "POKEMON BLUE")

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        self.number_of_pokemon = bcd_to_dec(self.pyboy.memory[ADDR_NUMBER_OF_POKEMON])
        _total_items = bcd_to_dec(self.pyboy.memory[ADDR_TOTAL_ITEMS])
        self.total_items = _total_items - 1 # This is because the cancel button seems to be counted as an item.
        # Extract the time in game:
        _hours = _bcd_to_dec(self.pyboy.memory[ADDR_HOURS: ADDR_HOURS+2])
        _minutes = _bcd_to_dec(self.pyboy.memory[ADDR_MINUTES: ADDR_MINUTES+2])
        _seconds = bcd_to_dec(self.pyboy.memory[ADDR_SECONDS])
        self.game_time = f'{_hours}:{_minutes}:{_seconds}'

        # Check whether the player is in battle mode or out of battle
        if self.pyboy.memory[ADDR_BATTLE] == 1:
            self.battle_state = 'In Battle'
        else:
            self.battle_state = 'Overworld'


        scanline_parameters = self.pyboy.screen.tilemap_position_list
        # WX = scanline_parameters[0][2]
        WY = scanline_parameters[0][3]
        self.use_background(WY != 0)

    def _get_screen_background_tilemap(self):
        ### SIMILAR TO CURRENT pyboy.game_wrapper.game_area(), BUT ONLY FOR BACKGROUND TILEMAP, SO NPC ARE SKIPPED
        ((scx, scy), (wx, wy)) = self.pyboy.screen.get_tilemap_position()
        tilemap = np.array(self.pyboy.tilemap_background[:, :])
        return np.roll(np.roll(tilemap, -scy // 8, axis=0), -scx // 8, axis=1)[:18, :20]

    def _get_screen_walkable_matrix(self):
        walkable_tiles_indexes = []
        collision_ptr = self.pyboy.memory[0xD530] + (self.pyboy.memory[0xD531] << 8)
        tileset_type = self.pyboy.memory[0xFFD7]
        if tileset_type > 0:
            grass_tile_index = self.pyboy.memory[0xD535]
            if grass_tile_index != 0xFF:
                walkable_tiles_indexes.append(grass_tile_index + 0x100)
        for i in range(0x180):
            tile_index = self.pyboy.memory[collision_ptr + i]
            if tile_index == 0xFF:
                break
            else:
                walkable_tiles_indexes.append(tile_index + 0x100)
        screen_tiles = self._get_screen_background_tilemap()
        bottom_left_screen_tiles = screen_tiles[1 : 1 + screen_tiles.shape[0] : 2, ::2]
        walkable_matrix = np.isin(bottom_left_screen_tiles, walkable_tiles_indexes).astype(np.uint8)
        return walkable_matrix

    def game_area_collision(self):
        width = self.game_area_section[2]
        height = self.game_area_section[3]
        game_area = np.ndarray(shape=(height, width), dtype=np.uint32)
        _collision = self._get_screen_walkable_matrix()
        for i in range(height // 2):
            for j in range(width // 2):
                game_area[i * 2][j * 2 : j * 2 + 2] = _collision[i][j]
                game_area[i * 2 + 1][j * 2 : j * 2 + 2] = _collision[i][j]
        return game_area

    def __repr__(self):
        return ("Pokemon Gen 1:\n"
                + f"Pokemon in Party: {self.number_of_pokemon}\n"
                + f"Battle State: {self.battle_state}\n"
                + f"Game Time: {self.game_time}\n"
                + f"Total items: {self.total_items}\n"
                + super().__repr__())
