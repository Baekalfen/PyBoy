#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import os
import platform
import subprocess
import sys
from pathlib import Path

import pytest
from tests.utils import kirby_rom, supermarioland_rom, tetris_rom

is_pypy = platform.python_implementation() == "PyPy"


@pytest.mark.skipif(os.environ.get("TEST_NO_EXAMPLES"), reason="Test examples disabled by ENV")
@pytest.mark.skipif(
    tetris_rom is None or kirby_rom is None or supermarioland_rom is None,
    reason="ROMs missing for gamewrapper examples"
)
@pytest.mark.parametrize(
    "gamewrapper, rom", [
        ("gamewrapper_tetris.py", tetris_rom),
        ("gamewrapper_mario.py", supermarioland_rom),
        ("gamewrapper_kirby.py", kirby_rom),
    ]
)
def test_record_replay(gamewrapper, rom):
    script_path = os.path.dirname(os.path.realpath(__file__))
    base = Path(f"{script_path}/../examples/")

    assert rom is not None
    return_code = subprocess.Popen([sys.executable, str(base / gamewrapper), str(Path(rom)), "--quiet"]).wait()
    if return_code != 0:
        sys.exit(return_code)
