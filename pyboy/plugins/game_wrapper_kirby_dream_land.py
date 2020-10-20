#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
__pdoc__ = {
    "GameWrapperKirbyDreamLand.cartridge_title": False,
    "GameWrapperKirbyDreamLand.post_tick": False,
}

from pyboy.logger import logger
from pyboy.utils import WindowEvent

from .base_plugin import PyBoyGameWrapper

try:
    from cython import compiled
    cythonmode = compiled
except ImportError:
    cythonmode = False


class GameWrapperKirbyDreamLand(PyBoyGameWrapper):
    """
    This class wraps Kirby Dream Land, and provides easy access to score and a "fitness" score for AIs.

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """
    cartridge_title = "KIRBY DREAM LA"

    def __init__(self, *args, **kwargs):
        self.shape = (20, 16)
        """The shape of the game area"""
        self.score = 0
        """The score provided by the game"""
        self.health = 0
        """The health provided by the game"""
        self.lives_left = 0
        """The lives remaining provided by the game"""
        self.fitness = 0
        """
        A built-in fitness scoring. Taking score, health, and lives left into account.

        .. math::
            fitness = score \\cdot health \\cdot lives\\_left
        """
        super().__init__(*args, game_area_section=(0, 0) + self.shape, game_area_wrap_around=True, **kwargs)

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        self.score = 0
        for n in range(4):
            self.score += self.pyboy.get_memory_value(0xD070 + n) * 10**n

        self.health = self.pyboy.get_memory_value(0xD086)
        self.lives_left = self.pyboy.get_memory_value(0xD089) - 1

        if self.game_has_started:
            self.fitness = self.score * self.health * self.lives_left

    def start_game(self, timer_div=None):
        """
        Call this function right after initializing PyBoy. This will navigate through menus to start the game at the
        first playable state.

        The state of the emulator is saved, and using `reset_game`, you can get back to this point of the game
        instantly.

        Kwargs:
            timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

        # Boot screen
        while True:
            self.pyboy.tick()
            self.tilemap_background.refresh_lcdc()
            if self.tilemap_background[0:3, 16] == [231, 224, 235]: # 'HAL' on the first screen
                break

        # Wait for transition to finish (start screen)
        for _ in range(25):
            self.pyboy.tick()

        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)

        # Wait for transition to finish (exit start screen, enter level intro screen)
        for _ in range(60):
            self.pyboy.tick()

        # Skip level intro
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)

        # Wait for transition to finish (exit level intro screen, enter game)
        for _ in range(60):
            self.pyboy.tick()

        self.game_has_started = True

        self.saved_state.seek(0)
        self.pyboy.save_state(self.saved_state)

        self._set_timer_div(timer_div)

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, you can call this method at any time to reset the game.

        Kwargs:
            timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)

        self._set_timer_div(timer_div)

    def game_area(self):
        """
        Use this method to get a matrix of the "game area" of the screen.

        ```text
              0   1   2   3   4   5   6   7   8   9
          ____________________________________________________________________________________
          0  | 383 383 383 301 383 383 383 297 383 383 383 301 383 383 383 297 383 383 383 293
          1  | 383 383 383 383 300 294 295 296 383 383 383 383 300 294 295 296 383 383 299 383
          2  | 311 318 319 320 383 383 383 383 383 383 383 383 383 383 383 383 383 301 383 383
          3  | 383 383 383 321 322 383 383 383 383 383 383 383 383 383 383 383 383 383 300 294
          4  | 383 383 383 383 323 290 291 383 383 383 313 312 311 318 319 320 383 290 291 383
          5  | 383 383 383 383 324 383 383 383 383 315 314 383 383 383 383 321 322 383 383 383
          6  | 383 383 383 383 324 293 292 383 383 316 383 383 383 383 383 383 323 383 383 383
          7  | 383 383 383 383 324 383 383 298 383 317 383 383 383 383 383 383 324 383 383 383
          8  | 319 320 383 383 324 383 383 297 383 317 383 383 383 152 140 383 324 383 383 307
          9  | 383 321 322 383 324 294 295 296 383 325 383 383 383 383 383 383 326 272 274 309
          10 | 383 383 323 383 326 383 383 383 2   18  383 330 331 331 331 331 331 331 331 331
          11 | 274 383 324 272 274 272 274 272 274 272 274 334 328 328 328 328 328 328 328 328
          12 | 331 331 331 331 331 331 331 331 331 331 331 328 328 328 328 328 328 328 328 328
          13 | 328 328 328 277 278 328 328 328 328 328 328 328 328 277 278 328 328 277 278 277
          14 | 328 277 278 279 281 277 278 328 328 277 278 277 278 279 281 277 278 279 281 279
          15 | 278 279 281 280 282 279 281 277 278 279 281 279 281 280 282 279 281 280 282 280
        ```

        Returns
        -------
        memoryview:
            Simplified 2-dimensional memoryview of the screen
        """
        return PyBoyGameWrapper.game_area(self)

    def game_over(self):
        return self.health == 0

    def __repr__(self):
        adjust = 4
        # yapf: disable
        return (
            f"Kirby Dream Land:\n" +
            f"Score: {self.score}\n" +
            f"Health: {self.health}\n" +
            f"Lives left: {self.lives_left}\n" +
            f"Fitness: {self.fitness}\n" +
            "Sprites on screen:\n" +
            "\n".join([str(s) for s in self._sprites_on_screen()]) +
            "\n" +
            "Tiles on screen:\n" +
            " "*5 + "".join([f"{i: <4}" for i in range(10)]) + "\n" +
            "_"*(adjust*20+4) +
            "\n" +
            "\n".join(
                [
                    f"{i: <3}| " + "".join([str(tile).ljust(adjust) for tile in line])
                    for i, line in enumerate(self.game_area())
                ]
            )
        )
        # yapf: enable
