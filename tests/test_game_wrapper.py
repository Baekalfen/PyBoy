#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import numpy as np

from pyboy import PyBoy
from pyboy.api.constants import LCDC_OFFSET, OAM_OFFSET, VRAM_OFFSET, TILES


def test_game_wrapper_basics(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)

    generic_wrapper = pyboy.game_wrapper
    assert generic_wrapper is not None
    pyboy.game_area()


def test_game_wrapper_sprites_tall(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)
    generic_wrapper = pyboy.game_wrapper
    assert generic_wrapper is not None
    pyboy.tick(120, False)

    pyboy.memory[LCDC_OFFSET] = (
        0b10000000  # LCD On
        | 0b10000100  # Sprites 8x16
        | 0b10000010  # Sprites on
    )

    pyboy.memory[VRAM_OFFSET : VRAM_OFFSET + 0x2000] = 0x00  # Clear all tile data!
    pyboy.memory[VRAM_OFFSET : VRAM_OFFSET + 32] = 0xFF  # First 2 tiles are black

    for y in [0, 8, 16, 24]:
        pyboy.memory[OAM_OFFSET : OAM_OFFSET + 4] = [
            y,  # Y: Value -16, so above the screen and move down
            16,  # X: A bit out
            0,  # Tile index 0
            0,  # Attributes
        ]
        pyboy.tick(1)

        if y == 0:
            assert len(np.where(generic_wrapper.game_area().flatten().flatten() != 256)[0]) == 0
        elif y == 8:
            assert len(np.where(generic_wrapper.game_area().flatten().flatten() != 256)[0]) == 1
        elif y == 16:
            assert len(np.where(generic_wrapper.game_area().flatten().flatten() != 256)[0]) == 2
        elif y == 24:
            assert len(np.where(generic_wrapper.game_area().flatten().flatten() != 256)[0]) == 2


def test_game_wrapper_mapping(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)
    assert np.all(pyboy.game_area() == 256)

    generic_wrapper = pyboy.game_wrapper
    assert generic_wrapper is not None
    pyboy.tick(5, True)
    assert np.all(
        pyboy.game_area()[8:11, 8:13]
        == np.array(
            [
                [1, 0, 1, 0, 0],
                [2, 3, 4, 5, 3],
                [0, 6, 0, 0, 6],
            ],
            dtype=np.uint32,
        )
    )

    # List-based mapping, don't call tick
    mapping = [x for x in range(TILES)]  # 1:1 mapping
    mapping[0] = 10
    mapping[1] = 10
    mapping[2] = 10
    mapping[3] = 10
    pyboy.game_area_mapping(mapping, 1000)
    assert np.all(
        pyboy.game_area()[8:11, 8:13]
        == np.array(
            [
                [10, 10, 10, 10, 10],
                [10, 10, 4, 5, 10],
                [10, 6, 10, 10, 6],
            ],
            dtype=np.uint32,
        )
    )

    # Array-based mapping, don't call tick
    mapping = np.asarray(mapping)
    mapping[0] = 1  # Map tile identifier 0 -> 1
    mapping[1] = 1  # Map tile identifier 1 -> 1
    mapping[2] = 1  # Map tile identifier 2 -> 1
    mapping[3] = 1  # Map tile identifier 3 -> 1
    pyboy.game_area_mapping(mapping, 1000)
    assert np.all(
        pyboy.game_area()[8:11, 8:13]
        == np.array(
            [
                [1, 1, 1, 1, 1],
                [1, 1, 4, 5, 1],
                [1, 6, 1, 1, 6],
            ],
            dtype=np.uint32,
        )
    )
