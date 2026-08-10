#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, file_path + "/../..")

from pyboy import PyBoy  # noqa

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    print("Usage: python gamewrapper_pandoras_blocks.py [ROM file]")
    exit(1)

quiet = "--quiet" in sys.argv
pyboy = PyBoy(filename, window="null" if quiet else "SDL2", scale=3, debug=not quiet)
pyboy.set_emulation_speed(0)
assert pyboy.cartridge_title == "DMGTRIS"

pandoras_blocks = pyboy.game_wrapper
pandoras_blocks.start_game(timer_div=0)

first_block = pandoras_blocks.next_block()
assert first_block in {"I", "Z", "S", "J", "L", "O", "T"}
assert pandoras_blocks.score == 0
assert pandoras_blocks.level == 0
assert pandoras_blocks.lines == 0

pandoras_blocks.set_block("T")
assert pandoras_blocks.next_block() == "T"

for frame in range(300):
    pyboy.tick(1, True)
    if frame % 2 == 0:
        pyboy.button("right")

assert pandoras_blocks.score == 0
assert pandoras_blocks.level == 0
assert pandoras_blocks.lines == 0
assert any(tile != 108 for tile in pandoras_blocks.game_area()[-1, :])

pyboy.stop(save=False)
