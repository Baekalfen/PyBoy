#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys
sys.path.append(".") # Adds higher directory to python modules path.

from test_replay import replay

rom_file = "ROMs/Tetris.gb"
replay_file = "tests/replays/tetris.replay"
# rom_file = "ROMs/POKEMON BLUE.gb"
# replay_file = "tests/replays/pokemon_blue.replay"

def test_opengl():
    replay(rom_file, replay_file, 'OpenGL')

def test_headless():
    replay(rom_file, replay_file, 'headless')

def test_sdl2():
    replay(rom_file, replay_file, 'SDL2')

def test_dummy():
    replay(rom_file, replay_file, 'dummy', verify=False)

def test_scanline():
    replay(rom_file, replay_file, 'scanline', verify=False)
