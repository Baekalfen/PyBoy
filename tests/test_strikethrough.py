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


# https://github.com/Ashiepaws/strikethrough.gb
@pytest.mark.xfail(reason="OAM DMA mid-scanline corrupts a different sprite than on hardware")
def test_strikethrough(strikethrough_file):
    pyboy = PyBoy(strikethrough_file, window="null", cgb=False)
    pyboy.set_emulation_speed(0)
    pyboy.tick(120, True)

    image = pyboy.screen.image.convert("RGB")
    pyboy.stop(save=False)

    png_path = Path("tests/references/strikethrough/strikethrough.png")
    assert png_path.exists(), "Reference image doesn't exist"
    old_image = PIL.Image.open(png_path).convert("RGB")
    diff = ImageChops.difference(image, old_image)
    if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
        image.show()
        old_image.show()
        diff.show()
    assert not diff.getbbox(), f"Images are different! {strikethrough_file}"
