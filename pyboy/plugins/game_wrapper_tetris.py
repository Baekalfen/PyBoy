#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
__pdoc__ = {
    "GameWrapperTetris.cartridge_title": False,
    "GameWrapperTetris.post_tick": False,
}


import numpy as np

import pyboy

from .base_plugin import PyBoyGameWrapper
from pyboy.api.constants import TILES

logger = pyboy.logging.get_logger(__name__)

# Table for translating game-representation of Tetromino types (8-bit int) to string
tetromino_table = {
    "L": 0,
    "J": 4,
    "I": 8,
    "O": 12,
    "Z": 16,
    "S": 20,
    "T": 24,
}
inverse_tetromino_table = {v: k for k, v in tetromino_table.items()}

NEXT_TETROMINO_ADDR = 0xC213

# Construct a translation table for tile ID's to a minimal/compressed id system
# Compressed assigns an ID to each Tetromino type
mapping_compressed = np.zeros(TILES, dtype=np.uint8)
# BLANK, J, Z, O, L, T, S, I, BLACK
tiles_types = [[47], [129], [130], [131], [132], [133], [134], [128, 136, 137, 138, 139, 143], [135]]
for tiles_type_ID, tiles_type in enumerate(tiles_types):
    for tile_ID in tiles_type:
        mapping_compressed[tile_ID] = tiles_type_ID

# Minimal has 3 id's: Background, Tetromino and "losing tile" (which fills the board when losing)
mapping_minimal = np.ones(TILES, dtype=np.uint8)  # For minimal everything is 1
mapping_minimal[47] = 0  # Except BLANK which is 0
mapping_minimal[135] = 2  # And background losing tiles BLACK which is 2


class GameWrapperTetris(PyBoyGameWrapper):
    """
    This class wraps Tetris, and provides easy access to score, lines and level for AIs.

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """

    cartridge_title = "TETRIS"
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

        # super().__init__(*args, **kwargs)

        # ROWS, COLS = self.shape
        # self._cached_game_area_tiles_raw = array("B", [0xFF] * (ROWS*COLS*4))
        # self._cached_game_area_tiles = memoryview(self._cached_game_area_tiles_raw).cast("I", shape=(ROWS, COLS))

        super().__init__(*args, game_area_section=(2, 0, 10, 18), game_area_follow_scxy=False, **kwargs)

    def _game_area_tiles(self):
        if self._tile_cache_invalid:
            self._cached_game_area_tiles = np.asarray(self.tilemap_background[2:12, :18], dtype=np.uint32)
            self._tile_cache_invalid = False
        return self._cached_game_area_tiles

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        blank = 47
        self.score = self._sum_number_on_screen(13, 3, 6, blank, 0)
        self.level = self._sum_number_on_screen(14, 7, 4, blank, 0)
        self.lines = self._sum_number_on_screen(14, 10, 4, blank, 0)

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
            if self.tilemap_background[2:9, 14] == [89, 25, 21, 10, 34, 14, 27]:  # '1PLAYER' on the first screen
                break
        self.pyboy.tick(5, False)

        # Start game. Just press Start when the game allows us.
        for i in range(2):
            self.pyboy.button("start")
            self.pyboy.tick(7, False)

        # We don't supply the timer_div arg here, as it won't have the desired effect
        PyBoyGameWrapper.start_game(self)
        self.reset_game(timer_div=timer_div)

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, you can call this method at any time to reset the game.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)
        self.pyboy.button("start")
        self.pyboy.tick(7, False)

    def game_area(self):
        """
        Use this method to get a matrix of the "game area" of the screen. This view is simplified to be perfect for
        machine learning applications.

        In Tetris, this is only the part of the screen where the "tetrominoes" are placed.
        The score, lines cleared, and level can be found in the variables of this class.

        ```text
             0   1   2   3   4   5   6   7   8   9
        ____________________________________________
        0  | 47  47  47  47  47  47  47  47  47  47
        1  | 47  47  47  47  47  47  47  47  47  47
        2  | 47  47  47  47  47  47  47  132 132 132
        3  | 47  47  47  47  47  47  47  132 47  47
        4  | 47  47  47  47  47  47  47  47  47  47
        5  | 47  47  47  47  47  47  47  47  47  47
        6  | 47  47  47  47  47  47  47  47  47  47
        7  | 47  47  47  47  47  47  47  47  47  47
        8  | 47  47  47  47  47  47  47  47  47  47
        9  | 47  47  47  47  47  47  47  47  47  47
        10 | 47  47  47  47  47  47  47  47  47  47
        11 | 47  47  47  47  47  47  47  47  47  47
        12 | 47  47  47  47  47  47  47  47  47  47
        13 | 47  47  47  47  47  47  47  47  47  47
        14 | 47  47  47  47  47  47  47  47  47  47
        15 | 47  47  47  47  47  47  47  47  47  47
        16 | 47  47  47  47  47  47  47  47  47  47
        17 | 47  47  47  47  47  47  138 139 139 143
        ```

        Returns
        -------
        memoryview:
            Simplified 2-dimensional memoryview of the screen
        """
        return PyBoyGameWrapper.game_area(self)

    def next_tetromino(self):
        """
        Returns the next Tetromino to drop.

        __NOTE:__ Don't use this function together with
        `pyboy.plugins.game_wrapper_tetris.GameWrapperTetris.set_tetromino`.

        Returns
        -------
        shape:
            `str` of which Tetromino will drop:

            * `"L"`: L-shape
            * `"J"`: reverse L-shape
            * `"I"`: I-shape
            * `"O"`: square-shape
            * `"Z"`: zig-zag left to right
            * `"S"`: zig-zag right to left
            * `"T"`: T-shape
        """
        # Bitmask, as the last two bits determine the direction
        return inverse_tetromino_table[self.pyboy.memory[NEXT_TETROMINO_ADDR] & 0b11111100]

    def set_tetromino(self, shape):
        """
        This function patches the random Tetromino routine in the ROM to output any given Tetromino instead.

        __NOTE__: Any changes here are not saved or loaded to game states! Use this function with caution and reapply
        any overrides when reloading the ROM. This also applies to
        `pyboy.plugins.game_wrapper_tetris.GameWrapperTetris.start_game` and
        `pyboy.plugins.game_wrapper_tetris.GameWrapperTetris.reset_game`.

        Args:
            shape (str): Define which Tetromino to use:
            * `"L"`: L-shape
            * `"J"`: reverse L-shape
            * `"I"`: I-shape
            * `"O"`: square-shape
            * `"Z"`: zig-zag left to right
            * `"S"`: zig-zag right to left
            * `"T"`: T-shape
        """

        if shape not in tetromino_table:
            raise KeyError("Invalid Tetromino shape!")

        shape_number = tetromino_table[shape]

        # http://149.154.154.153/wiki/Tetris_(Game_Boy):ROM_map
        # Replacing:
        # ROM0:206E FA 13 C2         ld   a,(C213)             ;load next Tetromino in accumulator
        # ROM0:20B0 F0 AE            ld   a,(ff00+AE)

        patch1 = [
            0x3E,  # LD A, Tetromino
            shape_number,  # Tetromino
            0x00,  # NOOP
        ]

        for i, byte in enumerate(patch1):
            self.pyboy.memory[0, 0x206E + i] = byte

        patch2 = [
            0x3E,  # LD A, Tetromino
            shape_number,  # Tetromino
        ]

        for i, byte in enumerate(patch2):
            self.pyboy.memory[0, 0x20B0 + i] = byte

    def game_over(self):
        """
        After calling `start_game`, you can call this method at any time to know if the game is over.

        Game over happens, when the game area is filled with Tetrominos without clearing any rows.
        """
        return self.tilemap_background[2, 0] == 135  # The tile that fills up the screen when the game is over

    def __repr__(self):
        return (
            "Tetris:\n"
            + f"Score: {self.score}\n"
            + f"Level: {self.level}\n"
            + f"Lines: {self.lines}\n"
            + super().__repr__()
        )
