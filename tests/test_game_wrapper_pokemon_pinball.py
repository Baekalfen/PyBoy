#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import platform
import sys

import numpy as np
import pytest

from pyboy import PyBoy
from pyboy.utils import WindowEvent
from pyboy.plugins.game_wrapper_pokemon_pinball import Stage


def test_pokemon_pinball_basics(pokemon_pinball_rom):
    pyboy = PyBoy(pokemon_pinball_rom, window_type="null",game_wrapper=True)
    pyboy.set_emulation_speed(0)
    assert pyboy.cartridge_title == "POKEPINBALLVPH"

    pokemon_pinball = pyboy.game_wrapper
    pokemon_pinball.start_game()

    assert pokemon_pinball.score == 0
    assert pokemon_pinball.balls_left == 2
    assert pokemon_pinball.current_stage == Stage.RED_BOTTOM.value
    pyboy.stop()
