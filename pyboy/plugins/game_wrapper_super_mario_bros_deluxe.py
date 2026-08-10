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
