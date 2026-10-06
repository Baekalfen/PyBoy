#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import platform
from pathlib import Path

import git
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


@pytest.fixture(scope="session")
def git_pokemon_red_experiments():
    if os.path.isfile("README/8.gif") or platform.system() == "Windows":
        return None

    import venv

    path = Path("PokemonRedExperiments")
    with FileLock(path.with_suffix(".lock")):
        if not os.path.isdir(path):
            # NOTE: No affiliation
            repo = git.Repo.clone_from("https://github.com/PWhiddy/PokemonRedExperiments.git", path)
            repo.head.reset("fa01143e4b8d165136199be7155757495d16e56a")
        _venv = venv.EnvBuilder(with_pip=True)
        _venv_path = Path(".venv")
        _venv.create(path / _venv_path)
        # _venv_context = _venv.ensure_directories(path / Path('.venv'))
        assert (
            os.system(f'cd {path} && . {_venv_path / "bin" / "activate"} && pip install -r baselines/requirements.txt')
            == 0
        )
        # Overwrite PyBoy with local version
        assert os.system(f'cd {path} && . {_venv_path / "bin" / "activate"} && pip install ../') == 0
    return str(path)
