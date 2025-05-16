#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import base64
import hashlib
import os
import sys
from unittest import mock

import pytest

from pyboy import PyBoy
from pyboy import __main__ as main
from pyboy.api.tile import Tile
from pyboy.utils import WindowEvent, cython_compiled
from pytest_lazy_fixtures import lf

try:
    import sdl2
except ImportError:
    sdl2 = None


def test_log_level_none(default_rom, capsys):
    PyBoy(default_rom, window="null")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_log_level_default(default_rom, capsys):
    PyBoy(default_rom, window="dummy")
    captured = capsys.readouterr()
    assert "pyboy.plugins.window_null      ERROR" in captured.out


def test_log_level_error(default_rom, capsys):
    PyBoy(default_rom, window="dummy", log_level="ERROR")
    captured = capsys.readouterr()
    assert "pyboy.plugins.window_null      ERROR" in captured.out


def test_log_level_critical(default_rom, capsys):
    PyBoy(default_rom, window="dummy", log_level="CRITICAL")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_tick_zero(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    # Not permitted, but shouldn't crash the emulator either
    pyboy.tick(0)


def test_memoryviewslice_type(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.tick()

    assert pyboy.screen.raw_buffer.__class__.__name__ in ("memoryview", "_memoryviewslice")
    assert pyboy.sound.raw_buffer.__class__.__name__ in ("memoryview", "_memoryviewslice")


def test_register_file(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    pyboy.set_emulation_speed(0)

    pyboy.register_file.A = 0x1AB
    assert pyboy.register_file.A == 0xAB
    pyboy.register_file.F = 0xFF
    assert pyboy.register_file.F == 0xF0  # Lower 4 bits always zero on F
    pyboy.register_file.SP = 0x1234
    assert pyboy.register_file.SP == 0x1234

    def change_sp(p):
        assert p.register_file.SP == 0xFFFE, "Expected 0xFFFE from boot ROM"
        p.register_file.SP = 0xFF00  # We should see this at the end too

    registers = [0] * 9

    def dump_registers(p):
        registers[0] = p.register_file.A
        registers[1] = p.register_file.F
        registers[2] = p.register_file.B
        registers[3] = p.register_file.C
        registers[4] = p.register_file.D
        registers[5] = p.register_file.E
        registers[6] = p.register_file.HL
        registers[7] = p.register_file.SP
        registers[8] = p.register_file.PC

    pyboy.hook_register(-1, 0x3, change_sp, pyboy)
    pyboy.hook_register(0, 0x100, dump_registers, pyboy)
    for _ in range(120):
        pyboy.tick()

    assert registers == [0x1, 208, 0, 0, 0, 143, 135, 0xFF00, 0x100]


def test_record_replay(boot_rom, default_rom, capsys):
    pyboy = PyBoy(default_rom, window="null", bootrom=boot_rom, record_input=True)
    pyboy.set_emulation_speed(0)
    pyboy.tick(1, True)
    pyboy.button_press("down")
    pyboy.tick(1, True)
    pyboy.button_press("up")
    pyboy.tick(2, True)
    pyboy.button_press("down")
    pyboy.tick(1, True)
    pyboy.button_press("up")
    pyboy.tick(1, True)

    events = pyboy._plugin_manager.record_replay.recorded_input
    assert len(events) == 4, "We assumed only 4 frames were recorded, as frames without events are skipped."
    frame_no, keys, frame_data = events[0]
    assert frame_no == 1, "We inserted the key on the second frame"
    assert keys[0] == WindowEvent.PRESS_ARROW_DOWN, "Check we have the right keypress"
    assert len(base64.b64decode(frame_data)) == 144 * 160 * 3, "Frame does not contain 160x144 of RGB data"

    pyboy.stop(save=False)

    with open(default_rom + ".replay", "rb") as f:
        m = hashlib.sha256()
        m.update(f.read())
        digest = m.digest()

    os.remove(default_rom + ".replay")

    assert digest == (
        b'r\x80\x19)\x1a\x88\r\xcc\xb9\xab\xa3\xda\xb1&i\xc8"\xc2\xfb\x8a\x01\x9b\xa81@\x92V=5\x92\\5'
    ), "The replay did not result in the expected output"

    # FIXME
    assert "To replay input consistently later, it is recommended to load a state at boot" in capsys.readouterr().out


def test_argv_parser(*args, capsys):
    parser = main.parser

    # Check error when ROM doesn't exist
    with pytest.raises(SystemExit):
        parser.parse_args("not_a_rom_file_that_would_exist.rom".split(" "))
    outerr = capsys.readouterr()
    assert outerr.out == ""
    assert "Filepath 'not_a_rom_file_that_would_exist.rom' couldn't be found, or isn't a file!" in outerr.err

    file_that_exists = "setup.py"
    # Check defaults
    empty = parser.parse_args(file_that_exists.split(" ")).__dict__
    for k, v in {
        "ROM": file_that_exists,
        "autopause": False,
        "bootrom": None,
        "debug": False,
        "loadstate": None,
        "no_input": False,
        "log_level": "WARNING",
        "record_input": False,
        "rewind": False,
        "scale": 3,
        "window": "SDL2",
    }.items():
        assert empty[k] == v

    # Check the assumed behavior of loadstate with and without argument
    assert parser.parse_args(file_that_exists.split(" ")).loadstate is None
    assert parser.parse_args(f"{file_that_exists} --loadstate".split(" ")).loadstate == main.INTERNAL_LOADSTATE
    assert (
        parser.parse_args(f"{file_that_exists} --loadstate {file_that_exists}".split(" ")).loadstate == file_that_exists
    )

    # Check flags become True
    flags = parser.parse_args(
        f"{file_that_exists} --debug --autopause --rewind --no-input --log-level INFO".split(" ")
    ).__dict__
    for k, v in {"autopause": True, "debug": True, "no_input": True, "log_level": "INFO", "rewind": True}.items():
        assert flags[k] == v


def test_argv_help_message(capsys):
    parser = main.parser

    # Simulate calling the script with --help
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])

    # Capture the output
    captured = capsys.readouterr()

    assert captured.out.startswith("usage:")
    # Just check a few options
    assert "--sound" in captured.out
    assert "--gameshark" in captured.out
    assert "--log-level" in captured.out
    assert "Now sets sound volume to 100%." in captured.out


def test_pause_toggle(default_rom):
    pyboy = PyBoy(default_rom, window="null")

    pyboy.send_input(WindowEvent.PAUSE_TOGGLE)
    pyboy.tick()
    assert pyboy.paused

    # Just verify pause sticks
    for _ in range(10):
        pyboy.tick()
        assert pyboy.paused

    pyboy.send_input(WindowEvent.PAUSE_TOGGLE)
    pyboy.tick()
    assert not pyboy.paused

    # Just verify unpause sticks
    for _ in range(10):
        pyboy.tick()
        assert not pyboy.paused


@pytest.mark.skipif(
    cython_compiled or not sdl2, reason="This test requires access to internal functions not available in Cython"
)
def test_no_input_enabled(default_rom):
    pyboy = PyBoy(default_rom, window="SDL2", no_input=True, sound_volume=0)
    pyboy.set_emulation_speed(0)
    with mock.patch("pyboy.plugins.window_sdl2.sdl2_event_pump", return_value=[WindowEvent(WindowEvent.PAUSE)]):
        pyboy.tick()
        assert not pyboy.paused

    pyboy.send_input(WindowEvent.PAUSE)
    pyboy.tick()
    assert pyboy.paused

    pyboy.send_input(WindowEvent.UNPAUSE)
    pyboy.tick()
    assert not pyboy.paused


@pytest.mark.skipif(
    cython_compiled or not sdl2, reason="This test requires access to internal functions not available in Cython"
)
def test_no_input_disabled(default_rom):
    pyboy = PyBoy(default_rom, window="SDL2", no_input=False, sound_volume=0)
    pyboy.set_emulation_speed(0)
    with mock.patch("pyboy.plugins.window_sdl2.sdl2_event_pump", return_value=[WindowEvent(WindowEvent.PAUSE)]):
        pyboy.tick()
        assert pyboy.paused

    pyboy.send_input(WindowEvent.PAUSE)
    pyboy.tick()
    assert pyboy.paused

    pyboy.send_input(WindowEvent.UNPAUSE)
    pyboy.tick()
    assert not pyboy.paused


def test_tilemaps(kirby_rom):
    pyboy = PyBoy(kirby_rom, window="null")
    pyboy.set_emulation_speed(0)
    pyboy.tick(120, False, False)

    bck_tilemap = pyboy.tilemap_background
    wdw_tilemap = pyboy.tilemap_window
    bck_tilemap._refresh_lcdc()
    wdw_tilemap._refresh_lcdc()
    assert bck_tilemap.map_offset != wdw_tilemap.map_offset

    assert bck_tilemap[0, 0] == 256
    assert bck_tilemap[30:, 29:] == [[254, 254], [256, 256], [256, 256]]
    # assert bck_tilemap[30::-1, 29::-1] == [[256, 256], [256, 256], [254, 254]] # TODO: Not supported
    assert bck_tilemap[30:32, 30:32] == [[256, 256], [256, 256]]
    assert bck_tilemap[:5, 0] == [256, 256, 256, 256, 170]
    assert bck_tilemap[:20, :10] == [
        [256, 256, 256, 256, 170, 176, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256],
        [256, 256, 256, 171, 173, 177, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256],
        [256, 256, 256, 172, 174, 178, 256, 256, 256, 256, 256, 256, 256, 256, 347, 363, 256, 256, 256, 256],
        [256, 256, 256, 288, 175, 179, 336, 352, 368, 268, 284, 300, 316, 332, 348, 364, 380, 256, 256, 256],
        [256, 257, 273, 289, 305, 321, 337, 353, 369, 269, 285, 301, 317, 333, 349, 365, 381, 256, 256, 256],
        [256, 258, 274, 290, 306, 322, 338, 354, 370, 270, 286, 302, 318, 334, 350, 366, 382, 256, 256, 256],
        [256, 259, 275, 291, 307, 323, 339, 355, 371, 271, 287, 303, 319, 335, 351, 367, 383, 256, 256, 256],
        [256, 256, 276, 292, 308, 324, 340, 356, 372, 272, 320, 260, 261, 262, 361, 182, 346, 256, 256, 256],
        [256, 256, 277, 293, 309, 325, 341, 357, 373, 128, 181, 362, 378, 299, 315, 331, 256, 256, 256, 256],
        [256, 256, 278, 294, 310, 326, 342, 358, 374, 129, 164, 132, 136, 140, 143, 146, 150, 167, 157, 168],
    ]
    assert isinstance(bck_tilemap.tile(0, 0), Tile)
    assert bck_tilemap.tile_identifier(0, 0) == 256
    bck_tilemap.use_tile_objects(True)
    assert isinstance(bck_tilemap.tile(0, 0), Tile)
    assert bck_tilemap.tile_identifier(0, 0) == 256
    assert isinstance(bck_tilemap[0, 0], Tile)

    assert wdw_tilemap[0, 0] == 256
    assert wdw_tilemap[:5, 0] == [256, 256, 256, 256, 256]
    assert wdw_tilemap[:20, :10] == [
        [256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256],
        [256, 256, 256, 256, 256, 256, 230, 224, 236, 228, 256, 241, 242, 224, 240, 242, 256, 256, 256, 256],
        [256, 256, 256, 256, 256, 256, 241, 238, 243, 237, 227, 256, 242, 228, 241, 242, 256, 256, 256, 256],
        [256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256],
        [256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256],
        [256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256],
        [256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256],
        [256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256],
        [256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256],
        [256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256],
    ]
    assert isinstance(wdw_tilemap.tile(0, 0), Tile)
    assert wdw_tilemap.tile_identifier(0, 0) == 256
    wdw_tilemap.use_tile_objects(True)
    assert isinstance(wdw_tilemap.tile(0, 0), Tile)
    assert wdw_tilemap.tile_identifier(0, 0) == 256
    assert isinstance(wdw_tilemap[0, 0], Tile)

    pyboy.stop(save=False)


def test_randomize_ram(default_rom):
    pyboy = PyBoy(default_rom, window="null", randomize=False)
    # RAM banks should all be 0 by default
    assert not any(pyboy.memory[0x8000:0xA000]), "VRAM not zeroed"
    assert not any(pyboy.memory[0xC000:0xE000]), "Internal RAM 0 not zeroed"
    assert not any(pyboy.memory[0xFE00:0xFEA0]), "OAM not zeroed"
    assert not any(pyboy.memory[0xFEA0:0xFF00]), "Non-IO internal RAM 0 not zeroed"
    assert not any(pyboy.memory[0xFF4C:0xFF80]), "Non-IO internal RAM 1 not zeroed"
    assert not any(pyboy.memory[0xFF80:0xFFFF]), "Internal RAM 1 not zeroed"
    pyboy.stop(save=False)

    pyboy = PyBoy(default_rom, window="null", randomize=True)
    # RAM banks should have at least one nonzero value now
    assert any(pyboy.memory[0x8000:0xA000]), "VRAM not randomized"
    assert any(pyboy.memory[0xC000:0xE000]), "Internal RAM 0 not randomized"
    assert any(pyboy.memory[0xFE00:0xFEA0]), "OAM not randomized"
    assert any(pyboy.memory[0xFEA0:0xFF00]), "Non-IO internal RAM 0 not randomized"
    assert any(pyboy.memory[0xFF4C:0xFF80]), "Non-IO internal RAM 1 not randomized"
    assert any(pyboy.memory[0xFF80:0xFFFF]), "Internal RAM 1 not randomized"
    pyboy.stop(save=False)


def test_not_cgb(pokemon_crystal_rom, boot_rom):
    pyboy = PyBoy(pokemon_crystal_rom, window="null", cgb=False, bootrom=boot_rom)
    pyboy.set_emulation_speed(0)
    pyboy.tick(60 * 10, True)

    assert pyboy.tilemap_background[1:16, 16] == [
        134,
        160,
        172,
        164,
        383,
        129,
        174,
        184,
        383,
        130,
        174,
        171,
        174,
        177,
        232,
    ]  # Assert that the screen says "Game Boy Color." at the bottom.

    pyboy.stop(save=False)


@pytest.mark.xfail
def test_debug1():
    sys.stderr.write("NO1!\n")


def test_debug2(capsys):
    sys.stderr.write("NO2!\n")
    capsys.readouterr()  # Clear buffers


@pytest.mark.skipif(os.environ.get("TEST_NO_UI"), reason="Skipping test because of UI")
@pytest.mark.parametrize("rom_fixture", [lf("default_rom"), lf("any_rom_cgb")])
def test_debug(rom_fixture):
    pyboy = PyBoy(rom_fixture, window="null", debug=True)
    pyboy.set_emulation_speed(0)
    pyboy.tick(1, True, True)
