#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

__pdoc__ = {
    "GameWrapperPandorasBlocks.cartridge_title": False,
    "GameWrapperPandorasBlocks.post_tick": False,
}


import numpy as np

import pyboy

from .base_plugin import PyBoyGameWrapper
from pyboy.api.constants import TILES

logger = pyboy.logging.get_logger(__name__)

PIECE_NAMES = ("I", "Z", "S", "J", "L", "O", "T")
piece_table = {name: piece for piece, name in enumerate(PIECE_NAMES)}

FIELD_EMPTY_TILE = 108
PIECE_TILE_START = 48
PIECE_TILE_END = 105
GAME_OVER_TILES = (145, 147, 167, 187)
TITLE_SCREEN_TILES = [171, 177, 179, 185, 187, 193, 195, 201, 203, 209, 211, 217, 219, 225]

GAME_STATE_ADDR = 0xFFFD
GAMEPLAY_STATE = 3
MODE_ADDR = 0xFFDB
MODE_GAME_OVER = 21
MODE_PRE_GAME_OVER = 24
NEXT_BLOCK_ADDR = 0xFFD2
LEVEL_ADDR = 0xFF90
SCORE_ADDR = 0xFFB8

mapping_compressed = np.zeros(TILES, dtype=np.uint8)
mapping_compressed[PIECE_TILE_START:PIECE_TILE_END] = 1
mapping_compressed[106] = 1  # Clearing line
mapping_compressed[107] = 1  # Ghost piece
for tile in GAME_OVER_TILES:
    mapping_compressed[tile] = 2

mapping_minimal = np.ones(TILES, dtype=np.uint8)
mapping_minimal[1] = 0
mapping_minimal[FIELD_EMPTY_TILE] = 0
for tile in GAME_OVER_TILES:
    mapping_minimal[tile] = 2


class GameWrapperPandorasBlocks(PyBoyGameWrapper):
    """
    This class wraps Pandora's Blocks and provides easy access to score, lines and level for AIs.

    Pandora's Blocks uses its level as the number of lines cleared, so ``lines`` and ``level`` have the same value.
    If you call ``print`` on an instance of this object, it will show an overview of everything this object provides.
    """

    cartridge_title = "DMGTRIS"
    mapping_compressed = mapping_compressed
    """
    Compressed mapping for `pyboy.PyBoy.game_area_mapping`
    """
    mapping_minimal = mapping_minimal
    """
    Minimal mapping for `pyboy.PyBoy.game_area_mapping`
    """

    def __init__(self, *args, **kwargs):
        self.score = 0
        """The score provided by the game"""
        self.level = 0
        """The current level"""
        self.lines = 0
        """The number of cleared lines"""

        super().__init__(*args, game_area_section=(2, 0, 10, 18), game_area_follow_scxy=False, **kwargs)

    def _game_area_tiles(self):
        if self._tile_cache_invalid:
            self._cached_game_area_tiles = np.asarray(self.tilemap_background[2:12, :18], dtype=np.uint32)
            self._tile_cache_invalid = False
        return self._cached_game_area_tiles

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        self.score = 0
        for digit in self.pyboy.memory[SCORE_ADDR : SCORE_ADDR + 8]:
            self.score = self.score * 10 + digit

        self.level = 0
        for digit in self.pyboy.memory[LEVEL_ADDR : LEVEL_ADDR + 4]:
            self.level = self.level * 10 + digit
        self.lines = self.level

    def _enter_gameplay(self):
        while self.pyboy.memory[GAME_STATE_ADDR] != GAMEPLAY_STATE:
            self.pyboy.button("start")
            for _ in range(8):
                self.pyboy.tick(1, False, False)
                if self.pyboy.memory[GAME_STATE_ADDR] == GAMEPLAY_STATE:
                    return

    def start_game(self, timer_div=None):
        """
        Call this function right after initializing PyBoy. This navigates through the intro and menu to start the game
        at the first playable state.

        The title-screen state is saved, and using `reset_game`, you can get back to this point instantly.

        Args:
            timer_div (int): Replace timer's DIV register with this value.
        """
        while self.tilemap_background[3:17, 2] != TITLE_SCREEN_TILES:
            self.pyboy.tick(1, False, False)

        PyBoyGameWrapper.start_game(self, timer_div=timer_div)
        self._enter_gameplay()

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, you can call this method at any time to reset the game.

        Args:
            timer_div (int): Replace timer's DIV register with this value.
        """
        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)
        self._enter_gameplay()

    def game_area(self):
        """
        Return the 10 by 18 playfield as a matrix of tile identifiers.

        The score, lines cleared, and level are available as attributes of this class.
        """
        return PyBoyGameWrapper.game_area(self)

    def next_block(self):
        """
        Return the next block to drop.

        Returns
        -------
        shape:
            ``str`` identifying the block: ``"I"``, ``"Z"``, ``"S"``, ``"J"``, ``"L"``, ``"O"`` or ``"T"``.
        """
        return PIECE_NAMES[self.pyboy.memory[NEXT_BLOCK_ADDR]]

    def set_block(self, shape):
        """
        Set the next block to drop.

        Args:
            shape (str): One of ``"I"``, ``"Z"``, ``"S"``, ``"J"``, ``"L"``, ``"O"`` or ``"T"``.
        """
        if shape not in piece_table:
            raise KeyError("Invalid block shape!")
        self.pyboy.memory[NEXT_BLOCK_ADDR] = piece_table[shape]

    def game_over(self):
        """
        Return whether the current game has reached a game-over state.
        """
        return self.pyboy.memory[MODE_ADDR] in (MODE_GAME_OVER, MODE_PRE_GAME_OVER)

    def __repr__(self):
        return (
            "Pandora's Blocks:\n"
            + f"Score: {self.score}\n"
            + f"Level: {self.level}\n"
            + f"Lines: {self.lines}\n"
            + super().__repr__()
        )
