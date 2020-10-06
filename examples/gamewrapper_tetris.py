#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import sys

# Makes us able to import PyBoy from the directory below
file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, file_path + "/..")

from pyboy import PyBoy, WindowEvent # isort:skip

# Check if the ROM is given through argv
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    print("Usage: python mario_boiler_plate.py [ROM file]")
    exit(1)

quiet = "--quiet" in sys.argv
pyboy = PyBoy(filename, window_type="headless" if quiet else "SDL2", window_scale=3, debug=not quiet, game_wrapper=True)
pyboy.set_emulation_speed(0)
assert pyboy.cartridge_title() == "TETRIS"

tetris = pyboy.game_wrapper()
tetris.start_game(timer_div=0x00) # The timer_div works like a random seed in Tetris

assert tetris.next_tetromino() == "Z"
assert tetris.score == 0
assert tetris.level == 0
assert tetris.lines == 0
assert tetris.fitness == 0 # A built-in fitness score for AI development

blank_tile = 47
first_brick = False
for frame in range(1000): # Enough frames for the test. Otherwise do: `while not pyboy.tick():`
    pyboy.tick()

    # The playing "technique" is just to move the Tetromino to the right.
    if frame % 2 == 0: # Even frames
        pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
    elif frame % 2 == 1: # Odd frames
        pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)

    # Illustrating how we can extract the game board quite simply. This can be used to read the tile identifiers.
    game_area = tetris.game_area()
    # game_area is accessed as [<row>, <column>].
    # 'game_area[-1,:]' is asking for all (:) the columns in the last row (-1)
    if not first_brick and any(filter(lambda x: x != blank_tile, game_area[-1, :])):
        first_brick = True
        print("First brick touched the bottom!")
        print(tetris)

print("Final game board mask:")
print(tetris)

# We shouldn't have made any progress with the moves we made
assert tetris.score == 0
assert tetris.level == 0
assert tetris.lines == 0
assert tetris.fitness == 0 # A built-in fitness score for AI development

# Assert there is something on the bottom of the game area
assert any(filter(lambda x: x != blank_tile, game_area[-1, :]))
tetris.reset_game(timer_div=0x00)
assert tetris.next_tetromino() == "Z"
# After reseting, we should have a clean game area
assert all(filter(lambda x: x != blank_tile, game_area[-1, :]))

tetris.reset_game(timer_div=0x55) # The timer_div works like a random seed in Tetris
assert tetris.next_tetromino() == "O"

# Testing that it defaults to random Tetrominos
selection = set()
for _ in range(10):
    tetris.reset_game()
    selection.add(tetris.next_tetromino())
assert len(selection) > 1 # If it's random, we will see more than one kind

pyboy.stop()
