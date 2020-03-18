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


class GameWrapperSuperMarioLand(PyBoyGameWrapper):
    cartridge_title = "SUPER MARIOLAN"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.world = (0, 0)
        self.coins = 0
        self.lives_left = 0
        self.score = 0
        self.time_left = 0
        self.level_progress = 0
        self.fitness = 0

        ROWS, COLS = 20, 16
        self._cached_tiles_on_screen_raw = array('B', [0xFF] * (ROWS*COLS*4))

        if cythonmode:
            self._cached_tiles_on_screen = memoryview(self._cached_tiles_on_screen_raw).cast('I', shape=(ROWS, COLS))
        else:
            v = memoryview(self._cached_tiles_on_screen_raw).cast('I')
            self._cached_tiles_on_screen = [v[i:i+COLS] for i in range(0, COLS*ROWS, COLS)]

    def screen_matrix(self):
        tiles_matrix = self.tiles_on_screen()
        sprites = self.sprites_on_screen()
        for s in sprites:
            tiles_matrix[s.y//8-2][s.x//8] = s.tile_identifier
        return tiles_matrix

    def tiles_on_screen(self):
        if self._tile_cache_invalid:
            scroll_x = self.pyboy.get_screen().get_tilemap_position_list()[16, 0]
            self._cached_tiles_on_screen = np.asarray([[self.tilemap_background.get_tile_identifier(x%32, y) for x in range(scroll_x//8,scroll_x//8+20)] for y in range(2, 18)], dtype=np.uint32)
            self._tile_cache_invalid = False
        return self._cached_tiles_on_screen

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True
        if not self.game_has_started:
            self.tilemap_background.refresh_lcdc()
            if self.tilemap_background[0:5, 0] == [278, 266, 283, 274, 280]: # "MARIO" in the title bar
                self.game_has_started = True

        if self.game_has_started:
            print(self)

        self.world = self.tilemap_background[12, 1]-256, self.tilemap_background[14, 1]-256
        self.coins = (self.tilemap_background[9, 1]-256)*10 + self.tilemap_background[10, 1]-256
        self.lives_left = (self.tilemap_background[6, 0]-256)*10 + self.tilemap_background[7, 0]-256

        blank = 300
        self.score = sum([0 if x==blank else (x-256)*(10**(5-i)) for i, x in enumerate(self.tilemap_background[0:6, 1])])
        self.time_left = sum([0 if x==blank else (x-256)*(10**(2-i)) for i, x in enumerate(self.tilemap_background[17:20, 1])])

        level_block = self.pyboy.get_memory_value(0xC0AB)
        mario_x = self.pyboy.get_memory_value(0xC202)
        scx = self.pyboy.get_screen().get_tilemap_position_list()[16, 0]
        self.level_progress = level_block*16 + (scx-7)%16 + mario_x

        if self.game_has_started:
            end_score = self.score + self.time_left*10
            self.fitness = self.lives_left*10000 + end_score + self.level_progress*10

    def __repr__(self):
        adjust = 4
        return_data = (
                f"Super Mario Land: World {'-'.join([str(i) for i in self.world])}\n" +
                f"Coins: {self.coins}\n" +
                f"lives_left: {self.lives_left}\n" +
                f"Score: {self.score}\n" +
                f"Time left: {self.time_left}\n" +
                f"Level progress: {self.level_progress}\n" +
                f"Fitness: {self.fitness}\n" +
                "Sprites on screen:\n" +
                "\n".join([str(s) for s in self.sprites_on_screen()]) +
                "\n" +
                "Tiles on screen:\n" +
                " "*5 + "".join([f"{i: <4}" for i in range(20)]) + "\n" +
                "_"*(adjust*20+4) +
                "\n" +
                "\n".join(
                    [
                        f"{i: <3}| " + "".join([str(tile).ljust(adjust) for tile in line])
                        for i, line in enumerate(self.screen_matrix())
                    ]
                )
            )
        return return_data
