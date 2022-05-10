#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os.path
import urllib.request
from pathlib import Path

import PIL
from pyboy import PyBoy

OVERWRITE_PNGS = False


# https://github.com/alloncm/MagenTests
def test_magen_test():
    # Has to be in here. Otherwise all test workers will import this file, and cause an error.
    magen_test_file = "magen_test2.gb"
    if not os.path.isfile(magen_test_file):
        print(urllib.request.urlopen("https://pyboy.dk/mirror/LICENSE.magen_test.txt").read())
        magen_test_data = urllib.request.urlopen("https://pyboy.dk/mirror/magen_test_bg_oam_priority.gbc").read()
        with open(magen_test_file, "wb") as rom_file:
            rom_file.write(magen_test_data)

    pyboy = PyBoy(magen_test_file, window_type="headless")
    pyboy.set_emulation_speed(0)
    for _ in range(59):
        pyboy.tick()

    for _ in range(25):
        pyboy.tick()

    png_path = Path(f"test_results/{magen_test_file}.png")
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
        assert not diff.getbbox(), f"Images are different! {magen_test_file}"

    pyboy.stop(save=False)
