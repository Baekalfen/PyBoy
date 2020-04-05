#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
__pdoc__ = {
    "GameWrapperTetris.cartridge_title": False,
    "GameWrapperTetris.post_tick": False,
}

import logging
from array import array

import numpy as np
from pyboy.utils import WindowEvent

from .base_plugin import PyBoyGameWrapper

logger = logging.getLogger(__name__)

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False


class GameWrapperTetris(PyBoyGameWrapper):
    """
    This class wraps Tetris, and provides easy access to score, lines, level and a "fitness" score for AIs.

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """
    cartridge_title = "TETRIS"

    def __init__(self, *args, **kwargs):
        self.shape = (10, 18)
        """The shape of the game area"""
        self.score = 0
        """The score provided by the game"""
        self.level = 0
        """The current level"""
        self.lines = 0
        """The number of cleared lines"""
        self.fitness = 0
        """
        A built-in fitness scoring. The scoring is equals to `score`.

        .. math::
            fitness = score
        """
        super().__init__(*args, **kwargs)

        ROWS, COLS = self.shape
        self._cached_game_area_tiles_raw = array("B", [0xFF] * (ROWS*COLS*4))

        if cythonmode:
            self._cached_game_area_tiles = memoryview(self._cached_game_area_tiles_raw).cast("I", shape=(ROWS, COLS))
        else:
            v = memoryview(self._cached_game_area_tiles_raw).cast("I")
            self._cached_game_area_tiles = [v[i:i + COLS] for i in range(0, COLS * ROWS, COLS)]

    def _game_area_tiles(self):
        if self._tile_cache_invalid:
            self._cached_game_area_tiles = np.asarray(self.tilemap_background[2:12, :18], dtype=np.uint32)
            self._tile_cache_invalid = False
        return self._cached_game_area_tiles

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        blank = 47
        self.tilemap_background.refresh_lcdc()
        self.score = self._sum_number_on_screen(13, 3, 6, blank, 0)
        self.level = self._sum_number_on_screen(14, 7, 4, blank, 0)
        self.lines = self._sum_number_on_screen(14, 10, 4, blank, 0)

        if self.game_has_started:
            self.fitness = self.score

    def start_game(self):
        """
        Call this function right after initializing PyBoy. This will navigate through menus to start the game at the
        first playable state.

        The state of the emulator is saved, and using `reset_game`, you can get back to this point of the game
        instantly.
        """
        if not self.pyboy.frame_count == 0:
            logger.warning("Calling start_game from an already running game. This might not work.")

        # Boot screen
        while True:
            self.pyboy.tick()
            self.tilemap_background.refresh_lcdc()
            if self.tilemap_background[2:9, 14] == [89, 25, 21, 10, 34, 14, 27]: # '1PLAYER' on the first screen
                break

        # Start game. Just press Start when the game allows us.
        for _ in range(3):
            self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
            self.pyboy.tick()
            self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)

            for _ in range(6):
                self.pyboy.tick()

        self.game_has_started = True

        self.saved_state.seek(0)
        self.pyboy.save_state(self.saved_state)

    def reset_game(self):
        """
        After calling `start_game`, you can call this method at any time to reset the game.
        """
        self.saved_state.seek(0)
        self.pyboy.load_state(self.saved_state)
        self.post_tick()

    def _game_area_np(self):
        return np.asarray(self.game_area())

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
        tiles_matrix = self._game_area_tiles()
        sprites = self._sprites_on_screen()
        for s in sprites:
            if s.x < 12 * 8:
                tiles_matrix[s.y // 8][s.x // 8 - 2] = s.tile_identifier
        return tiles_matrix

    def __repr__(self):
        adjust = 4
        # yapf: disable
        return (
            f"Tetris:\n" +
            f"Score: {self.score}\n" +
            f"Level: {self.level}\n" +
            f"Lines: {self.lines}\n" +
            f"Fitness: {self.fitness}\n" +
            "Sprites on screen:\n" +
            "\n".join([str(s) for s in self._sprites_on_screen()]) +
            "\n" +
            "Tiles on screen:\n" +
            " "*5 + "".join([f"{i: <4}" for i in range(10)]) + "\n" +
            "_"*(adjust*10+4) +
            "\n" +
            "\n".join(
                [
                    f"{i: <3}| " + "".join([str(tile).ljust(adjust) for tile in line])
                    for i, line in enumerate(self._game_area_np())
                ]
            )
        )
        # yapf: enable
