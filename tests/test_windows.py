#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os

import pytest
from tests.test_replay import replay
from tests.utils import BOOTROM_FRAMES_UNTIL_LOGO, default_rom

replay_file = "tests/replays/default_rom.replay"


def test_headless():
    replay(default_rom, replay_file, "headless", bootrom_file=None, padding_frames=BOOTROM_FRAMES_UNTIL_LOGO)


def test_dummy():
    replay(default_rom, replay_file, "dummy", bootrom_file=None, verify=False)


@pytest.mark.skipif(os.environ.get("TEST_NO_UI"), reason="Skipping test, as there is no UI")
def test_sdl2():
    replay(default_rom, replay_file, "SDL2", bootrom_file=None, padding_frames=BOOTROM_FRAMES_UNTIL_LOGO)


@pytest.mark.skipif(os.environ.get("TEST_NO_UI"), reason="Skipping test, as there is no UI")
def test_opengl():
    replay(default_rom, replay_file, "OpenGL", bootrom_file=None, padding_frames=BOOTROM_FRAMES_UNTIL_LOGO)
