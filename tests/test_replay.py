#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import base64
import hashlib
import io
import json
import os
import sys
import time
import zlib
from unittest import mock

import numpy as np
import pytest

from pyboy import PyBoy, WindowEvent, utils

event_filter = [
    WindowEvent.PRESS_SPEED_UP,
    WindowEvent.RELEASE_SPEED_UP,
    WindowEvent.SCREEN_RECORDING_TOGGLE,
    WindowEvent._INTERNAL_RENDERER_FLUSH,
]
# Set to true to reset tests
RESET_REPLAYS = False


def verify_screen_image_np(pyboy, saved_array):
    match = np.all(np.frombuffer(saved_array, dtype=np.uint8).reshape(144, 160, 3) == pyboy.screen.ndarray)
    if not match and not os.environ.get("TEST_CI"):
        from PIL import Image
        original = Image.frombytes("RGB", (160, 144), np.frombuffer(saved_array, dtype=np.uint8).reshape(144, 160, 3))
        original.show()
        new = pyboy.screen.image
        new.show()
        import PIL.ImageChops
        PIL.ImageChops.difference(original, new).show()

    assert match


def verify_file_hash(rom_file, b64_target_hash):
    with open(rom_file, "rb") as f:
        m = hashlib.sha256()
        m.update(f.read())
        b64_romhash = base64.b64encode(m.digest()).decode("utf8")
        assert b64_romhash == b64_target_hash


def move_gif(game, dest):
    record_dir = "recordings"
    for _ in range(10):
        try:
            gif = sorted(filter(lambda x: game in x, os.listdir(record_dir)))[-1]
            os.replace(record_dir + "/" + gif, dest)
            break
        except:
            time.sleep(1)
    else:
        raise FileNotFoundError(f"Couldn't find gif to move for game {game}")


def replay(
    ROM,
    replay,
    window="null",
    verify=False,
    record_gif=None,
    gif_destination=None,
    rewind=False,
    bootrom_file=None,
    overwrite=RESET_REPLAYS,
    gif_hash=None,
    randomize=False,
    padding_frames=0,
    stop_frame=-1,
    cgb=None,
):
    with open(replay, "rb") as f:
        recorded_input, b64_romhash, b64_state = json.loads(zlib.decompress(f.read()).decode("ascii"))

    verify_file_hash(ROM, b64_romhash)
    state_data = io.BytesIO(base64.b64decode(b64_state.encode("utf8"))) if b64_state is not None else None

    pyboy = PyBoy(
        ROM,
        window_type=window,
        bootrom_file=bootrom_file,
        disable_input=True,
        rewind=rewind,
        randomize=randomize,
        cgb=cgb,
        record_input=(RESET_REPLAYS and window in ["SDL2", "null", "OpenGL"]),
    )
    pyboy.set_emulation_speed(0)
    if state_data is not None:
        pyboy.load_state(state_data)
    else:
        pyboy.tick(padding_frames, True)

    # Filters out the blacklisted events
    recorded_input = list(
        map(
            lambda event_tuple:
            (event_tuple[0], list(filter(lambda x: x not in event_filter, event_tuple[1])), event_tuple[2]),
            recorded_input
        )
    )

    frame_count = 0
    next_event = recorded_input.pop(0)

    recording = False
    while recorded_input != [] and stop_frame != frame_count:
        if record_gif is not None and (frame_count in record_gif):
            pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
            recording ^= True

        if next_event[0] == frame_count:
            for e in next_event[1]:
                pyboy.send_input(e)

                if verify and not overwrite and frame_count > 1: # First frame or two might be wrong on old statefiles
                    verify_screen_image_np(pyboy, base64.b64decode(next_event[2].encode("utf8")))
            next_event = recorded_input.pop(0)
        frame_count += 1
        # if frame_count % 30 == 0:
        #     print(frame_count)
        #     breakpoint()
        pyboy.tick(1, True)

    print(frame_count)
    # If end-frame in record_gif is high than frame counter
    if recording:
        pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
        # We need to run an extra cycle for the screen recording to save
        pyboy.tick(1, True)
        print(frame_count)
        recording ^= True

    if gif_destination:
        move_gif(pyboy.cartridge_title(), gif_destination)
        if gif_hash is not None and not overwrite and sys.platform == "darwin":
            verify_file_hash(gif_destination, gif_hash)

    if overwrite:
        with open(replay, "wb") as f:
            f.write(
                zlib.compress(
                    json.dumps((pyboy._plugin_manager.record_replay.recorded_input, b64_romhash, b64_state)).encode()
                )
            )

    pyboy.stop(save=False)


def test_pokemon(pokemon_blue_rom, boot_rom):
    replay(
        pokemon_blue_rom,
        "tests/replays/pokemon_blue.replay",
        stop_frame=1074,
        bootrom_file=boot_rom,
    )


def test_pokemon_gif1(pokemon_gold_rom, boot_rom):
    replay(
        pokemon_gold_rom,
        "tests/replays/pokemon_gold_gif.replay",
        record_gif=(1, 2714),
        gif_destination="extras/README/1.gif",
        bootrom_file=boot_rom,
    )


def test_pokemon_gif2(pokemon_blue_rom, boot_rom):
    replay(
        pokemon_blue_rom,
        "tests/replays/pokemon_blue_gif2.replay",
        record_gif=(0, 180),
        gif_destination="extras/README/2.gif",
        bootrom_file=boot_rom,
    )


def test_tetris(tetris_rom, boot_rom):
    replay(
        tetris_rom,
        "tests/replays/tetris.replay",
        bootrom_file=boot_rom,
    )


def test_supermarioland(supermarioland_rom, boot_rom):
    replay(
        supermarioland_rom,
        "tests/replays/supermarioland.replay",
        bootrom_file=boot_rom,
    )


def test_kirby(kirby_rom, boot_rom):
    replay(
        kirby_rom,
        "tests/replays/kirby_gif.replay",
        record_gif=(0, 360),
        gif_destination="extras/README/4.gif",
        bootrom_file=boot_rom,
    )


def test_rewind(supermarioland_rom, boot_rom):
    replay(
        supermarioland_rom,
        "tests/replays/supermarioland_rewind.replay",
        record_gif=(130, 544),
        gif_destination="extras/README/5.gif",
        rewind=True,
        bootrom_file=None,
    )
