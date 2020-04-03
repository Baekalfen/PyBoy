#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

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
    cartridge_title = "TETRIS"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.score = 0
        self.level = 0
        self.lines = 0
        self.fitness = 0

        ROWS, COLS = 10, 18
        self._cached_tiles_on_screen_raw = array('B', [0xFF] * (ROWS*COLS*4))

        if cythonmode:
            self._cached_tiles_on_screen = memoryview(self._cached_tiles_on_screen_raw).cast('I', shape=(ROWS, COLS))
        else:
            v = memoryview(self._cached_tiles_on_screen_raw).cast('I')
            self._cached_tiles_on_screen = [v[i:i+COLS] for i in range(0, COLS*ROWS, COLS)]

    def _game_area_np(self):
        return np.asarray(self.game_area())

    def game_area(self):
        tiles_matrix = self.tiles_on_screen()
        sprites = self.sprites_on_screen()
        for s in sprites:
            if s.x < 12*8:
                tiles_matrix[s.y//8][s.x//8-2] = s.tile_identifier
        return tiles_matrix

    def tiles_on_screen(self):
        if self._tile_cache_invalid:
            self._cached_tiles_on_screen = np.asarray(self.tilemap_background[2:12, :18], dtype=np.uint32)
            self._tile_cache_invalid = False
        return self._cached_tiles_on_screen

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        blank = 47
        self.score = self._sum_number_on_screen(13, 3, 6, blank, 0)
        self.level = self._sum_number_on_screen(14, 7, 4, blank, 0)
        self.lines = self._sum_number_on_screen(14, 10, 4, blank, 0)

        if self.game_has_started:
            self.fitness = self.score

    def start_game(self):
        if not self.pyboy.frame_count == 0:
            logger.warning('Calling start_game from an already running game. This might not work.')

        # Boot screen
        while True:
            self.pyboy.tick()
            self.tilemap_background.refresh_lcdc()
            if self.tilemap_background[2:9, 14] == [89, 25, 21, 10, 34, 14, 27]: # '1PLAYER' on the first screen
                break

        # Start game. Just press Start when the game allows us.
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)

        for _ in range(6):
            self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)

        for _ in range(6):
            self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)

        for _ in range(6):
            self.pyboy.tick()

        self.game_has_started = True

        self.saved_state.seek(0)
        self.pyboy.save_state(self.saved_state)

    def reset_game(self):
        self.saved_state.seek(0)
        self.pyboy.load_state(self.saved_state)
        self.post_tick()

    def __repr__(self):
        adjust = 4
        return_data = (
                f"Tetris:\n" +
                f"Score: {self.score}\n" +
                f"Level: {self.level}\n" +
                f"Lines: {self.lines}\n" +
                f"Fitness: {self.fitness}\n" +
                "Sprites on screen:\n" +
                "\n".join([str(s) for s in self.sprites_on_screen()]) +
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
        return return_data
