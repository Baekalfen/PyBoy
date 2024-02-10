#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import doctest
import os
import shutil
import zlib
from pathlib import Path
from unittest import mock

import numpy as np
import pytest

from . import PyBoy

np.set_printoptions(threshold=2**32)
np.set_printoptions(linewidth=np.inf)


@pytest.fixture(scope="session")
def default_rom():
    return str(Path("pyboy/default_rom.gb"))


tetris_game_area = np.array([
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
                            dtype=np.uint32)


@pytest.fixture(autouse=True)
def doctest_fixtures(doctest_namespace, default_rom):
    pyboy = PyBoy(default_rom, window_type="null", symbols_file="extras/default_rom/default_rom.sym")

    # We mock get_sprite_by_tile_identifier as default_rom doesn't use sprites
    with mock.patch("pyboy.PyBoy.get_sprite_by_tile_identifier", return_value=[[0, 2, 4], []]), \
        mock.patch("pyboy.PyBoy.game_area_collision", return_value=np.zeros(shape=(10,9), dtype=np.uint32)), \
        mock.patch("pyboy.PyBoy.game_area", return_value=tetris_game_area), \
        mock.patch("pyboy.PyBoy.load_state", return_value=None), \
        mock.patch("PIL.Image.Image.show", return_value=None), \
        mock.patch("pyboy.PyBoy", return_value=pyboy):

        pyboy.set_emulation_speed(0)
        pyboy.tick(10) # Just a few to get the logo up
        doctest_namespace["pyboy"] = pyboy
        doctest_namespace["newline"] = "\n"

        yield None


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
            if lineno - i == last:
                grouped_examples[-1].append(example)
            else:
                grouped_examples.append([example])
                last = lineno - i
            last += example.source.count("\n") - 1 # Handle multi-line definitions
            last += example.want.count("\n") # Handle multi-line definitions

        # TODO: Better naming
        for test in [
            doctest.DocTest(x, globs, f"{name}_{i}", filename, 0, text) for i, x in enumerate(grouped_examples)
        ]:
            if test.examples:
                yield pytest.DoctestItem.from_parent(self, name=test.name, runner=runner, dtest=test)


# NOTE: Taken from Pytest
def pytest_collect_file(file_path, parent):
    config = parent.config
    if file_path.suffix == ".py":
        txt = DoctestTextfile.from_parent(parent, path=file_path)
        return txt
    return None
