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


@pytest.mark.parametrize("cgb", [False, True])
def test_which(cgb, which_file):
    pyboy = PyBoy(which_file, window="null", cgb=cgb)
    pyboy.set_emulation_speed(0)
    pyboy.tick(59, True)
    pyboy.tick(25, True)

    png_path = Path(f"tests/test_results/{'cgb' if cgb else 'dmg'}_{os.path.basename(which_file)}.png")
    image = pyboy.screen.image
    if OVERWRITE_PNGS:
        png_path.parents[0].mkdir(parents=True, exist_ok=True)
        image.save(png_path)
    else:
        # Converting to RGB as ImageChops.difference cannot handle Alpha: https://github.com/python-pillow/Pillow/issues/4849
        old_image = PIL.Image.open(png_path).convert("RGB")
        diff = PIL.ImageChops.difference(image.convert("RGB"), old_image)
        if diff.getbbox() and not os.environ.get("TEST_CI"):
            image.show()
            old_image.show()
            diff.show()
        assert not diff.getbbox(), f"Images are different! {which_file}"

    pyboy.stop(save=False)
