#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import numpy as np

import pyboy
from pyboy.api.constants import TILES_CGB
from pyboy.utils import PyBoyException, PyBoyInvalidInputException, bcd_to_dec, dec_to_bcd

from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)

ADDR_LEVEL_SET = 0xC160
ADDR_LEVEL = 0xC162
ADDR_SCORE = 0xC17A
ADDR_TIME_LEFT = 0xC17D
ADDR_LIVES_LEFT = 0xC17F
ADDR_COINS = 0xC1F2
ADDR_MENU_SELECTION = 0xC1A8
ADDR_CHALLENGE_UNLOCK = 0xC18E
ADDR_PLAYER_STATE = 0xC1C1
ADDR_PLAYER_X = 0xC1CA
ADDR_LEVEL_X = 0xFFA7
ADDR_MODE = 0xFFB5

MODE_TITLE_SCREEN = 0x03
MODE_MAIN_MENU = 0x19
MODE_FILE_SELECT = 0x17
MODE_WORLD_MAP = 0x05
MODE_LEVEL = 0x0B

# The table is in ROM bank 3 at 03:6D16 (Tile16_InteractTypes).
INTERACTION_TABLE_BANK = 3
INTERACTION_TABLE_ADDRESS = 0x6D16
METATILE_MAP_BANK = 6
METATILE_MAP_ADDRESS = 0xD000
METATILE_MAP_WIDTH = 256
METATILE_MAP_HEIGHT = 16
METATILE_SCREEN_WIDTH = 16
METATILE_SCREEN_SIZE = 0x100
DEFAULT_SPRITE_OFFSET = 0x100

mapping_minimal = np.arange(TILES_CGB, dtype=np.uint32)
mapping_compressed = mapping_minimal


class GameWrapperSuperMarioBrosDeluxe(PyBoyGameWrapper):
    """
    Wrapper for Super Mario Bros. Deluxe.

    The optional ``level`` argument to :meth:`start_game` uses the game's
    built-in level selector. For the original game, levels 0 through 31 are
    World 1-1 through World 8-4. Set ``level_set=1`` for the For Super
    Players levels.
    """

    cartridge_title = "MARIO DELUXAHY"
    mapping_minimal = mapping_minimal
    mapping_compressed = mapping_compressed

    def __init__(self, *args, **kwargs):
        self.world = (0, 0)
        self.level = 0
        self.selected_level = 0
        self.selected_level_set = 0
        self.level_selected = False
        self.coins = 0
        self.lives_left = 0
        self.score = 0
        self.time_left = 0
        self.level_progress = 0
        super().__init__(*args, game_area_section=(0, 2, 20, 16), game_area_follow_scxy=True, **kwargs)
        self.metatile_interaction_types = None
        self.sprite_offset = DEFAULT_SPRITE_OFFSET

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        self.level = self.pyboy.memory[ADDR_LEVEL]
        self.world = (int(self.level // 4 + 1), int(self.level % 4 + 1)) if self.level < 0x20 else (0, int(self.level))
        self.coins = self.pyboy.memory[ADDR_COINS]
        self.lives_left = self.pyboy.memory[ADDR_LIVES_LEFT]
        self.score = bcd_to_dec(int.from_bytes(self.pyboy.memory[ADDR_SCORE : ADDR_SCORE + 3], "little"), byte_width=3)
        self.time_left = bcd_to_dec(
            int.from_bytes(self.pyboy.memory[ADDR_TIME_LEFT : ADDR_TIME_LEFT + 2], "little"), byte_width=2
        )
        self.level_progress = self.pyboy.memory[ADDR_LEVEL_X] + int.from_bytes(
            self.pyboy.memory[ADDR_PLAYER_X : ADDR_PLAYER_X + 2], "little"
        )

    def _game_area_tiles(self):
        """Return interaction types for the visible 16x16 metatile map."""
        if self._tile_cache_invalid:
            if self.metatile_interaction_types is None:
                self.metatile_interaction_types = np.asarray(
                    self.pyboy.memory[
                        INTERACTION_TABLE_BANK, INTERACTION_TABLE_ADDRESS : INTERACTION_TABLE_ADDRESS + 0x100
                    ],
                    dtype=np.uint32,
                )
            xx, yy, width, height = self.game_area_section
            tiles = np.zeros((height, width), dtype=np.uint32)
            for y in range(height):
                scroll_x, scroll_y = self.pyboy.screen.tilemap_position_list[(yy + y) * 8][:2]
                for x in range(width):
                    world_x = scroll_x + (xx + x) * 8
                    world_y = scroll_y + (yy + y) * 8
                    metatile_x = world_x // 16
                    metatile_y = world_y // 16
                    if not (0 <= metatile_x < METATILE_MAP_WIDTH * 2 and 0 <= metatile_y < METATILE_MAP_HEIGHT):
                        continue
                    screen = metatile_x // METATILE_SCREEN_WIDTH
                    bank = METATILE_MAP_BANK + screen // 16
                    address = (
                        METATILE_MAP_ADDRESS
                        + (screen % 16) * METATILE_SCREEN_SIZE
                        + metatile_y * METATILE_SCREEN_WIDTH
                        + metatile_x % METATILE_SCREEN_WIDTH
                    )
                    metatile = self.pyboy.memory[bank, address]
                    tiles[y, x] = self.metatile_interaction_types[metatile]
            self._cached_game_area_tiles = tiles
            self._tile_cache_invalid = False
        return self._cached_game_area_tiles

    def game_area(self):
        """
        Return the visible metatile interaction types with sprites overlaid.

        Background values are the stable interaction codes used by the game,
        rather than graphics-dependent 8x8 VRAM tile IDs. The codes are
        defined by ``Tile16_InteractTypes`` in the game's ROM.
        """
        tiles_matrix = np.asarray(self._game_area_tiles(), dtype=np.uint32)
        sprites = self._sprites_on_screen()
        xx, yy, width, height = self.game_area_section
        for sprite in sprites:
            x = (sprite.x // 8) - xx
            y = (sprite.y // 8) - yy
            if 0 <= x < width and 0 <= y < height:
                tiles_matrix[y, x] = self.mapping[sprite.tile_identifier] + self.sprite_offset
            if len(sprite.tiles) == 2 and 0 <= x < width and 0 <= y + 1 < height:
                tiles_matrix[y + 1, x] = self.mapping[sprite.tile_identifier + 1] + self.sprite_offset
        return tiles_matrix

    def _press(self, button):
        self.pyboy.button_press(button)
        for _ in range(20):
            self.pyboy.tick(1, False)
        self.pyboy.button_release(button)

    def _wait_for_mode(self, *modes):
        while self.pyboy.memory[ADDR_MODE] not in modes:
            self.pyboy.tick(1, False)
        for _ in range(100):
            self.pyboy.tick(1, False)

    def set_lives_left(self, amount):
        """Set Mario's lives to a value between 0 and 99."""
        if not 0 <= amount <= 99:
            raise PyBoyInvalidInputException(f"{amount} is out of bounds. Only values between 0 and 99 allowed.")
        self.pyboy.memory[ADDR_LIVES_LEFT] = amount

    def set_time_left(self, time):
        """Set the level timer to a value between 0 and 999."""
        if not 0 <= time <= 999:
            raise PyBoyInvalidInputException(f"{time} is out of bounds. Only values between 0 and 999 allowed.")
        value = dec_to_bcd(time, byte_width=2)
        self.pyboy.memory[ADDR_TIME_LEFT] = value & 0xFF
        self.pyboy.memory[ADDR_TIME_LEFT + 1] = value >> 8

    def set_level(self, level, level_set=0):
        """
        Select a level for the game's debug level selector.

        ``level_set=0`` selects Super Mario Bros.; ``level_set=1`` selects
        For Super Players.
        """
        if not 0 <= level <= 0x63:
            raise PyBoyInvalidInputException(f"{level} is out of bounds. Only values between 0 and 99 allowed.")
        if level_set not in (0, 1):
            raise PyBoyInvalidInputException(f"{level_set} is out of bounds. Only 0 or 1 is allowed.")
        self.pyboy.memory[ADDR_LEVEL_SET] = level_set
        self.pyboy.memory[ADDR_LEVEL] = level
        self.selected_level = level
        self.selected_level_set = level_set
        self.level_selected = True

    def set_world_level(self, world, level, level_set=0):
        """
        Select a world and level to start from.

        World and level numbers are one-based, matching the game's display.
        The standard game has worlds 1-8 with four levels each.
        """
        if not 1 <= world <= 13:
            raise PyBoyInvalidInputException(f"{world} is out of bounds. Only worlds 1 through 13 are allowed.")
        if not 1 <= level <= 4:
            raise PyBoyInvalidInputException(f"{level} is out of bounds. Only levels 1 through 4 are allowed.")
        if level_set == 0 and world > 8:
            raise PyBoyInvalidInputException("Worlds 9 through 13 are only available in the For Super Players set.")
        self.set_level((world - 1) * 4 + level - 1, level_set)

    def start_game(self, timer_div=None, world_level=None, level=None, level_set=0, unlock_level_select=False):
        """
        Start a game from the title screen.

        ``world_level`` selects a one-based ``(world, level)`` tuple, matching
        Super Mario Land. ``level`` remains available for selecting a raw
        Deluxe level ID. ``unlock_level_select=True`` leaves the emulator in
        the Challenge selector instead of launching a level.
        """
        if self.game_has_started:
            raise PyBoyException("Gamewrapper already started! Use 'reset' instead.")
        if world_level is not None and level is not None:
            raise PyBoyInvalidInputException("Specify either world_level or level, not both.")
        if world_level is not None:
            self.set_world_level(*world_level, level_set=level_set)
        elif level is not None:
            self.set_level(level, level_set)

        self._wait_for_mode(MODE_TITLE_SCREEN)
        for _ in range(200):
            self.pyboy.tick(1, False)

        self._press("start")
        self._wait_for_mode(MODE_MAIN_MENU)

        if self.level_selected or unlock_level_select:
            self.pyboy.memory[ADDR_MENU_SELECTION] = 1
            self._press("a")
            self._wait_for_mode(0x1E)
            self.pyboy.memory[ADDR_CHALLENGE_UNLOCK] = 1

            if self.level_selected:
                self.set_level(self.selected_level, self.selected_level_set)
                self._press("a")
                self._wait_for_mode(MODE_WORLD_MAP)
                self._press("start")
                self._wait_for_mode(MODE_LEVEL)
        else:
            self._press("a")
            self._wait_for_mode(MODE_FILE_SELECT)
            self._press("a")
            self._wait_for_mode(MODE_WORLD_MAP)
            self._press("start")
            self._wait_for_mode(MODE_LEVEL)

        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

    def game_over(self):
        return self.pyboy.memory[ADDR_PLAYER_STATE] == 3 or self.pyboy.memory[ADDR_MODE] in (
            0x0E,
            0x10,
            0x11,
            0x14,
            0x1B,
        )

    def __repr__(self):
        return (
            f"Super Mario Bros. Deluxe: World {'-'.join(str(i) for i in self.world)}\n"
            f"Coins: {self.coins}\n"
            f"Lives left: {self.lives_left}\n"
            f"Score: {self.score}\n"
            f"Time left: {self.time_left}\n"
            f"Level progress: {self.level_progress}\n" + super().__repr__()
        )
