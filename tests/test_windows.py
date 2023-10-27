#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os

import pytest

from tests.test_replay import replay

from .conftest import BOOTROM_FRAMES_UNTIL_LOGO

replay_file = "tests/replays/default_rom.replay"


def test_null(default_rom):
    replay(default_rom, replay_file, "null", bootrom_file=None, padding_frames=BOOTROM_FRAMES_UNTIL_LOGO)


@pytest.mark.skipif(os.environ.get("TEST_NO_UI"), reason="Skipping test, as there is no UI")
def test_sdl2(default_rom):
    replay(default_rom, replay_file, "SDL2", bootrom_file=None, padding_frames=BOOTROM_FRAMES_UNTIL_LOGO)


@pytest.mark.skipif(os.environ.get("TEST_NO_UI"), reason="Skipping test, as there is no UI")
def test_opengl(default_rom):
    replay(default_rom, replay_file, "OpenGL", bootrom_file=None, padding_frames=BOOTROM_FRAMES_UNTIL_LOGO)
