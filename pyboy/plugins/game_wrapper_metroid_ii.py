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
        self.global_metroid_count = 0
        # may need to change game area section. Copied from the kirby code
        super().__init__(*args, game_area_section=(0, 0, 20, 16), game_area_follow_scxy=True, **kwargs)

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True
        
        # Access RAM for a ton of information about the game
        # I'm getting all of the values from datacrystal
        # https://datacrystal.tcrf.net/wiki/Metroid_II:_Return_of_Samus/RAM_map
        # I've skipped some of the values like music related ones

        # X position within area (pixels/screen)
        self.x_pos_pixels = self.pyboy.memory[0xD027]
        self.y_pos_pixels = self.pyboy.memory[0xD028]
        self.x_pos_area = self.pyboy.memory[0xD029]
        self.y_pos_area = self.pyboy.memory[0xD02A]

        self.samus_facing = self.pyboy.memory[0xD02B]
        self.current_major_upgrades = self.pyboy.memory[0xD045]
        # Yeah I have no idea, just says "related to interacting with water"
        self.water_info = self.pyboy.memory[0xD048]

        self.current_beam = self.pyboy.memory[0xD04D]
        self.current_e_tanks = self.pyboy.memory[0xD050]
        self.current_hp = self.pyboy.memory[0xD051]
        self.current_full_e_tanks = self.pyboy.memory[0xD052]
        self.current_missiles = self.pyboy.memory[0xD053]

        # Question mark next to this one on datacrystal
        # self.num_sprites_onscreen = self.pyboy.memory[0xD064]

        self.current_missile_capacity = self.pyboy.memory[0xD081]

        self.displayed_hp = self.pyboy.memory[0xD084]
        self.displayed_missiles = self.pyboy.memory[0xD086]
        self.global_metroid_count = self.pyboy.memory[0xD09A]
        self.local_metroid_count = self.pyboy.memory[0xD0A7]

        # TODO calculate health percent using E tank counts



    def start_game(self, timer_div=None):
        """
        Call this function right after initializing PyBoy. This will navigate through menus to start the game at the
        first playable state.

        The state of the emulator is saved, and using `reset_game`, you can get back to this point of the game
        instantly.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """

        # TODO  implement me
        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, you can call this method at any time to reset the game.

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        print("Reset called from metroid gamewrapper")
        # TODO implement me
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
            # super().__repr__()
        )
        # yapf: enable
