#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
from pathlib import Path

import pytest
from filelock import FileLock

from conftest import extra_test_rom_dir, url_download_dir

# Tests use this environment variable as a truthy flag; normalize explicit false values.
if os.environ.get("TEST_VERBOSE_IMAGES", "").strip().lower() in {"0", "false", "no", "off"}:
    os.environ.pop("TEST_VERBOSE_IMAGES", None)


BOOTROM_FRAMES_UNTIL_LOGO = 6
BOOTROM_FRAMES_UNTIL_END = 60 + BOOTROM_FRAMES_UNTIL_LOGO


# Reference images for the image comparison tests
@pytest.fixture(scope="session")
def references_dir():
    path = extra_test_rom_dir / Path("references")
    with FileLock(path.with_suffix(".lock")):
        if not os.path.isdir(path):
            url_download_dir("https://pyboy.dk/mirror/references/", path)
    return str(path) + "/"
