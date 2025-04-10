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

OVERWRITE_PNGS = False


@pytest.mark.parametrize("cgb", [False, True, None])
@pytest.mark.parametrize(
    "_bootrom, bootrom_name, frames",
    [(lf("boot_cgb_rom"), "cgb", 120), (lf("boot_rom"), "dmg", 270), (None, "builtin", 30)],
)
@pytest.mark.parametrize("rom", [lf("any_rom"), lf("any_rom_cgb")])
def test_all_modes(cgb, _bootrom, bootrom_name, frames, rom, any_rom_cgb):
    pyboy = PyBoy(rom, window="null", bootrom=_bootrom, cgb=cgb)
    pyboy.tick(frames, True)

    rom_name = "cgbrom" if rom == any_rom_cgb else "dmgrom"
    cgb_mode = "cgb" if cgb is True else ("dmg" if cgb is False else "None")
    png_path = Path(f"tests/test_results/all_modes/{rom_name}_{cgb_mode}_{bootrom_name}.png")
    image = pyboy.screen.image
    if OVERWRITE_PNGS:
        png_path.parents[0].mkdir(parents=True, exist_ok=True)
        image.save(png_path)
    else:
        old_image = PIL.Image.open(png_path).convert("RGB")
        diff = PIL.ImageChops.difference(image.convert("RGB"), old_image)
        if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
            image.show()
            old_image.show()
            diff.show()
        assert not diff.getbbox(), f"Images are different! {(cgb, _bootrom, frames, rom)}"

    pyboy.stop(save=False)
