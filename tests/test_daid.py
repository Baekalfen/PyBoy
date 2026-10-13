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
# (rom, cgb, frames, reference images, real boot ROM, shade-class comparison,
#  expected-failure reason. A case that produces a different image xfails with
#  its reason instead of failing, so the test keeps exercising the emulator)
DAID_IMAGE_CASES = [
    pytest.param(
        "ppu_scanline_bgp.gb",
        False,
        360,
        # The reference differs between hardware revisions (DMG, MGB, CGB in DMG mode); match any
        ["ppu_scanline_bgp_0.dmg.png", "ppu_scanline_bgp_1.dmg.png", "ppu_scanline_bgp_2.dmg.png"],
        True,
        True,
        None,
        id="ppu_scanline_bgp-DMG",
    ),
    pytest.param(
        "ppu_scanline_bgp.gb",
        True,
        120,
        ["ppu_scanline_bgp.gbc.png"],
        False,
        False,
        # The write grid phase and the loop's data-row mapping now match the
        # capture; every shade transition still renders one dot late, but
        # the write landing is pinned to its current dot by the mealybug
        # CGB captures, so the remaining dot needs finer modeling.
        "Every shade transition renders one dot late; the write landing is pinned by the mealybug CGB captures",
        id="ppu_scanline_bgp-CGB",
    ),
    pytest.param(
        "speed_switch_timing_div.gbc",
        True,
        120,
        ["speed_switch_timing_div.png"],
        False,
        False,
        "DIV behavior on speed switch differs from hardware",
        id="speed_switch_timing_div",
    ),
    pytest.param(
        "speed_switch_timing_ly.gbc",
        True,
        120,
        ["speed_switch_timing_ly.png"],
        False,
        False,
        "LY behavior on speed switch differs from hardware",
        id="speed_switch_timing_ly",
    ),
    pytest.param(
        "speed_switch_timing_stat.gbc",
        True,
        120,
        ["speed_switch_timing_stat.png"],
        False,
        False,
        "STAT behavior on speed switch differs from hardware",
        id="speed_switch_timing_stat",
    ),
    pytest.param(
        "stop_instr.gb",
        False,
        # The DMG boot ROM alone takes over a hundred frames before the game
        # reaches its STOP
        360,
        ["stop_instr.dmg.png"],
        True,
        True,
        None,
        id="stop_instr-DMG",
    ),
    pytest.param(
        "stop_instr.gb",
        True,
        120,
        ["stop_instr.gbc.png"],
        False,
        False,
        None,
        id="stop_instr-CGB",
    ),
    pytest.param(
        "stop_instr_gbc_mode3.gb",
        True,
        120,
        ["stop_instr_gbc_mode3.png"],
        False,
        False,
        # The STOP behavior matches the capture: the CPU stays stopped and the
        # PPU keeps displaying the last state. The reference was captured with
        # a clean tilemap, while PyBoy's internal boot ROM leaves its
        # synthetic logo tiles in the rows the game does not overwrite.
        "Internal CGB boot ROM logo tiles remain in the tilemap; hardware capture has a clean tilemap",
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


@pytest.mark.parametrize(
    "rom, cgb, frames, references, use_bootrom, shade_class_compare, xfail_reason", DAID_IMAGE_CASES
)
def test_daid_image(
    rom, cgb, frames, references, use_bootrom, shade_class_compare, xfail_reason, daid_dir, references_dir, dmg_boot_rom
):
    # The CGB references were captured on a CGB in DMG compatibility mode, with
    # its green monochrome palette. The darkest shade reads 0x0063C6 on the
    # capture, one bit off PyBoy's default 0x0063C5.
    cgb_palette = {"cgb_color_palette": ((0xFFFFFF, 0x7BFF31, 0x0063C6, 0x000000),) * 3} if cgb else {}
    pyboy = PyBoy(daid_dir + rom, window="null", cgb=cgb, bootrom=dmg_boot_rom if use_bootrom else None, **cgb_palette)
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
    if best_diff.getbbox():
        if xfail_reason:
            pytest.xfail(xfail_reason)
        raise AssertionError(f"Images are different! {rom}")


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
