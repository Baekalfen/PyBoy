#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy.botsupport.sprite import Sprite

from .base_plugin import PyBoyGameWrapper


class GameWrapperTetris(PyBoyGameWrapper):
    cartridge_title = "TETRIS"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tilemap_background = self.pyboy.get_tilemap_background()
        self.game_has_started = False
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

    def screen_matrix(self):
        tiles_matrix = self.tiles_on_screen()
        sprites = self.sprites_on_screen()
        for s in sprites:
            if s.x < 12*8:
                tiles_matrix[s.y//8][s.x//8-2] = s.tile_identifier
        return tiles_matrix

    def tiles_on_screen(self):
        if self._tile_cache_invalid:
            self._cached_tiles_on_screen = self.tilemap_background[2:12, 0:18]
            self._tile_cache_invalid = False
        return self._cached_tiles_on_screen

    def sprites_on_screen(self):
        if self._sprite_cache_invalid:
            self._cached_sprites_on_screen = [sprite for sprite in (Sprite(self.mb, s) for s in range(40)) if sprite.on_screen]
            self._sprite_cache_invalid = False
        return self._cached_sprites_on_screen

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True
        if not self.game_has_started:
            self.tilemap_background.refresh_lcdc()
            if self.tilemap_background[14:19, 1] == [28, 12, 24, 27, 14]: # "SCORSCORE the title bar
                self.game_has_started = True
            return 0

        if self.game_has_started:
            print(self)

    @property
    def score(self):
        blank = 47
        return sum([0 if x==blank else x*(10**(5-i)) for i, x in enumerate(self.tilemap_background[13:19, 3])])

    @property
    def level(self):
        blank = 47
        return sum([0 if x==blank else x*(10**(3-i)) for i, x in enumerate(self.tilemap_background[14:18, 7])])

    @property
    def lines(self):
        blank = 47
        return sum([0 if x==blank else x*(10**(3-i)) for i, x in enumerate(self.tilemap_background[14:18, 10])])

    @property
    def fitness(self):
        if self.game_has_started:
            return self.score
        else:
            return 0

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
                        for i, line in enumerate(self.screen_matrix())
                    ]
                )
            )
        return return_data
