#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

__pdoc__ = {
    "GameWrapperPokemonGen1.cartridge_title": False,
    "GameWrapperPokemonGen1.post_tick": False,
}

import numpy as np
from pyboy.utils import WindowEvent
from pyboy.logger import logger
from ..base_plugin import PyBoyGameWrapper
from .core.gen_1_memory_manager import Gen1MemoryManager
from .utils import get_character_index, STRING_TERMINATOR, ASCII_DELTA
from data.constants.status import Statuses

PKMN_SIZE = 0x2C
BYTE_ORDER = 'big'


try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False


class GameWrapperPokemonGen1(PyBoyGameWrapper):
    """
    This class wraps Pokemon Red/Blue.

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """
    cartridge_title = None

    def __init__(self, *args, **kwargs):
        self.shape = (20, 18)
        super().__init__(*args, game_area_section=(0, 0) + self.shape, game_area_wrap_around=True, **kwargs)
        self.memory_manager = Gen1MemoryManager(self.pyboy)

    def enabled(self):
        return self.pyboy_argv.get("game_wrapper") and ((self.pyboy.cartridge_title() == "POKEMON RED") or
                                                        (self.pyboy.cartridge_title() == "POKEMON BLUE"))

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        scanline_parameters = self.pyboy.botsupport_manager().screen().tilemap_position_list()
        WX = scanline_parameters[0][2]
        WY = scanline_parameters[0][3]
        self.use_background(WY != 0)

    def _get_screen_background_tilemap(self):
        ### SIMILAR TO CURRENT pyboy.game_wrapper()._game_area_np(), BUT ONLY FOR BACKGROUND TILEMAP, SO NPC ARE SKIPPED
        bsm = self.pyboy.botsupport_manager()
        ((scx, scy), (wx, wy)) = bsm.screen().tilemap_position()
        tilemap = np.array(bsm.tilemap_background()[:, :])
        return np.roll(np.roll(tilemap, -scy // 8, axis=0), -scx // 8, axis=1)[:18, :20]

    def _get_screen_walkable_matrix(self):
        walkable_tiles_indexes = []
        collision_ptr = self.pyboy.get_memory_value(0xD530) + (self.pyboy.get_memory_value(0xD531) << 8)
        tileset_type = self.pyboy.get_memory_value(0xFFD7)
        if tileset_type > 0:
            grass_tile_index = self.pyboy.get_memory_value(0xD535)
            if grass_tile_index != 0xFF:
                walkable_tiles_indexes.append(grass_tile_index + 0x100)
        for i in range(0x180):
            tile_index = self.pyboy.get_memory_value(collision_ptr + i)
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

    def set_text(self, text, address):
        """Sets text at address.

        Will always add a string terminator (80) at the end.
        """
        i = 0
        for character in text:
            try:
                self.pyboy.set_memory_value(address + i, get_character_index(character))
                i += 1
            except:
                pass
        self.pyboy.set_memory_value(address + i, STRING_TERMINATOR)

    def set_rom_text(self, text, bank, address):
        i = 0
        for character in text:
            try:
                self.pyboy.override_memory_value(bank, address + i, get_character_index(character))
                i += 1
            except:
                pass

    def set_player_name(self, name):
        """
        Sets the player name.

        Args:
            name (string): Name to be set (will be trimmed at 8 characters).
        """
        self.set_text(name[:8], 0xD158)

    def get_player_name(self):
        """
        Returns player name.
        """
        return self.get_text(0xD158)

    def set_rival_name(self, name):
        """
        Sets the rival name.

        Args:
            name (string): Name to be set (will be trimmed at 8 characters).
        """
        self.set_text(name[:8], 0xD34A)

    def get_rival_name(self):
        """
        Returns rival name.
        """
        return self.get_text(0xD34A)

    def get_text(self, address, cap = 16):
        """
        Retrieves a string from a given address.

        Args:
            address (int): Address from where to retrieve text from.
            cap (int): Maximum expected length of string (default: 16).
        """
        i = 0
        text = ''
        while i < cap:
            value = self.pyboy.get_memory_value(address + i)
            try:
                text += chr(value - ASCII_DELTA)
            except:
                pass
            if value == STRING_TERMINATOR:
                break
            i += 1
        return text

    def set_palette_to_darkness(self):
        self.pyboy.set_memory_value(0xD35D, 6)

    def get_pokemon(self, party_index):
        return self.memory_manager.load_pokemon_from_party(party_index)

    def set_player_monster_asleep(self, index):
        self.set_player_monster_status(index, Statuses.ASLEEP)

    def set_player_monster_poisoned(self, index):
        self.set_player_monster_status(index, Statuses.POISONED)

    def set_player_monster_burned(self, index):
        self.set_player_monster_status(index, Statuses.BURNED)

    def set_player_monster_frozen(self, index):
        self.set_player_monster_status(index, Statuses.FROZEN)

    def set_player_monster_paralyzed(self, index):
        self.set_player_monster_status(index, Statuses.PARALYZED)

    def set_player_monster_no_ailment(self, index):
        self.set_player_monster_status(index, 0)

    def get_player_money(self):
        return self.get_int_at_address(0xD347, size=3)

    def set_active_player_monster_status(self, status):
        self.pyboy.set_memory_value(0xD018, status)

    def set_active_player_monster_asleep(self):
        self.set_active_player_monster_status(Statuses.ASLEEP)

    def set_active_player_monster_poisoned(self):
        self.set_active_player_monster_status(Statuses.POISONED)

    def set_active_player_monster_burned(self):
        self.set_active_player_monster_status(Statuses.BURNED)

    def set_active_player_monster_frozen(self):
        self.set_active_player_monster_status(Statuses.FROZEN)

    def set_active_player_monster_paralyzed(self):
        self.set_active_player_monster_status(Statuses.PARALYZED)

    def set_active_player_monster_no_ailment(self):
        self.set_active_player_monster_status(0)

    def set_active_player_monster_move(self, index, move):
        self.pyboy.set_memory_value(0xD01C + index, move)

    def set_active_opponent_monster_move(self, index, move):
        self.pyboy.set_memory_value(0xCFED + index, move)

    def set_active_player_monster_nickname(self, nickname):
        self.set_text(nickname[:10], 0xD009)

    def set_active_opponent_monster_nickname(self, nickname):
        self.set_text(nickname[:10], 0xCFDA)

    def set_active_opponent_monster_status(self, status):
        self.pyboy.set_memory_value(0xCFE9, status)

    def set_active_opponent_monster_asleep(self):
        self.set_active_opponent_monster_status(Statuses.ASLEEP)

    def set_active_opponent_monster_poisoned(self):
        self.set_active_opponent_monster_status(Statuses.POISONED)

    def set_active_opponent_monster_burned(self):
        self.set_active_opponent_monster_status(Statuses.BURNED)

    def set_active_opponent_monster_frozen(self):
        self.set_active_opponent_monster_status(Statuses.FROZEN)

    def set_active_opponent_monster_paralyzed(self):
        self.set_active_opponent_monster_status(Statuses.PARALYZED)

    def set_active_opponent_monster_no_ailment(self):
        self.set_active_opponent_monster_status(0)

    def heal_player_monster(self, index):
        """
        Fully heals a player monster.

        Args:
            index (int): Which monster to change (0-5).
        """
        self.set_player_monster_no_ailment(index)
        max_hp = self.get_player_monster_max_hp(index)
        self.set_player_monster_current_hp(index, max_hp)

    def heal_active_player_monster(self):
        self.set_active_player_monster_no_ailment()
        max_hp = self.get_active_player_monster_max_hp()
        self.set_active_player_monster_current_hp(max_hp)

    def is_battle_happening(self):
        return self.pyboy.get_memory_value(0xD057) != 0

    def get_current_map(self):
        return self.pyboy.get_memory_value(0xD35E)

    # TODO: Add player position functions
