#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os.path
from pathlib import Path

import PIL
import pytest
from pytest_lazy_fixtures import lf

from pyboy import PyBoy

OVERWRITE_PNGS = True


@pytest.mark.parametrize(
    "cgb, bootrom",
    [
        (False, None),
        (True, None),
        (False, lf("boot_rom")),
        (True, lf("boot_cgb_rom")),
    ],
)
def test_which(cgb, bootrom, which_file):
    pyboy = PyBoy(which_file, window="null", cgb=cgb, bootrom=bootrom)
    pyboy.set_emulation_speed(0)
    pyboy.tick(59, True)
    pyboy.tick(25, True)

    if bootrom is not None:
        pyboy.tick(400, True)

    png_path = Path(
        f"tests/test_results/which/{'cgb' if cgb else 'dmg'}_{'builtin' if bootrom is None else 'native'}_{os.path.basename(which_file)}.png"
    )
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
        assert not diff.getbbox(), f"Images are different! {which_file}"

    pyboy.stop(save=False)
