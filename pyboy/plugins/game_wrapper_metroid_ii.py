#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
__pdoc__ = {
    "GameWrapperMetroidII.cartridge_title": False,
    "GameWrapperMetroidII.post_tick": False,
}

import pyboy
from pyboy import utils
from pyboy.utils import WindowEvent
# for memory
from pyboy.utils import bcd_to_dec

from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)


class GameWrapperMetroidII(PyBoyGameWrapper):
    """
    This class wraps Metroid II, and provides easy access for AIs.
    If you call `print` on an instance of this object,
    it will show an overview of everything this object provides.
    """
    cartridge_title = "METROID2"

    def __init__(self, *args, **kwargs):

        self.x_pos_pixels = 0
        self.y_pos_pixels = 0
        self.x_pos_area = 0
        self.y_pos_area = 0
        self.pose = 0
        self.samus_facing = 0
        self.major_upgrades = 0
        self.beam = 0
        self.e_tanks = 0
        self.hp = 99
        self.full_e_tanks = 0
        self.missiles = 30
        self.missile_capacity = 30
        self.displayed_hp = 99
        self.displayed_missiles = 30
        self.global_metroid_count = 39
        self.local_metroid_count = 39

        self._game_over = False        
        # Screen shows 20x17 tiles
        super().__init__(*args, game_area_section=(0, 0, 20, 17), game_area_follow_scxy=True, **kwargs)

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True
        
        # All RAM addresses and constants sourced from:
        # https://datacrystal.tcrf.net/wiki/Metroid_II:_Return_of_Samus/RAM_map
        # https://github.com/alex-west/M2RoS/blob/main/SRC/constants.asm

        # TODO BEN change this at some point
        # Check screen for the word "GAME" (as in GAME OVER)
        # this could be done much faster by checking health
        # There's a death animation so the extra few seconds over thousands of
        # runs *could* add up. Proper timing analysis could confirm this
        if self.tilemap_background[6:10, 8] == [342, 336, 348, 340]:
            self._game_over = True
            # No need to update the rest of the values, we're dead!
            return

        # X position within area (pixels/screen)
        # In Metroid
        self.x_pos_pixels = self.pyboy.memory[0xD027]
        self.y_pos_pixels = self.pyboy.memory[0xD029]
        self.x_pos_area = self.pyboy.memory[0xD028]
        self.y_pos_area = self.pyboy.memory[0xD02A]

        self.pose = self.pyboy.memory[0xD020]
        self.samus_facing = self.pyboy.memory[0xD02B]
        self.major_upgrades = self.pyboy.memory[0xD045]

        # 8 bit (0b0000 1000) is missles mode, see constants in disassembly
        self.beam = bcd_to_dec(self.pyboy.memory[0xD04D])

        self.e_tanks = bcd_to_dec(self.pyboy.memory[0xD050])
        self.hp = bcd_to_dec(self.pyboy.memory[0xD051])
        self.full_e_tanks = self.pyboy.memory[0xD052]

        self.missiles = bcd_to_dec(self.pyboy.memory[0xD053])
        self.missile_capacity = bcd_to_dec(self.pyboy.memory[0xD081])

        # TODO figure out if there is a difference between these and the other
        # values
        self.displayed_hp = self.pyboy.memory[0xD084]
        self.displayed_missiles = bcd_to_dec(self.pyboy.memory[0xD086])

        self.global_metroid_count = bcd_to_dec(self.pyboy.memory[0xD09A])
        self.local_metroid_count = bcd_to_dec(self.pyboy.memory[0xD0A7])

        # TODO Verify these equations
        # self.real_health = self.full_e_tanks * 99) + self.hp
        # self.health_percent = self.real_health / ((self.e_tanks+1)*99)



    def start_game(self, timer_div=None):
        """
        Call this function right after initializing PyBoy. This will navigate through menus to start the game at the
        first playable state.

        The state of the emulator is saved, and using `reset_game`, you can get back to this point of the game
        instantly.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """

        # TODO Figure out the minimum possible values for these
        # instead of 300 and 500
        self.pyboy.tick(False)
        self.pyboy.button("start")
        self.pyboy.tick(300, False)

        # start the game
        self.pyboy.button("start")
        # wait for samus's "blinking" to stop
        self.pyboy.tick(500, False)
        
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
        # yapf: disable
        return (
            f"Metroid II:\n" +
            f"x_pos_pixels: {self.x_pos_pixels}\n" +
            f"y_pos_pixels: {self.y_pos_pixels}\n" +
            f"x_pos_area: {self.x_pos_area}\n" +
            f"y_pos_area: {self.y_pos_area}\n" +
            f"pose: {self.pose}\n" +
            f"samus_facing: {self.samus_facing}\n" +
            f"major_upgrades: {self.major_upgrades}\n" +
            f"beam: {self.beam}\n" +
            f"e_tanks: {self.e_tanks}\n" +
            f"hp: {self.hp}\n" +
            f"full_e_tanks: {self.full_e_tanks}\n" +
            f"missiles: {self.missiles}\n" +
            f"missile_capacity: {self.missile_capacity}\n" +
            f"displayed_hp: {self.displayed_hp}\n" +
            f"displayed_missiles: {self.displayed_missiles}\n" +
            f"global_metroid_count: {self.global_metroid_count}\n" +
            f"local_metroid_count: {self.local_metroid_count}\n" +
            super().__repr__()
        )
        # yapf: enable
