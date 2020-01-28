#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import base64
import hashlib
import io
import json
import os
import time
import zlib

import numpy as np
from pyboy import PyBoy, windowevent

from . import utils

event_filter = [windowevent.PRESS_SPEED_UP, windowevent.RELEASE_SPEED_UP, windowevent.SCREEN_RECORDING_TOGGLE]


def verify_screen_image_np(pyboy, saved_array):
    match = np.all(np.frombuffer(saved_array, dtype=np.uint8).reshape(144, 160, 3) == pyboy.get_screen_ndarray())
    if not match:
        from PIL import Image
        original = Image.frombytes("RGB", (160, 144), np.frombuffer(saved_array, dtype=np.uint8).reshape(144, 160, 3))
        original.show()
        new = pyboy.get_screen_image()
        new.show()
        breakpoint()
    assert match


def verify_rom_hash(rom_file, b64_target_hash):
    with open(rom_file, 'rb') as f:
        m = hashlib.sha256()
        m.update(f.read())
        b64_romhash = base64.b64encode(m.digest()).decode('utf8')
        assert b64_romhash == b64_target_hash


def move_gif(game, dest):
    record_dir = 'recordings'
    for _ in range(3):
        try:
            gif = sorted(filter(lambda x: game in x, os.listdir(record_dir)))[-1]
            os.replace(record_dir + '/' + gif, dest)
            break
        except:
            time.sleep(1)
    else:
        raise FileNotFoundError(f"Couldn't find gif to move for game {game}")


def replay(ROM, replay, window='headless', verify=True, record_gif=None, gif_destination=None, enable_rewind=False):
    with open(replay, 'rb') as f:
        recorded_input, b64_romhash, b64_state = json.loads(zlib.decompress(f.read()).decode('ascii'))

    verify_rom_hash(ROM, b64_romhash)
    state_data = io.BytesIO(base64.b64decode(b64_state.encode('utf8'))) if b64_state is not None else None

    pyboy = PyBoy(ROM, window_type=window, bootrom_file=utils.boot_rom, disable_input=True, hide_window=False,
                  enable_rewind=enable_rewind)
    pyboy.set_emulation_speed(0)
    if state_data is not None:
        pyboy.load_state(state_data)

    # Filters out the blacklisted events
    recorded_input = list(
        map(lambda event_tuple: (
            event_tuple[0],
            list(filter(lambda x: x not in event_filter, event_tuple[1])),
            event_tuple[2]
            ),
            recorded_input)
        )

    frame_count = 0
    next_event = recorded_input.pop(0)

    recording = False
    while recorded_input != []:
        if record_gif is not None and (frame_count in record_gif):
            pyboy.send_input(windowevent.SCREEN_RECORDING_TOGGLE)
            recording ^= True

        if next_event[0] == frame_count:
            for e in next_event[1]:
                pyboy.send_input(e)

                if verify:
                    verify_screen_image_np(pyboy, base64.b64decode(next_event[2].encode('utf8')))
            next_event = recorded_input.pop(0)
        frame_count += 1
        # if frame_count % 30 == 0:
        #     print(frame_count)
        #     breakpoint()
        pyboy.tick()

    # If end-frame in record_gif is high than frame counter
    # if recording:
    #     pyboy.send_input(windowevent.SCREEN_RECORDING_TOGGLE)
    #     recording ^= True

    if gif_destination:
        move_gif(pyboy.get_cartridge_title(), gif_destination)

    pyboy.stop(save=False)


def test_pokemon():
    replay(utils.pokemon_blue_rom, "tests/replays/pokemon_blue.replay")


def test_pokemon_gif1():
    replay(utils.pokemon_blue_rom, "tests/replays/pokemon_blue_gif1.replay", record_gif=(630, 3540),
           gif_destination="README/1.gif")


def test_pokemon_gif2():
    replay(utils.pokemon_blue_rom, "tests/replays/pokemon_blue_gif2.replay", record_gif=(0, 180),
           gif_destination="README/2.gif")


def test_tetris():
    replay(utils.tetris_rom, "tests/replays/tetris.replay")


def test_supermarioland_gif():
    replay(utils.supermarioland_rom, "tests/replays/supermarioland_gif.replay", record_gif=(120, 660),
           gif_destination="README/3.gif")


def test_supermarioland():
    replay(utils.supermarioland_rom, "tests/replays/supermarioland.replay")


def test_kirby():
    replay(utils.kirby_rom, "tests/replays/kirby_gif.replay", record_gif=(0, 360),
           gif_destination="README/4.gif")


def test_rewind():
    replay(utils.supermarioland_rom, "tests/replays/supermarioland_rewind.replay", record_gif=(416, 643),
           gif_destination="README/5.gif", enable_rewind=True)
