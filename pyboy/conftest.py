#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import doctest
import hashlib
import io
import os
import time
import urllib.request
from pathlib import Path
from unittest import mock
from zipfile import ZipFile

import numpy as np
import pytest
from filelock import FileLock

from pyboy.utils import cython_compiled

from . import PyBoy

np.set_printoptions(threshold=2**32)
np.set_printoptions(linewidth=np.inf)

default_rom_path = "test_roms/secrets/"

extra_test_rom_dir = Path("test_roms/")
os.makedirs(extra_test_rom_dir, exist_ok=True)


def url_open(url):
    # https://stackoverflow.com/questions/62684468/pythons-requests-triggers-cloudflares-security-while-urllib-does-not
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0"}
    for _ in range(5):
        try:
            request = urllib.request.Request(url, headers=headers)
            return urllib.request.urlopen(request).read()
        except urllib.error.HTTPError as ex:
            print("HTTPError in url_open", ex)
            time.sleep(3)


def locate_roms(path=default_rom_path):
    if not os.path.isdir(path):
        print(f"locate_roms: No directory found: {path}")
        return {}

    gb_files = map(
        lambda x: path + x,
        filter(
            lambda x: x.lower().endswith(".gb") or x.lower().endswith(".gbc") or x.endswith(".bin"), os.listdir(path)
        ),
    )

    entries = {}
    for rom in gb_files:
        with open(rom, "rb") as f:
            m = hashlib.sha256()
            m.update(f.read())
            entries[rom] = m.digest()

    return entries


rom_entries = None


def locate_sha256(digest):
    global rom_entries
    if rom_entries is None:
        rom_entries = locate_roms()
    digest_bytes = bytes.fromhex(digest.decode("ASCII"))
    return next(filter(lambda kv: kv[1] == digest_bytes, rom_entries.items()), [None])[0]


@pytest.fixture(scope="session")
def secrets():
    path = extra_test_rom_dir / Path("secrets")
    with FileLock(path.with_suffix(".lock")):
        if not os.path.isdir(path):
            if not os.environ.get("PYTEST_SECRETS_KEY"):
                pytest.skip("Cannot access secrets")
            from cryptography.fernet import Fernet

            fernet = Fernet(os.environ["PYTEST_SECRETS_KEY"].encode())

            test_data = url_open("https://pyboy.dk/mirror/test_data.encrypted")
            data = io.BytesIO()
            data.write(fernet.decrypt(test_data))

            with ZipFile(data, "r") as _zip:
                _zip.extractall(path)
    return str(path)


@pytest.fixture(scope="session")
def default_rom():
    return str(Path("pyboy/default_rom.gb"))


@pytest.fixture(scope="session")
def default_rom_cgb():
    return str(Path("pyboy/default_rom_cgb.gb"))


@pytest.fixture(scope="session")
def supermarioland_rom(secrets):
    return locate_sha256(b"470d6c45c9bcf7f0397d00c1ae6de727c63dd471049c8eedbefdc540ceea80b4")


@pytest.fixture(scope="session")
def pokemon_pinball_rom(secrets):
    return locate_sha256(b"7672001d4710272009df6a41e3cbada65decd56e0eb2f185cb3d59c08d33ea0e")


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
def doctest_fixtures(doctest_namespace, default_rom, default_rom_cgb, supermarioland_rom, pokemon_pinball_rom):
    pyboy = PyBoy(default_rom, window="null", symbols="extras/default_rom/default_rom.sym")
    pyboy_cgb = PyBoy(default_rom_cgb, window="null", symbols="extras/default_rom/default_rom_cgb.sym")

    def mock_PyBoy(filename, *args, **kwargs):
        if not os.path.isfile(filename):
            filename = default_rom
        kwargs.pop("window", None)
        return PyBoy(filename, *args, window="null", **kwargs)

    if cython_compiled:
        pytest.skip("Cannot mock components if compiled with Cython")

    # We mock get_sprite_by_tile_identifier as default_rom doesn't use sprites
    # fmt: off
    with mock.patch("pyboy.PyBoy.get_sprite_by_tile_identifier", return_value=[[0, 2, 4], []]), \
        mock.patch("pyboy.PyBoy.game_area_collision", return_value=np.zeros(shape=(10,9), dtype=np.uint32)), \
        mock.patch("pyboy.PyBoy.game_area", return_value=tetris_game_area), \
        mock.patch("pyboy.PyBoy.load_state", return_value=None), \
        mock.patch("pyboy.PyBoy.stop", return_value=None), \
        mock.patch("pyboy.PyBoy.rtc_lock_experimental", return_value=None), \
        mock.patch("PIL.Image.Image.show", return_value=None):
        # fmt: on

        pyboy.set_emulation_speed(0)
        pyboy.tick(10)  # Just a few to get the logo up
        doctest_namespace["pyboy"] = pyboy
        doctest_namespace["pyboy_cgb"] = pyboy_cgb
        doctest_namespace["PyBoy"] = mock_PyBoy
        doctest_namespace["newline"] = "\n"
        doctest_namespace["supermarioland_rom"] = supermarioland_rom
        doctest_namespace["pokemon_pinball_rom"] = pokemon_pinball_rom

        yield None


@pytest.fixture(autouse=True, scope="function")
def check_stderr_empty(request):
    capsys = request.getfixturevalue("capsys")
    yield
    # If tests want to ignore errors on stderr, they should issue capsys.readouterr() after known errors
    captured = capsys.readouterr()
    try:
        assert captured.err == "", "stderr is not empty"
        # assert captured.out == "", "stdout is not empty"
    except AssertionError as e:
        raise e


# Code taken from PyTest is licensed with the following:
# The MIT License (MIT)

# Copyright (c) 2004 Holger Krekel and others

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# NOTE: Taken from Pytest
class PytestDoctestRunner(doctest.DebugRunner):
    """Runner to collect failures.

    Note that the out variable in this case is a list instead of a
    stdout-like object.
    """

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
        # if isinstance(exc_info[1], OutcomeException):
        #     raise exc_info[1]
        # if isinstance(exc_info[1], bdb.BdbQuit):
        #     outcomes.exit("Quitting debugger")
        failure = doctest.UnexpectedException(test, example, exc_info)
        if self.continue_on_failure:
            out.append(failure)
        else:
            raise failure


# NOTE: Taken from Pytest
class DoctestTextfile(pytest.Module):
    obj = None

    def collect(self):
        import doctest

        # Inspired by doctest.testfile; ideally we would use it directly,
        # but it doesn't support passing a custom checker.
        encoding = self.config.getini("doctest_encoding")
        text = self.path.read_text(encoding)
        filename = str(self.path)
        name = self.path.name
        globs = {"__name__": "__main__"}

        optionflags = doctest.ELLIPSIS

        runner = PytestDoctestRunner(
            verbose=False,
            optionflags=optionflags,
            checker=doctest.OutputChecker(),
            continue_on_failure=False,
        )

        parser = doctest.DocTestParser()
        examples = parser.get_examples(text, name)

        if not examples:
            return

        last = examples[0].lineno
        grouped_examples = [[]]
        for (lineno, example), i in zip([(e.lineno, e) for e in examples], range(len(examples))):
            # Fix parsing error when example ends
            example.want = example.want.split("```\n")[0]  # Stop parsing, if the docstring ends

            if lineno - i == last:
                grouped_examples[-1].append(example)
            else:
                grouped_examples.append([example])
                last = lineno - i
            last += example.source.count("\n") - 1  # Handle multi-line definitions
            last += example.want.count("\n")  # Handle multi-line definitions

        # TODO: Better naming
        for test in [
            doctest.DocTest(x, globs, f"{name}_{i}", filename, 0, text) for i, x in enumerate(grouped_examples)
        ]:
            if test.examples:
                yield pytest.DoctestItem.from_parent(self, name=test.name, runner=runner, dtest=test)


# NOTE: Taken from Pytest
def pytest_collect_file(file_path, parent):
    if file_path.suffix == ".py":
        txt = DoctestTextfile.from_parent(parent, path=file_path)
        return txt
    return None
