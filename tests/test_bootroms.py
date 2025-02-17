#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os.path
import sys
from io import BytesIO
from pathlib import Path

import PIL
import pytest
from pytest_lazy_fixtures import lf

from pyboy import PyBoy

OVERWRITE_PNGS = False


@pytest.mark.parametrize("cgb", [False, True, None])
@pytest.mark.parametrize("_bootrom, frames", [(lf("boot_cgb_rom"), 120), (lf("boot_rom"), 270), (None, 30)])
@pytest.mark.parametrize("rom", [lf("any_rom"), lf("any_rom_cgb")])
def test_all_modes(cgb, _bootrom, frames, rom, any_rom_cgb):
    pyboy = PyBoy(rom, window="null", bootrom=_bootrom, cgb=cgb)
    pyboy.tick(frames, True)

    rom_name = "cgbrom" if rom == any_rom_cgb else "dmgrom"
    png_path = Path(f"tests/test_results/all_modes/{rom_name}_{cgb}_{os.path.basename(str(_bootrom))}.png")
    image = pyboy.screen.image
    if OVERWRITE_PNGS:
        png_path.parents[0].mkdir(parents=True, exist_ok=True)
        png_buf = BytesIO()
        image.save(png_buf, "png")
        with open(png_path, "wb") as f:
            f.write(b"".join([(x ^ 0b10011101).to_bytes(1, sys.byteorder) for x in png_buf.getvalue()]))
    else:
        png_buf = BytesIO()
        with open(png_path, "rb") as f:
            data = f.read()
            png_buf.write(b"".join([(x ^ 0b10011101).to_bytes(1, sys.byteorder) for x in data]))
        png_buf.seek(0)

        old_image = PIL.Image.open(png_buf).convert("RGB")
        diff = PIL.ImageChops.difference(image.convert("RGB"), old_image)
        if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
            image.show()
            old_image.show()
            diff.show()
        assert not diff.getbbox(), f"Images are different! {(cgb, _bootrom, frames, rom)}"

    pyboy.stop(save=False)
