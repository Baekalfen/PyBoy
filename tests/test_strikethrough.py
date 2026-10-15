#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
from pathlib import Path

import PIL
from PIL import ImageChops

from pyboy import PyBoy


# https://github.com/Ashiepaws/strikethrough.gb
def test_strikethrough(strikethrough_file, references_dir):
    pyboy = PyBoy(strikethrough_file, window="null", cgb=False)
    pyboy.set_emulation_speed(0)
    pyboy.tick(120, True)

    image = pyboy.screen.image.convert("RGB")
    pyboy.stop(save=False)

    png_path = Path(f"{references_dir}strikethrough/strikethrough.png")
    assert png_path.exists(), "Reference image doesn't exist"
    old_image = PIL.Image.open(png_path).convert("RGB")
    diff = ImageChops.difference(image, old_image)
    if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
        image.show()
        old_image.show()
        diff.show()
    assert not diff.getbbox(), "OAM DMA mid-scanline interference differs from hardware"
