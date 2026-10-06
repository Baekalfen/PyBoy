#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# This collector applies only to Markdown Wiki pages.
import os
import sys
from pathlib import Path

import pytest

DOCS_DIR = Path(__file__).resolve().parent
REPO_ROOT = DOCS_DIR.parent
WIKI_DIR = DOCS_DIR / "wiki"

# The ROM fixtures are defined in the root conftest.py and are available
# everywhere. These are the names the wiki pages use in doctests.
WIKI_ROMS = (
    "kirby_rom",
    "pandorasblocks_rom",
    "pokemon_blue_rom",
    "supermariobrosdeluxe_rom",
    "supermarioland_rom",
    "tetris_rom",
)

sys.path.insert(0, str(REPO_ROOT))

from conftest import DoctestTextfile  # noqa

from pyboy import PyBoy  # noqa


@pytest.fixture(autouse=True)
def doctest_fixtures(request, doctest_namespace, default_rom, default_boot_rom):
    # The ROM fixtures are only resolved for the names the page actually
    # uses, so pages without ROMs run without the secrets. The secrets
    # fixture skips, if the ROMs cannot be decrypted.
    text = request.node.path.read_text()
    missing = []
    for name in WIKI_ROMS:
        if name in text:
            rom = request.getfixturevalue(name)
            if rom is None:
                missing.append(name)
            else:
                doctest_namespace[name] = rom
    if missing:
        pytest.skip(f"requires optional ROM(s): {', '.join(missing)}")

    pyboy = PyBoy(
        default_rom,
        window="null",
        symbols=str(REPO_ROOT / "extras/default_rom/default_rom.sym"),
    )

    def mock_PyBoy(filename, *args, **kwargs):
        if isinstance(filename, type(...)) or not os.path.isfile(filename):
            filename = default_rom
        if isinstance(kwargs.get("bootrom_file"), type(...)):
            kwargs["bootrom_file"] = default_boot_rom
        if kwargs.get("window") is None or kwargs["window"] == "SDL2":
            kwargs["window"] = "null"
        return PyBoy(filename, *args, **kwargs)

    pyboy.set_emulation_speed(0)
    pyboy.tick(10)
    doctest_namespace["pyboy"] = pyboy
    doctest_namespace["PyBoy"] = mock_PyBoy

    yield None

    recordings = Path.cwd() / "recordings"
    assets = WIKI_DIR / "assets"
    for pattern, target in (
        ("SUPER*.gif", "SUPERMARIOLAND.gif"),
        ("TETRIS*.gif", "TETRIS.gif"),
        ("KIRBY*.gif", "KIRBY.gif"),
    ):
        for recording in recordings.glob(pattern):
            recording.replace(assets / target)
    if recordings.exists() and not any(recordings.iterdir()):
        recordings.rmdir()


# NOTE: Taken from Pytest
class WikiDoctestTextfile(DoctestTextfile):
    def configure_parser(self, parser):
        # Wiki pages use code blocks, where every line would otherwise be
        # parsed as a blank or comment line.
        parser._IS_BLANK_OR_COMMENT = lambda x: False


# Only Markdown Wiki pages are collected here. RST pages use the other
# documentation test paths.
def pytest_collect_file(file_path, parent):
    if file_path.suffix == ".md" and WIKI_DIR in file_path.parents:
        return WikiDoctestTextfile.from_parent(parent, path=file_path)
    return None
