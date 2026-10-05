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

# https://github.com/CasualPokePlayer/test-roms
CPP_CASES = [
    pytest.param("ramg-mbc3-test.gb", 120, marks=pytest.mark.xfail(reason="Not expected to pass yet")),
    pytest.param("latch-rtc-test.gb", 120, marks=pytest.mark.xfail(reason="RTC latch behavior differs from hardware")),
    pytest.param(
        "rtc-invalid-banks-test.gb",
        120,
        marks=pytest.mark.xfail(reason="RTC invalid bank handling differs from hardware"),
    ),
    pytest.param("sgb-ext-test.gb", 600, marks=pytest.mark.xfail(reason="SGB features are not emulated")),
]


@pytest.mark.parametrize("rom, frames", CPP_CASES)
def test_cpp(rom, frames, cpp_dir):
    pyboy = PyBoy(cpp_dir + rom, window="null", cgb=False)
    pyboy.set_emulation_speed(0)
    pyboy.tick(frames, True)

    image = pyboy.screen.image.convert("RGB")
    pyboy.stop(save=False)

    png_path = Path(f"tests/references/cpp/{rom[:-3]}.png")
    assert png_path.exists(), "Reference image doesn't exist"
    old_image = PIL.Image.open(png_path).convert("RGB")
    diff = ImageChops.difference(image, old_image)
    if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
        image.show()
        old_image.show()
        diff.show()
    assert not diff.getbbox(), f"Images are different! {rom}"
