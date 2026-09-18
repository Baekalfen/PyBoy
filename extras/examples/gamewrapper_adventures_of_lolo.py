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
    print("Usage: python gamewrapper_adventures_of_lolo.py [ROM file]")
    exit(1)

quiet = "--quiet" in sys.argv
pyboy = PyBoy(filename, window="null" if quiet else "SDL2", scale=3, debug=not quiet)
pyboy.set_emulation_speed(0)
assert pyboy.cartridge_title == "LOLO2"

lolo = pyboy.game_wrapper
# Room 38 is the first graded room. The 163 slots run tutorial, intermediate, advanced, pro.
lolo.start_game(room=38)
assert lolo.room_label() == "int 1-1"

print(lolo)

# The rooms are flat and uncompressed in ROM, so a layout can be read without playing it.
for row in lolo.room_layout(38):
    print(f"  |{row}|")

assert lolo.hearts_left == sum(1 for _ in lolo.hearts())
assert not lolo.room_solved()
assert not lolo.game_over()

# Lolo lives on a half-cell grid: about 20 frames of a held direction moves one whole cell,
# and half that moves half of one. The enemies only move when he does.
start = lolo.lolo
for direction in ("right", "right", "down"):
    pyboy.button(direction, 20)
    lolo.settle()
    print(f"{direction}: Lolo at {lolo.lolo}, {lolo.hearts_left} hearts left, enemies at {lolo.enemies()}")

print(f"Lolo went from {start} to {lolo.lolo}")
print(f"The door at {lolo.door} is {'open' if lolo.door_open() else 'shut'}")

# A death is not a flag anywhere in RAM: the cartridge puts the room back the way it was, and
# the hearts already collected come back with it. That is what `game_over` reports.
if lolo.game_over():
    print("Lolo lost a life")
    lolo.reset_game()
    assert not lolo.game_over()

pyboy.stop(save=False)
