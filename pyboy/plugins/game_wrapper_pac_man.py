#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
__pdoc__ = {
    "GameWrapperPacMan.cartridge_title": False,
    "GameWrapperPacMan.post_tick": False,
}

import pyboy
from pyboy.utils import PyBoyException

from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)

def enabled(self):
    import hashlib

    try:
        with open(self.pyboy.gamerom_file, "rb") as f:
            rom_hash = hashlib.md5(f.read()).hexdigest()
        return rom_hash == "cd9027e147f4605f26ee261c537441b3"
    except Exception as e:
        logger.error(f"Error occurred while checking ROM hash: {e}")
        return False


ADDR_SCORE_LO  = 0xD637   # tens + ones
ADDR_SCORE_MID = 0xD638   # thousands + hundreds
ADDR_SCORE_HI  = 0xD639   # hundred-thousands + ten-thousands

ADDR_LIVES = 0xD641
ADDR_LEVEL = 0xD643


def _bcd_score(lo, mid, hi):

    def bcd(b):
        return (b >> 4) * 10 + (b & 0x0F)

    return bcd(hi) * 10_000 + bcd(mid) * 100 + bcd(lo)


class GameWrapperPacMan(PyBoyGameWrapper):


    cartridge_title = "PAC-MAN"

    def __init__(self, *args, **kwargs):
        self.score = 0
        self.lives_left = 0
        self.level = 0
        self._game_over = False

        super().__init__(*args, game_area_section=(0, 2, 20, 16), game_area_follow_scxy=True, **kwargs)


    def post_tick(self):
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        self.score = _bcd_score(
            self.pyboy.memory[ADDR_SCORE_LO],
            self.pyboy.memory[ADDR_SCORE_MID],
            self.pyboy.memory[ADDR_SCORE_HI],
        )

        prev_lives = self.lives_left
        self.lives_left = self.pyboy.memory[ADDR_LIVES]
        #Calculating game over based on the previous lives
        if prev_lives > 0 and self.lives_left == 0:
            self._game_over = True

        self.level = self.pyboy.memory[ADDR_LEVEL]

    def game_over(self):
        return self._game_over

    def start_game(self, timer_div=None):
        if self.game_has_started:
            raise PyBoyException("Game already started. Call reset_game() to restart.")

        # Tick until the title screen score row shows the "1UP" label tile (287).
        # That tile only appears once the title-screen HUD has been drawn, which
        # means the attract loop has completed its boot sequence.
        while self.tilemap_background[0, 0] != 287:
            self.pyboy.tick(1, False)

        self.pyboy.button("start")
        self.pyboy.tick(1, False)

        # Wait until LIVES register is populated — that confirms Pac-Man has
        # spawned and the first playable frame is ready.
        while self.pyboy.memory[ADDR_LIVES] == 0:
            self.pyboy.tick(1, False)

        PyBoyGameWrapper.start_game(self, timer_div=timer_div)

    def reset_game(self, timer_div=None):

        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)
        self._game_over = False

    def __repr__(self):
        return (
            f"Pac-Man\n"
            f"Score:      {self.score}\n"
            f"Lives left: {self.lives_left}\n"
            f"Level:      {self.level}\n"
            f"Game over:  {self._game_over}\n"
        ) + super().__repr__()