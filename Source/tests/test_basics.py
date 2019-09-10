#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys

from tests import utils

sys.path.append(".") # isort:skip
from pyboy import PyBoy, windowevent # isort:skip


any_rom = utils.tetris_rom


def test_all_argv():
    pyboy = PyBoy(any_rom, window_type="dummy", bootrom_file=utils.boot_rom, disable_input=True, hide_window=True)
    pyboy.tick()
    pyboy.send_input(windowevent.QUIT)
    pyboy.stop(save=False)


def test_all_buttons():
    pyboy = PyBoy(any_rom, window_type="dummy", bootrom_file=utils.boot_rom, disable_input=True, hide_window=True)
    pyboy.tick()
    pyboy.stop(save=False)
