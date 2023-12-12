#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import platform
import sys

import numpy as np
import pytest

from pyboy import PyBoy, WindowEvent

py_version = platform.python_version()[:3]
is_pypy = platform.python_implementation() == "PyPy"


def test_game_wrapper_basics(default_rom):
    pyboy = PyBoy(default_rom, window_type="null")
    pyboy.set_emulation_speed(0)

    generic_wrapper = pyboy.game_wrapper
    assert generic_wrapper is not None
    # pyboy.game_area()
    pyboy.stop()
