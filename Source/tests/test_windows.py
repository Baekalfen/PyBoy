#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from test_replay import replay
from tests import utils

replay_file = "tests/replays/kirby_gif.replay"


def test_opengl():
    replay(utils.kirby_rom, replay_file, 'OpenGL')


def test_headless():
    replay(utils.kirby_rom, replay_file, 'headless')


def test_sdl2():
    replay(utils.kirby_rom, replay_file, 'SDL2')


def test_dummy():
    replay(utils.kirby_rom, replay_file, 'dummy', verify=False)


def test_scanline():
    replay(utils.kirby_rom, replay_file, 'scanline', verify=False)
