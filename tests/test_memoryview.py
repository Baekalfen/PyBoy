#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pytest

from pyboy import PyBoy
from pyboy.utils import PyBoyInvalidInputException, PyBoyOutOfBoundsException


def test_memoryview(default_rom, boot_rom):
    p = PyBoy(default_rom, window="null", bootrom=boot_rom)

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
    with pytest.raises(PyBoyInvalidInputException):
        p.memory[:10] == []
    with pytest.raises(PyBoyInvalidInputException):
        p.memory[20:10] == []
    with pytest.raises(PyBoyInvalidInputException):
        p.memory[:10:] == []
    with pytest.raises(PyBoyInvalidInputException):
        p.memory[0xFF00:] == []
    with pytest.raises(PyBoyInvalidInputException):
        p.memory[0xFF00::] == []
    with pytest.raises(PyBoyInvalidInputException):
        p.memory[:10] = 0
    with pytest.raises(PyBoyInvalidInputException):
        p.memory[:10:] = 0
    with pytest.raises(PyBoyInvalidInputException):
        p.memory[0xFF00:] = 0
    with pytest.raises(PyBoyInvalidInputException):
        p.memory[0xFF00::] = 0

    # Attempt write to ROM area
    p.memory[0:10] = 1
    assert p.memory[0:10] == bootrom_bytes[:10]

    # Actually do write to RAM area
    assert p.memory[0xC000:0xC00A] == [0] * 10
    p.memory[0xC000:0xC00A] = 123
    assert p.memory[0xC000:0xC00A] == [123] * 10

    # Attempt to write slice to ROM area
    p.memory[0:5] = [0, 1, 2, 3, 4]
    assert p.memory[0:10] == bootrom_bytes[:10]

    # Actually do write slice to RAM area
    p.memory[0xC000:0xC00A] = [0] * 10
    assert p.memory[0xC000:0xC00A] == [0] * 10
    p.memory[0xC000:0xC00A] = [1] * 10
    assert p.memory[0xC000:0xC00A] == [1] * 10

    # Attempt to write too large memory slice into memory area
    with pytest.raises(PyBoyInvalidInputException):
        p.memory[0xC000:0xC001] = [1] * 10

    # Attempt to write too small memory slice into memory area
    with pytest.raises(PyBoyInvalidInputException):
        p.memory[0xC000:0xC00A] = [1] * 2

    # Read specific ROM bank
    assert p.memory[0, 0x00:0x10] == rom_bytes[:16]
    assert p.memory[1, 0x00] == 0
    with pytest.raises(PyBoyInvalidInputException):
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

    with pytest.raises(PyBoyOutOfBoundsException):
        # Out of bounds
        p.memory[0, 0x00:0x9000]


def test_cgb_banks(cgb_acid_file):  # Any CGB file
    p = PyBoy(cgb_acid_file, window="null")

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

    with pytest.raises(PyBoyInvalidInputException):
        # Slicing currently unsupported
        p.memory[0:2, 0xD000:0xD010] = 1

    with pytest.raises(PyBoyOutOfBoundsException):
        p.memory[8, 0xD000]  # Only bank 0-7

    with pytest.raises(PyBoyOutOfBoundsException):
        p.memory[8, 0xD000] = 1  # Only bank 0-7


def test_get_set_override(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(1, False, False)

    assert pyboy.memory[0xFF40] == 0x00
    pyboy.memory[0xFF40] = 0x12
    assert pyboy.memory[0xFF40] == 0x12

    assert pyboy.memory[0, 0x0002] == 0x42  # Taken from ROM bank 0
    assert pyboy.memory[0x0002] == 0xFF  # Taken from bootrom
    assert pyboy.memory[-1, 0x0002] == 0xFF  # Taken from bootrom
    pyboy.memory[-1, 0x0002] = 0x01  # Change bootrom
    assert pyboy.memory[-1, 0x0002] == 0x01  # New value in bootrom
    assert pyboy.memory[0, 0x0002] == 0x42  # Taken from ROM bank 0

    pyboy.memory[0xFF50] = 1  # Disable bootrom
    assert pyboy.memory[0x0002] == 0x42  # Taken from ROM bank 0

    pyboy.memory[0, 0x0002] = 0x12
    assert pyboy.memory[0x0002] == 0x12
    assert pyboy.memory[0, 0x0002] == 0x12

    pyboy.stop(save=False)


def test_boundaries(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)

    # Boot ROM boundary - Expecting 0 to 0xFF both including to change
    assert pyboy.memory[-1, 0x00] != 0
    assert pyboy.memory[-1, 0xFF] != 0
    pyboy.memory[-1, 0:0x100] = [0] * 0x100  # Clear boot ROM
    with pytest.raises(PyBoyOutOfBoundsException):
        pyboy.memory[-1, 0:0x101] = [0] * 0x101  # Out of bounds
    assert pyboy.memory[-1, 0x00] == 0
    assert pyboy.memory[-1, 0xFF] == 0

    pyboy.memory[0xFF50] = 1  # Disable bootrom

    pyboy.memory[0, 0x0000] = 123
    pyboy.memory[0, 0x3FFF] = 123
    pyboy.memory[1, 0x4000] = 123  # Notice bank! [0,0x4000] would wrap around to 0

    # ROM Bank 0 boundary - Expecting 0 to 0x3FFF both including to change
    pyboy.memory[0, 0:0x4000] = [0] * 0x4000
    with pytest.raises(PyBoyOutOfBoundsException):
        pyboy.memory[0, 0:0x4001] = [0] * 0x4001  # Over boundary!

    # NOTE: Not specifying bank! Defaulting to 0 up to 0x3FFF and then 1 at 0x4000
    assert pyboy.memory[0x0000] == 0
    assert pyboy.memory[0x3FFF] == 0
    assert pyboy.memory[0x4000] == 123
    pyboy.memory[0, 0:0x4000] = [1] * 0x4000
    assert pyboy.memory[0x0000] == 1
    assert pyboy.memory[0x3FFF] == 1
    assert pyboy.memory[0x4000] == 123
