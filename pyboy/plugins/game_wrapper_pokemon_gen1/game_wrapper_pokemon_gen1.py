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
from .data.memory_addrs.misc import MONEY_ADDR
from .core.pokedex import Pokedex
from .core.pokemon import Pokemon
from .core.player import Player
from .core.mem_manager import MemoryManager
from .core.game_state import GameState

PKMN_SIZE = 0x2C
BYTE_ORDER = 'big'



class GameWrapperPokemonGen1(PyBoyGameWrapper):
    """
    This class wraps Pokemon Red/Blue.

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """
    cartridge_title = None
    
    def __init__(self, *args, **kwargs):
        self.shape = (20, 18)
        super().__init__(*args, game_area_section=(0, 0) + self.shape, game_area_wrap_around=True, **kwargs)
        self.mem_manager = MemoryManager(self.pyboy)

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
        collision_ptr = self._read_multibyte_value(0xD530, num_bytes=2)
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

    def get_pokemon_from_party(self, party_index):
        return Pokemon.load_pokemon_from_party(self.mem_manager, party_index)
    
    def get_all_pokemon_from_party(self):
        num_pokemon = self.mem_manager.read_hex_from_memory(0xD163, 1)
        pokemon_team = [self.get_pokemon_from_party(i+1) for i in range(num_pokemon)]
        return pokemon_team

    def get_pokedex(self):
        return Pokedex.load_pokedex(self.mem_manager)
    
    def get_player(self):
        return Player.load_player(self.mem_manager)
    
    def get_player_location(self):
        player_sprite_y = self.mem_manager.read_hex_from_memory(0xD361, 1)
        player_sprite_x = self.mem_manager.read_hex_from_memory(0xD362, 1)
        player_sprite_map_id = self.mem_manager.read_hex_from_memory(0xD35E, 1)

        return (player_sprite_x, player_sprite_y)
    
    def get_game_state(self):
        return GameState.load_game_state(self.mem_manager)
    
    def get_screen(self):
        return self.pyboy.botsupport_manager().screen()
    
    def get_screen_array(self):
        return self.get_screen().screen_ndarray()
    
    '''
    WARNING

    The following functions are NOT meant to be used consistently. They exist only as
    a way to call the heper memory access functions for testing memory fields. They 
    WILL BE REMOVED. Ideally, some form of the memory access functions will appear in 
    PyBoy proper, but alternatively and data accesses made with these functions should
    be turned into a named function in the game wrapper. If you find yourself using these 
    functions consistenly, please open up an issue at https://github.com/SnarkAttack/PyBoy
    and indicate the memory addresses you are accessing and their use so that a named function
    can be created. If you need those memory values, other people might too.
    '''

    def read_memory(self, address, num_bytes, read_type):
        if read_type == 'hex':
            return self.mem_manager.read_hex_from_memory(address, num_bytes)
        elif read_type == 'address':
            return self.mem_manager.read_address_from_memory(address, num_bytes)
        elif read_type == 'bcd':
            return self.mem_manager.read_bcd_from_memory(address, num_bytes)
        elif read_type == 'text':
            return self.mem_manager.read_text_from_memory(address, num_bytes)
        else:
            raise ValueError(f"{read_type} is not a valid read type")