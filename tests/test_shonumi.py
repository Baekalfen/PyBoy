#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os.path
from pathlib import Path

import PIL
import pytest

from pyboy import PyBoy


@pytest.mark.parametrize(
    "rom",
    [
        "LYC.gb",
        "sprite_suite.gb",
    ],
)
def test_shonumi(rom, shonumi_dir, references_dir):
    pyboy = PyBoy(shonumi_dir + rom, window="null", color_palette=(0xFFFFFF, 0x999999, 0x606060, 0x000000))
    pyboy.set_emulation_speed(0)

    # sprite_suite.gb
    # 60 PyBoy Boot
    # 23 Loading
    # 48 Progress to screenshot
    pyboy.tick(60 + 23 + 48, True)

    reference_path = Path(f"{references_dir}GB Tests/{rom.removesuffix('.gb')}.png")
    image = pyboy.screen.image
    assert reference_path.exists(), "Reference image doesn't exist"
    reference_image = PIL.Image.open(reference_path).convert("RGB")
    reference_image = reference_image.resize(image.size, resample=PIL.Image.Dither.NONE)
    diff = PIL.ImageChops.difference(image.convert("RGB"), reference_image)

    if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
        image.show()
        reference_image.show()
        diff.show()
    assert not diff.getbbox(), f"Image differs from reference! {rom}"

    pyboy.stop(save=False)
