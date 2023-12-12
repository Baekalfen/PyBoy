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
    print("Usage: python gamewrapper_mario.py [ROM file]")
    exit(1)

quiet = "--quiet" in sys.argv
pyboy = PyBoy(filename, window_type="null" if quiet else "SDL2", window_scale=3, debug=not quiet, game_wrapper=True)
pyboy.set_emulation_speed(0)
assert pyboy.cartridge_title() == "SUPER MARIOLAN"

mario = pyboy.game_wrapper
mario.start_game()

assert mario.score == 0
assert mario.lives_left == 2
assert mario.time_left == 400
assert mario.world == (1, 1)
assert mario.fitness == 0 # A built-in fitness score for AI development
last_fitness = 0

print(mario)

pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
for _ in range(1000):
    assert mario.fitness >= last_fitness
    last_fitness = mario.fitness

    pyboy.tick(1, True)
    if mario.lives_left == 1:
        assert last_fitness == 27700
        assert mario.fitness == 17700 # Loosing a live, means 10.000 points in this fitness scoring
        print(mario)
        break
else:
    print("Mario didn't die?")
    exit(2)

mario.reset_game()
assert mario.lives_left == 2

pyboy.stop()
