#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import hashlib
import io
import os
import urllib.request
from pathlib import Path
from zipfile import ZipFile

import pytest
from filelock import FileLock

BOOTROM_FRAMES_UNTIL_LOGO = 6
BOOTROM_FRAMES_UNTIL_END = 60 + BOOTROM_FRAMES_UNTIL_LOGO


def url_open(url):
    # https://stackoverflow.com/questions/62684468/pythons-requests-triggers-cloudflares-security-while-urllib-does-not
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0"}
    request = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(request).read()


def locate_bootrom(target_digest, path="ROMs/"):
    if not os.path.isdir(path):
        print(f"locate_bootrom: No directory found: {path}")
        return None

    files = map(lambda x: path + x, filter(lambda x: x.endswith(".bin"), os.listdir("ROMs")))

    digest_bytes = bytes.fromhex(target_digest.decode("ASCII"))

    for rom in files:
        with open(rom, "rb") as f:
            m = hashlib.sha256()
            m.update(f.read())
            if m.digest() == digest_bytes:
                return rom


def locate_roms(path="ROMs/"):
    if not os.path.isdir(path):
        print(f"locate_roms: No directory found: {path}")
        return {}

    gb_files = map(
        lambda x: path + x,
        filter(lambda x: x.lower().endswith(".gb") or x.lower().endswith(".gbc"), os.listdir("ROMs"))
    )

    entries = {}
    for rom in gb_files:
        with open(rom, "rb") as f:
            m = hashlib.sha256()
            m.update(f.read())
            entries[rom] = m.digest()

    return entries


def locate_sha256(entries, digest):
    digest_bytes = bytes.fromhex(digest.decode("ASCII"))
    return next(filter(lambda kv: kv[1] == digest_bytes, entries.items()), [None])[0]


rom_entries = locate_roms()


@pytest.fixture
def boot_rom():
    return locate_bootrom(b"cf053eccb4ccafff9e67339d4e78e98dce7d1ed59be819d2a1ba2232c6fce1c7")


@pytest.fixture
def boot_rom_cgb():
    return locate_bootrom(b"b4f2e416a35eef52cba161b159c7c8523a92594facb924b3ede0d722867c50c7")


@pytest.fixture
def default_rom():
    return str(Path("pyboy/default_rom.gb"))


@pytest.fixture
def pokemon_blue_rom():
    return locate_sha256(rom_entries, b"2a951313c2640e8c2cb21f25d1db019ae6245d9c7121f754fa61afd7bee6452d")


@pytest.fixture
def pokemon_crystal_rom():
    return locate_sha256(rom_entries, b"d6702e353dcbe2d2c69183046c878ef13a0dae4006e8cdff521cca83dd1582fe")


@pytest.fixture
def tetris_rom():
    return locate_sha256(rom_entries, b"7fde11dd4e594a6905deccd57943d2909ecb37665a030741c42155aeb346323b")


@pytest.fixture
def supermarioland_rom():
    return locate_sha256(rom_entries, b"470d6c45c9bcf7f0397d00c1ae6de727c63dd471049c8eedbefdc540ceea80b4")


@pytest.fixture
def kirby_rom():
    return locate_sha256(rom_entries, b"0f6dba94fae248d419083001c42c02a78be6bd3dff679c895517559e72c98d58")


# default_rom last, as it doesn't have the Nintendo logo
@pytest.fixture
def any_rom(pokemon_blue_rom, tetris_rom, supermarioland_rom, kirby_rom, default_rom):
    return pokemon_blue_rom or tetris_rom or supermarioland_rom or kirby_rom or default_rom


@pytest.fixture
def any_rom_cgb(pokemon_crystal_rom):
    return pokemon_crystal_rom


extra_test_rom_dir = "test_roms/"
os.makedirs(extra_test_rom_dir, exist_ok=True)


@pytest.fixture
def samesuite_dir():
    path = extra_test_rom_dir + "SameSuite"
    with FileLock(path + ".lock") as lock:
        if not os.path.isdir(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.SameSuite.txt"))
            samesuite_data = io.BytesIO(url_open("https://pyboy.dk/mirror/SameSuite.zip"))
            with ZipFile(samesuite_data) as _zip:
                _zip.extractall(path)
    return path + "/"


@pytest.fixture
def mooneye_dir():
    path = extra_test_rom_dir + "mooneye"
    with FileLock(path + ".lock") as lock:
        if not os.path.isdir(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.mooneye.txt"))
            mooneye_data = io.BytesIO(url_open("https://pyboy.dk/mirror/mooneye.zip"))
            with ZipFile(mooneye_data) as _zip:
                _zip.extractall(path)
    return path + "/"


@pytest.fixture
def magen_test_file():
    path = extra_test_rom_dir + "magen_test2.gb"
    with FileLock(path + ".lock") as lock:
        if not os.path.isfile(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.magen_test.txt"))
            magen_test_data = url_open("https://pyboy.dk/mirror/magen_test_bg_oam_priority.gbc")
            with open(path, "wb") as rom_file:
                rom_file.write(magen_test_data)
    return path


@pytest.fixture
def blargg_dir():
    path = Path(extra_test_rom_dir) / Path("blargg")
    with FileLock(path.with_suffix(".lock")) as lock:
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
    return path


@pytest.fixture
def dmg_acid_file():
    path = extra_test_rom_dir + "dmg_acid2.gb"
    with FileLock(path + ".lock") as lock:
        if not os.path.isfile(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.dmg-acid2.txt"))
            dmg_acid_data = url_open("https://pyboy.dk/mirror/dmg-acid2.gb")
            with open(path, "wb") as rom_file:
                rom_file.write(dmg_acid_data)
    return path


@pytest.fixture
def cgb_acid_file():
    path = extra_test_rom_dir + "cgb_acid2.gbc"
    with FileLock(path + ".lock") as lock:
        if not os.path.isfile(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.cgb-acid2.txt"))
            cgb_acid_data = url_open("https://pyboy.dk/mirror/cgb-acid2.gbc")
            with open(path, "wb") as rom_file:
                rom_file.write(cgb_acid_data)
    return path


@pytest.fixture
def shonumi_dir():
    # Has to be in here. Otherwise all test workers will import this file, and cause an error.
    path = extra_test_rom_dir + "GB Tests"
    if not os.path.isdir(path):
        print(url_open("https://pyboy.dk/mirror/SOURCE.GBTests.txt"))
        shonumi_data = io.BytesIO(url_open("https://pyboy.dk/mirror/GB%20Tests.zip"))
        with ZipFile(shonumi_data) as _zip:
            _zip.extractall(path)
    return path + "/"


@pytest.fixture
def rtc3test_file():
    path = extra_test_rom_dir + "rtc3test.gb"
    if not os.path.isfile(path):
        print(url_open("https://pyboy.dk/mirror/LICENSE.rtc3test.txt"))
        rtc3test_data = url_open("https://pyboy.dk/mirror/rtc3test.gb")
        with open(path, "wb") as rom_file:
            rom_file.write(rtc3test_data)
    return path
