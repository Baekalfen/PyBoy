#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import hashlib
import os
import urllib.request
from pathlib import Path

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

boot_rom = locate_bootrom(b"cf053eccb4ccafff9e67339d4e78e98dce7d1ed59be819d2a1ba2232c6fce1c7")
boot_rom_cgb = locate_bootrom(b"b4f2e416a35eef52cba161b159c7c8523a92594facb924b3ede0d722867c50c7")
default_rom = str(Path("pyboy/default_rom.gb"))
pokemon_blue_rom = locate_sha256(rom_entries, b"2a951313c2640e8c2cb21f25d1db019ae6245d9c7121f754fa61afd7bee6452d")
pokemon_crystal_rom = locate_sha256(rom_entries, b"d6702e353dcbe2d2c69183046c878ef13a0dae4006e8cdff521cca83dd1582fe")
tetris_rom = locate_sha256(rom_entries, b"7fde11dd4e594a6905deccd57943d2909ecb37665a030741c42155aeb346323b")
supermarioland_rom = locate_sha256(rom_entries, b"470d6c45c9bcf7f0397d00c1ae6de727c63dd471049c8eedbefdc540ceea80b4")
kirby_rom = locate_sha256(rom_entries, b"0f6dba94fae248d419083001c42c02a78be6bd3dff679c895517559e72c98d58")

# default_rom last, as it doesn't have the Nintendo logo
any_rom = pokemon_blue_rom or tetris_rom or supermarioland_rom or kirby_rom or default_rom
