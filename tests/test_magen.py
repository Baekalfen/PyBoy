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


# https://github.com/alloncm/MagenTests
@pytest.mark.parametrize(
    "rom, reference",
    [
        ("bg_oam_priority.gbc", "hardware_screenshot.jpg"),
        ("hblank_vram_dma.gbc", "expected_green_screen.png"),
        ("key0_lock_after_boot.gbc", "expected_green_screen.png"),
        ("mbc_oob_sram_mbc1.gbc", "expected_green_screen.png"),
        ("mbc_oob_sram_mbc3.gbc", "expected_green_screen.png"),
        ("mbc_oob_sram_mbc5.gbc", "expected_green_screen.png"),
        ("oam_internal_priority.gbc", "oam_internal_priority.png"),
        ("ppu_disabled_state.gbc", "expected_green_screen.png"),
    ],
)
def test_magen_test(rom, reference, magen_dir, references_dir):
    pyboy = PyBoy(magen_dir + "/" + rom, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(59, True)
    pyboy.tick(25, True)

    image = pyboy.screen.image
    reference_image = PIL.Image.open(Path(f"{references_dir}magen/{reference}")).convert("RGB")
    if reference == "hardware_screenshot.jpg":
        reference_image = reference_image.crop((160, 32, 800, 608))
    elif reference == "oam_internal_priority.png":
        screen = PIL.Image.new("RGB", (320, 288), "white")
        screen.paste(reference_image, (0, -8))
        reference_image = screen
    else:
        reference_image = reference_image.crop((0, 0, 640, 574))
    reference_image = reference_image.resize(image.size, resample=PIL.Image.Dither.NONE)

    def color_classes(source):
        classes = bytearray()
        pixels = source.tobytes()
        for red, green, blue in zip(pixels[0::3], pixels[1::3], pixels[2::3]):
            if green > 100 and green > red * 1.3 and green > blue * 1.3:
                classes.append(1)
            elif red > 100 and red > green * 1.3 and red > blue * 1.3:
                classes.append(2)
            elif blue > 100 and blue > red * 1.3 and blue > green * 1.3:
                classes.append(3)
            else:
                classes.append(0)
        return PIL.Image.frombytes("L", source.size, bytes(classes))

    reference_classes = color_classes(reference_image)
    image_classes = color_classes(image.convert("RGB"))
    diff = ImageChops.difference(image_classes, reference_classes)
    if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
        image.show()
        reference_image.show()
        diff.show()
    assert not diff.getbbox(), f"Image differs from reference! {rom}"

    pyboy.stop(save=False)
