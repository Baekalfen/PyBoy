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


# https://github.com/mattcurrie/cgb-acid-hell
@pytest.mark.xfail(reason="PPU timing differs from hardware")
def test_cgb_acid_hell(cgb_acid_hell_file, references_dir):
    pyboy = PyBoy(cgb_acid_hell_file, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(120, True)

    image = pyboy.screen.image.convert("RGB")
    pyboy.stop(save=False)

    png_path = Path(f"{references_dir}cgb-acid-hell/cgb-acid-hell.png")
    assert png_path.exists(), "Reference image doesn't exist"
    old_image = PIL.Image.open(png_path).convert("RGB")
    diff = ImageChops.difference(image, old_image)
    if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
        image.show()
        old_image.show()
        diff.show()
    assert not diff.getbbox(), f"Images are different! {cgb_acid_hell_file}"
