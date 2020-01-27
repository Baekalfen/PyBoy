#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import hashlib
import io
import os

import numpy as np
import PIL
import pytest
from pyboy import PyBoy, botsupport, windowevent

boot_rom = "ROMs/DMG_ROM.bin"
tetris_rom = "ROMs/Tetris.gb"
any_rom = tetris_rom


def test_misc():
    pyboy = PyBoy(any_rom, window_type="dummy", bootrom_file=boot_rom, disable_input=True, hide_window=True)
    pyboy.tick()
    pyboy.stop(save=False)


def test_tiles():
    pyboy = PyBoy(tetris_rom, window_type='headless', disable_input=True, hide_window=True)
    pyboy.set_emulation_speed(0)

    tile = pyboy.get_window_tile_map().get_tile(0, 0)
    image = tile.image()
    assert isinstance(image, PIL.Image.Image)
    ndarray = tile.image_ndarray()
    assert isinstance(ndarray, np.ndarray)
    assert ndarray.shape == (8, 8, 4)
    assert ndarray.dtype == np.uint8
    data = tile.image_data()
    assert data.shape == (8, 8)

    for identifier in range(384):
        t = pyboy.get_tile(identifier)
        assert t.identifier == identifier
        if identifier > 0xFF:
            assert t.index[1] == identifier - botsupport.constants.LOW_TILEDATA_NTILES
        else:
            assert t.index[1] == identifier
    with pytest.raises(Exception):
        pyboy.get_tile(-1)
    with pytest.raises(Exception):
        pyboy.get_tile(385)

    pyboy.stop(save=False)


@pytest.mark.skipif(os.environ.get('TEST_NO_UI'), reason="Skipping test, as there is no UI")
def test_screen_buffer_and_image():
    for window, dims, cformat, boot_logo_hash_predigested in [
            # These are different because the underlying format is different. We'll test the actual image afterwards.
            ("SDL2", (160, 144), 'RGBA',
                b'=\xff\xf9z 6\xf0\xe9\xcb\x05J`PM5\xd4rX+\x1b~z\xef1\xe0\x82\xc4t\x06\x82\x12C'),
            ("headless", (160, 144), 'RGBA',
                b'=\xff\xf9z 6\xf0\xe9\xcb\x05J`PM5\xd4rX+\x1b~z\xef1\xe0\x82\xc4t\x06\x82\x12C'),
            ("OpenGL", (144, 160), 'RGB',
                b's\xd1R\x88\xe0a\x14\xd0\xd2\xecOk\xe8b\xae.\x0e\x1e\xb6R\xc2\xe9:\xa2\x0f\xae\xa2\x89M\xbf\xd8|')
            ]:

        pyboy = PyBoy(any_rom, window_type=window, window_scale=1, bootrom_file=boot_rom, disable_input=True,
                      hide_window=True)
        pyboy.set_emulation_speed(0)
        for n in range(275): # Iterate to boot logo
            pyboy.tick()

        assert pyboy.get_raw_screen_buffer_dims() == dims
        assert pyboy.get_raw_screen_buffer_format() == cformat

        boot_logo_hash = hashlib.sha256()
        boot_logo_hash.update(pyboy.get_raw_screen_buffer())
        assert boot_logo_hash.digest() == boot_logo_hash_predigested
        assert isinstance(pyboy.get_raw_screen_buffer(), bytes)

        # The output of `get_screen_image` is supposed to be homogeneous, which means a shared hash between versions.
        boot_logo_png_hash_predigested = (
                b'\xf4b,(\xbe\xaa\xf8\xec\x06\x9fJ-\x84\xd3I\x16\xb8'
                b'\xe3\xd0\xd5\xae\x80\x01\x1e\x96\xba!1\xeb\xd1\xce_'
            )
        boot_logo_png_hash = hashlib.sha256()
        image = pyboy.get_screen_image()
        assert isinstance(image, PIL.Image.Image)
        image_data = io.BytesIO()
        image.save(image_data, format='BMP')
        boot_logo_png_hash.update(image_data.getvalue())
        assert boot_logo_png_hash.digest() == boot_logo_png_hash_predigested

        # get_screen_ndarray
        numpy_hash = hashlib.sha256()
        numpy_array = np.ascontiguousarray(pyboy.get_screen_ndarray())
        assert isinstance(pyboy.get_screen_ndarray(), np.ndarray)
        assert numpy_array.shape == (144, 160, 3)
        numpy_hash.update(numpy_array.tobytes())
        assert numpy_hash.digest() == (
                b'\r\t\x87\x131\xe8\x06\x82\xcaO=\n\x1e\xa2K$'
                b'\xd6\x8e\x91R( H7\xd8a*B+\xc7\x1f\x19'
            )

        pyboy.stop(save=False)


def test_tetris():
    NEXT_TETROMINO = 0xC213

    def verify_screen_image(predigested):
        screen_hash = hashlib.sha256()
        image = pyboy.get_screen_image()
        image_data = io.BytesIO()
        image.save(image_data, format='BMP')
        screen_hash.update(image_data.getvalue())
        short_digest = screen_hash.digest()[:10] # Just for quick verification, and make the code less ugly
        if short_digest != predigested:
            print("Didn't match: " + str(short_digest))
            image.show()
            breakpoint()
        assert short_digest == predigested, "Didn't match: " + str(short_digest)

    pyboy = PyBoy(tetris_rom, bootrom_file="pyboy_fast", window_type='headless', disable_input=True, hide_window=True)
    pyboy.set_emulation_speed(0)

    first_brick = False
    tile_map = pyboy.get_window_tile_map()
    state_data = io.BytesIO()
    for frame in range(5282): # Enough frames to get a "Game Over". Otherwise do: `while not pyboy.tick():`
        pyboy.tick()

        assert pyboy.get_screen_position() == ((0, 0), (-7, 0))

        # Start game. Just press Start and A when the game allows us.
        # The frames are not 100% accurate.
        if frame == 20:
            verify_screen_image(b"O'\tw\xa8{\xb3\xd7]\t")
        elif frame == 144:
            verify_screen_image(b'X37?\xb6\xa1I\xf25\xc1')
            pyboy.send_input(windowevent.PRESS_BUTTON_START)
        elif frame == 145:
            pyboy.send_input(windowevent.RELEASE_BUTTON_START)
        elif frame == 152:
            verify_screen_image(b'~K\xe0\xa8"\xdb\xdd\xd9\x07\x80')
            pyboy.send_input(windowevent.PRESS_BUTTON_A)
        elif frame == 153:
            pyboy.send_input(windowevent.RELEASE_BUTTON_A)
        elif frame == 156:
            verify_screen_image(b'x\xb0\xfb)\xa0c<?am')
            pyboy.send_input(windowevent.PRESS_BUTTON_A)
        elif frame == 157:
            pyboy.send_input(windowevent.RELEASE_BUTTON_A)
        elif frame == 162:
            verify_screen_image(b'{\x93\xaa\xdc\xdc\xa3\xc3\x97\x8ez')
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
                    assert game_board_matrix == (
                            [[303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
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
                             [303, 303, 303, 303, 303, 303, 303, 303, 130, 130]]
                        )

                    tile_map.use_tile_objects(True)

                    t1 = tile_map[0, 0]
                    t2 = tile_map.get_tile(0, 0)
                    t3 = tile_map.get_tile(1, 0)
                    assert t1 == t2, "Testing __eq__ method of Tile object"
                    assert t1 != t3, "Testing not __eq__ method of Tile object"

                    game_board_matrix = [[x.identifier for x in row] for row in tile_map[2:12, :18]]
                    tile_map.use_tile_objects(False)
                    assert game_board_matrix == (
                            [[303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
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
                             [303, 303, 303, 303, 303, 303, 303, 303, 130, 130]]
                        )

            if frame == 1014:
                assert not first_brick

            if frame == 1015:
                assert first_brick

                # Test that all tiles says 'low' tile data, as sprites cannot use high tile data
                # NOTE: Would have used reduce, but Cython on Ubuntu 18.04 didn't like it
                all_low = False
                for s in [pyboy.get_sprite(n) for n in range(40)]:
                    all_low |= s.tiles[0].index[0]
                assert not all_low

                s1 = pyboy.get_sprite(0)
                s2 = pyboy.get_sprite(1)
                assert s1 == s1
                assert s1 != s2
                assert s1.tiles[0] == s2.tiles[0], "Testing equal tiles of two different sprites"

                # Test that both ways of getting indexes works and provides the same result.
                all_sprites = [(s.x, s.y, s.tiles[0].index[1], s.on_screen)
                               for s in [pyboy.get_sprite(n) for n in range(40)]]
                all_sprites2 = [(s.x, s.y, s.tile_index, s.on_screen) for s in [pyboy.get_sprite(n) for n in range(40)]]
                all_sprites3 = [(s.x, s.y, s.tile_identifier, s.on_screen)
                                for s in [pyboy.get_sprite(n) for n in range(40)]]
                assert all_sprites == all_sprites2
                assert all_sprites == all_sprites3

                # Verify data with known reference
                assert all_sprites == (
                    [(0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (80, 144, 130, True),
                     (88, 144, 130, True),
                     (88, 152, 130, True),
                     (96, 152, 130, True),
                     (136, 128, 131, True),
                     (144, 128, 131, True),
                     (136, 136, 131, True),
                     (144, 136, 131, True),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False),
                     (0, 0, 0, False)]
                    )

                assert pyboy.get_memory_value(NEXT_TETROMINO) == 12
                with open('tmp.state', 'wb') as f:
                    pyboy.save_state(f)
                pyboy.save_state(state_data)
                pyboy.set_memory_value(NEXT_TETROMINO, 11)
                assert pyboy.get_memory_value(NEXT_TETROMINO) == 11
                break

    for frame in range(1016, 1866):
        pyboy.tick()
        if frame == 1017:
            assert pyboy.get_memory_value(NEXT_TETROMINO) == 11 # Would have been 4 otherwise

        if frame == 1865:
            game_board_matrix = list(tile_map[2:12, :18])
            assert game_board_matrix == (
                    [[303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
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
                     [303, 303, 303, 303, 137, 303, 303, 303, 130, 130]]
                    )

    state_data.seek(0) # Reset to the start of the buffer. Otherwise, we call `load_state` at end of file
    with open('tmp.state', 'rb') as f:
        for _f in [f, state_data]: # Tests both file-written state and in-memory state
            pyboy.load_state(_f) # Reverts memory state to before we changed the Tetromino
            pyboy.tick()
            for frame in range(1016, 5282):
                pyboy.tick()
                if frame == 1017:
                    assert pyboy.get_memory_value(NEXT_TETROMINO) == 4 # Will 11 if load_state doesn't work

                if frame == 1865:
                    game_board_matrix = list(tile_map[2:12, :18])
                    assert game_board_matrix == (
                            [[303, 303, 303, 303, 303, 303, 303, 303, 303, 303],
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
                             [303, 303, 303, 303, 131, 131, 303, 130, 130, 303],
                             [303, 303, 303, 303, 131, 131, 303, 303, 130, 130]]
                                )
    os.remove('tmp.state')

    verify_screen_image(b'\xd4\xc6\x12\xe5\xe9\xa8\xbaZ\x9c\xe3')
    pyboy.stop(save=False)

# # Blargg's tests verifies this
# def test_get_serial():
#     pass


def test_disable_title():
    # Simply tests, that no exception is generated
    pyboy = PyBoy(any_rom, window_type="dummy", disable_input=True, hide_window=True)
    pyboy.disable_title()
    pyboy.tick()
    pyboy.stop(save=False)
