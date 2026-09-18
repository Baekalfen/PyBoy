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
    print("Usage: python gamewrapper_flipull.py [ROM file]")
    exit(1)

quiet = "--quiet" in sys.argv
pyboy = PyBoy(filename, window="null" if quiet else "SDL2", scale=3, debug=not quiet)
pyboy.set_emulation_speed(0)
assert pyboy.cartridge_title == "FLIPULL"

flipull = pyboy.game_wrapper
flipull.start_game(stage=8)

# The stage table is read out of the cartridge, so it always matches the ROM in hand.
stages = flipull.stages()
number, clear_target, blocks = stages[7]
assert (flipull.stage, flipull.clear_target, flipull.blocks_remaining) == (number, clear_target, blocks)
print(f"{len(stages)} stages in the cartridge. Stage {number}: {blocks} blocks, clear at {clear_target}")

print(flipull)

# Which button throws, which sprites the player and the block in his hand are, and how long a
# direction has to be held for one row, are all measured off the cartridge rather than assumed.
flipull.calibrate()
print(f"Throw: {flipull.throw_button.upper()}, hold {flipull.press_ticks} frames to move one row")
print(f"Player is OAM slot {flipull.player_sprite}, holding a block of type {flipull.held_block()}")
print(f"Player is on row {flipull.player_row()}, which holds {flipull.row_blocks(flipull.player_row())}")

# Throw once. Nothing is settled until the block has crossed the field, landed, dropped its
# column and arced back into his hand, which is what `settle` waits out.
before = flipull.blocks_remaining
pyboy.button(flipull.throw_button, flipull.press_ticks)
flipull.settle()
print(f"Blocks: {before} -> {flipull.blocks_remaining} after {flipull.throws} throw(s)")

assert flipull.blocks_remaining <= before
assert not flipull.game_over()

flipull.reset_game()
assert flipull.blocks_remaining == before

pyboy.stop(save=False)
