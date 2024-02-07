#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import shutil
from pathlib import Path
from unittest import mock

import pytest

from . import PyBoy


@pytest.fixture(scope="session")
def default_rom():
    return str(Path("pyboy/default_rom.gb"))


@pytest.fixture(autouse=True)
def doctest_fixtures(doctest_namespace, default_rom):
    # We mock get_sprite_by_tile_identifier as default_rom doesn't use sprites
    with mock.patch("pyboy.PyBoy.get_sprite_by_tile_identifier", return_value=[[0, 2, 4], []]):
        pyboy = PyBoy(default_rom, window_type="null", symbols_file="extras/default_rom/default_rom.sym")
        pyboy.set_emulation_speed(0)
        pyboy.tick(10) # Just a few to get the logo up
        doctest_namespace["pyboy"] = pyboy

        try:
            os.remove("file.rom")
        except:
            pass
        shutil.copyfile(default_rom, "file.rom")
        yield None
    os.remove("file.rom")
