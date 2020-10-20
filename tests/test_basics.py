#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import base64
import hashlib
import os

import pytest
from pyboy import PyBoy, WindowEvent
from pyboy import __main__ as main
from pyboy.botsupport.tile import Tile
from tests.utils import boot_rom, default_rom, kirby_rom


@pytest.mark.skipif(not boot_rom, reason="ROM not present")
def test_record_replay():
    pyboy = PyBoy(default_rom, window_type="headless", bootrom_file=boot_rom, record_input=True)
    pyboy.set_emulation_speed(0)
    pyboy.tick()
    pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
    pyboy.tick()
    pyboy.send_input(WindowEvent.PRESS_ARROW_UP)
    pyboy.tick()
    pyboy.tick()
    pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
    pyboy.tick()
    pyboy.send_input(WindowEvent.PRESS_ARROW_UP)
    pyboy.tick()

    events = pyboy.plugin_manager.record_replay.recorded_input
    assert len(events) == 4, "We assumed only 4 frames were recorded, as frames without events are skipped."
    frame_no, keys, frame_data = events[0]
    assert frame_no == 1, "We inserted the key on the second frame"
    assert keys[0] == WindowEvent.PRESS_ARROW_DOWN, "Check we have the right keypress"
    assert sum(base64.b64decode(frame_data)) / 0xFF == 144 * 160 * 3, "Frame does not contain 160x144 of RGB data"

    pyboy.stop(save=False)

    with open(default_rom + ".replay", "rb") as f:
        m = hashlib.sha256()
        m.update(f.read())
        digest = m.digest()

    os.remove(default_rom + ".replay")

    assert digest == b"\xc0\xfe\x0f\xaa\x1b0YY\x1a\x174\x8c\xad\xeaDZ\x1dQ\xa8\xa2\x9fA\xaap\x15(\xc9\xd9#\xd4]{", \
        "The replay did not result in the expected output"


@pytest.mark.skipif(not boot_rom, reason="ROM not present")
def test_profiling():
    pyboy = PyBoy(default_rom, window_type="dummy", bootrom_file=boot_rom, profiling=True)
    pyboy.set_emulation_speed(0)
    pyboy.tick()

    hitrate = pyboy._cpu_hitrate()
    CHECK_SUM = 7524
    assert sum(hitrate) == CHECK_SUM, "The amount of instructions called in the first frame of the boot-ROM has changed"

    assert list(main.profiling_printer(hitrate)) == [
        "17c          BIT 7,H 2507",
        " 32       LD (HL-),A 2507",
        " 20         JR NZ,r8 2507",
        " af            XOR A 1",
        " 31        LD SP,d16 1",
        " 21        LD HL,d16 1",
    ], "The output of the profiling formatter has changed. Either the output is wrong, or the formatter has changed."
    pyboy.stop(save=False)


def test_argv_parser(*args):
    parser = main.parser

    # Check error when ROM doesn't exist
    with pytest.raises(SystemExit):
        parser.parse_args("not_a_rom_file_that_would_exist.rom".split(" "))

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
        "log_level": "INFO",
        "profiling": False,
        "record_input": False,
        "rewind": False,
        "scale": 3,
        "window_type": "SDL2"
    }.items():
        assert empty[k] == v

    # Check the assumed behavior of loadstate with and without argument
    assert parser.parse_args(file_that_exists.split(" ")).loadstate is None
    assert parser.parse_args(f"{file_that_exists} --loadstate".split(" ")).loadstate == main.INTERNAL_LOADSTATE
    assert parser.parse_args(
        f"{file_that_exists} --loadstate {file_that_exists}".split(" ")
    ).loadstate == file_that_exists

    # Check flags become True
    flags = parser.parse_args(
        f"{file_that_exists} --debug --autopause --profiling --rewind --no-input --log-level INFO".split(" ")
    ).__dict__
    for k, v in {
        "autopause": True,
        "debug": True,
        "no_input": True,
        "log_level": "INFO",
        "profiling": True,
        "rewind": True
    }.items():
        assert flags[k] == v


@pytest.mark.skipif(not kirby_rom, reason="ROM not present")
def test_tilemaps():
    pyboy = PyBoy(kirby_rom, window_type="dummy")
    pyboy.set_emulation_speed(0)
    for _ in range(120):
        pyboy.tick()

    bck_tilemap = pyboy.botsupport_manager().tilemap_background()
    wdw_tilemap = pyboy.botsupport_manager().tilemap_window()

    assert bck_tilemap[0, 0] == 256
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
        [256, 256, 278, 294, 310, 326, 342, 358, 374, 129, 164, 132, 136, 140, 143, 146, 150, 167, 157, 168]
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
        [256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256, 256]
    ]
    assert isinstance(wdw_tilemap.tile(0, 0), Tile)
    assert wdw_tilemap.tile_identifier(0, 0) == 256
    wdw_tilemap.use_tile_objects(True)
    assert isinstance(wdw_tilemap.tile(0, 0), Tile)
    assert wdw_tilemap.tile_identifier(0, 0) == 256
    assert isinstance(wdw_tilemap[0, 0], Tile)

    pyboy.stop(save=False)


def test_randomize_ram():
    pyboy = PyBoy(default_rom) # randomize=False, by default
    # RAM banks should all be 0 by default
    assert not any([pyboy.get_memory_value(x) for x in range(0x8000, 0xA000)]), "VRAM not zeroed"
    assert not any([pyboy.get_memory_value(x) for x in range(0xC000, 0xE000)]), "Internal RAM 0 not zeroed"
    assert not any([pyboy.get_memory_value(x) for x in range(0xFE00, 0xFEA0)]), "OAM not zeroed"
    assert not any([pyboy.get_memory_value(x) for x in range(0xFEA0, 0xFF00)]), "Non-IO internal RAM 0 not zeroed"
    assert not any([pyboy.get_memory_value(x) for x in range(0xFF4C, 0xFF80)]), "Non-IO internal RAM 1 not zeroed"
    assert not any([pyboy.get_memory_value(x) for x in range(0xFF80, 0xFFFF)]), "Internal RAM 1 not zeroed"
    pyboy.stop(save=False)

    pyboy = PyBoy(default_rom, randomize=True)
    # RAM banks should have nonzero values now
    assert any([pyboy.get_memory_value(x) for x in range(0x8000, 0xA000)]), "VRAM not randomized"
    assert any([pyboy.get_memory_value(x) for x in range(0xC000, 0xE000)]), "Internal RAM 0 not randomized"
    assert any([pyboy.get_memory_value(x) for x in range(0xFE00, 0xFEA0)]), "OAM not randomized"
    assert any([pyboy.get_memory_value(x) for x in range(0xFEA0, 0xFF00)]), "Non-IO internal RAM 0 not randomized"
    assert any([pyboy.get_memory_value(x) for x in range(0xFF4C, 0xFF80)]), "Non-IO internal RAM 1 not randomized"
    assert any([pyboy.get_memory_value(x) for x in range(0xFF80, 0xFFFF)]), "Internal RAM 1 not randomized"
    pyboy.stop(save=False)
