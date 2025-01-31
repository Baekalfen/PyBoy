#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

__pdoc__ = {
    "GameWrapperCastlevaniaTheAdventure.cartridge_title": False,
    "GameWrapperCastlevaniaTheAdventure.post_tick": False,
}

import numpy as np

import pyboy
from pyboy.utils import bcd_to_dec

from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)

ADDR_LEVEL_SCORE = 0xC034 # BCD
LEVEL_SCORE_BYTE_WIDTH = 3
MAX_LEVEL_SCORE = 99999

ADDR_TIME_LEFT_SECONDS = 0xC436 # BCD
ADDR_TIME_LEFT_MINUTES = 0xC437 # BCD

ADDR_LIVES_LEFT = 0xC040 # BCD
MAX_LIVES = 0x99

ADDR_HEALTH = 0xC519
MAX_HEALTH = 10

ADDR_WHIPE_LEVEL = 0xC51C # 00, 01 or 02
ADDR_WHIPE_THROW_BULLET = 0xC51D # 00 False, 0x80 True (if ADDR_WHIPE_LEVEL >= 02)
MAX_WHIPE_LEVEL = 2

ADDR_INVINCIBLE_TIMER = 0xC02C


class GameWrapperCastlevaniaTheAdventure(PyBoyGameWrapper):
    """
    This class wraps Castlevania The Adventure, and provides easy access for AIs.

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """

    cartridge_title = "CASTLEVANIA AD"

    def __init__(self, *args, **kwargs):
        self.level_score = 0
        """The level score provided by the game"""
        self.time_left = 0
        """Time remaining (in seconds) provided by the game"""
        self.lives_left = 0
        """The lives remaining provided by the game"""
        self.health = 0
        """The health provided by the game"""
        self.whipe_level = 0
        """The whipe level provided by the game. Can be 0, 1 or 2."""
        self.invincible_timer = 0
        """The timer for invincible mode provided by the game. Player is invincible if timer is higher than 0"""

        super().__init__(*args, game_area_section=(0, 0, 19, 16), game_area_follow_scxy=True, **kwargs)

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        self.level_score = bcd_to_dec(
            int.from_bytes(self.pyboy.memory[ADDR_LEVEL_SCORE:ADDR_LEVEL_SCORE + LEVEL_SCORE_BYTE_WIDTH], "little"),
            byte_width=LEVEL_SCORE_BYTE_WIDTH
        )
        self.time_left = (
            bcd_to_dec(self.pyboy.memory[ADDR_TIME_LEFT_SECONDS]) +
            bcd_to_dec(self.pyboy.memory[ADDR_TIME_LEFT_MINUTES]) * 60
        )
        self.lives_left = bcd_to_dec(self.pyboy.memory[ADDR_LIVES_LEFT])
        self.whipe_level = self.pyboy.memory[ADDR_WHIPE_LEVEL]
        self.invincible_timer = self.pyboy.memory[ADDR_INVINCIBLE_TIMER]
        self.health = self.pyboy.memory[ADDR_HEALTH]

    def start_game(self, timer_div=None):
        """
        Call this function right after initializing PyBoy. This will navigate through menus to start the game at the
        first playable state.

        The state of the emulator is saved, and using `reset_game`, you can get back to this point of the game
        instantly.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """

        # Boot screen
        while True:
            self.pyboy.tick(1, False)
            if self.tilemap_background[1, 6:10] == [256, 327, 334, 256]: # 'KONAMI' logo on the first screen
                break

        self.pyboy.button("start") # Skip brand
        self.pyboy.tick(7, False) # Wait for transition to finish (start screen)
        self.pyboy.button("start") # Start level
        self.pyboy.tick(300, False) # Skip level transition

        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

    def game_over(self):
        return self.health == 0

    def __repr__(self):
        # yapf: disable
        return (
            f"Castlevania The Adventure:\n\n" +
            f"Score: {self.level_score}\n" +
            f"Time left: {self.time_left}\n" +
            f"Lives left: {self.lives_left}\n" +
            f"Health: {self.health}\n" +
            f"Whipe level: {self.whipe_level}\n"+
            f"Invincible timer: {self.invincible_timer}\n" +
            super().__repr__()
        )
        # yapf: enable
