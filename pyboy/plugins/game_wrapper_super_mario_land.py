#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import logging

from pyboy.utils import WindowEvent

from .base_plugin import PyBoyGameWrapper

logger = logging.getLogger(__name__)

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False


class GameWrapperSuperMarioLand(PyBoyGameWrapper):
    cartridge_title = "SUPER MARIOLAN"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, game_area_section = (0, 2, 20, 16), game_area_wrap_around=True, **kwargs)

        self.world = (0, 0)
        self.coins = 0
        self.lives_left = 0
        self.score = 0
        self.time_left = 0
        self.level_progress = 0
        self._level_progress_max = 0
        self.fitness = 0

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        self.world = self.tilemap_background[12, 1]-256, self.tilemap_background[14, 1]-256
        blank = 300
        self.coins = self._sum_number_on_screen(9, 1, 2, blank, -256)
        self.lives_left = self._sum_number_on_screen(6, 0, 2, blank, -256)
        self.score = self._sum_number_on_screen(0, 1, 6, blank, -256)
        self.time_left = self._sum_number_on_screen(17, 1, 3, blank, -256)

        level_block = self.pyboy.get_memory_value(0xC0AB)
        mario_x = self.pyboy.get_memory_value(0xC202)
        scx = self.pyboy.botsupport_manager().screen().tilemap_position_list()[16][0]
        self.level_progress = level_block*16 + (scx-7)%16 + mario_x

        if self.game_has_started:
            self._level_progress_max = max(self.level_progress, self._level_progress_max)
            end_score = self.score + self.time_left*10
            self.fitness = self.lives_left*10000 + end_score + self._level_progress_max*10

    def start_game(self):
        if not self.pyboy.frame_count == 0:
            logger.warning('Calling start_game from an already running game. This might not work.')

        # Boot screen
        while True:
            self.pyboy.tick()
            if self.tilemap_background[6:11, 13] == [284, 285, 266, 283, 285]: # "START" on the main menu
                break
        self.pyboy.tick()
        self.pyboy.tick()
        self.pyboy.tick()

        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)

        while True:
            self.pyboy.tick()
            self.tilemap_background.refresh_lcdc()

            # "MARIO" in the title bar and 0 is placed at score
            if self.tilemap_background[0:5, 0] == [278, 266, 283, 274, 280] and \
               self.tilemap_background[5, 1] == 256:
                self.game_has_started = True
                break

        self.saved_state.seek(0)
        self.pyboy.save_state(self.saved_state)

    def reset_game(self):
        self.saved_state.seek(0)
        self.pyboy.load_state(self.saved_state)
        self.post_tick()

    def __repr__(self):
        adjust = 4
        return (
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
                    for i, line in enumerate(self.game_area())
                ]
            )
        )
