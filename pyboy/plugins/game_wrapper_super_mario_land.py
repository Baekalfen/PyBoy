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
from pyboy.utils import PyBoyException, PyBoyInvalidInputException, _bcd_to_dec, bcd_to_dec, dec_to_bcd
from pyboy.api.constants import TILES

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
    142,
    143,
    221,
    222,
    231,
    232,
    233,
    234,
    235,
    236,
    301,
    302,
    303,
    304,
    319,
    340,
    352,
    353,
    355,
    356,
    357,
    358,
    359,
    360,
    361,
    362,
    381,
    382,
    383,
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

mapping_minimal = np.zeros(TILES, dtype=np.uint8)
minimal_list = [
    base_scripts + plane + submarine,
    coin + mushroom + heart + star + lever,
    neutral_blocks + moving_blocks + pushable_blokcs + question_block + pipes,
    goomba
    + koopa
    + plant
    + moth
    + flying_moth
    + sphinx
    + big_sphinx
    + fist
    + bill
    + projectiles
    + shell
    + explosion
    + spike,
]
for i, tile_list in enumerate(minimal_list):
    for tile in tile_list:
        mapping_minimal[tile] = i + 1

mapping_compressed = np.zeros(TILES, dtype=np.uint8)
compressed_list = [
    base_scripts,
    plane,
    submarine,
    shoots,
    coin,
    mushroom,
    heart,
    star,
    lever,
    neutral_blocks,
    moving_blocks,
    pushable_blokcs,
    question_block,
    pipes,
    goomba,
    koopa,
    plant,
    moth,
    flying_moth,
    sphinx,
    big_sphinx,
    fist,
    bill,
    projectiles,
    shell,
    explosion,
    spike,
]
for i, tile_list in enumerate(compressed_list):
    for tile in tile_list:
        mapping_compressed[tile] = i + 1

np_in_mario_tiles = np.vectorize(lambda x: x in base_scripts)

# Apparantly that address is for lives left
# https://datacrystal.romhacking.net/wiki/Super_Mario_Land:RAM_map
ADDR_TIME_LEFT = 0xDA01
ADDR_LIVES_LEFT = 0xDA15
ADDR_LIVES_LEFT_DISPLAY = 0x9806
ADDR_WORLD_LEVEL = 0xFFB4
ADDR_WIN_COUNT = 0xFF9A


def _bcm_to_dec(value):
    return (value >> 4) * 10 + (value & 0x0F)


class GameWrapperSuperMarioLand(PyBoyGameWrapper):
    """
    This class wraps Super Mario Land, and provides easy access to score, coins, lives left, time left and world for AIs.

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.

    ![Super Mario Land](supermarioland.png)
    ```python
    >>> pyboy = PyBoy(supermarioland_rom)
    >>> pyboy.game_wrapper.start_game()
    >>> pyboy.tick(1, True)
    True
    >>> pyboy.screen.image.resize((320,288)).save('docs/plugins/supermarioland.png') # The exact screenshot shown above
    >>> pyboy.game_wrapper
    Super Mario Land: World 1-1
    Coins: 0
    lives_left: 2
    Score: 0
    Time left: 400
    Level progress: 251
    Sprites on screen:
    Sprite [3]: Position: (35, 112), Shape: (8, 8), Tiles: (Tile: 0), On screen: True
    Sprite [4]: Position: (43, 112), Shape: (8, 8), Tiles: (Tile: 1), On screen: True
    Sprite [5]: Position: (35, 120), Shape: (8, 8), Tiles: (Tile: 16), On screen: True
    Sprite [6]: Position: (43, 120), Shape: (8, 8), Tiles: (Tile: 17), On screen: True
    Tiles on screen:
           0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19
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
    12 | 300 368 369 300   0   1 300 306 307 305 300 300 300 300 350 300 300 300 300 300
    13 | 310 370 371 300  16  17 300 305 300 305 300 300 300 300 300 350 300 300 300 300
    14 | 352 352 352 352 352 352 352 352 352 352 352 352 352 352 352 352 352 352 352 352
    15 | 353 353 353 353 353 353 353 353 353 353 353 353 353 353 353 353 353 353 353 353
    ```

    """

    cartridge_title = "SUPER MARIOLAND"
    mapping_compressed = mapping_compressed
    """
    Compressed mapping for `pyboy.PyBoy.game_area_mapping`

    Example using `mapping_compressed`, Mario is `1`. He is standing on the ground which is `10`:
    ```python
    >>> pyboy = PyBoy(supermarioland_rom)
    >>> pyboy.game_wrapper.start_game()
    >>> pyboy.game_wrapper.game_area_mapping(pyboy.game_wrapper.mapping_compressed, 0)
    >>> pyboy.game_wrapper.game_area()
    array([[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0,  0,  0,  0,  0, 13,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0, 14, 14,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [ 0, 14, 14,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
           [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
           [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]], dtype=uint32)
    ```
    """
    mapping_minimal = mapping_minimal
    """
    Minimal mapping for `pyboy.PyBoy.game_area_mapping`

    Example using `mapping_minimal`, Mario is `1`. He is standing on the ground which is `3`:
    ```python
    >>> pyboy = PyBoy(supermarioland_rom)
    >>> pyboy.game_wrapper.start_game()
    >>> pyboy.game_wrapper.game_area_mapping(pyboy.game_wrapper.mapping_minimal, 0)
    >>> pyboy.game_wrapper.game_area()
    array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 3, 3, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 3, 3, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
           [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]], dtype=uint32)
    ```
    """

    def __init__(self, *args, **kwargs):
        self.world = (0, 0)
        """
        Provides the current "world" Mario is in, as a tuple of as two integers (world, level).

        You can force a level change with `GameWrapperSuperMarioLand.set_world_level`.

        Example:
        ```python
        >>> pyboy = PyBoy(supermarioland_rom)
        >>> pyboy.game_wrapper.start_game()
        >>> pyboy.game_wrapper.world
        (1, 1)
        ```

        """
        self.coins = 0
        """
        The number of collected coins.

        Example:
        ```python
        >>> pyboy = PyBoy(supermarioland_rom)
        >>> pyboy.game_wrapper.start_game()
        >>> pyboy.game_wrapper.coins
        0
        ```
        """
        self.lives_left = 0
        """
        The number of lives Mario has left.

        You can change this with `GameWrapperSuperMarioLand.set_lives_left`.

        Example:
        ```python
        >>> pyboy = PyBoy(supermarioland_rom)
        >>> pyboy.game_wrapper.start_game()
        >>> pyboy.game_wrapper.lives_left
        2
        ```
        """
        self.score = 0
        """
        The score provided by the game

        Example:
        ```python
        >>> pyboy = PyBoy(supermarioland_rom)
        >>> pyboy.game_wrapper.start_game()
        >>> pyboy.game_wrapper.score
        0
        ```
        """
        self.time_left = 0
        """
        The number of seconds left to finish the level.

        You can change this with `GameWrapperSuperMarioLand.set_time_left`.

        Example:
        ```python
        >>> pyboy = PyBoy(supermarioland_rom)
        >>> pyboy.game_wrapper.start_game()
        >>> pyboy.game_wrapper.time_left
        400
        ```
        """
        self.level_progress = 0
        """
        An integer of the current "global" X position in this level. Can be used for AI scoring.

        Example:
        ```python
        >>> pyboy = PyBoy(supermarioland_rom)
        >>> pyboy.game_wrapper.start_game()
        >>> pyboy.game_wrapper.level_progress
        251
        ```
        """

        super().__init__(*args, game_area_section=(0, 2, 20, 16), game_area_follow_scxy=True, **kwargs)

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        world_level = self.pyboy.memory[ADDR_WORLD_LEVEL]
        self.world = world_level >> 4, world_level & 0x0F
        blank = 300
        self.coins = self._sum_number_on_screen(9, 1, 2, blank, -256)
        self.lives_left = bcd_to_dec(self.pyboy.memory[ADDR_LIVES_LEFT])
        self.score = self._sum_number_on_screen(0, 1, 6, blank, -256)

        _time_left = _bcd_to_dec(self.pyboy.memory[ADDR_TIME_LEFT : ADDR_TIME_LEFT + 2])
        self.time_left = _time_left[0] + _time_left[1] * 100

        level_block = self.pyboy.memory[0xC0AB]
        mario_x = self.pyboy.memory[0xC202]
        scx = self.pyboy.screen.tilemap_position_list[16][0]
        self.level_progress = level_block * 16 + (scx - 7) % 16 + mario_x

    def set_time_left(self, time):
        """
        Set the amount of time left to any number between 0 and 999.

        This should only be called when the game has started.

        Example:
        ```python
        >>> pyboy = PyBoy(supermarioland_rom)
        >>> pyboy.game_wrapper.start_game()
        >>> pyboy.game_wrapper.time_left
        400
        >>> pyboy.game_wrapper.set_time_left(123)
        >>> pyboy.tick(1, False)
        True
        >>> pyboy.game_wrapper.time_left
        123
        ```

        Args:
            time (int): The wanted time left
        """
        if not self.game_has_started:
            logger.warning("Please call set_lives_left after starting the game")

        if 0 <= time <= 999:
            self.pyboy.memory[ADDR_TIME_LEFT] = dec_to_bcd(time % 100)
            self.pyboy.memory[ADDR_TIME_LEFT + 1] = time // 100
        else:
            raise PyBoyInvalidInputException(f"{time} is out of bounds. Only values between 0 and 999 allowed.")

    def set_lives_left(self, amount):
        """
        Set the amount lives to any number between 0 and 99.

        This should only be called when the game has started.

        Example:
        ```python
        >>> pyboy = PyBoy(supermarioland_rom)
        >>> pyboy.game_wrapper.start_game()
        >>> pyboy.game_wrapper.lives_left
        2
        >>> pyboy.game_wrapper.set_lives_left(10)
        >>> pyboy.tick(1, False)
        True
        >>> pyboy.game_wrapper.lives_left
        10
        ```

        Args:
            amount (int): The wanted number of lives
        """
        if not self.game_has_started:
            logger.warning("Please call set_lives_left after starting the game")

        if 0 <= amount <= 99:
            v = dec_to_bcd(amount)
            self.pyboy.memory[ADDR_LIVES_LEFT] = v
            self.pyboy.memory[ADDR_LIVES_LEFT_DISPLAY] = (v >> 4) & 0xF
            self.pyboy.memory[ADDR_LIVES_LEFT_DISPLAY + 1] = v & 0xF
        else:
            raise PyBoyInvalidInputException(f"{amount} is out of bounds. Only values between 0 and 99 allowed.")

    def set_world_level(self, world, level):
        """
        Patches the handler for pressing start in the menu. It hardcodes a world and level to always "continue" from.

        Example:
        ```python
        >>> pyboy = PyBoy(supermarioland_rom)
        >>> pyboy.game_wrapper.set_world_level(3, 2)
        >>> pyboy.game_wrapper.start_game()
        >>> pyboy.game_wrapper.world
        (3, 2)
        ```

        Args:
            world (int): The world to select a level from, 0-3
            level (int): The level to start from, 0-2
        """

        for i in range(0x450, 0x461):
            self.pyboy.memory[0, i] = 0x00

        patch1 = [
            0x3E,  # LD A, d8
            (world << 4) | (level & 0x0F),  # d8
        ]

        for i, byte in enumerate(patch1):
            self.pyboy.memory[0, 0x451 + i] = byte

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

        Example:
        ```python
        >>> pyboy = PyBoy(supermarioland_rom)
        >>> pyboy.game_wrapper.start_game(world_level=(4,1))
        >>> pyboy.game_wrapper.world
        (4, 1)
        ```

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
            * world_level (tuple): (world, level) to start the game from
            * unlock_level_select (bool): Unlock level selector menu
        """

        if self.game_has_started:
            raise PyBoyException("Gamewrapper already started! Use 'reset' instead.")

        if world_level is not None:
            self.set_world_level(*world_level)

        # Boot screen
        while True:
            self.pyboy.tick(1, False)
            if self.tilemap_background[6:11, 13] == [284, 285, 266, 283, 285]:  # "START" on the main menu
                break

        self.pyboy.tick(3, False)
        self.pyboy.button("start")
        self.pyboy.tick(1, False)

        while True:
            if (
                unlock_level_select and self.pyboy.frame_count == 71
            ):  # An arbitrary frame count, where the write will work
                self.pyboy.memory[ADDR_WIN_COUNT] = 2 if unlock_level_select else 0
                break
            self.pyboy.tick(1, False)

            # "MARIO" in the title bar and 0 is placed at score
            if self.tilemap_background[0:5, 0] == [278, 266, 283, 274, 280] and self.tilemap_background[5, 1] == 256:
                # Game has started
                break

        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

    def reset_game(self, timer_div=None):
        """
        After calling `start_game`, use this method to reset Mario to the beginning of `start_game`.

        If you want to reset to other worlds or levels of the game -- for example world 1-2 or 3-1 -- reset the entire
        emulator and provide the `world_level` on `start_game`.

        Example:
        ```python
        >>> pyboy = PyBoy(supermarioland_rom)
        >>> pyboy.game_wrapper.start_game()
        >>> pyboy.game_wrapper.reset_game()
        ```

        Kwargs:
            * timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """
        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)

    def game_area(self):
        """
        Use this method to get a matrix of the "game area" of the screen. This view is simplified to be perfect for
        machine learning applications.

        In Super Mario Land, this is almost the entire screen, expect for the top part showing the score, lives left
        and so on. These values can be found in the variables of this class.

        In this example using `GameWrapperSuperMarioLand.mapping_minimal`, Mario is `1`. He is standing on the ground which is `3`:
        ```python
        >>> pyboy = PyBoy(supermarioland_rom)
        >>> pyboy.game_wrapper.start_game()
        >>> pyboy.game_wrapper.game_area_mapping(pyboy.game_wrapper.mapping_minimal, 0)
        >>> pyboy.game_wrapper.game_area()
        array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 3, 3, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 3, 3, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
               [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]], dtype=uint32)
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
        return self.pyboy.memory[0xC0A4] == 0x39

    def __repr__(self):
        return (
            f"Super Mario Land: World {'-'.join([str(i) for i in self.world])}\n"
            f"Coins: {self.coins}\n"
            + f"lives_left: {self.lives_left}\n"
            + f"Score: {self.score}\n"
            + f"Time left: {self.time_left}\n"
            + f"Level progress: {self.level_progress}\n"
            + super().__repr__()
        )
