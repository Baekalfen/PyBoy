#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import hashlib
import io
import os

import numpy as np
import PIL
import pytest
from PIL import ImageChops
from pyboy import PyBoy, WindowEvent
from pyboy.botsupport.tile import Tile

from .conftest import BOOTROM_FRAMES_UNTIL_LOGO


def test_misc(default_rom):
    pyboy = PyBoy(default_rom, window_type="dummy")
    pyboy.set_emulation_speed(0)
    pyboy.tick()
    pyboy.stop(save=False)


def test_tiles(default_rom):
    pyboy = PyBoy(default_rom, window_type="dummy")
    pyboy.set_emulation_speed(0)
    for _ in range(BOOTROM_FRAMES_UNTIL_LOGO):
        pyboy.tick()

    tile = pyboy.botsupport_manager().tilemap_window().tile(0, 0)
    assert isinstance(tile, Tile)

    tile = pyboy.botsupport_manager().tile(1)
    image = tile.image()
    assert isinstance(image, PIL.Image.Image)
    ndarray = tile.image_ndarray()
    assert isinstance(ndarray, np.ndarray)
    assert ndarray.shape == (8, 8, 4)
    assert ndarray.dtype == np.uint8
    data = tile.image_data()
    assert data.shape == (8, 8)

    assert [[x for x in y] for y in data
           ] == [[0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff],
                 [0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff],
                 [0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff],
                 [0xffffffff, 0xff000000, 0xff000000, 0xff000000, 0xff000000, 0xff000000, 0xffffffff, 0xffffffff],
                 [0xffffffff, 0xff000000, 0xff000000, 0xff000000, 0xff000000, 0xff000000, 0xff000000, 0xffffffff],
                 [0xffffffff, 0xff000000, 0xff000000, 0xffffffff, 0xffffffff, 0xff000000, 0xff000000, 0xffffffff],
                 [0xffffffff, 0xff000000, 0xff000000, 0xffffffff, 0xffffffff, 0xff000000, 0xff000000, 0xffffffff],
                 [0xffffffff, 0xff000000, 0xff000000, 0xffffffff, 0xffffffff, 0xff000000, 0xff000000, 0xffffffff]]

    for identifier in range(384):
        t = pyboy.botsupport_manager().tile(identifier)
        assert t.tile_identifier == identifier
    with pytest.raises(Exception):
        pyboy.botsupport_manager().tile(-1)
    with pytest.raises(Exception):
        pyboy.botsupport_manager().tile(385)

    pyboy.stop(save=False)


def test_screen_buffer_and_image(tetris_rom, boot_rom):
    cformat = "RGBA"
    boot_logo_hash_predigested = b"_M\x0e\xd9\xe2\xdb\\o]\x83U\x93\xebZm\x1e\xaaFR/Q\xa52\x1c{8\xe7g\x95\xbcIz"

    pyboy = PyBoy(tetris_rom, window_type="headless", bootrom_file=boot_rom)
    pyboy.set_emulation_speed(0)
    for n in range(275): # Iterate to boot logo
        pyboy.tick()

    assert pyboy.botsupport_manager().screen().raw_screen_buffer_dims() == (144, 160)
    assert pyboy.botsupport_manager().screen().raw_screen_buffer_format() == cformat

    boot_logo_hash = hashlib.sha256()
    boot_logo_hash.update(pyboy.botsupport_manager().screen().raw_screen_buffer())
    assert boot_logo_hash.digest() == boot_logo_hash_predigested
    assert isinstance(pyboy.botsupport_manager().screen().raw_screen_buffer(), bytes)

    # The output of `screen_image` is supposed to be homogeneous, which means a shared hash between versions.
    boot_logo_png_hash_predigested = (
        b"\x1b\xab\x90r^\xfb\x0e\xef\xf1\xdb\xf8\xba\xb6:^\x01"
        b"\xa4\x0eR&\xda9\xfcg\xf7\x0f|\xba}\x08\xb6$"
    )
    boot_logo_png_hash = hashlib.sha256()
    image = pyboy.botsupport_manager().screen().screen_image()
    assert isinstance(image, PIL.Image.Image)
    image_data = io.BytesIO()
    image.save(image_data, format="BMP")
    boot_logo_png_hash.update(image_data.getvalue())
    assert boot_logo_png_hash.digest() == boot_logo_png_hash_predigested

    # Screenshot shortcut
    image1 = pyboy.botsupport_manager().screen().screen_image()
    image2 = pyboy.screen_image()
    diff = ImageChops.difference(image1, image2)
    assert not diff.getbbox()

    # screen_ndarray
    numpy_hash = hashlib.sha256()
    numpy_array = np.ascontiguousarray(pyboy.botsupport_manager().screen().screen_ndarray())
    assert isinstance(pyboy.botsupport_manager().screen().screen_ndarray(), np.ndarray)
    assert numpy_array.shape == (144, 160, 3)
    numpy_hash.update(numpy_array.tobytes())
    assert numpy_hash.digest(
    ) == (b"\r\t\x87\x131\xe8\x06\x82\xcaO=\n\x1e\xa2K$"
          b"\xd6\x8e\x91R( H7\xd8a*B+\xc7\x1f\x19")

    pyboy.stop(save=False)


def test_tetris(tetris_rom):
    NEXT_TETROMINO = 0xC213

    pyboy = PyBoy(tetris_rom, bootrom_file="pyboy_fast", window_type="dummy", game_wrapper=True)
    pyboy.set_emulation_speed(0)
    tetris = pyboy.game_wrapper()
    tetris.set_tetromino("T")

    first_brick = False
    tile_map = pyboy.botsupport_manager().tilemap_window()
    state_data = io.BytesIO()
    for frame in range(5282): # Enough frames to get a "Game Over". Otherwise do: `while not pyboy.tick():`
        pyboy.tick()

        assert pyboy.botsupport_manager().screen().tilemap_position() == ((0, 0), (-7, 0))

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

        # Play game. When we are passed the 168th frame, the game has begone.
        # The "technique" is just to move the Tetromino to the right.
        elif frame > 168:
            if frame % 2 == 0:
                pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
            elif frame % 2 == 1:
                pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)

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
                # 303 is the white background tile index
                if any(filter(lambda x: x != 303, tile_map[2:12, 17])):
                    first_brick = True
                    print(frame)
                    print("First brick touched the bottom!")

                    game_board_matrix = list(tile_map[2:12, :18])
                    assert game_board_matrix == ([[303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 133, 133, 133],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 133, 303]])

                    tile_map.use_tile_objects(True)

                    t1 = tile_map[0, 0]
                    t2 = tile_map.tile(0, 0)
                    t3 = tile_map.tile(1, 0)
                    assert t1 == t2, "Testing __eq__ method of Tile object"
                    assert t1 != t3, "Testing not __eq__ method of Tile object"

                    game_board_matrix = [[x.tile_identifier for x in row] for row in tile_map[2:12, :18]]
                    tile_map.use_tile_objects(False)
                    assert game_board_matrix == ([[303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 133, 133, 133],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 133, 303]])

            if frame == 1012:
                assert not first_brick

            if frame == 1014:
                assert first_brick

                s1 = pyboy.botsupport_manager().sprite(0)
                s2 = pyboy.botsupport_manager().sprite(1)
                assert s1 == s1
                assert s1 != s2
                assert s1.tiles[0] == s2.tiles[0], "Testing equal tiles of two different sprites"

                # Test that both ways of getting identifiers work and provides the same result.
                all_sprites = [(s.x, s.y, s.tiles[0].tile_identifier, s.on_screen)
                               for s in [pyboy.botsupport_manager().sprite(n) for n in range(40)]]
                all_sprites2 = [(s.x, s.y, s.tile_identifier, s.on_screen)
                                for s in [pyboy.botsupport_manager().sprite(n) for n in range(40)]]
                assert all_sprites == all_sprites2

                # Verify data with known reference
                # pyboy.botsupport_manager().screen().screen_image().show()
                assert all_sprites == ([
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (72, 128, 133, True),
                    (80, 128, 133, True),
                    (88, 128, 133, True),
                    (80, 136, 133, True),
                    (120, 112, 133, True),
                    (128, 112, 133, True),
                    (136, 112, 133, True),
                    (128, 120, 133, True),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                ])

                assert pyboy.get_memory_value(NEXT_TETROMINO) == 24
                assert tetris.next_tetromino() == "T"

                tmp_state = io.BytesIO()
                pyboy.save_state(tmp_state)
                pyboy.save_state(state_data)
                break

    pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
    pyboy.tick()

    pre_load_game_board_matrix = None
    for frame in range(1016, 1865):
        pyboy.tick()

        if frame == 1864:
            game_board_matrix = list(tile_map[2:12, :18])
            assert game_board_matrix == ([[303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 133, 133, 133, 303, 133, 133, 133],
                                          [303, 303, 303, 303, 133, 303, 303, 303, 133, 303]])
            pre_load_game_board_matrix = game_board_matrix

    state_data.seek(0) # Reset to the start of the buffer. Otherwise, we call `load_state` at end of file
    tmp_state.seek(0)
    for _f in [tmp_state, state_data]: # Tests both file-written state and in-memory state
        pyboy.load_state(_f) # Reverts memory state to before we changed the Tetromino
        pyboy.tick()
        for frame in range(1016, 1865):
            pyboy.tick()

            if frame == 1864:
                game_board_matrix = list(tile_map[2:12, :18])
                assert game_board_matrix == pre_load_game_board_matrix
                break
    pyboy.stop(save=False)


def test_tilemap_position_list(supermarioland_rom):
    pyboy = PyBoy(supermarioland_rom, window_type="dummy")
    pyboy.set_emulation_speed(0)
    for _ in range(100):
        pyboy.tick()

    # Start the game
    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)

    # Move right for 100 frame
    pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
    for _ in range(100):
        pyboy.tick()

    # Get screen positions, and verify the values
    positions = pyboy.botsupport_manager().screen().tilemap_position_list()
    for y in range(1, 16):
        assert positions[y][0] == 0 # HUD
    for y in range(16, 144):
        assert positions[y][0] >= 50 # Actual screen position
        last_y = positions[y][0]

    # Progress another 10 frames to see and increase in SCX
    for _ in range(10):
        pyboy.tick()

    # Get screen positions, and verify the values
    positions = pyboy.botsupport_manager().screen().tilemap_position_list()
    for y in range(1, 16):
        assert positions[y][0] == 0 # HUD
    for y in range(16, 144):
        assert positions[y][0] >= last_y + 10 # Actual screen position

    pyboy.stop(save=False)


def get_set_override(default_rom):
    pyboy = PyBoy(default_rom, window_type="dummy")
    pyboy.set_emulation_speed(0)
    pyboy.tick()

    assert pyboy.get_memory_value(0xFF40) == 0x91
    assert pyboy.set_memory_value(0xFF40) == 0x12
    assert pyboy.get_memory_value(0xFF40) == 0x12

    assert pyboy.get_memory_value(0x0002) == 0xFE
    assert pyboy.override_memory_value(0x0002) == 0x12
    assert pyboy.get_memory_value(0x0002) == 0x12

    pyboy.stop(save=False)
