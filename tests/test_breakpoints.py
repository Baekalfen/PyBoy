#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import io
import platform
import shutil
from unittest.mock import Mock

import pytest

from pyboy import PyBoy

is_pypy = platform.python_implementation() == "PyPy"


def test_debugprompt(default_rom, monkeypatch):
    pyboy = PyBoy(default_rom, window_type="null", breakpoints="0:0100,-1:0", debug=False)
    pyboy.set_emulation_speed(0)

    # Break at 0, step once, continue, break at 100, continue
    monkeypatch.setattr("sys.stdin", io.StringIO("n\nc\nc\n"))
    for _ in range(120):
        pyboy.tick()

    if is_pypy:
        assert not pyboy.mb.bootrom_enabled


@pytest.mark.parametrize("commands", ["n\nc\n", "n\nn\nc\n", "c\nc\n", "n\nn\nn\nn\nn\nn\nc\n"])
def test_debugprompt2(default_rom, monkeypatch, commands):
    pyboy = PyBoy(default_rom, window_type="null", breakpoints="-1:0,-1:3", debug=False)
    pyboy.set_emulation_speed(0)

    monkeypatch.setattr("sys.stdin", io.StringIO(commands))
    for _ in range(120):
        pyboy.tick()

    if is_pypy:
        assert not pyboy.mb.bootrom_enabled


def test_register_hooks(default_rom):
    pyboy = PyBoy(default_rom, window_type="null")
    pyboy.set_emulation_speed(0)

    mock = Mock()
    pyboy.hook_register(0, 0x100, mock.method1, None)
    pyboy.hook_register(0, 0x1000, mock.method2, None)
    for _ in range(120):
        pyboy.tick()

    mock.method1.assert_called()
    mock.method2.assert_not_called()


def test_register_hook_context(default_rom):
    pyboy = PyBoy(default_rom, window_type="null")
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
    pyboy = PyBoy(default_rom, window_type="null")
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
    pyboy = PyBoy(default_rom, window_type="null")
    pyboy.set_emulation_speed(0)

    with pytest.raises(ValueError):
        pyboy._lookup_symbol("Main.waitVBlank")


def test_symbols_auto_locate(default_rom):
    new_path = "extras/default_rom/default_rom.gb"
    shutil.copyfile(default_rom, new_path)
    pyboy = PyBoy(new_path, window_type="null")
    pyboy.set_emulation_speed(0)

    _bank, _addr = pyboy._lookup_symbol("Main.waitVBlank")
    assert _bank is not None
    assert _addr is not None


def test_symbols_path_locate(default_rom):
    pyboy = PyBoy(default_rom, window_type="null", symbols_file="extras/default_rom/default_rom.sym")
    pyboy.set_emulation_speed(0)

    _bank, _addr = pyboy._lookup_symbol("Main.waitVBlank")
    assert _bank is not None
    assert _addr is not None


def test_register_hook_label(default_rom):
    pyboy = PyBoy(default_rom, window_type="null", symbols_file="extras/default_rom/default_rom.sym")
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
    pyboy = PyBoy(default_rom, window_type="null")
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
    pyboy = PyBoy(default_rom, window_type="null")
    pyboy.set_emulation_speed(0)

    mock = Mock()
    with pytest.raises(ValueError):
        pyboy.hook_register(0, 0x100, mock.method1, None)
        pyboy.hook_register(0, 0x100, mock.method1, None)


def test_deregister_hooks(default_rom):
    pyboy = PyBoy(default_rom, window_type="null")
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
    pyboy = PyBoy(default_rom, window_type="null")
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
