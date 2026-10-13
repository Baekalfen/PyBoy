#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
from pathlib import Path

import PIL
from PIL import ImageChops
import pytest

from pyboy import PyBoy


def dmg_shade_classes(image):
    # The reference images are captured from hardware with its own shade
    # mapping (0xFF, 0xAA, 0x55, 0x00), and PyBoy renders with a different
    # palette, so compare shade classes instead of exact RGB values
    pixels = image.convert("L").tobytes()
    classes = bytearray(len(pixels))
    for i, gray in enumerate(pixels):
        classes[i] = 3 if gray <= 40 else 2 if gray <= 120 else 1 if gray <= 200 else 0
    return PIL.Image.frombytes("L", image.size, bytes(classes))


# https://github.com/gbdev/GBEmulatorShootout/tree/main/testroms/daid
# (rom, cgb, frames, reference images, real boot ROM, shade-class comparison)
DAID_IMAGE_CASES = [
    pytest.param(
        "ppu_scanline_bgp.gb",
        False,
        360,
        # The reference differs between hardware revisions (DMG, MGB, CGB in DMG mode); match any
        ["ppu_scanline_bgp_0.dmg.png", "ppu_scanline_bgp_1.dmg.png", "ppu_scanline_bgp_2.dmg.png"],
        True,
        True,
        id="ppu_scanline_bgp-DMG",
    ),
    pytest.param(
        "ppu_scanline_bgp.gb",
        True,
        120,
        ["ppu_scanline_bgp.gbc.png"],
        False,
        False,
        marks=pytest.mark.xfail(reason="BGP change mid-scanline timing differs from hardware"),
        id="ppu_scanline_bgp-CGB",
    ),
    pytest.param(
        "speed_switch_timing_div.gbc",
        True,
        120,
        ["speed_switch_timing_div.png"],
        False,
        False,
        marks=pytest.mark.xfail(reason="DIV behavior on speed switch differs from hardware"),
        id="speed_switch_timing_div",
    ),
    pytest.param(
        "speed_switch_timing_ly.gbc",
        True,
        120,
        ["speed_switch_timing_ly.png"],
        False,
        False,
        marks=pytest.mark.xfail(reason="LY behavior on speed switch differs from hardware"),
        id="speed_switch_timing_ly",
    ),
    pytest.param(
        "speed_switch_timing_stat.gbc",
        True,
        120,
        ["speed_switch_timing_stat.png"],
        False,
        False,
        marks=pytest.mark.xfail(reason="STAT behavior on speed switch differs from hardware"),
        id="speed_switch_timing_stat",
    ),
    pytest.param(
        "stop_instr.gb",
        False,
        120,
        ["stop_instr.dmg.png"],
        False,
        False,
        marks=pytest.mark.xfail(reason="STOP does not stop the PPU as on DMG hardware"),
        id="stop_instr-DMG",
    ),
    pytest.param(
        "stop_instr.gb",
        True,
        120,
        ["stop_instr.gbc.png"],
        False,
        False,
        marks=pytest.mark.xfail(reason="STOP does not behave as on CGB hardware"),
        id="stop_instr-CGB",
    ),
    pytest.param(
        "stop_instr_gbc_mode3.gb",
        True,
        120,
        ["stop_instr_gbc_mode3.png"],
        False,
        False,
        marks=pytest.mark.xfail(reason="STOP during mode 3 does not behave as on CGB hardware"),
        id="stop_instr_gbc_mode3",
    ),
]


@pytest.fixture(scope="session")
def dmg_boot_rom(secrets):
    # The daid image tests that reflect DMG hardware captures need the real
    # boot ROM; the bundled one does not run the PPU in the same way
    path = Path(secrets) / "DMG_ROM.bin"
    if not path.exists():
        pytest.skip("DMG boot ROM not available")
    return str(path)


@pytest.mark.parametrize("rom, cgb, frames, references, use_bootrom, shade_class_compare", DAID_IMAGE_CASES)
def test_daid_image(
    rom, cgb, frames, references, use_bootrom, shade_class_compare, daid_dir, references_dir, dmg_boot_rom
):
    pyboy = PyBoy(daid_dir + rom, window="null", cgb=cgb, bootrom=dmg_boot_rom if use_bootrom else None)
    pyboy.set_emulation_speed(0)
    pyboy.tick(frames, True)

    image = pyboy.screen.image.convert("RGB")
    pyboy.stop(save=False)

    if shade_class_compare:
        # The references are captured from hardware with its own shade
        # mapping, so compare shade classes instead of exact RGB values
        image = dmg_shade_classes(image)

    best_diff = None
    best_diff_pixels = None
    for reference in references:
        png_path = Path(f"{references_dir}daid/{reference}")
        assert png_path.exists(), "Reference image doesn't exist"
        old_image = PIL.Image.open(png_path).convert("RGB")
        if shade_class_compare:
            old_image = dmg_shade_classes(old_image)
        diff = ImageChops.difference(image, old_image)
        diff_pixels = sum(1 for value in diff.tobytes() if value)
        if best_diff_pixels is None or diff_pixels < best_diff_pixels:
            best_diff = diff
            best_diff_pixels = diff_pixels

    if best_diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
        image.show()
        best_diff.show()
    assert not best_diff.getbbox(), f"Images are different! {rom}"


def test_daid_rom_and_ram(daid_dir):
    pyboy = PyBoy(daid_dir + "rom_and_ram.gb", window="null", cgb=False)
    pyboy.set_emulation_speed(0)
    pyboy.tick(240, True)

    # daid test ROMs use tiles 0x100 + ASCII for their font
    text = ""
    for y in range(18):
        for x in range(20):
            tile = pyboy.tilemap_background[x, y] & 0xFF
            text += chr(tile) if 32 <= tile < 127 else " "
        text += "\n"
    pyboy.stop(save=False)

    assert "ROM+RAM:" in text, text
    assert "No SRAM enable req." in text, text
    assert "SRAM > 2K" in text, text
