#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os

import pytest

from . import utils
from .test_replay import replay

replay_file = "tests/replays/kirby_gif.replay"


def test_headless():
    replay(utils.kirby_rom, replay_file, "headless")


def test_dummy():
    replay(utils.kirby_rom, replay_file, "dummy", verify=False)


@pytest.mark.skipif(os.environ.get("TEST_NO_UI"), reason="Skipping test, as there is no UI")
def test_opengl():
    replay(utils.kirby_rom, replay_file, "OpenGL")


@pytest.mark.skipif(os.environ.get("TEST_NO_UI"), reason="Skipping test, as there is no UI")
def test_sdl2():
    replay(utils.kirby_rom, replay_file, "SDL2")


@pytest.mark.skipif(os.environ.get("TEST_NO_UI"), reason="Skipping test, as there is no UI")
def test_scanline():
    replay(utils.kirby_rom, replay_file, "scanline", verify=False)
