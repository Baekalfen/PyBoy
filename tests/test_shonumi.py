#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
import os.path
import platform
import urllib.request
from pathlib import Path
from zipfile import ZipFile

import PIL
import pytest
from pyboy import PyBoy
from tests.utils import default_rom


@pytest.mark.parametrize("rom", [
    "GB Tests/LYC.gb",
    "GB Tests/sprite_suite.gb",
])
def test_shonumi(rom):
    # Has to be in here. Otherwise all test workers will import this file, and cause an error.
    shonumi_dir = "GB Tests"
    if not os.path.isdir(shonumi_dir):
        print(urllib.request.urlopen("https://pyboy.dk/mirror/SOURCE.GBTests.txt").read())
        shonumi_data = io.BytesIO(urllib.request.urlopen("https://pyboy.dk/mirror/GB%20Tests.zip").read())
        with ZipFile(shonumi_data) as _zip:
            _zip.extractall(shonumi_dir)

    pyboy = PyBoy(rom, window_type="headless", color_palette=(0xFFFFFF, 0x999999, 0x606060, 0x000000))
    pyboy.set_emulation_speed(0)

    # sprite_suite.gb
    # 60 PyBoy Boot
    # 23 Loading
    # 50 Progress to screenshot
    for _ in range(60 + 23 + 50):
        pyboy.tick()

    png_path = Path(f"test_results/{rom}.png")
    png_path.parents[0].mkdir(parents=True, exist_ok=True)
    image = pyboy.botsupport_manager().screen().screen_image()

    old_image = PIL.Image.open(png_path)
    old_image = old_image.resize(image.size, resample=PIL.Image.NEAREST)
    diff = PIL.ImageChops.difference(image, old_image)

    if diff.getbbox() and not os.environ.get("TEST_CI"):
        image.show()
        old_image.show()
        diff.show()
    assert not diff.getbbox(), f"Images are different! {rom}"

    pyboy.stop(save=False)
