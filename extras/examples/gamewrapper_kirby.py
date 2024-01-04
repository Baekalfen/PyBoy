#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import sys

# Makes us able to import PyBoy from the directory below
file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, file_path + "/../..")

from pyboy import PyBoy, WindowEvent # isort:skip

# Check if the ROM is given through argv
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    print("Usage: python gamewrapper_kirby.py [ROM file]")
    exit(1)

quiet = "--quiet" in sys.argv
pyboy = PyBoy(filename, window_type="null" if quiet else "SDL2", window_scale=3, debug=not quiet, game_wrapper=True)
pyboy.set_emulation_speed(0)
assert pyboy.cartridge_title == "KIRBY DREAM LA"

kirby = pyboy.game_wrapper
kirby.start_game()

assert kirby.score == 0
assert kirby.lives_left == 4
assert kirby.health == 6

pyboy.button_press("right")
for _ in range(280): # Walk for 280 ticks
    # We tick one frame at a time to still render the screen for every step
    pyboy.tick(1, True)

assert kirby.score == 800
assert kirby.health == 5

print(kirby)

kirby.reset_game()
assert kirby.score == 0
assert kirby.health == 6

pyboy.stop()
