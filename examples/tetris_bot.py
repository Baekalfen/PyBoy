#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import os.path
import sys
import traceback
from pprint import pprint

from pyboy import PyBoy, WindowEvent


def getROM(ROMdir):
    # Give a list of ROMs to start
    found_files = list(filter(lambda f: f.lower().endswith(".gb") or f.lower().endswith(".gbc"), os.listdir(ROMdir)))
    for i, f in enumerate(found_files):
        print("%s\t%s" % (i + 1, f))
    filename = input("Write the name or number of the tetris ROM file:\n")

    try:
        filename = ROMdir + found_files[int(filename) - 1]
    except:
        filename = ROMdir + filename

    return filename


if __name__ == "__main__":
    bootROM = None
    ROMdir = "ROMs/"

    # Verify directories
    if bootROM is not None and not os.path.exists(bootROM):
        print("Boot-ROM not found. Please copy the Boot-ROM to '%s'. Using replacement in the meanwhile..." % bootROM)
        bootROM = None

    if not os.path.exists(ROMdir) and len(sys.argv) < 2:
        print("ROM folder not found. Please copy the Game-ROM to '%s'" % ROMdir)
        exit()

    try:
        # Check if the ROM is given through argv
        if len(sys.argv) > 1: # First arg is SDL2/PyGame
            filename = sys.argv[1]
        else:
            filename = getROM(ROMdir)

        # Start PyBoy and run loop
        if "--quiet" in sys.argv:
            window = 'headless'
        else:
            window = 'SDL2'
        pyboy = PyBoy(filename, window_type=window, window_scale=3, bootrom_file=bootROM)
        pyboy.set_emulation_speed(0)
        print("Screen pos:", pyboy.botsupport_manager().screen().tilemap_position())

        first_brick = False
        tile_map = pyboy.tilemap_window()
        for frame in range(5282): # Enough frames to get a "Game Over". Otherwise do: `while not pyboy.tick():`
            pyboy.tick()
            # print ("frame:", frame)

            # Start game. Just press Start and A when the game allows us.
            # The frames are not 100% accurate.
            if frame == 144:
                pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
            elif frame == 145:
                pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
            elif frame == 152:
                pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
            elif frame == 153:
                pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
            elif frame == 156:
                pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
            elif frame == 157:
                pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
            elif frame == 162:
                pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
            elif frame == 163:
                pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)

            elif frame == 4480:
                # Illustrating how we can extract the game board quite simply. This can be used to read the tile indexes
                # To find the exact slice needed, try printing the tile_map
                # >>> print(tile_map)
                #      0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  25  26  27  28  29  30  31
                # __________________________________________________________________________________________________________________________________
                # 0  | 42  123 47  47  47  47  47  47  47  47  47  47  123 48  49  49  49  49  49  50  47  47  47  47  47  47  47  47  47  47  47  47
                # 1  | 42  124 47  47  47  47  47  47  47  47  47  47  124 68  28  12  24  27  14  69  47  47  47  47  47  47  47  47  47  47  47  47
                # 2  | 42  125 47  47  47  47  47  47  47  47  47  47  125 103 70  70  70  70  70  104 47  47  47  47  47  47  47  47  47  47  47  47
                # 3  | 42  123 47  47  47  47  47  47  47  47  47  47  123 47  47  47  47  47  0   47  47  47  47  47  47  47  47  47  47  47  47  47
                # 4  | 42  124 47  47  47  47  47  47  47  47  47  47  124 67  52  52  52  52  52  52  47  47  47  47  47  47  47  47  47  47  47  47
                # 5  | 42  125 47  47  47  47  47  47  47  47  47  47  125 48  49  49  49  49  49  50  47  47  47  47  47  47  47  47  47  47  47  47
                # 6  | 42  123 47  47  47  47  47  47  47  47  47  47  123 54  21  14  31  14  21  55  47  47  47  47  47  47  47  47  47  47  47  47
                # 7  | 42  124 47  47  47  47  47  47  47  47  47  47  124 54  47  47  47  0   47  55  47  47  47  47  47  47  47  47  47  47  47  47
                # 8  | 42  125 47  47  47  47  47  47  47  47  47  47  125 64  66  66  66  66  66  65  47  47  47  47  47  47  47  47  47  47  47  47
                # 9  | 42  123 47  47  47  47  47  47  47  47  47  47  123 54  21  18  23  14  28  55  47  47  47  47  47  47  47  47  47  47  47  47
                # 10 | 42  124 47  47  47  47  47  47  47  47  47  47  124 54  47  47  47  0   47  55  47  47  47  47  47  47  47  47  47  47  47  47
                # 11 | 42  125 47  47  47  47  47  47  47  47  47  47  125 51  52  52  52  52  52  53  47  47  47  47  47  47  47  47  47  47  47  47
                # 12 | 42  123 47  47  47  47  47  47  47  47  47  47  123 43  56  57  57  57  57  58  47  47  47  47  47  47  47  47  47  47  47  47
                # 13 | 42  124 47  47  47  47  47  47  47  47  47  47  124 43  59  47  47  47  47  60  47  47  47  47  47  47  47  47  47  47  47  47
                # 14 | 42  125 47  47  47  47  47  47  47  47  47  47  125 43  59  47  47  47  47  60  47  47  47  47  47  47  47  47  47  47  47  47
                # 15 | 42  123 47  47  47  47  47  47  47  47  47  47  123 43  59  47  47  47  47  60  47  47  47  47  47  47  47  47  47  47  47  47
                # 16 | 42  124 47  47  47  47  47  47  47  130 130 47  124 43  59  47  47  47  47  60  47  47  47  47  47  47  47  47  47  47  47  47
                # 17 | 42  125 47  47  47  47  47  47  47  47  130 130 125 43  61  62  62  62  62  63  47  47  47  47  47  47  47  47  47  47  47  47
                # 18 | 47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47
                # 19 | 47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47
                # 20 | 47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47
                # 21 | 47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47
                # 22 | 47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47
                # 23 | 47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47
                # 24 | 47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47
                # 25 | 47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47
                # 26 | 47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47
                # 27 | 47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47
                # 28 | 47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47
                # 29 | 47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47
                # 30 | 47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47
                # 31 | 47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47  47

                print("Final game board:")
                game_board_matrix = tile_map[2:12, 0:18]
                pprint(game_board_matrix)

                print("Final game board mask:")
                game_board_matrix = [[0 if x == 47 else 1 for x in row] for row in tile_map[2:12, 0:18]]
                pprint(game_board_matrix)

            # Play game. When we are passed the 168th frame, the game has begone.
            # The "technique" is just to move the Tetromino to the right.
            elif frame > 168:
                if frame % 2 == 0:
                    pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
                elif frame % 2 == 1:
                    pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)

                # As an example, it could be useful to know the coordinates
                # of the sprites on the screen and which they look like.
                if frame == 170: # Arbitrary frame where we read out all sprite on the screen
                    for n in range(40):
                        sprite = pyboy.botsupport_manager().sprite(n)
                        if sprite.on_screen:
                            print(sprite)

                # Show how we can read the tile data for the screen. We can use
                # this to see when one of the Tetrominos touch the bottom. This
                # could be used to extract a matrix of the occupied squares by
                # iterating from the top to the bottom of the screen.
                # Sidenote: The currently moving Tetromino is a sprite, so it
                # won't show up in the tile data. The tile data shows only the
                # placed Tetrominos.
                # We could also read out the score from the screen instead of
                # finding the corresponding value in RAM.
                if not first_brick:
                    # 17 for the bottom tile when zero-indexed
                    # 2 because we skip the border on the left side. Then we take a slice of 10 more tiles
                    # 47 is the white background tile index
                    if any(filter(lambda x: x == 47, tile_map[2:12, 17])):
                        first_brick = True
                        print("First brick touched the bottom!")

                        # Illustrating how we can extract the game board quite simply. This can be
                        # used to read the tile indexes
                        game_board_matrix = tile_map[2:12, 0:18]
                        pprint(game_board_matrix)
        pyboy.stop()

    except KeyboardInterrupt:
        print("Interrupted by keyboard")
    except Exception:
        traceback.print_exc()
