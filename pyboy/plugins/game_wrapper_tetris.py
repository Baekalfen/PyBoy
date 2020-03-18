#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from array import array

import numpy as np

from .base_plugin import PyBoyGameWrapper

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

    def screen_matrix_np(self):
        return np.asarray(self.screen_matrix())

    def screen_matrix(self):
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
        if not self.game_has_started:
            self.tilemap_background.refresh_lcdc()
            if self.tilemap_background[14:19, 1] == [28, 12, 24, 27, 14]: # "SCORE" the title bar
                self.game_has_started = True

        if self.game_has_started:
            print(self)

        blank = 47
        self.score = sum([0 if x==blank else x*(10**(5-i)) for i, x in enumerate(self.tilemap_background[13:19, 3])])
        self.level = sum([0 if x==blank else x*(10**(3-i)) for i, x in enumerate(self.tilemap_background[14:18, 7])])
        self.lines = sum([0 if x==blank else x*(10**(3-i)) for i, x in enumerate(self.tilemap_background[14:18, 10])])

        if self.game_has_started:
            self.fitness = self.score

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
                        for i, line in enumerate(self.screen_matrix_np())
                    ]
                )
            )
        return return_data
