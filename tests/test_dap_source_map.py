#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""Builds the tiny `extras/default_rom` project with the real `rgbasm`/`rgblink` tools (skipped
if they aren't installed) and checks that `dap_source_map` recovers the exact source line for a
handful of known instructions -- covering explicit inline `SECTION "x", ROM0[$addr]` addresses,
colon-less local labels (`.waitVBlank`), two labels pointing at the same address, and an
unrecognized directive (`INCBIN`) correctly giving up instead of guessing."""

import os
import shutil
import subprocess

import pytest

import pyboy
from pyboy.plugins.dap_disassembler import disassemble_one
from pyboy.plugins.dap_source_map import build_source_map, find_entry_files, parse_map_file, parse_sym_file

DEFAULT_ROM_SRC = os.path.join(os.path.dirname(pyboy.__file__), "..", "extras", "default_rom")

pytestmark = pytest.mark.skipif(
    any(shutil.which(tool) is None for tool in ("rgbasm", "rgblink", "rgbfix")),
    reason="RGBDS tools not installed",
)


@pytest.fixture
def built_rom(tmp_path):
    obj = tmp_path / "default_rom.obj"
    sym = tmp_path / "default_rom.sym"
    map_file = tmp_path / "default_rom.map"
    gb = tmp_path / "default_rom.gb"

    subprocess.run(["rgbasm", "-o", str(obj), "default_rom.asm"], cwd=DEFAULT_ROM_SRC, check=True, capture_output=True)
    subprocess.run(
        ["rgblink", "-m", str(map_file), "-n", str(sym), "-o", str(gb), str(obj)], check=True, capture_output=True
    )
    subprocess.run(["rgbfix", "-p0", "-f", "hg", str(gb)], check=True, capture_output=True)
    return gb, sym, map_file


def test_source_map_default_rom(built_rom):
    gb, sym, map_file = built_rom
    root = os.path.abspath(DEFAULT_ROM_SRC)

    emu = pyboy.PyBoy(str(gb), window="null", symbols=str(sym))
    try:
        entries = find_entry_files(root)
        # `default_rom_cgb.asm` also `INCLUDE`s "default_rom.asm", so the latter is correctly
        # *not* auto-detected as an entry file on its own -- pass it explicitly instead, since
        # this test only assembled the (non-CGB) `default_rom.gb` variant.
        assert entries  # sanity check the auto-detection heuristic runs without error

        sections = parse_map_file(str(map_file))
        mapping = build_source_map(
            root, ["default_rom.asm"], emu.rom_symbols_inverse, sections, emu.memory, disassemble_one
        )
        inline_mapping = build_source_map(
            root, ["default_rom.asm"], emu.rom_symbols_inverse, {}, emu.memory, disassemble_one
        )
    finally:
        emu.stop(save=False)

    def line_at(bank, addr):
        entry = mapping.get((bank, addr))
        assert entry is not None, f"No mapping for {bank}:{addr:#x}"
        path, line = entry
        assert os.path.normpath(path) == os.path.normpath(os.path.join(root, "default_rom.asm"))
        return line

    # `SECTION "Header", ROM0[$100]` -- an explicit inline address (no `.map` entry needed).
    assert line_at(0, 0x100) == 5  # nop
    assert line_at(0, 0x101) == 6  # jp Main
    assert inline_mapping[(0, 0x100)] == (os.path.join(root, "default_rom.asm"), 5)
    assert inline_mapping[(0, 0x101)] == (os.path.join(root, "default_rom.asm"), 6)

    # `SECTION "Main", ROM0[$150]`, reached via the `.map` file (`layout.link`-assigned banks
    # aren't needed here since it's ROM0, but this exercises the same lookup path as ROMX would).
    assert line_at(0, 0x150) == 32  # nop
    assert line_at(0, 0x151) == 33  # di
    assert line_at(0, 0x152) == 34  # jp .setup

    # Colon-less local label (`.waitVBlank`, no trailing `:`) correctly re-anchors the address.
    waitvblank_bank, waitvblank_addr = emu.rom_symbols_inverse["Main.waitVBlank"]
    assert line_at(waitvblank_bank, waitvblank_addr) == 38  # ldh a, [rLY]

    # `INCBIN` can't be sized without understanding the binary file it pulls in -- mapping must
    # give up there rather than guess, so nothing past it in that section is (wrongly) mapped.
    tileset_bank, tileset_addr = emu.rom_symbols_inverse["Tileset"]
    assert mapping.get((tileset_bank, tileset_addr)) is None

    # Two labels can share one address; the first actual data line is still the useful source
    # location, rather than either zero-width label declaration.
    tilemap_bank, tilemap_addr = emu.rom_symbols_inverse["Tilemap"]
    assert emu.rom_symbols_inverse["Tilemap2"] == (tilemap_bank, tilemap_addr)
    assert line_at(tilemap_bank, tilemap_addr) == 18


def test_parse_bootrom_symbols(tmp_path):
    symbol_file = tmp_path / "bootrom.sym"
    symbol_file.write_text("00:0000 main\n00:00fc exit\n", encoding="utf-8")

    assert parse_sym_file(str(symbol_file)) == {"main": (0, 0), "exit": (0, 0xFC)}
    assert parse_sym_file(str(symbol_file), bank_override=-1) == {"main": (-1, 0), "exit": (-1, 0xFC)}
