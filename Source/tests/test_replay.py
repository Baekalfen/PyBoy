#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys
sys.path.append(".") # Adds higher directory to python modules path.

import json
import zlib
import base64
import numpy as np

from pyboy import windowevent
from pyboy import PyBoy

boot_rom = "ROMs/DMG_ROM.bin"

event_filter = [windowevent.PRESS_SPEED_UP, windowevent.RELEASE_SPEED_UP]

def verify_screen_image_np(pyboy, saved_array):
    match = np.all(np.frombuffer(saved_array, dtype=np.uint8).reshape(144, 160, 3) == pyboy.get_screen_ndarray())
    # if not match:
    #     from PIL import Image
    #     original = Image.frombytes("RGB", (160,144), np.frombuffer(saved_array, dtype=np.uint8).reshape(144, 160, 3))
    #     original.show()
    #     new = pyboy.get_screen_image()
    #     new.show()
    #     breakpoint()
    return match

def replay(ROM, replay, window='headless', verify=True):
    pyboy = PyBoy(ROM, window_type=window, bootrom_file=boot_rom)
    pyboy.set_emulation_speed(False)
    with open(replay, 'rb') as f:
        recorded_input = json.loads(zlib.decompress(f.read()).decode('ascii'))

    # Filters out the blacklisted events
    recorded_input = list(map(lambda event_tuple: (event_tuple[0], list(filter(lambda x: x not in event_filter, event_tuple[1])), event_tuple[2]), recorded_input))

    frame_count = 0
    next_event = recorded_input.pop(0)

    while recorded_input != []:
        if next_event[0] == frame_count:
            for e in next_event[1]:
                pyboy.send_input(e)
                if verify:
                    assert verify_screen_image_np(pyboy, base64.b64decode(next_event[2].encode('utf8')))
            next_event = recorded_input.pop(0)
        frame_count += 1
        pyboy.tick()

    pyboy.stop(save=False)

def test_pokemon():
    replay("ROMs/POKEMON BLUE.gb", "tests/replays/pokemon_blue.replay")

def test_tetris():
    replay("ROMs/Tetris.gb", "tests/replays/tetris.replay")

def test_supermarioland():
    replay("ROMs/SuperMarioLand.gb", "tests/replays/supermarioland.replay")

def test_kirby():
    replay("ROMs/Kirby.gb", "tests/replays/kirby.replay")

