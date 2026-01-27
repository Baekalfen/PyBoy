#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os.path
from pathlib import Path

import PIL
import pytest

from pyboy import PyBoy

OVERWRITE_PNGS = False


# https://github.com/alloncm/MagenTests
@pytest.mark.parametrize(
    "rom, image",
    [
        ("bg_oam_priority.gbc", True),  # Screenshot
        ("hblank_vram_dma.gbc", False),
        ("key0_lock_after_boot.gbc", False),
        ("mbc_oob_sram_mbc1.gbc", False),
        ("mbc_oob_sram_mbc3.gbc", False),
        ("mbc_oob_sram_mbc5.gbc", False),
        ("oam_internal_priority.gbc", True),  # Screenshot
        ("ppu_disabled_state.gbc", False),
    ],
)
def test_magen_test(rom, image, magen_dir):
    pyboy = PyBoy(magen_dir + "/" + rom, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(59, True)
    pyboy.tick(25, True)

    if image:
        png_path = Path(f"tests/test_results/magen/{os.path.basename(rom)}.png")
        image = pyboy.screen.image
        if OVERWRITE_PNGS:
            png_path.parents[0].mkdir(parents=True, exist_ok=True)
            image.save(png_path)
        else:
            assert png_path.exists(), "Test result doesn't exist"
            # Converting to RGB as ImageChops.difference cannot handle Alpha: https://github.com/python-pillow/Pillow/issues/4849
            old_image = PIL.Image.open(png_path).convert("RGB")
            diff = PIL.ImageChops.difference(image.convert("RGB"), old_image)
            if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
                image.show()
                old_image.show()
                diff.show()
            assert not diff.getbbox(), f"Images are different! {magen_test_file}"
    else:
        # Check the screen is green
        assert pyboy.screen.image.getpixel((0, 0)) == (0, 248, 0, 255)

    pyboy.stop(save=False)
