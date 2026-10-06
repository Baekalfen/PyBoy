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

# https://github.com/gbdev/GBEmulatorShootout/tree/main/testroms/daid
# (rom, cgb, frames, reference images, xfail reason)
DAID_IMAGE_CASES = [
    pytest.param(
        "ppu_scanline_bgp.gb",
        False,
        120,
        # The reference differs between hardware revisions (DMG, MGB, CGB in DMG mode); match any
        ["ppu_scanline_bgp_0.dmg.png", "ppu_scanline_bgp_1.dmg.png", "ppu_scanline_bgp_2.dmg.png"],
        marks=pytest.mark.xfail(reason="BGP change mid-scanline timing differs from hardware"),
    ),
    pytest.param(
        "ppu_scanline_bgp.gb",
        True,
        120,
        ["ppu_scanline_bgp.gbc.png"],
        marks=pytest.mark.xfail(reason="BGP change mid-scanline timing differs from hardware"),
    ),
    pytest.param(
        "speed_switch_timing_div.gbc",
        True,
        120,
        ["speed_switch_timing_div.png"],
        marks=pytest.mark.xfail(reason="DIV behavior on speed switch differs from hardware"),
    ),
    pytest.param(
        "speed_switch_timing_ly.gbc",
        True,
        120,
        ["speed_switch_timing_ly.png"],
        marks=pytest.mark.xfail(reason="LY behavior on speed switch differs from hardware"),
    ),
    pytest.param(
        "speed_switch_timing_stat.gbc",
        True,
        120,
        ["speed_switch_timing_stat.png"],
        marks=pytest.mark.xfail(reason="STAT behavior on speed switch differs from hardware"),
    ),
    pytest.param(
        "stop_instr.gb",
        False,
        120,
        ["stop_instr.dmg.png"],
        marks=pytest.mark.xfail(reason="STOP does not stop the PPU as on DMG hardware"),
    ),
    pytest.param(
        "stop_instr.gb",
        True,
        120,
        ["stop_instr.gbc.png"],
        marks=pytest.mark.xfail(reason="STOP does not behave as on CGB hardware"),
    ),
    pytest.param(
        "stop_instr_gbc_mode3.gb",
        True,
        120,
        ["stop_instr_gbc_mode3.png"],
        marks=pytest.mark.xfail(reason="STOP during mode 3 does not behave as on CGB hardware"),
    ),
]


@pytest.mark.parametrize("rom, cgb, frames, references", DAID_IMAGE_CASES)
def test_daid_image(rom, cgb, frames, references, daid_dir, references_dir):
    pyboy = PyBoy(daid_dir + rom, window="null", cgb=cgb)
    pyboy.set_emulation_speed(0)
    pyboy.tick(frames, True)

    image = pyboy.screen.image.convert("RGB")
    pyboy.stop(save=False)

    best_diff = None
    best_diff_pixels = None
    for reference in references:
        png_path = Path(f"{references_dir}daid/{reference}")
        assert png_path.exists(), "Reference image doesn't exist"
        old_image = PIL.Image.open(png_path).convert("RGB")
        diff = ImageChops.difference(image, old_image)
        diff_pixels = sum(1 for p in diff.getdata() if p != (0, 0, 0))
        if best_diff_pixels is None or diff_pixels < best_diff_pixels:
            best_diff = diff
            best_diff_pixels = diff_pixels

    if best_diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
        image.show()
        best_diff.show()
    assert not best_diff.getbbox(), f"Images are different! {rom}"


@pytest.mark.xfail(reason="Not expected to pass yet")
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
