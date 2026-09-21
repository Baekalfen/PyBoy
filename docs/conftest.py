#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# This collector applies only to Markdown Wiki pages.
import doctest
import hashlib
import os
import re
import sys
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pytest
from filelock import FileLock


DOCS_DIR = Path(__file__).resolve().parent
REPO_ROOT = DOCS_DIR.parent
WIKI_DIR = DOCS_DIR / "wiki"
SECRET_ROM_DIR = REPO_ROOT / "test_roms/secrets"
WIKI_ROM_HASHES = {
    "kirby_rom": "0f6dba94fae248d419083001c42c02a78be6bd3dff679c895517559e72c98d58",
    "pokemon_blue_rom": "2a951313c2640e8c2cb21f25d1db019ae6245d9c7121f754fa61afd7bee6452d",
    "supermariobrosdeluxe_rom": "db81dd4acbd0c7a3b9004f169ee278450c764c842ae777abd28073fbedf4078b",
    "supermarioland_rom": "470d6c45c9bcf7f0397d00c1ae6de727c63dd471049c8eedbefdc540ceea80b4",
    "tetris_rom": "7fde11dd4e594a6905deccd57943d2909ecb37665a030741c42155aeb346323b",
}


def locate_secret_rom(digest):
    if not SECRET_ROM_DIR.is_dir():
        return None
    for path in SECRET_ROM_DIR.iterdir():
        if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == digest:
            return path
    return None


WIKI_ROM_PATHS = {name: locate_secret_rom(digest) for name, digest in WIKI_ROM_HASHES.items()}
sys.path.insert(0, str(REPO_ROOT))

from pyboy import PyBoy  # noqa


np.set_printoptions(threshold=2**32)
np.set_printoptions(linewidth=np.inf)


@pytest.fixture(scope="session")
def default_rom():
    return str(REPO_ROOT / "pyboy/default_rom.gb")


@pytest.fixture(scope="session")
def default_boot_rom():
    return str(REPO_ROOT / "pyboy/core/bootrom_dmg.bin")


@pytest.fixture(scope="session")
def pandorasblocks_rom():
    path = REPO_ROOT / "test_roms" / "PandorasBlocks.gbc"
    with FileLock(path.with_suffix(".lock")):
        if not path.is_file():
            with urlopen("https://pyboy.dk/mirror/LICENSE.PandorasBlocks.txt", timeout=30) as response:
                print(response.read().decode())
            with urlopen("https://pyboy.dk/mirror/PandorasBlocks.gbc", timeout=30) as response:
                rom = response.read()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(rom)
    return str(path)


@pytest.fixture(autouse=True)
def doctest_fixtures(request, doctest_namespace, default_rom, default_boot_rom):
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
    for name, path in WIKI_ROM_PATHS.items():
        doctest_namespace[name] = str(path) if path else None
    if request.node.path.name == "pandoras-blocks.md":
        doctest_namespace["pandorasblocks_rom"] = request.getfixturevalue("pandorasblocks_rom")

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


# Code taken from PyTest is licensed with the following:
# The MIT License (MIT)
#
# Copyright (c) 2004 Holger Krekel and others
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# NOTE: Taken from Pytest
class PytestDoctestRunner(doctest.DebugRunner):
    """Runner to collect failures."""

    def __init__(
        self,
        checker=None,
        verbose=None,
        optionflags: int = 0,
        continue_on_failure: bool = True,
    ) -> None:
        super().__init__(checker=checker, verbose=verbose, optionflags=optionflags)
        self.continue_on_failure = continue_on_failure

    def report_failure(
        self,
        out,
        test: "doctest.DocTest",
        example: "doctest.Example",
        got: str,
    ) -> None:
        failure = doctest.DocTestFailure(test, example, got)
        if self.continue_on_failure:
            out.append(failure)
        else:
            raise failure

    def report_unexpected_exception(
        self,
        out,
        test: "doctest.DocTest",
        example: "doctest.Example",
        exc_info,
    ) -> None:
        failure = doctest.UnexpectedException(test, example, exc_info)
        if self.continue_on_failure:
            out.append(failure)
        else:
            raise failure


# NOTE: Taken from Pytest
class DoctestTextfile(pytest.Module):
    obj = None

    _EXAMPLE_RE_SH = re.compile(
        r"""
    # Source consists of a PS1 line followed by zero or more PS2 lines.
    (?P<source>
        (?:^(?P<indent> [ ]*) $    .*)    # PS1 line
        (?:\n           [ ]*  .*)*)  # PS2 lines
    \n?
    # Want consists of any non-blank lines that do not start with PS1.
    (?P<want> (?:(?![ ]*$)    # Not a blank line
                    .+$\n?       # But any other line
                )*)
    """,
        re.MULTILINE | re.VERBOSE,
    )

    def collect(self):
        encoding = self.config.getini("doctest_encoding")
        text = self.path.read_text(encoding)
        filename = str(self.path)
        name = self.path.name
        globs = {"__name__": "__main__"}

        runner = PytestDoctestRunner(
            verbose=False,
            optionflags=doctest.ELLIPSIS,
            checker=doctest.OutputChecker(),
            continue_on_failure=False,
        )

        parser = doctest.DocTestParser()
        parser._IS_BLANK_OR_COMMENT = lambda x: False
        examples = parser.get_examples(text, name)
        missing_roms = [
            name for name, path in WIKI_ROM_PATHS.items() if name in text and (path is None or not path.is_file())
        ]
        skip_reason = f"requires optional ROM(s): {', '.join(missing_roms)}" if missing_roms else None

        if not examples:
            return

        last = examples[0].lineno
        grouped_examples = [[]]
        for (lineno, example), i in zip(
            [(example.lineno, example) for example in examples],
            range(len(examples)),
        ):
            example.want = example.want.split("```\n")[0]

            if lineno - i == last:
                grouped_examples[-1].append(example)
            else:
                grouped_examples.append([example])
                last = lineno - i
            last += example.source.count("\n") - 1
            last += example.want.count("\n")

        for test in [
            doctest.DocTest(
                examples,
                globs,
                f"{name}_{i}",
                filename,
                0,
                text,
            )
            for i, examples in enumerate(grouped_examples)
        ]:
            if test.examples:
                item = pytest.DoctestItem.from_parent(
                    self,
                    name=test.name,
                    runner=runner,
                    dtest=test,
                )
                if skip_reason:
                    item.add_marker(pytest.mark.skip(reason=skip_reason))
                yield item


# Only Markdown Wiki pages are collected here. RST pages use the other
# documentation test paths.
def pytest_collect_file(file_path, parent):
    if file_path.suffix == ".md" and WIKI_DIR in file_path.parents:
        return DoctestTextfile.from_parent(parent, path=file_path)
    return None
