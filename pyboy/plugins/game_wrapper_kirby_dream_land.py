#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
__pdoc__ = {
    "GameWrapperKirbyDreamLand.cartridge_title": False,
    "GameWrapperKirbyDreamLand.post_tick": False,
}

import pyboy
from pyboy.utils import PyBoyException

from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)


class GameWrapperKirbyDreamLand(PyBoyGameWrapper):
    """
    This class wraps Kirby Dream Land, and provides easy access for AIs.

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """

    cartridge_title = "KIRBY DREAM LAN"

    def __init__(self, *args, **kwargs):
        self.score = 0
        """The score provided by the game"""
        self.health = 0
        """The health provided by the game"""
        self.lives_left = 0
        """The lives remaining provided by the game"""
        self._game_over = False
        """The game over state"""

        super().__init__(*args, game_area_section=(0, 0, 20, 16), game_area_follow_scxy=True, **kwargs)

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        self.score = 0
        score_digits = 4
        for n in range(score_digits):
            self.score += self.pyboy.memory[0xD070 + n] * 10 ** (score_digits - n)

        # Check if game is over
        prev_health = self.health
        self.health = self.pyboy.memory[0xD086]
        if self.lives_left == 0:
            if prev_health > 0 and self.health == 0:
                self._game_over = True

        self.lives_left = self.pyboy.memory[0xD089] - 1

    def start_game(self, timer_div=None):
        """
        Call this function right after initializing PyBoy. This will navigate through menus to start the game at the
        first playable state.

        The state of the emulator is saved, and using `reset_game`, you can get back to this point of the game
        instantly.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        if self.game_has_started:
            raise PyBoyException("Gamewrapper already started! Use 'reset' instead.")

        # Boot screen
        while True:
            self.pyboy.tick(1, False)
            if self.tilemap_background[0:3, 16] == [231, 224, 235]:  # 'HAL' on the first screen
                break

        # Wait for transition to finish (start screen)
        self.pyboy.tick(25, False)
        self.pyboy.button("start")
        self.pyboy.tick()

        # Wait for transition to finish (exit start screen, enter level intro screen)
        self.pyboy.tick(60, False)

        # Skip level intro
        self.pyboy.button("start")
        self.pyboy.tick()

        # Wait for transition to finish (exit level intro screen, enter game)
        self.pyboy.tick(60, False)

        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, you can call this method at any time to reset the game.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        self._game_over = False
        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)

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
        return self._game_over

    def __repr__(self):
        return (
            "Kirby Dream Land:\n"
            + f"Score: {self.score}\n"
            + f"Health: {self.health}\n"
            + f"Lives left: {self.lives_left}\n"
            + super().__repr__()
        )
