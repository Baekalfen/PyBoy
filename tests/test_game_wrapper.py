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

py_version = platform.python_version()[:3]
is_pypy = platform.python_implementation() == "PyPy"


def test_game_wrapper_basics(default_rom):
    pyboy = PyBoy(default_rom, window_type="null")
    pyboy.set_emulation_speed(0)

    generic_wrapper = pyboy.game_wrapper
    assert generic_wrapper is not None
    pyboy.game_area()
    pyboy.stop()


def test_game_wrapper_mapping(default_rom):
    pyboy = PyBoy(default_rom, window_type="null", debug=True)
    pyboy.set_emulation_speed(0)
    assert np.all(pyboy.game_area() == 256)

    generic_wrapper = pyboy.game_wrapper
    assert generic_wrapper is not None
    pyboy.tick(5, True)
    assert np.all(
        pyboy.game_area()[8:11,
                          8:13] == np.array([
                              [1, 0, 1, 0, 0],
                              [2, 3, 4, 5, 3],
                              [0, 6, 0, 0, 6],
                          ], dtype=np.uint32)
    )

    # List-based mapping, don't call tick
    mapping = [x for x in range(384)] # 1:1 mapping
    mapping[0] = 10
    mapping[1] = 10
    mapping[2] = 10
    mapping[3] = 10
    pyboy.game_area_mapping(mapping, 1000)
    assert np.all(
        pyboy.game_area()[8:11, 8:13] == np.array([
            [10, 10, 10, 10, 10],
            [10, 10, 4, 5, 10],
            [10, 6, 10, 10, 6],
        ],
                                                  dtype=np.uint32)
    )

    # Array-based mapping, don't call tick
    mapping = np.asarray(mapping)
    mapping[0] = 1 # Map tile identifier 0 -> 1
    mapping[1] = 1 # Map tile identifier 1 -> 1
    mapping[2] = 1 # Map tile identifier 2 -> 1
    mapping[3] = 1 # Map tile identifier 3 -> 1
    pyboy.game_area_mapping(mapping, 1000)
    assert np.all(
        pyboy.game_area()[8:11,
                          8:13] == np.array([
                              [1, 1, 1, 1, 1],
                              [1, 1, 4, 5, 1],
                              [1, 6, 1, 1, 6],
                          ], dtype=np.uint32)
    )

    pyboy.stop()
