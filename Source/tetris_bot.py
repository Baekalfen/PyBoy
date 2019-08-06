#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import traceback
import os.path
import os
import sys
from pprint import pprint
from pyboy import windowevent
from pyboy import PyBoy


def getROM(ROMdir):
    # Give a list of ROMs to start
    found_files = list(filter(lambda f: f.lower().endswith(".gb") or f.lower().endswith(".gbc"), os.listdir(ROMdir)))
    for i, f in enumerate(found_files):
        print ("%s\t%s" % (i + 1, f))
    filename = input("Write the name or number of the tetris ROM file:\n")

    try:
        filename = ROMdir + found_files[int(filename) - 1]
    except:
        filename = ROMdir + filename

    return filename


if __name__ == "__main__":
    bootROM = None
    ROMdir = "ROMs/"
    scale = 1

    # Verify directories
    if bootROM is not None and not os.path.exists(bootROM):
        print ("Boot-ROM not found. Please copy the Boot-ROM to '%s'. Using replacement in the meanwhile..." % bootROM)
        bootROM = None

    if not os.path.exists(ROMdir) and len(sys.argv) < 2:
        print ("ROM folder not found. Please copy the Game-ROM to '%s'" % ROMdir)
        exit()

    try:
        # Check if the ROM is given through argv
        if len(sys.argv) > 1: # First arg is SDL2/PyGame
            filename = sys.argv[1]
        else:
            filename = getROM(ROMdir)

        # Start PyBoy and run loop
        pyboy = PyBoy('SDL2', 3, filename, bootROM)
        pyboy.set_emulation_speed(False)
        print ("Screen pos:", pyboy.get_screen_position())

        first_brick = False
        view = pyboy.get_tile_view(False)
        for frame in range(5282): # Enough frames to get a "Game Over". Otherwise do: `while not pyboy.tick():`
            pyboy.tick()
            # print ("frame:", frame)

            # Start game. Just press Start and A when the game allows us.
            # The frames are not 100% accurate.
            if frame == 144:
                pyboy.send_input(windowevent.PRESS_BUTTON_START)
            elif frame == 145:
                pyboy.send_input(windowevent.RELEASE_BUTTON_START)
            elif frame == 152:
                pyboy.send_input(windowevent.PRESS_BUTTON_A)
            elif frame == 153:
                pyboy.send_input(windowevent.RELEASE_BUTTON_A)
            elif frame == 156:
                pyboy.send_input(windowevent.PRESS_BUTTON_A)
            elif frame == 157:
                pyboy.send_input(windowevent.RELEASE_BUTTON_A)
            elif frame == 162:
                pyboy.send_input(windowevent.PRESS_BUTTON_A)
            elif frame == 163:
                pyboy.send_input(windowevent.RELEASE_BUTTON_A)

            # Play game. When we are passed the 168th frame, the game has begone.
            # The "technique" is just to move the Tetromino to the right.
            elif frame > 168:
                if frame % 2 == 0:
                    pyboy.send_input(windowevent.PRESS_ARROW_RIGHT)
                elif frame % 2 == 1:
                    pyboy.send_input(windowevent.RELEASE_ARROW_RIGHT)


                # As an example, it could be useful to know the coordinates
                # of the sprites on the screen and which they look like.
                if frame == 170: # Arbitrary frame where we read out all sprite on the screen
                    for n in range(40):
                        sprite = pyboy.get_sprite(n)
                        if sprite.on_screen:
                            print ("Sprite:", sprite.x, sprite.y, sprite.tile)

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
                    for n in range(10):
                        # 17 for the bottom tile when zero-indexed (144/8 == 18)
                        # +2 because we skip the border on the left side. Then we iterate inwards for 10 tiles
                        # 47 is the white background tile index
                        if view.get_tile(n+2, 17) != 47:
                            first_brick = True
                            print ("First brick touched the bottom!")

                            # Illustrating how we can extract the game board quite simply. This can be used to read the tile indexes
                            game_board_matrix = [[view.get_tile(x+2,y) for x in range(10)] for y in range(18)]
                            pprint(game_board_matrix)

                            break

        pyboy.stop()

    except KeyboardInterrupt:
        print ("Interrupted by keyboard")
    except Exception as ex:
        traceback.print_exc()
