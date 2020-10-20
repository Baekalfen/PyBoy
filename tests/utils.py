#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import hashlib
import os
from pathlib import Path

BOOTROM_FRAMES_UNTIL_LOGO = 6
BOOTROM_FRAMES_UNTIL_END = 60 + BOOTROM_FRAMES_UNTIL_LOGO


def locate_bootrom(path="ROMs/"):
    if not os.path.isdir(path):
        print(f"No directory found: {path}")
        return None

    files = map(lambda x: path + x, filter(lambda x: x.endswith(".bin"), os.listdir("ROMs")))
    target_digest = b"cf053eccb4ccafff9e67339d4e78e98dce7d1ed59be819d2a1ba2232c6fce1c7"
    digest_bytes = bytes.fromhex(target_digest.decode("ASCII"))

    for rom in files:
        with open(rom, "rb") as f:
            m = hashlib.sha256()
            m.update(f.read())
            if m.digest() == digest_bytes:
                return rom


def locate_roms(path="ROMs/"):
    if not os.path.isdir(path):
        print(f"No directory found: {path}")
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

boot_rom = locate_bootrom()
default_rom = str(Path("pyboy/default_rom.gb"))
pokemon_blue_rom = locate_sha256(rom_entries, b"2a951313c2640e8c2cb21f25d1db019ae6245d9c7121f754fa61afd7bee6452d")
tetris_rom = locate_sha256(rom_entries, b"7fde11dd4e594a6905deccd57943d2909ecb37665a030741c42155aeb346323b")
supermarioland_rom = locate_sha256(rom_entries, b"470d6c45c9bcf7f0397d00c1ae6de727c63dd471049c8eedbefdc540ceea80b4")
kirby_rom = locate_sha256(rom_entries, b"0f6dba94fae248d419083001c42c02a78be6bd3dff679c895517559e72c98d58")

# default_rom last, as it doesn't have the Nintendo logo
any_rom = pokemon_blue_rom or tetris_rom or supermarioland_rom or kirby_rom or default_rom
