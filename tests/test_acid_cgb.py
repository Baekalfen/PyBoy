#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os.path
from pathlib import Path

import PIL

from pyboy import PyBoy

OVERWRITE_PNGS = False


# https://github.com/mattcurrie/cgb-acid2
def test_cgb_acid(cgb_acid_file):
    pyboy = PyBoy(cgb_acid_file, window_type="headless")
    pyboy.set_emulation_speed(0)
    for _ in range(59):
        pyboy.tick()

    for _ in range(25):
        pyboy.tick()

    png_path = Path(f"tests/test_results/{os.path.basename(cgb_acid_file)}.png")
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
        assert not diff.getbbox(), f"Images are different! {cgb_acid_file}"

    pyboy.stop(save=False)
