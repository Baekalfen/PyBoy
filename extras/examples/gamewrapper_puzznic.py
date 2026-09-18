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
    print("Usage: python gamewrapper_puzznic.py [ROM file]")
    exit(1)

quiet = "--quiet" in sys.argv
pyboy = PyBoy(filename, window="null" if quiet else "SDL2", scale=3, debug=not quiet)
pyboy.set_emulation_speed(0)
assert pyboy.cartridge_title == "PUZZNIC"

puzznic = pyboy.game_wrapper
# The round can be reached two ways: `password` types it on the title screen the way a player
# would, and `stage` pokes the loader instead. The passwords come off the cartridge itself.
passwords = puzznic.passwords()
print(f"{len(passwords)} passwords in the cartridge, round 4 is {passwords[3]}")
puzznic.start_game(stage=0)

print(puzznic)

# Nothing has been matched away yet, so the two counters agree and the grid agrees with them.
assert puzznic.blocks_total > 0
assert puzznic.blocks_remaining == puzznic.blocks_total
assert len(puzznic.blocks()) == puzznic.blocks_remaining
assert not puzznic.stage_cleared()

# The cursor walks the playfield on its own; holding "a" turns a direction into a push.
cursor = puzznic.cursor
for _ in range(3):
    pyboy.button("right", 6)
    pyboy.tick(8, True)
    puzznic.settle()
print(f"Cursor went from {cursor} to {puzznic.cursor}")

# A push only happens where there is a block to push, so the board may well be untouched.
print(f"Blocks cleared: {puzznic.blocks_cleared}")
print(f"Blocks of each type left: {puzznic.block_counts()}")

puzznic.reset_game()
assert puzznic.blocks_remaining == puzznic.blocks_total

pyboy.stop(save=False)
