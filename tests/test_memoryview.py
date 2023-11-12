#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pytest

from pyboy import PyBoy


def test_memoryview(default_rom, boot_rom):
    p = PyBoy(default_rom, bootrom_file=boot_rom)

    with open(default_rom, "rb") as f:
        rom_bytes = [ord(f.read(1)) for x in range(16)]

    with open(boot_rom, "rb") as f:
        bootrom_bytes = [ord(f.read(1)) for x in range(16)]

    assert p.memory[0] == 49
    assert p.memory[0:10] == bootrom_bytes[:10]
    assert p.memory[0:10:2] == bootrom_bytes[:10:2]

    assert p.memory[0xFFF0:0x10000] == [0] * 16
    p.memory[0xFFFF] = 1
    assert p.memory[0xFFF0:0x10000] == [0] * 15 + [1]
    assert p.memory[0xFFFF] == 1

    # Requires start and end address
    with pytest.raises(AssertionError):
        p.memory[:10] == []
    with pytest.raises(AssertionError):
        p.memory[20:10] == []
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
    assert p.memory[0:10] == bootrom_bytes[:10]

    # Actually do write to RAM area
    assert p.memory[0xC000:0xC00a] == [0] * 10
    p.memory[0xC000:0xC00a] = 123
    assert p.memory[0xC000:0xC00a] == [123] * 10

    # Attempt to write slice to ROM area
    p.memory[0:5] = [0, 1, 2, 3, 4]
    assert p.memory[0:10] == bootrom_bytes[:10]

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
    assert p.memory[0, 0x00:0x10] == rom_bytes[:16]
    assert p.memory[1, 0x00] == 0
    with pytest.raises(AssertionError):
        # Slicing currently unsupported
        assert p.memory[0:2, 0x00:0x10] == []

    # Write to RAM bank
    p.memory[1, 0xA000] = 0
    assert p.memory[1, 0xA000] == 0
    assert p.memory[1, 0xA001] == 0
    p.memory[1, 0xA000] = 1
    assert p.memory[1, 0xA000] == 1
    p.memory[1, 0xA000:0xA010] = 2
    assert p.memory[1, 0xA000] == 2
    assert p.memory[1, 0xA001] == 2

    with pytest.raises(AssertionError):
        # Out of bounds
        p.memory[0, 0x00:0x9000]


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
