#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pytest

from pyboy import PyBoy


def test_memoryview(default_rom):
    p = PyBoy(default_rom)

    assert p.memory[0] == 49
    assert p.memory[0:10] == [49, 254, 255, 33, 0, 128, 175, 34, 124, 254]
    assert p.memory[0:10:2] == [49, 255, 0, 175, 124]

    assert p.memory[0xFFF0:0x10000] == [0] * 16
    p.memory[0xFFFF] = 1
    assert p.memory[0xFFF0:0x10000] == [0] * 15 + [1]
    assert p.memory[0xFFFF] == 1

    # Requires start and end address
    with pytest.raises(AssertionError):
        p.memory[:10] == []
    with pytest.raises(AssertionError):
        p.memory[:10:] == []
    with pytest.raises(AssertionError):
        p.memory[0xFF00:] == []
    with pytest.raises(AssertionError):
        p.memory[0xFF00::] == []
    with pytest.raises(AssertionError):
        p.memory[:10] = 0
    with pytest.raises(AssertionError):
        p.memory[:10:] = 0
    with pytest.raises(AssertionError):
        p.memory[0xFF00:] = 0
    with pytest.raises(AssertionError):
        p.memory[0xFF00::] = 0

    # Attempt write to ROM area
    p.memory[0:10] = 1
    assert p.memory[0:10] == [49, 254, 255, 33, 0, 128, 175, 34, 124, 254]

    # Actually do write to RAM area
    assert p.memory[0xC000:0xC00a] == [0] * 10
    p.memory[0xC000:0xC00a] = 123
    assert p.memory[0xC000:0xC00a] == [123] * 10

    # Attempt to write slice to ROM area
    p.memory[0:5] = [0, 1, 2, 3, 4]
    assert p.memory[0:10] == [49, 254, 255, 33, 0, 128, 175, 34, 124, 254]

    # Actually do write slice to RAM area
    p.memory[0xC000:0xC00a] = [0] * 10
    assert p.memory[0xC000:0xC00a] == [0] * 10
    p.memory[0xC000:0xC00a] = [1] * 10
    assert p.memory[0xC000:0xC00a] == [1] * 10

    # Attempt to write too large memory slice into memory area
    with pytest.raises(AssertionError):
        p.memory[0xC000:0xC001] = [1] * 10

    # Attempt to write too small memory slice into memory area
    with pytest.raises(AssertionError):
        p.memory[0xC000:0xC00a] = [1] * 2

    # Read specific ROM bank
    assert p.memory[0, 0x00:0x10] == [64, 65, 66, 67, 68, 69, 70, 65, 65, 65, 71, 65, 65, 65, 72, 73]
    assert p.memory[1, 0x00] == 0
    with pytest.raises(AssertionError):
        # Slicing currently unsupported
        assert p.memory[0:2, 0x00:0x10] == []


def test_cgb_banks(cgb_acid_file): # Any CGB file
    p = PyBoy(cgb_acid_file)

    # Read VRAM banks through both aliases
    assert p.memory[0, 0x8000:0x8010] == [0] * 16
    assert p.memory[1, 0x8000:0x8010] == [0] * 16

    # Set some value in VRAM
    p.memory[0, 0x8000:0x8010] = [1] * 16
    p.memory[1, 0x8000:0x8010] = [2] * 16

    # Read same value from both VRAM banks through both aliases
    assert p.memory[0, 0x8000:0x8010] == [1] * 16
    assert p.memory[1, 0x8000:0x8010] == [2] * 16

    # Read WRAM banks through both aliases
    assert p.memory[0, 0xC000:0xC010] == [0] * 16
    assert p.memory[7, 0xC000:0xC010] == [0] * 16
    assert p.memory[0, 0xD000:0xD010] == [0] * 16
    assert p.memory[7, 0xD000:0xD010] == [0] * 16

    # Set some value in WRAM
    p.memory[0, 0xC000:0xC010] = [1] * 16
    p.memory[7, 0xC000:0xC010] = [2] * 16

    # Read same value from both WRAM banks through both aliases
    assert p.memory[0, 0xC000:0xC010] == [1] * 16
    assert p.memory[7, 0xC000:0xC010] == [2] * 16
    assert p.memory[0, 0xD000:0xD010] == [1] * 16
    assert p.memory[7, 0xD000:0xD010] == [2] * 16

    with pytest.raises(AssertionError):
        # Slicing currently unsupported
        p.memory[0:2, 0xD000:0xD010] = 1

    with pytest.raises(AssertionError):
        p.memory[8, 0xD000] # Only bank 0-7

    with pytest.raises(AssertionError):
        p.memory[8, 0xD000] = 1 # Only bank 0-7
