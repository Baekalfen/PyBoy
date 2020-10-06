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
from pyboy import PyBoy, WindowEvent
from pyboy.botsupport.tile import Tile
from tests.utils import BOOTROM_FRAMES_UNTIL_LOGO, any_rom, boot_rom, default_rom, supermarioland_rom, tetris_rom


def test_misc():
    pyboy = PyBoy(default_rom, window_type="dummy")
    pyboy.tick()
    pyboy.stop(save=False)


def test_tiles():
    pyboy = PyBoy(default_rom, window_type="headless")
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


@pytest.mark.skipif(not boot_rom or any_rom == default_rom, reason="ROM not present")
def test_screen_buffer_and_image():
    cformat = "RGBA"
    boot_logo_hash_predigested = b"=\xff\xf9z 6\xf0\xe9\xcb\x05J`PM5\xd4rX+\x1b~z\xef1\xe0\x82\xc4t\x06\x82\x12C"
    boot_logo_hash_predigested = \
        b"s\xd1R\x88\xe0a\x14\xd0\xd2\xecOk\xe8b\xae.\x0e\x1e\xb6R\xc2\xe9:\xa2\x0f\xae\xa2\x89M\xbf\xd8|"

    pyboy = PyBoy(any_rom, window_type="headless", bootrom_file=boot_rom)
    pyboy.set_emulation_speed(0)
    for n in range(275): # Iterate to boot logo
        pyboy.tick()

    assert pyboy.botsupport_manager().screen().raw_screen_buffer_dims() == (160, 144)
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


@pytest.mark.skipif(not tetris_rom, reason="ROM not present")
def test_tetris():
    NEXT_TETROMINO = 0xC213

    pyboy = PyBoy(tetris_rom, bootrom_file="pyboy_fast", window_type="headless", game_wrapper=True)
    pyboy.set_emulation_speed(0)

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
                                                  [303, 303, 303, 303, 303, 303, 303, 130, 130, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 130, 130]])

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
                                                  [303, 303, 303, 303, 303, 303, 303, 130, 130, 303],
                                                  [303, 303, 303, 303, 303, 303, 303, 303, 130, 130]])

            if frame == 1014:
                assert not first_brick

            if frame == 1015:
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
                assert all_sprites == ([
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (-8, -16, 0, False),
                    (72, 128, 130, True),
                    (80, 128, 130, True),
                    (80, 136, 130, True),
                    (88, 136, 130, True),
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
                tetris = pyboy.game_wrapper()
                assert tetris.next_tetromino() == "T"

                with open("tmp.state", "wb") as f:
                    pyboy.save_state(f)
                pyboy.save_state(state_data)
                pyboy.set_memory_value(NEXT_TETROMINO, 11)
                assert pyboy.get_memory_value(NEXT_TETROMINO) == 11
                assert tetris.next_tetromino() == "I"
                break

    for frame in range(1016, 1866):
        pyboy.tick()
        if frame == 1017:
            assert pyboy.get_memory_value(NEXT_TETROMINO) == 11 # Would have been 4 otherwise

        if frame == 1865:
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
                                          [303, 303, 303, 303, 128, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 136, 303, 303, 303, 303, 303],
                                          [303, 303, 303, 303, 136, 303, 303, 130, 130, 303],
                                          [303, 303, 303, 303, 137, 303, 303, 303, 130, 130]])

    state_data.seek(0) # Reset to the start of the buffer. Otherwise, we call `load_state` at end of file
    with open("tmp.state", "rb") as f:
        for _f in [f, state_data]: # Tests both file-written state and in-memory state
            pyboy.load_state(_f) # Reverts memory state to before we changed the Tetromino
            pyboy.tick()
            for frame in range(1016, 5282):
                pyboy.tick()
                if frame == 1017:
                    assert pyboy.get_memory_value(NEXT_TETROMINO) == 8

                if frame == 1865:
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
                                                  [303, 303, 303, 133, 133, 133, 303, 130, 130, 303],
                                                  [303, 303, 303, 303, 133, 303, 303, 303, 130, 130]])
    os.remove("tmp.state")

    pyboy.stop(save=False)


@pytest.mark.skipif(not supermarioland_rom, reason="ROM not present")
def test_tilemap_position_list():
    pyboy = PyBoy(supermarioland_rom, window_type="headless")
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
        assert positions[y][0] == 49 # Actual screen position

    # Progress another 10 frames to see and increase in SCX
    for _ in range(10):
        pyboy.tick()

    # Get screen positions, and verify the values
    positions = pyboy.botsupport_manager().screen().tilemap_position_list()
    for y in range(1, 16):
        assert positions[y][0] == 0 # HUD
    for y in range(16, 144):
        assert positions[y][0] == 59 # Actual screen position

    pyboy.stop(save=False)


def get_set_override():
    pyboy = PyBoy(default_rom, window_type="dummy")
    pyboy.tick()

    assert pyboy.get_memory_value(0xFF40) == 0x91
    assert pyboy.set_memory_value(0xFF40) == 0x12
    assert pyboy.get_memory_value(0xFF40) == 0x12

    assert pyboy.get_memory_value(0x0002) == 0xFE
    assert pyboy.override_memory_value(0x0002) == 0x12
    assert pyboy.get_memory_value(0x0002) == 0x12

    pyboy.stop(save=False)
