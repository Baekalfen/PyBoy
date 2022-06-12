#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import hashlib
import io
import os
import time
import urllib.request
from pathlib import Path
from zipfile import ZipFile

import pytest
from cryptography.fernet import Fernet
from filelock import FileLock

BOOTROM_FRAMES_UNTIL_LOGO = 6
BOOTROM_FRAMES_UNTIL_END = 60 + BOOTROM_FRAMES_UNTIL_LOGO

default_rom_path = "test_roms/secrets/"


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
        )
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
def boot_rom(secrets):
    return locate_sha256(b"cf053eccb4ccafff9e67339d4e78e98dce7d1ed59be819d2a1ba2232c6fce1c7")


@pytest.fixture(scope="session")
def boot_cgb_rom(secrets):
    return locate_sha256(b"b4f2e416a35eef52cba161b159c7c8523a92594facb924b3ede0d722867c50c7")


@pytest.fixture(scope="session")
def default_rom(secrets):
    return str(Path("pyboy/default_rom.gb"))


@pytest.fixture(scope="session")
def pokemon_blue_rom(secrets):
    return locate_sha256(b"2a951313c2640e8c2cb21f25d1db019ae6245d9c7121f754fa61afd7bee6452d")


@pytest.fixture(scope="session")
def pokemon_crystal_rom(secrets):
    return locate_sha256(b"d6702e353dcbe2d2c69183046c878ef13a0dae4006e8cdff521cca83dd1582fe")


@pytest.fixture(scope="session")
def tetris_rom(secrets):
    return locate_sha256(b"7fde11dd4e594a6905deccd57943d2909ecb37665a030741c42155aeb346323b")


@pytest.fixture(scope="session")
def supermarioland_rom(secrets):
    return locate_sha256(b"470d6c45c9bcf7f0397d00c1ae6de727c63dd471049c8eedbefdc540ceea80b4")


@pytest.fixture(scope="session")
def kirby_rom(secrets):
    return locate_sha256(b"0f6dba94fae248d419083001c42c02a78be6bd3dff679c895517559e72c98d58")


# default_rom last, as it doesn't have the Nintendo logo
@pytest.fixture(scope="session")
def any_rom(secrets, pokemon_blue_rom, tetris_rom, supermarioland_rom, kirby_rom, default_rom):
    return pokemon_blue_rom or tetris_rom or supermarioland_rom or kirby_rom or default_rom


@pytest.fixture(scope="session")
def any_rom_cgb(secrets, pokemon_crystal_rom):
    return pokemon_crystal_rom


extra_test_rom_dir = "test_roms/"
os.makedirs(extra_test_rom_dir, exist_ok=True)


@pytest.fixture(scope="session")
def samesuite_dir():
    path = extra_test_rom_dir + "SameSuite"
    with FileLock(path + ".lock") as lock:
        if not os.path.isdir(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.SameSuite.txt"))
            samesuite_data = io.BytesIO(url_open("https://pyboy.dk/mirror/SameSuite.zip"))
            with ZipFile(samesuite_data) as _zip:
                _zip.extractall(path)
    return path + "/"


@pytest.fixture(scope="session")
def mooneye_dir():
    path = extra_test_rom_dir + "mooneye"
    with FileLock(path + ".lock") as lock:
        if not os.path.isdir(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.mooneye.txt"))
            mooneye_data = io.BytesIO(url_open("https://pyboy.dk/mirror/mooneye.zip"))
            with ZipFile(mooneye_data) as _zip:
                _zip.extractall(path)
    return path + "/"


@pytest.fixture(scope="session")
def magen_test_file():
    path = extra_test_rom_dir + "magen_test2.gb"
    with FileLock(path + ".lock") as lock:
        if not os.path.isfile(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.magen_test.txt"))
            magen_test_data = url_open("https://pyboy.dk/mirror/magen_test_bg_oam_priority.gbc")
            with open(path, "wb") as rom_file:
                rom_file.write(magen_test_data)
    return path


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
def dmg_acid_file():
    path = extra_test_rom_dir + "dmg_acid2.gb"
    with FileLock(path + ".lock") as lock:
        if not os.path.isfile(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.dmg-acid2.txt"))
            dmg_acid_data = url_open("https://pyboy.dk/mirror/dmg-acid2.gb")
            with open(path, "wb") as rom_file:
                rom_file.write(dmg_acid_data)
    return path


@pytest.fixture(scope="session")
def cgb_acid_file():
    path = extra_test_rom_dir + "cgb_acid2.gbc"
    with FileLock(path + ".lock") as lock:
        if not os.path.isfile(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.cgb-acid2.txt"))
            cgb_acid_data = url_open("https://pyboy.dk/mirror/cgb-acid2.gbc")
            with open(path, "wb") as rom_file:
                rom_file.write(cgb_acid_data)
    return path


@pytest.fixture(scope="session")
def shonumi_dir():
    # Has to be in here. Otherwise all test workers will import this file, and cause an error.
    path = extra_test_rom_dir + "GB Tests"
    if not os.path.isdir(path):
        print(url_open("https://pyboy.dk/mirror/SOURCE.GBTests.txt"))
        shonumi_data = io.BytesIO(url_open("https://pyboy.dk/mirror/GB%20Tests.zip"))
        with ZipFile(shonumi_data) as _zip:
            _zip.extractall(path)
    return path + "/"


@pytest.fixture(scope="session")
def rtc3test_file():
    path = extra_test_rom_dir + "rtc3test.gb"
    if not os.path.isfile(path):
        print(url_open("https://pyboy.dk/mirror/LICENSE.rtc3test.txt"))
        rtc3test_data = url_open("https://pyboy.dk/mirror/rtc3test.gb")
        with open(path, "wb") as rom_file:
            rom_file.write(rtc3test_data)
    return path


@pytest.fixture(scope="session")
def secrets():
    path = extra_test_rom_dir + "secrets"
    with FileLock(path + ".lock") as lock:
        if not os.path.isfile(path):
            fernet = Fernet(os.environ["PYTEST_SECRETS_KEY"].encode())

            test_data = url_open("https://pyboy.dk/mirror/test_data.encrypted")
            data = io.BytesIO()
            data.write(fernet.decrypt(test_data))

            with ZipFile(data, "r") as _zip:
                _zip.extractall(path)
    return path


def pack_secrets():
    data = io.BytesIO()
    with ZipFile(data, "w") as _zip:
        for rom in [globals()[x] for x in globals().keys() if x.endswith("_rom") and x != "any_rom"]:
            _rom = rom.__pytest_wrapped__.obj()
            _zip.write(_rom, os.path.basename(_rom))

    key = Fernet.generate_key()
    fernet = Fernet(key)
    with open("test_data.encrypted", "wb") as f:
        f.write(fernet.encrypt(data.getvalue()))

    print(key.decode())
