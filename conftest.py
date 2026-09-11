#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
# The shared fixtures and helpers for the conftest.py files in tests/, pyboy/
# and docs/. The subdirectory conftests import what they need from here.

import doctest
import hashlib
import io
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pytest
from filelock import FileLock

np.set_printoptions(threshold=2**32)
np.set_printoptions(linewidth=np.inf)

default_rom_path = "test_roms/secrets/"

extra_test_rom_dir = Path("test_roms/")
os.makedirs(extra_test_rom_dir, exist_ok=True)


DOCUMENTATION_IMAGES = (
    "Kirby1.png",
    "Kirby2.png",
    "PokemonGen1-1.png",
    "PokemonGen1-2.png",
    "PokemonGen1-3.png",
    "PandorasBlocks.png",
    "SuperMarioBrosDeluxe.png",
    "SuperMarioLand1.png",
    "SuperMarioLand2.png",
    "Tetris1.png",
    "Tetris2.png",
)

TEST_ARTIFACTS = (
    "frame.png",
    "state_file.state",
    "tile_1.png",
)


def url_open(url):
    # https://stackoverflow.com/questions/62684468/pythons-requests-triggers-cloudflares-security-while-urllib-does-not
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0"}
    last_error = None
    for _ in range(5):
        try:
            request = urllib.request.Request(url, headers=headers)
            return urllib.request.urlopen(request).read()
        except urllib.error.URLError as ex:
            print("Error in url_open", url, ex)
            last_error = ex
            time.sleep(3)
    raise ConnectionError(f"Failed to download '{url}' after 5 attempts") from last_error


def url_download_dir(url, path):
    # Recursively mirrors a directory served by nginx with autoindex enabled
    # into path. The url must end with a slash. The href attributes in the
    # listing are URL-encoded, so they are requested as-is and decoded for the
    # local file names. Existing files are skipped, so an interrupted download
    # resumes where it left off. The directory is only created after the
    # listing is fetched, so a failed download leaves nothing behind.
    listing = url_open(url).decode("ascii")
    path.mkdir(parents=True, exist_ok=True)
    for href in re.findall(r'href="([^"]+)"', listing):
        if href.startswith(("../", "/", "?")):
            continue
        if href.endswith("/"):
            url_download_dir(url + href, path / urllib.parse.unquote(href))
        else:
            file_path = path / urllib.parse.unquote(href)
            if not os.path.isfile(file_path):
                file_path.write_bytes(url_open(url + href))


def download_file(path, license_url, file_url):
    # Downloads file_url into path, if it does not already exist. The license
    # is printed on the first download only.
    with FileLock(path.with_suffix(".lock")):
        if not os.path.isfile(path):
            print(url_open(license_url))
            data = url_open(file_url)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as rom_file:
                rom_file.write(data)


def download_zip(path, license_url, zip_url):
    # Extracts zip_url into the directory path, if it does not already exist.
    # The license is printed on the first download only.
    with FileLock(path.with_suffix(".lock")):
        if not os.path.isdir(path):
            print(url_open(license_url))
            data = io.BytesIO(url_open(zip_url))
            with ZipFile(data) as _zip:
                _zip.extractall(path)


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


def refresh_rom_entries():
    global rom_entries
    rom_entries = locate_roms()
    rom_entries.update(locate_roms("ROMs/"))


def locate_sha256(digest):
    global rom_entries
    if rom_entries is None:
        rom_entries = locate_roms()
    digest_bytes = bytes.fromhex(digest.decode("ASCII"))
    return next(filter(lambda kv: kv[1] == digest_bytes, rom_entries.items()), [None])[0]


def decrypt_secrets(path):
    # Decrypts the secret ROMs into path, if the PYTEST_SECRETS_KEY environment
    # variable is set. Returns False, if the key is missing and the secrets
    # are not already present.
    with FileLock(path.with_suffix(".lock")):
        if not os.path.isdir(path):
            key = os.environ.get("PYTEST_SECRETS_KEY")
            if not key:
                return False
            from cryptography.fernet import Fernet

            fernet = Fernet(key.encode())

            test_data = url_open("https://pyboy.dk/mirror/test_data.encrypted")
            data = io.BytesIO()
            data.write(fernet.decrypt(test_data))

            with ZipFile(data, "r") as _zip:
                _zip.extractall(path)
    return True


@pytest.fixture(scope="session")
def secrets():
    path = extra_test_rom_dir / Path("secrets")
    if not decrypt_secrets(path):
        pytest.skip("Cannot access secrets")
    return str(path)


@pytest.fixture(scope="session")
def default_rom():
    return str(Path("pyboy/default_rom.gb"))


@pytest.fixture(scope="session")
def default_rom_cgb():
    return str(Path("pyboy/default_rom_cgb.gb"))


@pytest.fixture(scope="session")
def default_boot_rom():
    return str(Path("pyboy/core/bootrom_dmg.bin"))


@pytest.fixture(scope="session")
def supermarioland_rom(secrets):
    return locate_sha256(b"470d6c45c9bcf7f0397d00c1ae6de727c63dd471049c8eedbefdc540ceea80b4")


@pytest.fixture(scope="session")
def pokemon_pinball_rom(secrets):
    return locate_sha256(b"7672001d4710272009df6a41e3cbada65decd56e0eb2f185cb3d59c08d33ea0e")


@pytest.fixture(scope="session")
def pokemon_blue_rom(secrets):
    return locate_sha256(b"2a951313c2640e8c2cb21f25d1db019ae6245d9c7121f754fa61afd7bee6452d")


@pytest.fixture(scope="session")
def boot_rom(secrets):
    return locate_sha256(b"cf053eccb4ccafff9e67339d4e78e98dce7d1ed59be819d2a1ba2232c6fce1c7")


@pytest.fixture(scope="session")
def boot_cgb_rom(secrets):
    return locate_sha256(b"b4f2e416a35eef52cba161b159c7c8523a92594facb924b3ede0d722867c50c7")


@pytest.fixture(scope="session")
def pokemon_red_rom(secrets):
    return locate_sha256(b"5ca7ba01642a3b27b0cc0b5349b52792795b62d3ed977e98a09390659af96b7b")


@pytest.fixture(scope="session")
def pokemon_gold_rom(secrets):
    return locate_sha256(b"fb0016d27b1e5374e1ec9fcad60e6628d8646103b5313ca683417f52b97e7e4e")


@pytest.fixture(scope="session")
def pokemon_crystal_rom(secrets):
    return locate_sha256(b"d6702e353dcbe2d2c69183046c878ef13a0dae4006e8cdff521cca83dd1582fe")


@pytest.fixture(scope="session")
def mbc5_rom(secrets, pokemon_pinball_rom):
    return pokemon_pinball_rom


@pytest.fixture(scope="session")
def tetris_rom(secrets):
    return locate_sha256(b"7fde11dd4e594a6905deccd57943d2909ecb37665a030741c42155aeb346323b")


@pytest.fixture(scope="session")
def supermariobrosdeluxe_rom(secrets):
    return locate_sha256(b"db81dd4acbd0c7a3b9004f169ee278450c764c842ae777abd28073fbedf4078b")


@pytest.fixture(scope="session")
def kirby_rom(secrets):
    return locate_sha256(b"0f6dba94fae248d419083001c42c02a78be6bd3dff679c895517559e72c98d58")


@pytest.fixture(scope="session")
def any_rom(secrets, tetris_rom):
    return tetris_rom


@pytest.fixture(scope="session")
def any_rom_cgb(secrets, pokemon_crystal_rom):
    return pokemon_crystal_rom


# https://github.com/Villadelfia/dmgtris
@pytest.fixture(scope="session")
def pandorasblocks_rom():
    path = extra_test_rom_dir / Path("PandorasBlocks.gbc")
    download_file(
        path, "https://pyboy.dk/mirror/LICENSE.PandorasBlocks.txt", "https://pyboy.dk/mirror/PandorasBlocks.gbc"
    )
    return str(path)


@pytest.fixture(scope="session")
def samesuite_dir():
    path = extra_test_rom_dir / Path("SameSuite")
    download_zip(path, "https://pyboy.dk/mirror/LICENSE.SameSuite.txt", "https://pyboy.dk/mirror/SameSuite.zip")
    return str(path) + "/"


@pytest.fixture(scope="session")
def mooneye_dir():
    path = extra_test_rom_dir / Path("mooneye")
    download_zip(path, "https://pyboy.dk/mirror/LICENSE.mooneye.txt", "https://pyboy.dk/mirror/mooneye.zip")
    return str(path) + "/"


# https://github.com/mattcurrie/mealybug-tearoom-tests
@pytest.fixture(scope="session")
def mealybug_dir():
    path = extra_test_rom_dir / Path("mealybug")
    download_zip(
        path, "https://pyboy.dk/mirror/LICENSE.mealybug.txt", "https://pyboy.dk/mirror/mealybug-tearoom-tests.zip"
    )
    return str(path) + "/"


# https://github.com/alloncm/MagenTests
@pytest.fixture(scope="session")
def magen_dir():
    path = extra_test_rom_dir / Path("MagenTests")
    download_zip(path, "https://pyboy.dk/mirror/LICENSE.MagenTests.txt", "https://pyboy.dk/mirror/MagenTests2.zip")
    return str(path) + "/"


@pytest.fixture(scope="session")
def blargg_dir():
    path = Path(extra_test_rom_dir) / Path("blargg")
    with FileLock(path.with_suffix(".lock")):
        if not os.path.isdir(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.blargg.txt"))

            for name in [
                "cgb_sound",
                "cpu_instrs",
                "dmg_sound",
                "halt_bug",
                "instr_timing",
                "interrupt_time",
                "mem_timing-2",
                "mem_timing",
                "oam_bug",
            ]:
                blargg_data = io.BytesIO(url_open(f"https://pyboy.dk/mirror/blargg/{name}.zip"))
                with ZipFile(blargg_data) as _zip:
                    _zip.extractall(path)
    return str(path)


# https://github.com/ZoomTen/mbc30test (WTFPL license)
@pytest.fixture(scope="session")
def mbc30_test_file():
    path = extra_test_rom_dir / Path("MBC3_Test.gbc")
    download_file(path, "https://pyboy.dk/mirror/LICENSE.MBC3_Test.txt", "https://pyboy.dk/mirror/MBC3_Test.gbc")
    return str(path)


@pytest.fixture(scope="session")
def dmg_acid_file():
    path = extra_test_rom_dir / Path("dmg_acid2.gb")
    download_file(path, "https://pyboy.dk/mirror/LICENSE.dmg-acid2.txt", "https://pyboy.dk/mirror/dmg-acid2.gb")
    return str(path)


@pytest.fixture(scope="session")
def cgb_acid_file():
    path = extra_test_rom_dir / Path("cgb_acid2.gbc")
    download_file(path, "https://pyboy.dk/mirror/LICENSE.cgb-acid2.txt", "https://pyboy.dk/mirror/cgb-acid2.gbc")
    return str(path)


@pytest.fixture(scope="session")
def shonumi_dir():
    path = extra_test_rom_dir / Path("GB Tests")
    download_zip(path, "https://pyboy.dk/mirror/SOURCE.GBTests.txt", "https://pyboy.dk/mirror/GB%20Tests.zip")
    return str(path) + "/"


# https://github.com/Powerlated/TurtleTests
@pytest.fixture(scope="session")
def turtletests_dir():
    path = extra_test_rom_dir / Path("TurtleTests")
    download_zip(path, "https://pyboy.dk/mirror/LICENSE.TurtleTests.txt", "https://pyboy.dk/mirror/TurtleTests.zip")
    return str(path) + "/"


@pytest.fixture(scope="session")
def rtc3test_file():
    path = extra_test_rom_dir / Path("rtc3test.gb")
    download_file(path, "https://pyboy.dk/mirror/LICENSE.rtc3test.txt", "https://pyboy.dk/mirror/rtc3test.gb")
    return str(path)


# https://github.com/pinobatch/little-things-gb
# https://forums.nesdev.org/viewtopic.php?f=20&t=18023
@pytest.fixture(scope="session")
def firstwhite_file():
    path = extra_test_rom_dir / Path("firstwhite.gb")
    download_file(path, "https://pyboy.dk/mirror/LICENSE.firstwhite.txt", "https://pyboy.dk/mirror/firstwhite.gb")
    return str(path)


# https://github.com/mattcurrie/which.gb
@pytest.fixture(scope="session")
def which_file():
    path = extra_test_rom_dir / Path("which.gb")
    download_file(path, "https://pyboy.dk/mirror/LICENSE.which.txt", "https://pyboy.dk/mirror/which.gb")
    return str(path)


# https://github.com/nitro2k01/whichboot.gb
@pytest.fixture(scope="session")
def whichboot_file():
    path = extra_test_rom_dir / Path("whichboot.gb")
    download_file(path, "https://pyboy.dk/mirror/LICENSE.whichboot.txt", "https://pyboy.dk/mirror/whichboot.gb")
    return str(path)


# https://github.com/wyattferguson/2048-gb
@pytest.fixture(scope="session")
def gb2048_file():
    path = extra_test_rom_dir / Path("gb2048.gb")
    with FileLock(path.with_suffix(".lock")):
        if not os.path.isfile(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.2048.txt"))
            gb2048_data = url_open("https://pyboy.dk/mirror/2048.gb")
            with open(path, "wb") as rom_file:
                rom_file.write(gb2048_data)
            gb2048_sym = url_open("https://pyboy.dk/mirror/2048.gb.map")
            with open(str(path) + ".map", "wb") as sym_file:
                sym_file.write(gb2048_sym)
    return str(path)


# https://gitlab.com/BonsaiDen/vectroid.gb
@pytest.fixture(scope="session")
def vectroid_file():
    path = extra_test_rom_dir / Path("vectroid.gb")
    download_file(path, "https://pyboy.dk/mirror/LICENSE.vectroid.txt", "https://pyboy.dk/mirror/vectroid.gbc")
    return str(path)


# https://github.com/mattcurrie/cgb-acid-hell
@pytest.fixture(scope="session")
def cgb_acid_hell_file():
    path = extra_test_rom_dir / Path("cgb-acid-hell.gbc")
    download_file(
        path, "https://pyboy.dk/mirror/LICENSE.cgb-acid-hell.txt", "https://pyboy.dk/mirror/cgb-acid-hell.gbc"
    )
    return str(path)


# https://github.com/Ashiepaws/BullyGB
@pytest.fixture(scope="session")
def bully_file():
    path = extra_test_rom_dir / Path("bully.gb")
    download_file(path, "https://pyboy.dk/mirror/LICENSE.BullyGB.txt", "https://pyboy.dk/mirror/bully.gb")
    return str(path)


# https://github.com/Ashiepaws/strikethrough.gb
@pytest.fixture(scope="session")
def strikethrough_file():
    path = extra_test_rom_dir / Path("strikethrough.gb")
    download_file(path, "https://pyboy.dk/mirror/LICENSE.strikethrough.txt", "https://pyboy.dk/mirror/strikethrough.gb")
    return str(path)


# https://github.com/CasualPokePlayer/test-roms
@pytest.fixture(scope="session")
def cpp_dir():
    path = extra_test_rom_dir / Path("cpp")
    download_zip(
        path,
        "https://pyboy.dk/mirror/LICENSE.CasualPokePlayerTestRoms.txt",
        "https://pyboy.dk/mirror/CasualPokePlayerTestRoms.zip",
    )
    return str(path) + "/"


# https://github.com/gbdev/GBEmulatorShootout/tree/main/testroms/daid
@pytest.fixture(scope="session")
def daid_dir():
    path = extra_test_rom_dir / Path("daid")
    download_zip(path, "https://pyboy.dk/mirror/LICENSE.daid-testroms.txt", "https://pyboy.dk/mirror/daid-testroms.zip")
    return str(path) + "/"


# https://github.com/mmuszkow/gbprinter/tree/master
@pytest.fixture(scope="session")
def print_file():
    path = extra_test_rom_dir / Path("print.gb")
    download_file(path, "https://pyboy.dk/mirror/LICENSE.print.txt", "https://pyboy.dk/mirror/print.gb")
    return str(path)


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


def pack_secrets():
    refresh_rom_entries()

    # any_rom and any_rom_cgb are aliases for other fixtures, mbc5_rom
    # returns pokemon_pinball_rom, which is packed under its own fixture,
    # pandorasblocks_rom is downloaded from the mirror and not a secret, and
    # default_boot_rom is a repo file and not a secret either.
    excluded = ("any_rom", "any_rom_cgb", "mbc5_rom", "pandorasblocks_rom", "default_boot_rom")
    roms = {name: fixture for name, fixture in globals().items() if name.endswith("_rom") and name not in excluded}

    data = io.BytesIO()
    with ZipFile(data, "w") as _zip:
        for rom in roms.values():
            if rom == default_rom:
                continue
            _rom = rom.__wrapped__(None)
            _zip.write(_rom, os.path.basename(_rom))

    from cryptography.fernet import Fernet

    key = Fernet.generate_key()
    fernet = Fernet(key)
    with open("test_data.encrypted", "wb") as f:
        f.write(fernet.encrypt(data.getvalue()))

    print(key.decode())


def pytest_sessionfinish(session, exitstatus):
    if exitstatus != 0 or hasattr(session.config, "workerinput"):
        return

    assets = Path(__file__).parent / "docs/wiki/assets"
    for filename in DOCUMENTATION_IMAGES:
        source = Path.cwd() / filename
        if source.is_file():
            source.replace(assets / filename)

    for filename in TEST_ARTIFACTS:
        (Path.cwd() / filename).unlink(missing_ok=True)


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
    # Base collector for doctests in text files (.py and .md). Subclasses can
    # override configure_parser and skip_reason.
    obj = None

    def configure_parser(self, parser):
        pass

    def skip_reason(self, text):
        return None

    def collect(self):
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
        self.configure_parser(parser)
        examples = parser.get_examples(text, name)

        skip_reason = self.skip_reason(text)

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
                item = pytest.DoctestItem.from_parent(self, name=test.name, runner=runner, dtest=test)
                if skip_reason:
                    item.add_marker(pytest.mark.skip(reason=skip_reason))
                yield item
