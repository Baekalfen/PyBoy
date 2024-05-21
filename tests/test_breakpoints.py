#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
import os
import platform
import shutil
from unittest.mock import Mock

import PIL.ImageChops
import pytest

from pyboy import PyBoy

is_pypy = platform.python_implementation() == "PyPy"


def test_debugprompt(default_rom, monkeypatch):
    pyboy = PyBoy(default_rom, window="null", breakpoints="0:0100,-1:0", debug=False)
    pyboy.set_emulation_speed(0)

    # Break at 0, step once, continue, break at 100, continue
    monkeypatch.setattr("sys.stdin", io.StringIO("n\nc\nc\n"))
    for _ in range(120):
        pyboy.tick()

    if is_pypy:
        assert not pyboy.mb.bootrom_enabled


@pytest.mark.parametrize("commands", ["n\nc\n", "n\nn\nc\n", "c\nc\n", "n\nn\nn\nn\nn\nn\nc\n"])
def test_debugprompt2(default_rom, monkeypatch, commands):
    pyboy = PyBoy(default_rom, window="null", breakpoints="-1:0,-1:3", debug=False)
    pyboy.set_emulation_speed(0)

    monkeypatch.setattr("sys.stdin", io.StringIO(commands))
    for _ in range(120):
        pyboy.tick()

    if is_pypy:
        assert not pyboy.mb.bootrom_enabled


def test_register_hooks(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)

    mock = Mock()
    pyboy.hook_register(0, 0x100, mock.method1, None)
    pyboy.hook_register(0, 0x1000, mock.method2, None)
    for _ in range(120):
        pyboy.tick()

    mock.method1.assert_called()
    mock.method2.assert_not_called()


def test_register_hook_context(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)

    def _inner_callback(context):
        context.append(1)

    _context = []

    bank = -1 # "ROM bank number" for bootrom
    addr = 0xFC # Address of last instruction. Expected to execute once.
    pyboy.hook_register(bank, addr, _inner_callback, _context)
    for _ in range(120):
        pyboy.tick()

    assert len(_context) == 1


def test_register_hook_print(default_rom, capfd):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)

    def _inner_callback(context):
        print(context)

    bank = -1 # "ROM bank number" for bootrom
    addr = 0xFC # Address of last instruction. Expected to execute once.
    pyboy.hook_register(bank, addr, _inner_callback, "Hello!")
    for _ in range(120):
        pyboy.tick()

    out, err = capfd.readouterr()
    assert out == "Hello!\n"


def test_symbols_none(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)

    with pytest.raises(ValueError):
        pyboy._lookup_symbol("Main.waitVBlank")


def test_symbols_auto_locate(default_rom):
    new_path = "extras/default_rom/default_rom.gb"
    shutil.copyfile(default_rom, new_path)
    pyboy = PyBoy(new_path, window="null")
    pyboy.set_emulation_speed(0)

    _bank, _addr = pyboy._lookup_symbol("Main.waitVBlank")
    assert _bank is not None
    assert _addr is not None


def test_symbols_auto_locate_double_symbol(default_rom):
    pyboy = PyBoy(default_rom, window="null", symbols="extras/default_rom/default_rom.sym")
    pyboy.set_emulation_speed(0)

    _bank, _addr = pyboy.symbol_lookup("Tilemap")
    assert _bank is not None
    assert _addr is not None

    _bank2, _addr2 = pyboy.symbol_lookup("Tilemap2")
    assert _bank == _bank2
    assert _addr == _addr2


def test_symbols_bank0_wram(default_rom):
    pyboy = PyBoy(default_rom, window="null", symbols="extras/default_rom/default_rom.sym")
    pyboy.set_emulation_speed(0)

    pyboy.rom_symbols_inverse["test1"] = (0, 0xC000)
    pyboy.rom_symbols_inverse["test2"] = (0, 0xD000)

    _bank, _addr = pyboy.symbol_lookup("test1")
    assert _bank == 0 and _addr == 0xC000

    _bank, _addr = pyboy.symbol_lookup("test2")
    assert _bank == 0 and _addr == 0xD000

    pyboy.memory[pyboy.symbol_lookup("test1")]
    pyboy.memory[pyboy.symbol_lookup("test2")]


def test_symbols_path_locate(default_rom):
    pyboy = PyBoy(default_rom, window="null", symbols="extras/default_rom/default_rom.sym")
    pyboy.set_emulation_speed(0)

    _bank, _addr = pyboy._lookup_symbol("Main.waitVBlank")
    assert _bank is not None
    assert _addr is not None


def test_register_hook_label(default_rom):
    pyboy = PyBoy(default_rom, window="null", symbols="extras/default_rom/default_rom.sym")
    pyboy.set_emulation_speed(0)

    def _inner_callback(context):
        context.append(1)

    _context = []

    bank = None # Use None to look up symbol
    symbol = "Main.move" # Address of last instruction. Expected to execute once.
    pyboy.hook_register(bank, symbol, _inner_callback, _context)
    for _ in range(120):
        pyboy.tick()

    assert len(_context) == 31


def test_register_hook_context2(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)

    def _inner_callback(context):
        context.append(1)

    _context = []

    bank = -1 # "ROM bank number" for bootrom
    addr = 0x06 # Erase routine, expected 8192 times
    pyboy.hook_register(bank, addr, _inner_callback, _context)

    for _ in range(120):
        pyboy.tick()

    assert len(_context) == 0xA000 - 0x8000


def test_register_hooks_double(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)

    mock = Mock()
    with pytest.raises(ValueError):
        pyboy.hook_register(0, 0x100, mock.method1, None)
        pyboy.hook_register(0, 0x100, mock.method1, None)


def test_deregister_hooks(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)

    mock = Mock()

    pyboy.hook_register(0, 0x100, mock.method1, None)
    for _ in range(30):
        pyboy.tick()
    mock.method1.assert_not_called()

    pyboy.hook_deregister(0, 0x100)
    for _ in range(90):
        pyboy.tick()
    mock.method1.assert_not_called()


def test_deregister_hooks2(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)

    mock = Mock()
    # Pop in same order
    pyboy.hook_register(0, 0x100, mock.method1, None)
    pyboy.hook_register(0, 0x101, mock.method1, None)
    pyboy.hook_deregister(0, 0x100)
    pyboy.hook_deregister(0, 0x101)

    # Pop in reverse order
    pyboy.hook_register(0, 0x100, mock.method1, None)
    pyboy.hook_register(0, 0x101, mock.method1, None)
    pyboy.hook_deregister(0, 0x101)
    pyboy.hook_deregister(0, 0x100)


def test_data_hooking_failure(default_rom):
    ticks = 500

    # Run without hooks
    pyboy1 = PyBoy(default_rom, window="null")
    pyboy1.set_emulation_speed(0)
    pyboy1.tick(ticks, True)

    # Run with hooks
    pyboy2 = PyBoy(default_rom, window="null", symbols="extras/default_rom/default_rom.sym")
    pyboy2.set_emulation_speed(0)

    mock = Mock()
    # NOTE: We are not supposed to register hooks for data
    pyboy2.hook_register(None, "Tilemap", mock.method1, None)
    pyboy2.tick(ticks, True)
    mock.method1.assert_not_called() # Shouldn't be called, as it's not a function

    # Compare screens
    image1 = pyboy1.screen.image.convert("RGB")
    image2 = pyboy2.screen.image.convert("RGB")
    diff = PIL.ImageChops.difference(image1, image2)
    if not diff.getbbox() and not os.environ.get("TEST_CI"):
        image1.show()
        image2.show()
        diff.show()

    # NOTE: Expecting a failure!
    assert diff.getbbox(), f"Images are not different!"
