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


@pytest.mark.parametrize(
    "rom",
    [
        "window_y_trigger.gb",
        "window_y_trigger_wx_offscreen.gb",
    ],
)
def test_turtletests(rom, turtletests_dir):
    pyboy = PyBoy(turtletests_dir + rom, window="null")
    pyboy.tick(60 + 20, True)

    png_path = Path(f"tests/test_results/TurtleTest/{rom}.png")
    image = pyboy.screen.image
    if OVERWRITE_PNGS:
        png_path.parents[0].mkdir(parents=True, exist_ok=True)
        image.save(png_path)
    else:
        # Converting to RGB as ImageChops.difference cannot handle Alpha: https://github.com/python-pillow/Pillow/issues/4849
        old_image = PIL.Image.open(png_path).convert("RGB")
        diff = PIL.ImageChops.difference(image.convert("RGB"), old_image)

        if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
            image.show()
            old_image.show()
            diff.show()
        assert not diff.getbbox(), f"Images are different! {rom}"
