#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
import os.path
import platform
from pathlib import Path

import PIL
import pytest

from pyboy import PyBoy


@pytest.mark.parametrize("rom", [
    "LYC.gb",
    "sprite_suite.gb",
])
def test_shonumi(rom, shonumi_dir):
    pyboy = PyBoy(shonumi_dir + rom, window="null", color_palette=(0xFFFFFF, 0x999999, 0x606060, 0x000000))
    pyboy.set_emulation_speed(0)

    # sprite_suite.gb
    # 60 PyBoy Boot
    # 23 Loading
    # 48 Progress to screenshot
    pyboy.tick(60 + 23 + 48, True)

    png_path = Path(f"tests/test_results/GB Tests/{rom}.png")
    png_path.parents[0].mkdir(parents=True, exist_ok=True)
    image = pyboy.screen.image

    # Converting to RGB as ImageChops.difference cannot handle Alpha: https://github.com/python-pillow/Pillow/issues/4849
    old_image = PIL.Image.open(png_path).convert("RGB")
    old_image = old_image.resize(image.size, resample=PIL.Image.Dither.NONE)
    diff = PIL.ImageChops.difference(image.convert("RGB"), old_image)

    if diff.getbbox() and not os.environ.get("TEST_CI"):
        image.show()
        old_image.show()
        diff.show()
    assert not diff.getbbox(), f"Images are different! {rom}"

    pyboy.stop(save=False)
