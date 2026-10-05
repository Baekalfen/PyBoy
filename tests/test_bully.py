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


def decode_text(pyboy):
    # BullyGB uses tiles 0x100 + ASCII for its font
    text = ""
    for y in range(18):
        for x in range(20):
            tile = pyboy.tilemap_background[x, y] & 0xFF
            text += chr(tile) if 32 <= tile < 127 else " "
        text += "\n"
    return text


# https://github.com/Ashiepaws/BullyGB
@pytest.mark.xfail(reason="BullyGB reports 'Invalid initial DIV'")
def test_bully(bully_file):
    pyboy = PyBoy(bully_file, window="null", cgb=False)
    pyboy.set_emulation_speed(0)
    pyboy.tick(120, True)

    text = decode_text(pyboy)
    image = pyboy.screen.image.convert("RGB")
    pyboy.stop(save=False)

    assert "Passed" in text, f"BullyGB reported a failure:\n{text}"

    png_path = Path("tests/references/bully/bully.png")
    assert png_path.exists(), "Reference image doesn't exist"
    old_image = PIL.Image.open(png_path).convert("RGB")
    diff = ImageChops.difference(image, old_image)
    if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
        image.show()
        old_image.show()
        diff.show()
    assert not diff.getbbox(), f"Images are different! {bully_file}"
