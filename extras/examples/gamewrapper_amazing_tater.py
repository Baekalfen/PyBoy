#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import sys

# Makes us able to import PyBoy from the directory below
file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, file_path + "/../..")

from pyboy import PyBoy  # noqa

# Check if the ROM is given through argv
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    print("Usage: python gamewrapper_amazing_tater.py [ROM file]")
    exit(1)

quiet = "--quiet" in sys.argv
pyboy = PyBoy(filename, window="null" if quiet else "SDL2", scale=3, debug=not quiet)
pyboy.set_emulation_speed(0)
assert pyboy.cartridge_title == "AMAZING-TATER"

tater = pyboy.game_wrapper
# Rooms 0-40 are PUZZLE MODE's and 41-104 are BEGINNER MODE's, which is also what decides
# which entry of SELECT MODE the boot walks to.
tater.start_game(level=0)
assert tater.level_label() == "A-01"

print(tater)

assert tater.taters_total >= 1
assert tater.taters_home == 0
assert not tater.level_solved()
assert tater.exit_cell() is not None

# The room is already composed in work RAM, so everything a bot needs is a read away.
print(f"Room {tater.level_label()} is {tater.room_size[0]}x{tater.room_size[1]}")
print(f"Taters: {tater.taters()}")
print(f"Blocks: {len(tater.blocks())} squares, {len(tater.pits())} pits")
print(f"Turnstiles: {tater.turnstiles()}")

# Walk the character the controls are on one cell at a time. Nothing moves on its own here,
# so `settle` returns as soon as the step is over.
for direction in ("right", "right", "down"):
    pyboy.button(direction, 5)
    tater.settle()
    print(f"{direction}: taters now at {tater.taters()}")

# Select hands the controls to the next character, and the cartridge ignores anything pressed
# for the 33 frames after it, which `switch_tater` waits out.
if tater.taters_total > 1:
    tater.switch_tater()
    print(f"Controls are now on tater {tater.active_tater + 1}")

tater.reset_game()
assert tater.taters_home == 0

pyboy.stop(save=False)
