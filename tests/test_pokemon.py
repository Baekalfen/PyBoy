#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import PIL
import PIL.Image
from pyboy import PyBoy
from pathlib import Path
import os

OVERWRITE_PNGS = False


def check_image(image, path):
    png_path = Path(f"tests/test_results/pokemon_blue/{path}.png")
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
        assert not diff.getbbox(), f"Images are different! {path}"


def test_pokemon_basics(pokemon_blue_rom):
    pyboy = PyBoy(pokemon_blue_rom, window="null")
    pyboy.set_emulation_speed(0)

    pyboy.tick(60 * 7, True)
    for _ in range(40):
        pyboy.button("start")
        pyboy.tick(15, True)

    for _ in range(300):
        pyboy.button("a")
        pyboy.tick(15, True)

    # In mom's house
    check_image(pyboy.screen.image, "house")
    pyboy.button("start")
    pyboy.tick(30, True)
    check_image(pyboy.screen.image, "start_menu")
    pyboy.button("start")
    pyboy.tick(30, True)
    check_image(pyboy.screen.image, "house")

    pyboy.stop()
