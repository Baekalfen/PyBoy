#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
__pdoc__ = {
    "GameWrapperSuperMarioLand.cartridge_title": False,
    "GameWrapperSuperMarioLand.post_tick": False,
}

import numpy as np

import pyboy
from pyboy.utils import WindowEvent

from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)

# Mario and Daisy
base_scripts = list(range(81))
plane = list(range(99, 110))
submarine = list(range(112, 122))

# Mario shoots
shoots = [96, 110, 122]

# Bonuses
coin = [244]
mushroom = [131]
heart = [132]
star = [134]
flower = [224, 229]

# Lever for level end
lever = [255]

# Solid blocks
neutral_blocks = [
    142, 143, 221, 222, 231, 232, 233, 234, 235, 236, 301, 302, 303, 304, 319, 340, 352, 353, 355, 356, 357, 358, 359,
    360, 361, 362, 381, 382, 383
]
moving_blocks = [230, 238, 239]
pushable_blokcs = [128, 130, 354]
question_block = [129]
pipes = list(range(368, 381))

# Enemies
goomba = [144]
koopa = [150, 151, 152, 153]
plant = [146, 147, 148, 149]
moth = [160, 161, 162, 163, 176, 177, 178, 179]
flying_moth = [192, 193, 194, 195, 208, 209, 210, 211]
sphinx = [164, 165, 166, 167, 180, 181, 182, 183]
big_sphinx = [198, 199, 201, 202, 203, 204, 205, 214, 215, 217, 218, 219]
fist = [240, 241, 242, 243]
bill = [249]
projectiles = [172, 188, 196, 197, 212, 213, 226, 227]
shell = [154, 155]
explosion = [157, 158]
spike = [237]

TILES = 384
tiles_minimal = np.zeros(TILES, dtype=np.uint8)
minimal_list = [
    base_scripts + plane + submarine,
    coin + mushroom + heart + star + lever,
    neutral_blocks + moving_blocks + pushable_blokcs + question_block + pipes,
    goomba + koopa + plant + moth + flying_moth + sphinx + big_sphinx + fist + bill + projectiles + shell + explosion +
    spike,
]
for i, tile_list in enumerate(minimal_list):
    for tile in tile_list:
        tiles_minimal[tile] = i + 1

tiles_compressed = np.zeros(TILES, dtype=np.uint8)
compressed_list = [
    base_scripts, plane, submarine, shoots, coin, mushroom, heart, star, lever, neutral_blocks, moving_blocks,
    pushable_blokcs, question_block, pipes, goomba, koopa, plant, moth, flying_moth, sphinx, big_sphinx, fist, bill,
    projectiles, shell, explosion, spike
]
for i, tile_list in enumerate(compressed_list):
    for tile in tile_list:
        tiles_compressed[tile] = i + 1

np_in_mario_tiles = np.vectorize(lambda x: x in base_scripts)

# Apparantly that address is for lives left
# https://datacrystal.romhacking.net/wiki/Super_Mario_Land:RAM_map
ADDR_LIVES_LEFT = 0xDA15
ADDR_LIVES_LEFT_DISPLAY = 0x9806
ADDR_WORLD_LEVEL = 0xFFB4
ADDR_WIN_COUNT = 0xFF9A


def _bcm_to_dec(value):
    return (value >> 4) * 10 + (value & 0x0F)


class GameWrapperSuperMarioLand(PyBoyGameWrapper):
    """
    This class wraps Super Mario Land, and provides easy access to score, coins, lives left, time left, world and a
    "fitness" score for AIs.

    __Only world 1-1 is officially supported at the moment. Support for more worlds coming soon.__

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """
    cartridge_title = "SUPER MARIOLAN"
    tiles_compressed = tiles_compressed
    tiles_minimal = tiles_minimal

    def __init__(self, *args, **kwargs):
        self.shape = (20, 16)
        """The shape of the game area"""
        self.world = (0, 0)
        """Provides the current "world" Mario is in, as a tuple of as two integers (world, level)."""
        self.coins = 0
        """The number of collected coins."""
        self.lives_left = 0
        """The number of lives Mario has left"""
        self.score = 0
        """The score provided by the game"""
        self.time_left = 0
        """The number of seconds left to finish the level"""
        self.level_progress = 0
        """An integer of the current "global" X position in this level. Can be used for AI scoring."""
        self._level_progress_max = 0
        self.fitness = 0
        """
        A built-in fitness scoring. Taking points, level progression, time left, and lives left into account.

        .. math::
            fitness = (lives\\_left \\cdot 10000) + (score + time\\_left \\cdot 10) + (\\_level\\_progress\\_max \\cdot 10)
        """

        super().__init__(*args, game_area_section=(0, 2) + self.shape, game_area_wrap_around=True, **kwargs)

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        world_level = self.pyboy.get_memory_value(ADDR_WORLD_LEVEL)
        self.world = world_level >> 4, world_level & 0x0F
        blank = 300
        self.coins = self._sum_number_on_screen(9, 1, 2, blank, -256)
        self.lives_left = _bcm_to_dec(self.pyboy.get_memory_value(ADDR_LIVES_LEFT))
        self.score = self._sum_number_on_screen(0, 1, 6, blank, -256)
        self.time_left = self._sum_number_on_screen(17, 1, 3, blank, -256)

        level_block = self.pyboy.get_memory_value(0xC0AB)
        mario_x = self.pyboy.get_memory_value(0xC202)
        scx = self.pyboy.botsupport_manager().screen().tilemap_position_list()[16][0]
        self.level_progress = level_block*16 + (scx-7) % 16 + mario_x

        if self.game_has_started:
            self._level_progress_max = max(self.level_progress, self._level_progress_max)
            end_score = self.score + self.time_left * 10
            self.fitness = self.lives_left * 10000 + end_score + self._level_progress_max * 10

    def set_lives_left(self, amount):
        """
        Set the amount lives to any number between 0 and 99.

        This should only be called when the game has started.

        Args:
            amount (int): The wanted number of lives
        """
        if not self.game_has_started:
            logger.warning("Please call set_lives_left after starting the game")

        if 0 <= amount <= 99:
            tens = amount // 10
            ones = amount % 10
            self.pyboy.set_memory_value(ADDR_LIVES_LEFT, (tens << 4) | ones)
            self.pyboy.set_memory_value(ADDR_LIVES_LEFT_DISPLAY, tens)
            self.pyboy.set_memory_value(ADDR_LIVES_LEFT_DISPLAY + 1, ones)
        else:
            logger.error("%d is out of bounds. Only values between 0 and 99 allowed.", amount)

    def set_world_level(self, world, level):
        """
        Patches the handler for pressing start in the menu. It hardcodes a world and level to always "continue" from.

        Args:
            world (int): The world to select a level from, 0-3
            level (int): The level to start from, 0-2
        """

        for i in range(0x450, 0x461):
            self.pyboy.override_memory_value(0, i, 0x00)

        patch1 = [
            0x3E, # LD A, d8
            (world << 4) | (level & 0x0F), # d8
        ]

        for i, byte in enumerate(patch1):
            self.pyboy.override_memory_value(0, 0x451 + i, byte)

    def start_game(self, timer_div=None, world_level=None, unlock_level_select=False):
        """
        Call this function right after initializing PyBoy. This will start a game in world 1-1 and give back control on
        the first frame it's possible.

        The state of the emulator is saved, and using `reset_game`, you can get back to this point of the game
        instantly.

        The game has 4 major worlds with each 3 level. to start at a specific world and level, provide it as a tuple for
        the optional keyword-argument `world_level`.

        If you're not using the game wrapper for unattended use, you can unlock the level selector for the main menu.
        Enabling the selector, will make this function return before entering the game.

        Kwargs:
            timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
            world_level (tuple): (world, level) to start the game from
            unlock_level_select (bool): Unlock level selector menu
        """
        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

        if world_level is not None:
            self.set_world_level(*world_level)

        # Boot screen
        while True:
            self.pyboy.tick(1, False)
            if self.tilemap_background[6:11, 13] == [284, 285, 266, 283, 285]: # "START" on the main menu
                break

        self.pyboy.tick(3, False)
        self.pyboy.button("start")
        self.pyboy.tick(1, False)

        while True:
            if unlock_level_select and self.pyboy.frame_count == 71: # An arbitrary frame count, where the write will work
                self.pyboy.set_memory_value(ADDR_WIN_COUNT, 2 if unlock_level_select else 0)
                break
            self.pyboy.tick(1, False)
            self.tilemap_background.refresh_lcdc()

            # "MARIO" in the title bar and 0 is placed at score
            if self.tilemap_background[0:5, 0] == [278, 266, 283, 274, 280] and \
               self.tilemap_background[5, 1] == 256:
                self.game_has_started = True
                break

        self.saved_state.seek(0)
        self.pyboy.save_state(self.saved_state)

        self._set_timer_div(timer_div)

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, use this method to reset Mario to the beginning of world 1-1.

        If you want to reset to later parts of the game -- for example world 1-2 or 3-1 -- use the methods
        `pyboy.PyBoy.save_state` and `pyboy.PyBoy.load_state`.

        Kwargs:
            timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)

        self._set_timer_div(timer_div)

    def game_area(self):
        """
        Use this method to get a matrix of the "game area" of the screen. This view is simplified to be perfect for
        machine learning applications.

        In Super Mario Land, this is almost the entire screen, expect for the top part showing the score, lives left
        and so on. These values can be found in the variables of this class.

        In this example, Mario is `0`, `1`, `16` and `17`. He is standing on the ground which is `352` and `353`:
        ```text
             0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  17  18  19
        ____________________________________________________________________________________
        0  | 339 339 339 339 339 339 339 339 339 339 339 339 339 339 339 339 339 339 339 339
        1  | 320 320 320 320 320 320 320 320 320 320 320 320 320 320 320 320 320 320 320 320
        2  | 300 300 300 300 300 300 300 300 300 300 300 300 321 322 321 322 323 300 300 300
        3  | 300 300 300 300 300 300 300 300 300 300 300 324 325 326 325 326 327 300 300 300
        4  | 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300
        5  | 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300
        6  | 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300 300
        7  | 300 300 300 300 300 300 300 300 310 350 300 300 300 300 300 300 300 300 300 300
        8  | 300 300 300 300 300 300 300 310 300 300 350 300 300 300 300 300 300 300 300 300
        9  | 300 300 300 300 300 129 310 300 300 300 300 350 300 300 300 300 300 300 300 300
        10 | 300 300 300 300 300 310 300 300 300 300 300 300 350 300 300 300 300 300 300 300
        11 | 300 300 310 350 310 300 300 300 300 306 307 300 300 350 300 300 300 300 300 300
        12 | 300 368 369 300 0   1   300 306 307 305 300 300 300 300 350 300 300 300 300 300
        13 | 310 370 371 300 16  17  300 305 300 305 300 300 300 300 300 350 300 300 300 300
        14 | 352 352 352 352 352 352 352 352 352 352 352 352 352 352 352 352 352 352 352 352
        15 | 353 353 353 353 353 353 353 353 353 353 353 353 353 353 353 353 353 353 353 353
        ```

        Returns
        -------
        memoryview:
            Simplified 2-dimensional memoryview of the screen
        """
        return PyBoyGameWrapper.game_area(self)

    def game_over(self):
        # Apparantly that address is for game over
        # https://datacrystal.romhacking.net/wiki/Super_Mario_Land:RAM_map
        return self.pyboy.get_memory_value(0xC0A4) == 0x39

    def __repr__(self):
        adjust = 4
        # yapf: disable
        return (
            f"Super Mario Land: World {'-'.join([str(i) for i in self.world])}\n" +
            f"Coins: {self.coins}\n" +
            f"lives_left: {self.lives_left}\n" +
            f"Score: {self.score}\n" +
            f"Time left: {self.time_left}\n" +
            f"Level progress: {self.level_progress}\n" +
            f"Fitness: {self.fitness}\n" +
            "Sprites on screen:\n" +
            "\n".join([str(s) for s in self._sprites_on_screen()]) +
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
        # yapf: enable
