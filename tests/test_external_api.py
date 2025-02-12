#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import hashlib
import io
import time

import numpy as np
import PIL
import pytest
from PIL import ImageChops

from pyboy import PyBoy
from pyboy.api.tile import Tile
from pyboy.api.constants import TILES_CGB, TILES
from pyboy.utils import IntIOWrapper, PyBoyAssertException, PyBoyException, PyBoyOutOfBoundsException, WindowEvent

from .conftest import BOOTROM_FRAMES_UNTIL_LOGO

NDARRAY_COLOR_DEPTH = 4
NDARRAY_COLOR_FORMAT = "RGBA"


def test_misc(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(1, False, False)
    pyboy.stop(save=False)


def test_rtc_lock_no_rtc(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    with pytest.raises(PyBoyException):
        pyboy.rtc_lock_experimental(True)


def test_rtc_lock(pokemon_gold_rom):
    pyboy = PyBoy(pokemon_gold_rom, window="null")
    pyboy.rtc_lock_experimental(False)

    # Enable external RAM
    pyboy.memory[0x0000] = 0x0A

    # Reset seconds
    pyboy.memory[0x4000] = 0x08
    pyboy.memory[0xA000] = 0

    # Reset minutes
    pyboy.memory[0x4000] = 0x09
    pyboy.memory[0xA000] = 0

    # Reset hours
    pyboy.memory[0x4000] = 0x0A
    pyboy.memory[0xA000] = 0

    # Reset days (low)
    pyboy.memory[0x4000] = 0x0B
    pyboy.memory[0xA000] = 0

    # Reset days (high)
    pyboy.memory[0x4000] = 0x0C
    pyboy.memory[0xA000] = 0

    time.sleep(2)  # Induce a change in the seconds register

    # Pan docs:
    # When writing $00, and then $01 to this register, the current time becomes latched into the RTC registers
    pyboy.memory[0x6000] = 0
    pyboy.memory[0x6000] = 1

    # Pan docs:
    # When writing a value of $08-$0C, this will map the corresponding RTC register into memory at A000-BFFF
    pyboy.memory[0x4000] = 0x08
    assert pyboy.memory[0xA000] != 0

    pyboy.memory[0x4000] = 0x09
    assert pyboy.memory[0xA000] == 0

    pyboy.memory[0x4000] = 0x0A
    assert pyboy.memory[0xA000] == 0

    pyboy.memory[0x4000] = 0x0B
    assert pyboy.memory[0xA000] == 0

    pyboy.memory[0x4000] = 0x0C
    assert pyboy.memory[0xA000] == 0

    pyboy.rtc_lock_experimental(True)

    # Pan docs:
    # When writing $00, and then $01 to this register, the current time becomes latched into the RTC registers
    pyboy.memory[0x6000] = 0
    pyboy.memory[0x6000] = 1

    # Pan docs:
    # When writing a value of $08-$0C, this will map the corresponding RTC register into memory at A000-BFFF
    pyboy.memory[0x4000] = 0x08
    assert pyboy.memory[0xA000] == 0

    pyboy.memory[0x4000] = 0x09
    assert pyboy.memory[0xA000] == 0

    pyboy.memory[0x4000] = 0x0A
    assert pyboy.memory[0xA000] == 0

    pyboy.memory[0x4000] = 0x0B
    assert pyboy.memory[0xA000] == 0

    pyboy.memory[0x4000] = 0x0C
    assert pyboy.memory[0xA000] == 0


def test_faulty_state(default_rom):
    pyboy = PyBoy(default_rom, window="null")

    a = IntIOWrapper(io.BytesIO(b"abcd"))
    a.seek(0)
    a.write(0xFF)
    # Cython causes OverflowError, PyPy causes PyBoyOutOfBoundsException
    with pytest.raises((OverflowError, PyBoyOutOfBoundsException)):
        a.write(0x100)
    a.seek(0)
    assert a.read() == 0xFF
    assert a.read() == ord("b")
    assert a.read() == ord("c")
    assert a.read() == ord("d")
    with pytest.raises(PyBoyAssertException):
        a.read()

    b = io.BytesIO(b"\x001234")
    with pytest.raises(PyBoyAssertException):
        pyboy.load_state(b)
    b = io.BytesIO(b"991234")
    with pytest.raises(PyBoyException):
        pyboy.load_state(b)
    pyboy.stop(save=False)


def test_tiles(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(BOOTROM_FRAMES_UNTIL_LOGO, False)

    tile = pyboy.tilemap_window.tile(0, 0)
    assert isinstance(tile, Tile)

    pyboy.get_tile(TILES - 1)  # DMG
    with pytest.raises(PyBoyOutOfBoundsException):
        pyboy.get_tile(TILES)  # Not CGB

    tile = pyboy.get_tile(1)
    image = tile.image()
    assert isinstance(image, PIL.Image.Image)
    ndarray = tile.ndarray()
    assert isinstance(ndarray, np.ndarray)
    assert ndarray.shape == (8, 8, NDARRAY_COLOR_DEPTH)
    assert ndarray.dtype == np.uint8
    # data = tile.image_data()
    # assert data.shape == (8, 8)

    assert [[x & 0xFFFFFF for x in y] for y in ndarray.view(dtype=np.uint32).reshape(8, 8)] == [
        [0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF],
        [0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF],
        [0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF],
        [0xFFFFFF, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0xFFFFFF, 0xFFFFFF],
        [0xFFFFFF, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0xFFFFFF],
        [0xFFFFFF, 0x000000, 0x000000, 0xFFFFFF, 0xFFFFFF, 0x000000, 0x000000, 0xFFFFFF],
        [0xFFFFFF, 0x000000, 0x000000, 0xFFFFFF, 0xFFFFFF, 0x000000, 0x000000, 0xFFFFFF],
        [0xFFFFFF, 0x000000, 0x000000, 0xFFFFFF, 0xFFFFFF, 0x000000, 0x000000, 0xFFFFFF],
    ]

    for identifier in range(TILES):
        t = pyboy.get_tile(identifier)
        assert t.tile_identifier == identifier
    with pytest.raises(PyBoyException):
        pyboy.get_tile(-1)
    with pytest.raises(PyBoyException):
        pyboy.get_tile(TILES_CGB)

    pyboy.stop(save=False)


def test_tiles_cgb(any_rom_cgb):
    pyboy = PyBoy(any_rom_cgb, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(BOOTROM_FRAMES_UNTIL_LOGO, False)

    tile = pyboy.tilemap_window.tile(0, 0)
    assert isinstance(tile, Tile)

    tile = pyboy.get_tile(1)
    image = tile.image()
    assert isinstance(image, PIL.Image.Image)
    ndarray = tile.ndarray()
    assert isinstance(ndarray, np.ndarray)
    assert ndarray.shape == (8, 8, NDARRAY_COLOR_DEPTH)
    assert ndarray.dtype == np.uint8
    # data = tile.image_data()
    # assert data.shape == (8, 8)

    assert [[x & 0xFFFFFF for x in y] for y in ndarray.view(dtype=np.uint32).reshape(8, 8)] == [
        [0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF],
        [0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF],
        [0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF],
        [0xFFFFFF, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0xFFFFFF, 0xFFFFFF],
        [0xFFFFFF, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0xFFFFFF],
        [0xFFFFFF, 0x000000, 0x000000, 0xFFFFFF, 0xFFFFFF, 0x000000, 0x000000, 0xFFFFFF],
        [0xFFFFFF, 0x000000, 0x000000, 0xFFFFFF, 0xFFFFFF, 0x000000, 0x000000, 0xFFFFFF],
        [0xFFFFFF, 0x000000, 0x000000, 0xFFFFFF, 0xFFFFFF, 0x000000, 0x000000, 0xFFFFFF],
    ]

    for identifier in range(TILES_CGB):
        t = pyboy.get_tile(identifier)
        assert t.tile_identifier == identifier
    with pytest.raises(PyBoyException):
        pyboy.get_tile(-1)
    with pytest.raises(PyBoyException):
        pyboy.get_tile(TILES_CGB)

    pyboy.stop(save=False)


def test_screen_buffer_and_image(tetris_rom, boot_rom):
    cformat = "RGBA"
    # boot_logo_hash_predigested = b"_M\x0e\xd9\xe2\xdb\\o]\x83U\x93\xebZm\x1e\xaaFR/Q\xa52\x1c{8\xe7g\x95\xbcIz"

    pyboy = PyBoy(tetris_rom, window="null", bootrom=boot_rom)
    pyboy.set_emulation_speed(0)
    pyboy.tick(275, True)  # Iterate to boot logo

    assert pyboy.screen.raw_buffer_dims == (144, 160)
    assert pyboy.screen.raw_buffer_format == cformat

    boot_logo_hash = hashlib.sha256()

    if hasattr(pyboy.screen.raw_buffer, "tobytes"):
        boot_logo_hash.update(pyboy.screen.raw_buffer.tobytes())  # PyPy
    else:
        boot_logo_hash.update(pyboy.screen.raw_buffer.base)  # Cython
    # assert boot_logo_hash.digest() == boot_logo_hash_predigested
    # assert isinstance(pyboy.screen.raw_buffer, bytes)

    # The output of `image` is supposed to be homogeneous, which means a shared hash between versions.
    boot_logo_png_hash_predigested = (
        b"\x1b\xab\x90r^\xfb\x0e\xef\xf1\xdb\xf8\xba\xb6:^\x01" b"\xa4\x0eR&\xda9\xfcg\xf7\x0f|\xba}\x08\xb6$"
    )
    boot_logo_png_hash = hashlib.sha256()
    image = pyboy.screen.image.convert("RGB")
    assert isinstance(image, PIL.Image.Image)
    image_data = io.BytesIO()
    image.save(image_data, format="BMP")
    boot_logo_png_hash.update(image_data.getvalue())
    assert boot_logo_png_hash.digest() == boot_logo_png_hash_predigested

    # screen_ndarray
    numpy_hash = hashlib.sha256()
    numpy_array = np.ascontiguousarray(pyboy.screen.ndarray)
    assert isinstance(pyboy.screen.ndarray, np.ndarray)
    assert numpy_array.shape == (144, 160, NDARRAY_COLOR_DEPTH)
    numpy_hash.update(numpy_array.tobytes())
    # assert numpy_hash.digest(
    # ) == (b"\r\t\x87\x131\xe8\x06\x82\xcaO=\n\x1e\xa2K$"
    #       b"\xd6\x8e\x91R( H7\xd8a*B+\xc7\x1f\x19")

    ## Check PIL image is reference for performance
    ## Converting to RGB as ImageChops.difference cannot handle Alpha: https://github.com/python-pillow/Pillow/issues/4849

    # Initial, direct reference and copy are the same
    pyboy.tick(1, True)
    new_image1 = pyboy.screen.image
    _new_image1 = new_image1.copy()
    diff = ImageChops.difference(new_image1.convert("RGB"), _new_image1.convert("RGB"))
    assert not diff.getbbox()

    # Changing reference, and it now differs from copy
    nd_image = pyboy.screen.ndarray
    nd_image[:, :, :] = 0
    diff = ImageChops.difference(new_image1.convert("RGB"), _new_image1.convert("RGB"))
    assert diff.getbbox()

    # Old reference lives after tick, and equals new reference
    pyboy.tick(1, True)
    new_image2 = pyboy.screen.image
    diff = ImageChops.difference(new_image1.convert("RGB"), new_image2.convert("RGB"))
    assert not diff.getbbox()

    # Changing reference, and it now differs from copy
    new_image3 = new_image1.copy()
    nd_image[:, :, :] = 0xFF
    diff = ImageChops.difference(new_image1.convert("RGB"), new_image3.convert("RGB"))
    assert diff.getbbox()

    pyboy.stop(save=False)


def test_tetris(tetris_rom):
    NEXT_TETROMINO = 0xC213

    pyboy = PyBoy(tetris_rom, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(120, False, False)
    tetris = pyboy.game_wrapper
    tetris.set_tetromino("T")

    first_brick = False
    tile_map = pyboy.tilemap_background
    for frame in range(5282):  # Enough frames to get a "Game Over"
        pyboy.tick(1, False, False)

        assert pyboy.screen.get_tilemap_position() == ((0, 0), (-7, 0))

        # Start game. Just press Start and A when the game allows us.
        # The frames are not 100% accurate.
        if frame == 144:
            pyboy.button("start")
        elif frame == 152:
            pyboy.button("a")
        elif frame == 156:
            pyboy.button("a")
        elif frame == 162:
            pyboy.button("a")

        # Play game. When we are passed the 168th frame, the game has begone.
        # The "technique" is just to move the Tetromino to the right.
        elif frame > 168:
            if frame % 2 == 0:
                pyboy.button("right")

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
                # breakpoint()
                if any(filter(lambda x: x != 47, tile_map[2:12, 17])):
                    first_brick = True
                    print(frame)
                    print("First brick touched the bottom!")

                    game_board_matrix = list(tile_map[2:12, :18])
                    assert game_board_matrix == (
                        [
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 133, 133, 133],
                            [47, 47, 47, 47, 47, 47, 47, 47, 133, 47],
                        ]
                    )

                    tile_map.use_tile_objects(True)

                    t1 = tile_map[0, 0]
                    t2 = tile_map.tile(0, 0)
                    t3 = tile_map.tile(1, 0)
                    assert t1 == t2, "Testing __eq__ method of Tile object"
                    assert t1 != t3, "Testing not __eq__ method of Tile object"

                    game_board_matrix = [[x.tile_identifier for x in row] for row in tile_map[2:12, :18]]
                    tile_map.use_tile_objects(False)
                    assert game_board_matrix == (
                        [
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
                            [47, 47, 47, 47, 47, 47, 47, 133, 133, 133],
                            [47, 47, 47, 47, 47, 47, 47, 47, 133, 47],
                        ]
                    )

            if frame == 1014:
                assert not first_brick

            if frame == 1015:
                assert first_brick

                s1 = pyboy.get_sprite(0)
                s2 = pyboy.get_sprite(1)
                assert s1 == s1
                assert s1 != s2
                assert s1.tiles[0] == s2.tiles[0], "Testing equal tiles of two different sprites"

                # Test that both ways of getting identifiers work and provides the same result.
                all_sprites = [
                    (s.x, s.y, s.tiles[0].tile_identifier, s.on_screen)
                    for s in [pyboy.get_sprite(n) for n in range(40)]
                ]
                all_sprites2 = [
                    (s.x, s.y, s.tile_identifier, s.on_screen) for s in [pyboy.get_sprite(n) for n in range(40)]
                ]
                assert all_sprites == all_sprites2

                # Verify data with known reference
                # pyboy.screen.image.show()
                assert all_sprites == (
                    [
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
                    ]
                )

                assert pyboy.memory[NEXT_TETROMINO] == 24
                assert tetris.next_tetromino() == "T"


def test_tilemap_position_list(supermarioland_rom):
    pyboy = PyBoy(supermarioland_rom, window="null")
    pyboy.tick(1, False, False)
    assert len(pyboy.screen.tilemap_position_list) == 144, "Expected 144 scanlines"
    assert len(pyboy.screen.tilemap_position_list[0]) == 4, "Expected (SCX, SCY, WX, WY)"
    assert (
        sum((sum(x) for x in pyboy.screen.tilemap_position_list)) == 0
    ), "Expected LCD to be disabled, and positions be 0"
    pyboy.tick(99, False, False)

    # Start the game
    pyboy.button("start")
    pyboy.tick(1, False, False)

    # Move right for 100 frame
    pyboy.button_press("right")
    pyboy.tick(100, True)

    # Get screen positions, and verify the values
    positions = pyboy.screen.tilemap_position_list
    for y in range(1, 16):
        assert positions[y][0] == 0  # HUD
    for y in range(16, 144):
        assert positions[y][0] >= 49  # Actual screen position
        last_y = positions[y][0]

    # Progress another 10 frames to see and increase in SCX
    pyboy.tick(10, False, False)

    # Get screen positions, and verify the values
    positions = pyboy.screen.tilemap_position_list
    for y in range(1, 16):
        assert positions[y][0] == 0  # HUD
    for y in range(16, 144):
        assert positions[y][0] >= last_y + 10  # Actual screen position

    pyboy.stop(save=False)


def test_button(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)

    assert len(pyboy.events) == 0  # Nothing injected yet
    pyboy.button("start")
    assert len(pyboy.events) == 1  # Button press immediately
    assert pyboy.events[0] == WindowEvent.PRESS_BUTTON_START
    pyboy.tick(1, False, False)
    assert len(pyboy.events) == 1  # Button release delayed
    assert pyboy.events[0] == WindowEvent.RELEASE_BUTTON_START
    pyboy.tick(1, False, False)
    assert len(pyboy.events) == 0  # No input

    assert len(pyboy.events) == 0  # Nothing injected yet
    pyboy.button("start", 3)
    assert len(pyboy.events) == 1  # Button press immediately
    assert pyboy.events[0] == WindowEvent.PRESS_BUTTON_START
    pyboy.tick(1, False, False)
    assert len(pyboy.events) == 0  # No input
    pyboy.tick(1, False, False)
    assert len(pyboy.events) == 0  # No input
    pyboy.tick(1, False, False)
    assert len(pyboy.events) == 1  # Button release delayed
    assert pyboy.events[0] == WindowEvent.RELEASE_BUTTON_START
    pyboy.tick(1, False, False)
    assert len(pyboy.events) == 0  # No input
