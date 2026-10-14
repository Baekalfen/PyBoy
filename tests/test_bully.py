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
def test_bully(bully_file, references_dir, boot_cgb_rom):
    pyboy = PyBoy(bully_file, window="null", cgb=True, randomize=True, bootrom=boot_cgb_rom)
    pyboy.set_emulation_speed(0)
    pyboy.tick(500, True)

    text = decode_text(pyboy)
    image = pyboy.screen.image.convert("RGB")
    pyboy.stop(save=False)

    if "All tests OK" not in text:
        if os.environ.get("TEST_VERBOSE_IMAGES"):
            image.show()
        screen = " / ".join(line.strip() for line in text.splitlines() if line.strip())
        pytest.xfail(reason=f"BullyGB: {screen}")

    png_path = Path(f"{references_dir}bully/bully.png")
    assert png_path.exists(), "Reference image doesn't exist"
    old_image = PIL.Image.open(png_path).convert("RGB")
    diff = ImageChops.difference(image, old_image)
    if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
        image.show()
        old_image.show()
        diff.show()
    assert not diff.getbbox(), f"Images are different! {bully_file}"
