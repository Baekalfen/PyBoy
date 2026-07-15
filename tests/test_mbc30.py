#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
import os.path
from pathlib import Path

import PIL
import pytest

from pyboy import PyBoy
from pyboy.core.cartridge.cartridge import load_cartridge

OVERWRITE_PNGS = False


def make_rom(carttype, ram_size_code, rom_banks):
    rom = bytearray(rom_banks * 16 * 1024)
    rom[0x0134:0x013E] = b"MBC30 TEST"
    rom[0x0147] = carttype
    rom[0x0149] = ram_size_code
    checksum = 0
    for m in range(0x0134, 0x014D):
        checksum = (checksum - rom[m] - 1) & 0xFF
    rom[0x014D] = checksum
    return io.BytesIO(bytes(rom))


@pytest.mark.parametrize(
    "carttype, ram_size_code, rom_banks, mbc_name",
    [
        (0x10, 0x03, 2, "MBC3"),  # MBC3+TIMER+RAM+BATT, 32KB RAM
        (0x13, 0x03, 2, "MBC3"),  # MBC3+RAM+BATT, 32KB RAM
        (0x10, 0x05, 2, "MBC30"),  # 64KB RAM, RTC (Pokémon Crystal (JP))
        (0x13, 0x05, 2, "MBC30"),  # 64KB RAM, no RTC (MBC30 test ROM)
        (0x13, 0x03, 256, "MBC30"),  # 4MB ROM
    ],
)
def test_mbc30_detection(carttype, ram_size_code, rom_banks, mbc_name):
    cartridge = load_cartridge(make_rom(carttype, ram_size_code, rom_banks), None, None)
    assert type(cartridge).__name__ == mbc_name


def compare_screen(pyboy, name):
    png_path = Path(f"tests/test_results/mbc30/{name}.png")
    image = pyboy.screen.image.convert("RGB")
    if OVERWRITE_PNGS:
        png_path.parents[0].mkdir(parents=True, exist_ok=True)
        image.save(png_path)
    else:
        assert png_path.exists(), "Test result doesn't exist"
        old_image = PIL.Image.open(png_path).convert("RGB")
        diff = PIL.ImageChops.difference(image, old_image)
        if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
            image.show()
            old_image.show()
            diff.show()
        assert not diff.getbbox(), f"Images are different! {name}"


# https://github.com/ZoomTen/mbc30test
def test_mbc30_test_rom(mbc30_test_file):
    pyboy = PyBoy(mbc30_test_file, window="null")
    pyboy.set_emulation_speed(0)

    # The SRAM test runs on its own. "MBC30 SRAM OK!" means all 8 banks
    # were accessible ("MBC3 SRAM OK!" would mean only 4).
    pyboy.tick(610, True)
    compare_screen(pyboy, "sram_ok")

    # Pressing A starts the ROM test. "MBC30 ROM OK!" means all 256 ROM
    # banks were accessible.
    pyboy.button("a")
    pyboy.tick(520, True)
    compare_screen(pyboy, "rom_ok")

    pyboy.stop(save=False)
