#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
# https://github.com/mattcurrie/mealybug-tearoom-tests
#
# The tests verify PPU register changes made during STAT mode 3 (mid-scanline).
# Each ROM signals completion with a LD B,B software breakpoint after ~10
# vblanks and then renders the same result every frame, so the screenshot is
# stable and can be compared against the expected images from the upstream
# repository.

import os
from pathlib import Path

import PIL
from PIL import ImageChops
import pytest

from pyboy import PyBoy

REFERENCE_DIR = Path("tests/references/mealybug")

MEALYBUG_ROMS = [
    "m2_win_en_toggle.gb",
    "m3_bgp_change.gb",
    "m3_bgp_change_sprites.gb",
    "m3_lcdc_bg_en_change.gb",
    "m3_lcdc_bg_en_change2.gb",
    "m3_lcdc_bg_map_change.gb",
    "m3_lcdc_bg_map_change2.gb",
    "m3_lcdc_obj_en_change.gb",
    "m3_lcdc_obj_en_change_variant.gb",
    "m3_lcdc_obj_size_change.gb",
    "m3_lcdc_obj_size_change_scx.gb",
    "m3_lcdc_tile_sel_change.gb",
    "m3_lcdc_tile_sel_change2.gb",
    "m3_lcdc_tile_sel_win_change.gb",
    "m3_lcdc_tile_sel_win_change2.gb",
    "m3_lcdc_win_en_change_multiple.gb",
    "m3_lcdc_win_en_change_multiple_wx.gb",
    "m3_lcdc_win_map_change.gb",
    "m3_lcdc_win_map_change2.gb",
    "m3_obp0_change.gb",
    "m3_scx_high_5_bits.gb",
    "m3_scx_high_5_bits_change2.gb",
    "m3_scx_low_3_bits.gb",
    "m3_scy_change.gb",
    "m3_scy_change2.gb",
    "m3_window_timing.gb",
    "m3_window_timing_wx_0.gb",
    "m3_wx_4_change.gb",
    "m3_wx_4_change_sprites.gb",
    "m3_wx_5_change.gb",
    "m3_wx_6_change.gb",
]

# PyBoy does not yet implement all mid-scanline PPU register changes, which is
# what these tests target. They are xfailed until the PPU is improved, and
# will show as XPASS once they start matching the expected images.
DMG_KNOWN_FAILURES = {
    "m3_bgp_change.gb",
    "m3_bgp_change_sprites.gb",
    "m3_lcdc_bg_en_change.gb",
    "m3_lcdc_bg_map_change.gb",
    "m3_lcdc_obj_en_change.gb",
    "m3_lcdc_obj_en_change_variant.gb",
    "m3_lcdc_obj_size_change.gb",
    "m3_lcdc_obj_size_change_scx.gb",
    "m3_lcdc_tile_sel_change.gb",
    "m3_lcdc_tile_sel_win_change.gb",
    "m3_lcdc_win_en_change_multiple.gb",
    "m3_lcdc_win_en_change_multiple_wx.gb",
    "m3_lcdc_win_map_change.gb",
    "m3_obp0_change.gb",
    "m3_scx_high_5_bits.gb",
    "m3_scx_low_3_bits.gb",
    "m3_scy_change.gb",
    "m3_window_timing.gb",
    "m3_window_timing_wx_0.gb",
    "m3_wx_4_change.gb",
    "m3_wx_4_change_sprites.gb",
    "m3_wx_5_change.gb",
    "m3_wx_6_change.gb",
}

CGB_KNOWN_FAILURES = {
    "m3_bgp_change.gb",
    "m3_bgp_change_sprites.gb",
    "m3_lcdc_bg_en_change.gb",
    "m3_lcdc_bg_en_change2.gb",
    "m3_lcdc_bg_map_change.gb",
    "m3_lcdc_bg_map_change2.gb",
    "m3_lcdc_obj_en_change.gb",
    "m3_lcdc_obj_en_change_variant.gb",
    "m3_lcdc_obj_size_change.gb",
    "m3_lcdc_obj_size_change_scx.gb",
    "m3_lcdc_tile_sel_change.gb",
    "m3_lcdc_tile_sel_change2.gb",
    "m3_lcdc_tile_sel_win_change.gb",
    "m3_lcdc_tile_sel_win_change2.gb",
    "m3_lcdc_win_en_change_multiple.gb",
    "m3_lcdc_win_en_change_multiple_wx.gb",
    "m3_lcdc_win_map_change.gb",
    "m3_lcdc_win_map_change2.gb",
    "m3_obp0_change.gb",
    "m3_scx_high_5_bits.gb",
    "m3_scx_high_5_bits_change2.gb",
    "m3_scx_low_3_bits.gb",
    "m3_scy_change.gb",
    "m3_scy_change2.gb",
    "m3_window_timing.gb",
    "m3_window_timing_wx_0.gb",
    "m3_wx_4_change.gb",
    "m3_wx_4_change_sprites.gb",
    "m3_wx_5_change.gb",
    "m3_wx_6_change.gb",
}


def dmg_shade_classes(image):
    # PyBoy's default DMG palette (0xFFFFFF, 0x999999, 0x555555, 0x000000) and the
    # expected images (0xFF, 0xAA, 0x55, 0x00) map to the same four shade classes
    classes = bytearray()
    pixels = image.convert("RGB").tobytes()
    for red, green, blue in zip(pixels[0::3], pixels[1::3], pixels[2::3]):
        value = (red + green + blue) // 3
        if value >= 200:
            classes.append(0)
        elif value >= 120:
            classes.append(1)
        elif value >= 40:
            classes.append(2)
        else:
            classes.append(3)
    return PIL.Image.frombytes("L", image.size, bytes(classes))


def cgb_diff_image(image, reference_image):
    # PyBoy converts 5-bit color components as (c << 3), while the expected
    # images use (c << 3) | (c >> 2) -- a difference of up to 7 per channel
    return (
        ImageChops.difference(image.convert("RGB"), reference_image.convert("RGB"))
        .point(lambda v: 255 if v > 7 else 0)
        .convert("L")
    )


def apply_boot_logo_state(pyboy):
    # The expected images were captured on real hardware, where the boot ROM
    # has uploaded the Nintendo logo to VRAM before handing control to the
    # cartridge. PyBoy's bundled boot ROM draws its own splash screen instead,
    # so tests that rely on the boot state (for example m3_obp0_change.gb)
    # need the same VRAM contents replicated here. This mirrors what the DMG
    # boot ROM leaves behind: logo tiles $01-$18 built from the cartridge
    # header, the (R) tile $19, and the corresponding tilemap entries.
    for i in range(48):
        byte = pyboy.memory[0x0104 + i]
        base = 0x8010 + i * 8
        for nibble, offset in ((byte >> 4, 0), (byte & 0xF, 4)):
            # Each of the nibble's bits is doubled horizontally into a 2-bit pair
            row = 0
            for k in (3, 2, 1, 0):
                bit = (nibble >> k) & 1
                row = (row << 2) | (bit << 1) | bit
            pyboy.memory[base + offset] = row
            pyboy.memory[base + offset + 2] = row

    # (R) symbol, low bitplane only: one row every 2 bytes, high plane zero
    for row, value in enumerate((0x3C, 0x42, 0xB9, 0xA5, 0xB9, 0xA5, 0x42, 0x3C)):
        pyboy.memory[0x8190 + row * 2] = value

    # Tilemap: logo on rows 8-9, (R) at the start of row 10
    pyboy.memory[0x9910] = 0x19
    for i in range(12):
        pyboy.memory[0x9904 + i] = 0x01 + i
        pyboy.memory[0x9924 + i] = 0x0D + i

    # Clear splash remnants from the bundled boot ROM that the logo does not
    # overwrite
    pyboy.memory[0x9949] = 0
    pyboy.memory[0x994C] = 0


@pytest.mark.parametrize("cgb", [False, True], ids=["DMG", "CGB"])
@pytest.mark.parametrize("rom", MEALYBUG_ROMS)
def test_mealybug(cgb, rom, mealybug_dir):
    reference = REFERENCE_DIR / ("cgb" if cgb else "dmg") / (rom[:-3] + ".png")
    if not reference.exists():
        pytest.skip(f"No expected image for {rom} on {'CGB' if cgb else 'DMG'}")

    pyboy = PyBoy(mealybug_dir + rom, window="null", cgb=cgb)
    pyboy.set_emulation_speed(0)
    pyboy.tick(1, True)
    if not cgb:
        # The bundled boot ROM has finished its VRAM setup at this point, and
        # the cartridge has not started yet. The real boot ROM would leave the
        # Nintendo logo in VRAM here.
        apply_boot_logo_state(pyboy)
    pyboy.tick(58, True)
    pyboy.tick(20, True)
    image = pyboy.screen.image
    pyboy.stop(save=False)

    reference_image = PIL.Image.open(reference)
    if cgb:
        diff_image = cgb_diff_image(image, reference_image)
    else:
        diff_image = ImageChops.difference(dmg_shade_classes(image), dmg_shade_classes(reference_image)).point(
            lambda v: 255 if v else 0
        )
    diff_count = sum(1 for value in diff_image.tobytes() if value)

    if diff_count:
        if os.environ.get("TEST_VERBOSE_IMAGES"):
            image.show()
            reference_image.show()
            diff_image.show()
        known_failure = rom in (CGB_KNOWN_FAILURES if cgb else DMG_KNOWN_FAILURES)
        message = f"{rom} differs from the expected image in {diff_count} pixels at {diff_image.getbbox()}"
        if known_failure:
            pytest.xfail(message)
        pytest.fail(message)
