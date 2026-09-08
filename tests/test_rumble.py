#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy import PyBoy
import tempfile


def test_rumble_with_non_mbc5_cartridge(default_rom):
    pyboy = PyBoy(default_rom, window="null")

    # Default ROM is not MBC5, so rumble should not be supported
    assert pyboy.rumble.supported == False
    assert pyboy.rumble.enabled == False

    pyboy.stop(save=False)


def make_mbc5(_type, default_rom):
    with open(default_rom, "rb") as f:
        rom_data = bytearray(f.read())
    if len(rom_data) > 0x147:
        rom_data[0x147] = _type
        # Fix checksum by recalculating it using PyBoy's algorithm
        x = 0
        for m in range(0x134, 0x14D):
            x = x - rom_data[m] - 1
            x &= 0xFF
        rom_data[0x14D] = x

    temp_rom = tempfile.mkdtemp() + "/test_mbc5.gbc"
    with open(temp_rom, "wb") as f:
        f.write(rom_data)

    return str(temp_rom)


def test_rumble_with_mbc5_cartridge(default_rom):
    # Test with non-rumble MBC5 cartridge (0x19)
    pyboy_19 = PyBoy(make_mbc5(0x19, default_rom), window="null")
    assert pyboy_19.rumble.supported == False
    assert pyboy_19.rumble.enabled == False
    pyboy_19.stop(save=False)

    # Test with rumble MBC5 cartridge (0x1C)
    pyboy_1C = PyBoy(make_mbc5(0x1C, default_rom), window="null")
    assert pyboy_1C.rumble.supported == True
    assert pyboy_1C.rumble.enabled == False
    pyboy_1C.stop(save=False)

    # Test with MBC5+RUMBLE+RAM cartridge (0x1D)
    pyboy_1D = PyBoy(make_mbc5(0x1D, default_rom), window="null")
    assert pyboy_1D.rumble.supported == True
    assert pyboy_1D.rumble.enabled == False
    pyboy_1D.stop(save=False)

    # Test with MBC5+RUMBLE+RAM+BATT cartridge (0x1E)
    pyboy_1E = PyBoy(make_mbc5(0x1E, default_rom), window="null")
    assert pyboy_1E.rumble.supported == True
    assert pyboy_1E.rumble.enabled == False
    pyboy_1E.stop(save=False)


def test_rumble_setitem(default_rom):
    pyboy = PyBoy(make_mbc5(0x1C, default_rom), window="null")

    # Check that this ROM is detected as rumble-supported
    assert pyboy.rumble.supported == True
    assert pyboy.rumble.enabled == False

    # Write to RAM bank select register (0x4000-0x5fff) with bit 3 set
    pyboy.memory[0x4000] = 0x08  # Bit 3 is set
    assert pyboy.rumble.enabled == True

    # Write to RAM bank select register with bit 3 clear
    pyboy.memory[0x4000] = 0x00  # Bit 3 is clear
    assert pyboy.rumble.enabled == False

    # Write with other bits set but not bit 3
    pyboy.memory[0x4000] = 0x07  # Bits 0-2 set, bit 3 clear
    assert pyboy.rumble.enabled == False

    # Write with bit 3 and other bits set
    pyboy.memory[0x4000] = 0x0F  # All lower 4 bits set including bit 3
    assert pyboy.rumble.enabled == True

    pyboy.stop(save=False)
