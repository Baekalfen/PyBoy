#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

__pdoc__ = {
    "GameWrapper2048.cartridge_title": False,
    "GameWrapper2048.post_tick": False,
}

import pyboy
from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)


def enabled(self):
    import hashlib

    try:
        with open(self.pyboy.gamerom_file, "rb") as f:
            rom_hash = hashlib.md5(f.read()).hexdigest()
        return rom_hash == "6748719720d57a7dce48d07b2f3c5ede"
    except Exception as e:
        logger.error(f"Error occurred while checking ROM hash: {e}")
        return False


ADDR_SCORE_LOW = 0xC0E7
ADDR_SCORE_HIGH = 0xC0E8
ADDR_WINNER = 0xC0EB
ADDR_STATE = 0xC0EC
ADDR_BOARD_START = 0xC0B0

STATE_TITLE = 0
STATE_PLAYING = 1
STATE_WINNER = 2
STATE_GAMEOVER = 3


class GameWrapper2048(PyBoyGameWrapper):
    """
    This class wraps 2048 for Game Boy, and provides easy access for AIs.

    This game wrapper only works with the release of 2048 with MD5 6748719720d57a7dce48d07b2f3c5ede.

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """

    cartridge_title = None

    def __init__(self, *args, **kwargs):
        self.score = 0
        """The current score"""
        self.winner = False
        """True if the player has reached 2048"""
        self._game_over = False
        """True if the game is over"""
        self.board = [[0] * 5 for _ in range(5)]
        """The 5x5 board"""

        super().__init__(*args, game_area_section=(0, 0, 20, 18), **kwargs)

    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        low = self.pyboy.memory[ADDR_SCORE_LOW]
        high = self.pyboy.memory[ADDR_SCORE_HIGH]
        self.score = low + (high * 256)

        self.winner = self.pyboy.memory[ADDR_WINNER] == 1

        state = self.pyboy.memory[ADDR_STATE]
        self._game_over = state == STATE_GAMEOVER

        for i in range(25):
            addr = ADDR_BOARD_START + (i * 2)
            low = self.pyboy.memory[addr]
            high = self.pyboy.memory[addr + 1]
            val = high + (low * 256)
            row = i // 5
            col = i % 5
            self.board[row][col] = val

    def game_over(self):
        return self._game_over

    def __repr__(self):
        board_str = ""
        for row in self.board:
            board_str += "\t" + str(row) + "\n"

        return (
            "2048:\n"
            + f"Score: {self.score}\n"
            + f"Winner: {self.winner}\n"
            + f"Game Over: {self._game_over}\n"
            + f"Board:\n{board_str}"
            + super().__repr__()
        )
