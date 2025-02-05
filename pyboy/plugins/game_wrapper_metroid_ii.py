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
    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """
    cartridge_title = "METROID2"

    def __init__(self, *args, **kwargs):
        self._game_over = False        
        # may need to change game area section. Copied from the kirby code
        super().__init__(*args, game_area_section=(0, 0, 20, 16), game_area_follow_scxy=True, **kwargs)

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True
        
        # Access RAM for a ton of information about the game
        # I'm getting all of the values from datacrystal
        # https://datacrystal.tcrf.net/wiki/Metroid_II:_Return_of_Samus/RAM_map
        # I've skipped some of the values like music related ones

        # Constants from decomp project
        # https://github.com/alex-west/M2RoS/blob/main/SRC/constants.asm


        # Check screen for the word "GAME" (as in GAME OVER)
        # this could be done much faster by checking health
        # There's a death animation so the extra few seconds over thousands of
        # runs *could* add up?
        if self.tilemap_background[6:10, 8] == [342, 336, 348, 340]:
            self._game_over = True
            # No need to update the rest of the values, we're dead!
            return

        # X position within area (pixels/screen)
        self.x_pos_pixels = self.pyboy.memory[0xD027]
        self.y_pos_pixels = self.pyboy.memory[0xD029]
        self.x_pos_area = self.pyboy.memory[0xD028]
        self.y_pos_area = self.pyboy.memory[0xD02A]

        self.pose = self.pyboy.memory[0xD020]

        self.samus_facing = self.pyboy.memory[0xD02B]
        self.current_major_upgrades = self.pyboy.memory[0xD045]
        # Yeah I have no idea, just says "related to interacting with water"
        self.water_info = self.pyboy.memory[0xD048]

        # 8 bit (0b0000 1000) is missles mode
        self.current_beam = bcd_to_dec(self.pyboy.memory[0xD04D])

        self.current_e_tanks = bcd_to_dec(self.pyboy.memory[0xD050])
        self.current_hp = bcd_to_dec(self.pyboy.memory[0xD051])
        self.current_full_e_tanks = self.pyboy.memory[0xD052]
        self.current_missiles = bcd_to_dec(self.pyboy.memory[0xD053])

        # Question mark next to this one on datacrystal
        # self.num_sprites_onscreen = self.pyboy.memory[0xD064]

        self.current_missile_capacity = bcd_to_dec(self.pyboy.memory[0xD081])

        self.displayed_hp = self.pyboy.memory[0xD084]
        self.displayed_missiles = bcd_to_dec(self.pyboy.memory[0xD086])
        self.global_metroid_count = bcd_to_dec(self.pyboy.memory[0xD09A])
        self.local_metroid_count = bcd_to_dec(self.pyboy.memory[0xD0A7])

        # TODO calculate health percent using E tank counts (?)



    def start_game(self, timer_div=None):
        """
        Call this function right after initializing PyBoy. This will navigate through menus to start the game at the
        first playable state.

        The state of the emulator is saved, and using `reset_game`, you can get back to this point of the game
        instantly.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """

        # NOTE, I may be able to make these tick waits shorter
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
        # TODO implement me, I don't know if I really need to do anything here?

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
            # TODO add relevant variables to print for debugging purposes
            f"XY Pixels: {(self.x_pos_pixels, self.y_pos_pixels)}\n" + 
            f"XY Area: {(self.x_pos_area, self.y_pos_area)}\n" + 
            f"Pose: {self.pose}\t" + 
            f"Facing: {self.samus_facing}\n" + 
            f"Upgrades: {self.current_major_upgrades}\n" + 
            f"Water Info: {self.water_info}\n" + 
            f"Curr Beam: {self.current_beam}\n" +
            f"Curr E tanks: {self.current_e_tanks}\n" + 
            f"Curr HP: {self.current_hp}\n" + 
            f"Curr Full E Tanks: {self.current_full_e_tanks}\n" + 
            f"Curr missiles: {self.current_missiles}\n" + 
            f"Curr missile capacity: {self.current_missile_capacity}\n" + 
            f"Displayed HP: {self.displayed_hp}\n" + 
            f"Displayed Missiles: {self.displayed_missiles}\n"+
            f"GMC: {self.global_metroid_count}\n" +  
            f"LMC: {self.global_metroid_count}\n"
            # I don't like seeing the huge grid whne trying to develop
            # The sprite list can be messy too, since many things (especially
            # samus) are composed of multiple sprites, so simply running causes
            # the output to constantly change "shape", making it very difficult
            # to read
            # super().__repr__()
        )
        # yapf: enable
