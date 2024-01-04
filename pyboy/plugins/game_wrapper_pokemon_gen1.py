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
from pyboy import utils
from pyboy.utils import WindowEvent

from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)


class GameWrapperPokemonGen1(PyBoyGameWrapper):
    """
    This class wraps Pokemon Red/Blue, and provides basic access for AIs.

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """
    cartridge_title = None

    def __init__(self, *args, **kwargs):
        self.shape = (20, 18)
        super().__init__(*args, game_area_section=(0, 0) + self.shape, game_area_wrap_around=True, **kwargs)
        self.sprite_offset = 0x1000

    def enabled(self):
        return (self.pyboy.cartridge_title == "POKEMON RED") or (self.pyboy.cartridge_title == "POKEMON BLUE")

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        scanline_parameters = self.pyboy.screen.tilemap_position_list
        WX = scanline_parameters[0][2]
        WY = scanline_parameters[0][3]
        self.use_background(WY != 0)

    def _get_screen_background_tilemap(self):
        ### SIMILAR TO CURRENT pyboy.game_wrapper._game_area_np(), BUT ONLY FOR BACKGROUND TILEMAP, SO NPC ARE SKIPPED
        bsm = self.pyboy.botsupport_manager()
        ((scx, scy), (wx, wy)) = bsm.screen().tilemap_position()
        tilemap = np.array(bsm.tilemap_background[:, :])
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
        bottom_left_screen_tiles = screen_tiles[1:1 + screen_tiles.shape[0]:2, ::2]
        walkable_matrix = np.isin(bottom_left_screen_tiles, walkable_tiles_indexes).astype(np.uint8)
        return walkable_matrix

    def game_area_collision(self):
        width = self.game_area_section[2]
        height = self.game_area_section[3]
        game_area = np.ndarray(shape=(height, width), dtype=np.uint32)
        _collision = self._get_screen_walkable_matrix()
        for i in range(height // 2):
            for j in range(width // 2):
                game_area[i * 2][j * 2:j*2 + 2] = _collision[i][j]
                game_area[i*2 + 1][j * 2:j*2 + 2] = _collision[i][j]
        return game_area

    def __repr__(self):
        adjust = 4
        # yapf: disable
        return (
            f"Pokemon Gen 1:\n" +
            "Sprites on screen:\n" +
            "\n".join([str(s) for s in self._sprites_on_screen()]) +
            "\n" +
            "Tiles on screen:\n" +
            " "*5 + "".join([f"{i: <4}" for i in range(10)]) + "\n" +
            "_"*(adjust*20+4) +
            "\n" +
            "\n".join(
                [
                    f"{i: <3}| " + "".join([str(tile).ljust(adjust) for tile in line])
                    for i, line in enumerate(self.game_area())
                ]
            )
        )
        # yapf: enable
