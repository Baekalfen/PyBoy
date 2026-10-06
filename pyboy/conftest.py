#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
from unittest import mock

import numpy as np
import pytest

from conftest import DoctestTextfile

from . import PyBoy


tetris_game_area = np.array(
    [
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 130, 130, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 130, 130, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
        [47, 47, 47, 47, 47, 47, 47, 47, 47, 47],
    ],
    dtype=np.uint32,
)


@pytest.fixture(autouse=True)
def doctest_fixtures(
    doctest_namespace, default_rom, default_rom_cgb, supermarioland_rom, pokemon_pinball_rom, pokemon_blue_rom
):
    class DoctestProxy:
        def __init__(self, obj):
            self._obj = obj

        def __repr__(self):
            return repr(self._obj)

        def __getattr__(self, name):
            value = getattr(self._obj, name)
            if callable(value):

                def call(*args, **kwargs):
                    result = value(*args, **kwargs)
                    if type(result) is int and result == 0:
                        return None
                    return result

                return call
            return value

    class DoctestPyBoy:
        def __init__(self, pyboy):
            self._pyboy = pyboy

        def __getattr__(self, name):
            value = getattr(self._pyboy, name)
            if name in {"game_wrapper", "gameshark", "memory_scanner", "rumble"}:
                return DoctestProxy(value)
            if callable(value):

                def call(*args, **kwargs):
                    result = value(*args, **kwargs)
                    if type(result) is int and result == 0:
                        return None
                    return result

                return call
            return value

        def tick(self, *args, **kwargs):
            return self._pyboy.tick(*args, **kwargs)

        def get_sprite_by_tile_identifier(self, tile_identifiers, on_screen=True):
            return [[0, 2, 4], []]

        def game_area_collision(self):
            return np.zeros(shape=(10, 9), dtype=np.uint32)

        def game_area(self):
            return tetris_game_area

        def load_state(self, *args, **kwargs):
            return None

        def stop(self, *args, **kwargs):
            return None

        def rtc_lock_experimental(self, *args, **kwargs):
            return None

    pyboy = DoctestPyBoy(PyBoy(default_rom, window="null", symbols="extras/default_rom/default_rom.sym"))
    pyboy_cgb = DoctestPyBoy(PyBoy(default_rom_cgb, window="null", symbols="extras/default_rom/default_rom_cgb.sym"))

    def mock_PyBoy(filename, *args, **kwargs):
        if not os.path.isfile(filename):
            filename = default_rom
        kwargs.pop("window", None)
        return DoctestPyBoy(PyBoy(filename, *args, window="null", **kwargs))

    with mock.patch("PIL.Image.Image.show", return_value=None):
        pyboy.set_emulation_speed(0)
        pyboy.tick(10)  # Just a few to get the logo up
        doctest_namespace["pyboy"] = pyboy
        doctest_namespace["pyboy_cgb"] = pyboy_cgb
        doctest_namespace["PyBoy"] = mock_PyBoy
        doctest_namespace["newline"] = "\n"
        doctest_namespace["supermarioland_rom"] = supermarioland_rom
        doctest_namespace["pokemon_pinball_rom"] = pokemon_pinball_rom
        doctest_namespace["pokemon_blue_rom"] = pokemon_blue_rom

        yield None


# NOTE: Taken from Pytest
def pytest_collect_file(file_path, parent):
    if file_path.suffix == ".py":
        txt = DoctestTextfile.from_parent(parent, path=file_path)
        return txt
    return None
