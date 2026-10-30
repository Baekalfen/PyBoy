#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
from types import SimpleNamespace

import pytest

import pyboy.api.screen as screen_module
from pyboy import PyBoy

from tests.test_replay import replay

from .conftest import BOOTROM_FRAMES_UNTIL_LOGO

replay_file = "tests/replays/default_rom.replay"


def test_null(default_rom):
    replay(default_rom, replay_file, "null", bootrom_file=None, padding_frames=BOOTROM_FRAMES_UNTIL_LOGO)


@pytest.mark.skipif(os.environ.get("TEST_NO_UI"), reason="Skipping test, as there is no UI")
def test_sdl2(default_rom):
    replay(default_rom, replay_file, "SDL2", bootrom_file=None, padding_frames=BOOTROM_FRAMES_UNTIL_LOGO)


@pytest.mark.skip()  # Something is wrong with PyOpenGL at the moment on all platforms
@pytest.mark.skipif(os.environ.get("TEST_NO_UI"), reason="Skipping test, as there is no UI")
def test_opengl(default_rom):
    replay(default_rom, replay_file, "OpenGL", bootrom_file=None, padding_frames=BOOTROM_FRAMES_UNTIL_LOGO)


@pytest.mark.skipif(os.environ.get("TEST_NO_UI"), reason="Skipping test, as there is no UI")
def test_glfw(default_rom):
    replay(default_rom, replay_file, "GLFW", bootrom_file=None, padding_frames=BOOTROM_FRAMES_UNTIL_LOGO)


def test_post_tick_exceptions_bubble_up(default_rom, monkeypatch):
    pyboy = PyBoy(default_rom, window="null")
    try:

        def failing_frombuffer(*args, **kwargs):
            raise RuntimeError("post_tick failure")

        # _post_tick refreshes the PIL image when it is writable
        monkeypatch.setattr(screen_module, "Image", SimpleNamespace(frombuffer=failing_frombuffer))
        pyboy.screen.image.readonly = False

        with pytest.raises(RuntimeError, match="post_tick failure"):
            pyboy.tick(1)
    finally:
        pyboy.stop(save=False)
