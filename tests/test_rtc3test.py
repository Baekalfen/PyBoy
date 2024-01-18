#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os.path
from pathlib import Path

import PIL
import pytest

from pyboy import PyBoy, WindowEvent

OVERWRITE_PNGS = False


# https://github.com/aaaaaa123456789/rtc3test
@pytest.mark.skip("RTC is too unstable")
@pytest.mark.parametrize("subtest", [0, 1, 2])
def test_rtc3test(subtest, rtc3test_file):
    pyboy = PyBoy(rtc3test_file, window_type="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(59, True)
    pyboy.tick(25, True)

    for n in range(subtest):
        pyboy.button("down")
        pyboy.tick(2, True)

    pyboy.button("a")
    pyboy.tick(2, True)

    while True:
        # Continue until it says "(A) Return"
        if pyboy.tilemap_background[6:14, 17] == [193, 63, 27, 40, 55, 56, 53, 49]:
            break
        pyboy.tick(1, True)

    png_path = Path(f"tests/test_results/{rtc3test_file}_{subtest}.png")
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
        assert not diff.getbbox(), f"Images are different! {rtc3test_file}_{subtest}"

    pyboy.stop(save=False)
