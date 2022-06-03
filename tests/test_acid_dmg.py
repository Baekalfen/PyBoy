#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os.path
from pathlib import Path

import PIL
import pytest
from pyboy import PyBoy

from .utils import url_open

OVERWRITE_PNGS = False


@pytest.mark.parametrize("cgb", [False, True])
def test_dmg_acid(cgb):
    # Has to be in here. Otherwise all test workers will import this file, and cause an error.
    dmg_acid_file = "dmg_acid2.gb"
    if not os.path.isfile(dmg_acid_file):
        print(url_open("https://pyboy.dk/mirror/LICENSE.dmg-acid2.txt"))
        dmg_acid_data = url_open("https://pyboy.dk/mirror/dmg-acid2.gb")
        with open(dmg_acid_file, "wb") as rom_file:
            rom_file.write(dmg_acid_data)

    pyboy = PyBoy(dmg_acid_file, window_type="headless", cgb=cgb)
    pyboy.set_emulation_speed(0)
    for _ in range(59):
        pyboy.tick()

    for _ in range(25):
        pyboy.tick()

    png_path = Path(f"test_results/{'cgb' if cgb else 'dmg'}_{dmg_acid_file}.png")
    image = pyboy.botsupport_manager().screen().screen_image()
    if OVERWRITE_PNGS:
        png_path.parents[0].mkdir(parents=True, exist_ok=True)
        image.save(png_path)
    else:
        old_image = PIL.Image.open(png_path)
        diff = PIL.ImageChops.difference(image, old_image)
        if diff.getbbox() and not os.environ.get("TEST_CI"):
            image.show()
            old_image.show()
            diff.show()
        assert not diff.getbbox(), f"Images are different! {dmg_acid_file}"

    pyboy.stop(save=False)
