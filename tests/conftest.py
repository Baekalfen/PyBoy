#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import hashlib
import io
import os
import platform
import time
import urllib.request
from pathlib import Path
from zipfile import ZipFile

import numpy as np

np.set_printoptions(threshold=2**32)
np.set_printoptions(linewidth=np.inf)

import git
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
def default_rom():
    return str(Path("pyboy/default_rom.gb"))


@pytest.fixture(scope="session")
def pokemon_blue_rom(secrets):
    return locate_sha256(b"2a951313c2640e8c2cb21f25d1db019ae6245d9c7121f754fa61afd7bee6452d")


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
def tetris_rom(secrets):
    return locate_sha256(b"7fde11dd4e594a6905deccd57943d2909ecb37665a030741c42155aeb346323b")


@pytest.fixture(scope="session")
def supermarioland_rom(secrets):
    return locate_sha256(b"470d6c45c9bcf7f0397d00c1ae6de727c63dd471049c8eedbefdc540ceea80b4")


@pytest.fixture(scope="session")
def kirby_rom(secrets):
    return locate_sha256(b"0f6dba94fae248d419083001c42c02a78be6bd3dff679c895517559e72c98d58")


@pytest.fixture(scope="session")
def any_rom(default_rom):
    return default_rom


@pytest.fixture(scope="session")
def any_rom_cgb(secrets, pokemon_crystal_rom):
    return pokemon_crystal_rom


extra_test_rom_dir = Path("test_roms/")
os.makedirs(extra_test_rom_dir, exist_ok=True)


@pytest.fixture(scope="session")
def samesuite_dir():
    path = extra_test_rom_dir / Path("SameSuite")
    with FileLock(path.with_suffix(".lock")) as lock:
        if not os.path.isdir(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.SameSuite.txt"))
            samesuite_data = io.BytesIO(url_open("https://pyboy.dk/mirror/SameSuite.zip"))
            with ZipFile(samesuite_data) as _zip:
                _zip.extractall(path)
    return str(path) + "/"


@pytest.fixture(scope="session")
def mooneye_dir():
    path = extra_test_rom_dir / Path("mooneye")
    with FileLock(path.with_suffix(".lock")) as lock:
        if not os.path.isdir(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.mooneye.txt"))
            mooneye_data = io.BytesIO(url_open("https://pyboy.dk/mirror/mooneye.zip"))
            with ZipFile(mooneye_data) as _zip:
                _zip.extractall(path)
    return str(path) + "/"


@pytest.fixture(scope="session")
def magen_test_file():
    path = extra_test_rom_dir / Path("magen_test2.gb")
    with FileLock(path.with_suffix(".lock")) as lock:
        if not os.path.isfile(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.magen_test.txt"))
            magen_test_data = url_open("https://pyboy.dk/mirror/magen_test_bg_oam_priority.gbc")
            with open(path, "wb") as rom_file:
                rom_file.write(magen_test_data)
    return str(path)


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
    return str(path)


@pytest.fixture(scope="session")
def dmg_acid_file():
    path = extra_test_rom_dir / Path("dmg_acid2.gb")
    with FileLock(path.with_suffix(".lock")) as lock:
        if not os.path.isfile(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.dmg-acid2.txt"))
            dmg_acid_data = url_open("https://pyboy.dk/mirror/dmg-acid2.gb")
            with open(path, "wb") as rom_file:
                rom_file.write(dmg_acid_data)
    return str(path)


@pytest.fixture(scope="session")
def cgb_acid_file():
    path = extra_test_rom_dir / Path("cgb_acid2.gbc")
    with FileLock(path.with_suffix(".lock")) as lock:
        if not os.path.isfile(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.cgb-acid2.txt"))
            cgb_acid_data = url_open("https://pyboy.dk/mirror/cgb-acid2.gbc")
            with open(path, "wb") as rom_file:
                rom_file.write(cgb_acid_data)
    return str(path)


@pytest.fixture(scope="session")
def shonumi_dir():
    path = extra_test_rom_dir / Path("GB Tests")
    with FileLock(path.with_suffix(".lock")) as lock:
        if not os.path.isdir(path):
            print(url_open("https://pyboy.dk/mirror/SOURCE.GBTests.txt"))
            shonumi_data = io.BytesIO(url_open("https://pyboy.dk/mirror/GB%20Tests.zip"))
            with ZipFile(shonumi_data) as _zip:
                _zip.extractall(path)
    return str(path) + "/"


@pytest.fixture(scope="session")
def rtc3test_file():
    path = extra_test_rom_dir / Path("rtc3test.gb")
    with FileLock(path.with_suffix(".lock")) as lock:
        if not os.path.isfile(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.rtc3test.txt"))
            rtc3test_data = url_open("https://pyboy.dk/mirror/rtc3test.gb")
            with open(path, "wb") as rom_file:
                rom_file.write(rtc3test_data)
    return str(path)


# https://github.com/mattcurrie/which.gb
@pytest.fixture(scope="session")
def which_file():
    path = extra_test_rom_dir / Path("which.gb")
    with FileLock(path.with_suffix(".lock")) as lock:
        if not os.path.isfile(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.which.txt"))
            which_data = url_open("https://pyboy.dk/mirror/which.gb")
            with open(path, "wb") as rom_file:
                rom_file.write(which_data)
    return str(path)


# https://github.com/nitro2k01/whichboot.gb
@pytest.fixture(scope="session")
def whichboot_file():
    path = extra_test_rom_dir / Path("whichboot.gb")
    with FileLock(path.with_suffix(".lock")) as lock:
        if not os.path.isfile(path):
            print(url_open("https://pyboy.dk/mirror/LICENSE.whichboot.txt"))
            whichboot_data = url_open("https://pyboy.dk/mirror/whichboot.gb")
            with open(path, "wb") as rom_file:
                rom_file.write(whichboot_data)
    return str(path)


@pytest.fixture(scope="session")
def git_tetris_ai():
    if os.path.isfile("extras/README/7.gif") or platform.system() == "Windows":
        return None

    import venv
    path = Path("tetris")
    with FileLock(path.with_suffix(".lock")) as lock:
        if not os.path.isdir(path):
            # NOTE: No affiliation
            repo = git.Repo.clone_from("https://github.com/uiucanh/tetris.git", path)
            repo.head.reset("a098ba8c328d8e7c406787edf61fcb0130cb4c26")
        _venv = venv.EnvBuilder(with_pip=True)
        _venv_path = Path(".venv")
        _venv.create(path / _venv_path)
        # _venv_context = _venv.ensure_directories(path / Path('.venv'))
        assert os.system(
            f'cd {path} && . {_venv_path / "bin" / "activate"} && pip install numpy torch matplotlib graphviz'
        ) == 0
        # Overwrite PyBoy with local version
        assert os.system(f'cd {path} && . {_venv_path / "bin" / "activate"} && pip install ../') == 0
    return str(path)


@pytest.fixture(scope="session")
def git_pyboy_rl():
    if os.path.isfile("extras/README/6.gif") or platform.system() == "Windows":
        return None

    import venv
    path = Path("PyBoy-RL")
    with FileLock(path.with_suffix(".lock")) as lock:
        if not os.path.isdir(path):
            # NOTE: No affiliation
            repo = git.Repo.clone_from("https://github.com/lixado/PyBoy-RL.git", path)
            repo.head.reset("03034a2d72c19c8cdc96d95b50e446a0ab83b421")
        _venv = venv.EnvBuilder(with_pip=True)
        _venv_path = Path(".venv")
        _venv.create(path / _venv_path)
        # _venv_context = _venv.ensure_directories(path / Path('.venv'))
        assert os.system(f'cd {path} && . {_venv_path / "bin" / "activate"} && pip install -r requirements.txt') == 0
        # Overwrite PyBoy with local version
        assert os.system(f'cd {path} && . {_venv_path / "bin" / "activate"} && pip install ../') == 0
    return str(path)


@pytest.fixture(scope="session")
def git_pokemon_red_experiments():
    if os.path.isfile("README/8.gif") or platform.system() == "Windows":
        return None

    import venv
    path = Path("PokemonRedExperiments")
    with FileLock(path.with_suffix(".lock")) as lock:
        if not os.path.isdir(path):
            # NOTE: No affiliation
            repo = git.Repo.clone_from("https://github.com/PWhiddy/PokemonRedExperiments.git", path)
            repo.head.reset("fa01143e4b8d165136199be7155757495d16e56a")
        _venv = venv.EnvBuilder(with_pip=True)
        _venv_path = Path(".venv")
        _venv.create(path / _venv_path)
        # _venv_context = _venv.ensure_directories(path / Path('.venv'))
        assert os.system(
            f'cd {path} && . {_venv_path / "bin" / "activate"} && pip install -r baselines/requirements.txt'
        ) == 0
        # Overwrite PyBoy with local version
        assert os.system(f'cd {path} && . {_venv_path / "bin" / "activate"} && pip install ../') == 0
    return str(path)


@pytest.fixture(scope="session")
def secrets():
    path = extra_test_rom_dir / Path("secrets")
    with FileLock(path.with_suffix(".lock")) as lock:
        if not os.path.isdir(path):
            if not os.environ.get("PYTEST_SECRETS_KEY"):
                pytest.skip("Cannot access secrets")
            fernet = Fernet(os.environ["PYTEST_SECRETS_KEY"].encode())

            test_data = url_open("https://pyboy.dk/mirror/test_data.encrypted")
            data = io.BytesIO()
            data.write(fernet.decrypt(test_data))

            with ZipFile(data, "r") as _zip:
                _zip.extractall(path)
    return str(path)


def pack_secrets():
    global rom_entries
    rom_entries = locate_roms()
    rom_entries.update(locate_roms("ROMs/"))

    data = io.BytesIO()
    with ZipFile(data, "w") as _zip:
        for rom in [globals()[x] for x in globals().keys() if x.endswith("_rom") and x != "any_rom"]:
            _secrets_fixture = None
            if rom == default_rom:
                continue
            _rom = rom.__pytest_wrapped__.obj(_secrets_fixture)
            _zip.write(_rom, os.path.basename(_rom))

    key = Fernet.generate_key()
    fernet = Fernet(key)
    with open("test_data.encrypted", "wb") as f:
        f.write(fernet.encrypt(data.getvalue()))

    print(key.decode())
