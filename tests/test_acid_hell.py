#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
from pathlib import Path

import PIL
from PIL import ImageChops

from pyboy import PyBoy


# https://github.com/mattcurrie/cgb-acid-hell
def test_cgb_acid_hell(cgb_acid_hell_file, boot_cgb_rom, references_dir):
    pyboy = PyBoy(cgb_acid_hell_file, window="null", bootrom=boot_cgb_rom)
    pyboy.set_emulation_speed(0)
    pyboy.tick(300, True)

    image = pyboy.screen.image.convert("RGB")
    pyboy.stop(save=False)

    png_path = Path(f"{references_dir}cgb-acid-hell/cgb-acid-hell.png")
    assert png_path.exists(), "Reference image doesn't exist"
    old_image = PIL.Image.open(png_path).convert("RGB")
    # PyBoy converts 5-bit color components as (c << 3), while the reference
    # image uses (c << 3) | (c >> 2) -- a difference of up to 7 per channel.
    # Compare at the 5-bit precision the hardware palette actually has, the
    # same normalization the mealybug CGB references use.
    diff = ImageChops.difference(image, old_image).point(lambda v: 255 if v > 7 else 0).convert("L")
    if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
        image.show()
        old_image.show()
        diff.show()
    assert not diff.getbbox(), "PPU timing differs from hardware"
