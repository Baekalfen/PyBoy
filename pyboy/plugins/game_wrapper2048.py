#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

__pdoc__ = {
    "GameWrapper2048.cartridge_title": False,
    "GameWrapper2048.post_tick": False,
}


import pyboy
from pyboy.utils import PyBoyException
from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)


STATE_TITLE = 0
STATE_PLAYING = 1
STATE_WINNER = 2
STATE_GAMEOVER = 3

# "PRESS START" tiles on the title screen's window layer (row 5, columns 5-13)
TITLE_PRESS_START_TILES = [294, 309, 296, 292, 311, 296, 295, 291, 293]

# Valid tile values recognized by the ROM (src/board.c); anything else is an empty cell
VALID_TILE_VALUES = frozenset({0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048})


class GameWrapper2048(PyBoyGameWrapper):
    """
    This class wraps 2048 for Game Boy, and provides easy access for AIs.

    This game wrapper only works with the release of 2048 with MD5 1efd562975966b55ada5fb88e7a95f6e. It's required to
    also have the .map file for the ROM. See PyBoy mirror of open-source ROMs https://pyboy.dk/mirror/

    If you call `print` on an instance of this object, it will show an overview of everything this object provides.
    """

    cartridge_title = "2048"

    def __init__(self, *args, **kwargs):
        self.score = 0
        """The current score"""
        self.winner = False
        """True if the player has reached 2048"""
        self._game_over = False
        """True if the game is over"""
        self.board = [[0] * 5 for _ in range(5)]
        """The 5x5 board"""
        self._addrs_loaded = False

        super().__init__(*args, game_area_section=(0, 0, 20, 18), **kwargs)

    def _load_addresses(self):
        _, self._addr_board_start = self.pyboy.symbol_lookup("_board")
        _, self._addr_score = self.pyboy.symbol_lookup("_score")
        _, self._addr_winner = self.pyboy.symbol_lookup("_winner")
        _, self._addr_state = self.pyboy.symbol_lookup("_state")
        self._addrs_loaded = True

    def start_game(self, timer_div=None):
        """
        Call this function right after initializing PyBoy. This will navigate through the boot/title screen and
        start the game at the first playable state.

        The state of the emulator is saved, and using `reset_game`, you can get back to this point of the game
        instantly.

        Args:
            timer_div (int): Replace timer's DIV register with this value. Use `None` to randomize.
        """

        if self.game_has_started:
            raise PyBoyException("Gamewrapper already started! Use 'reset_game' instead.")

        if not self._addrs_loaded:
            self._load_addresses()

        # Wait for the title screen instead of ticking a fixed number of frames
        while list(self.tilemap_window[5:14, 5]) != TITLE_PRESS_START_TILES:
            self.pyboy.tick(1, False)

        self.pyboy.button("start")
        while self.pyboy.memory[self._addr_state] != STATE_PLAYING:
            self.pyboy.tick(1, False)

        # Wait for the starting tiles to spawn, plus a short input-ignore period
        while self._non_zero_tile_count() < 2:
            self.pyboy.tick(1, False)
        for _ in range(30):
            self.pyboy.tick(1, False)

        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

    def post_tick(self):
        if not self._addrs_loaded:
            self._load_addresses()

        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        low = self.pyboy.memory[self._addr_score]
        high = self.pyboy.memory[self._addr_score + 1]
        self.score = low + (high * 256)

        self.winner = self.pyboy.memory[self._addr_winner] == 1

        state = self.pyboy.memory[self._addr_state]
        self._game_over = state == STATE_GAMEOVER

        for i in range(25):
            addr = self._addr_board_start + (i * 2)
            low = self.pyboy.memory[addr]
            high = self.pyboy.memory[addr + 1]
            val = low + (high * 256)
            row = i // 5
            col = i % 5
            self.board[row][col] = val if val in VALID_TILE_VALUES else 0

    def game_over(self):
        return self._game_over

    def _non_zero_tile_count(self):
        count = 0
        for row in self.board:
            for tile in row:
                if tile != 0:
                    count += 1
        return count

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
