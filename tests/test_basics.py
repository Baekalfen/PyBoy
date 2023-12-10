#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import base64
import hashlib
import os
import os.path
import platform
import sys
from io import BytesIO
from pathlib import Path

import PIL
import pytest

from pyboy import PyBoy, WindowEvent
from pyboy import __main__ as main
from pyboy.api.tile import Tile

is_pypy = platform.python_implementation() == "PyPy"


def test_record_replay(boot_rom, default_rom):
    pyboy = PyBoy(default_rom, window_type="headless", bootrom_file=boot_rom, record_input=True)
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
        f"{file_that_exists} --debug --autopause --rewind --no-input --log-level INFO".split(" ")
    ).__dict__
    for k, v in {"autopause": True, "debug": True, "no_input": True, "log_level": "INFO", "rewind": True}.items():
        assert flags[k] == v


def test_tilemaps(kirby_rom):
    pyboy = PyBoy(kirby_rom, window_type="dummy")
    pyboy.set_emulation_speed(0)
    pyboy.tick(120, False)

    bck_tilemap = pyboy.tilemap_background
    wdw_tilemap = pyboy.tilemap_window

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


def test_randomize_ram(default_rom):
    pyboy = PyBoy(default_rom, window_type="dummy", randomize=False)
    # RAM banks should all be 0 by default
    assert not any([pyboy.get_memory_value(x) for x in range(0x8000, 0xA000)]), "VRAM not zeroed"
    assert not any([pyboy.get_memory_value(x) for x in range(0xC000, 0xE000)]), "Internal RAM 0 not zeroed"
    assert not any([pyboy.get_memory_value(x) for x in range(0xFE00, 0xFEA0)]), "OAM not zeroed"
    assert not any([pyboy.get_memory_value(x) for x in range(0xFEA0, 0xFF00)]), "Non-IO internal RAM 0 not zeroed"
    assert not any([pyboy.get_memory_value(x) for x in range(0xFF4C, 0xFF80)]), "Non-IO internal RAM 1 not zeroed"
    assert not any([pyboy.get_memory_value(x) for x in range(0xFF80, 0xFFFF)]), "Internal RAM 1 not zeroed"
    pyboy.stop(save=False)

    pyboy = PyBoy(default_rom, window_type="dummy", randomize=True)
    # RAM banks should have at least one nonzero value now
    assert any([pyboy.get_memory_value(x) for x in range(0x8000, 0xA000)]), "VRAM not randomized"
    assert any([pyboy.get_memory_value(x) for x in range(0xC000, 0xE000)]), "Internal RAM 0 not randomized"
    assert any([pyboy.get_memory_value(x) for x in range(0xFE00, 0xFEA0)]), "OAM not randomized"
    assert any([pyboy.get_memory_value(x) for x in range(0xFEA0, 0xFF00)]), "Non-IO internal RAM 0 not randomized"
    assert any([pyboy.get_memory_value(x) for x in range(0xFF4C, 0xFF80)]), "Non-IO internal RAM 1 not randomized"
    assert any([pyboy.get_memory_value(x) for x in range(0xFF80, 0xFFFF)]), "Internal RAM 1 not randomized"
    pyboy.stop(save=False)


def test_not_cgb(pokemon_crystal_rom):
    pyboy = PyBoy(pokemon_crystal_rom, window_type="dummy", cgb=False)
    pyboy.set_emulation_speed(0)
    pyboy.tick(60 * 7, False)

    assert pyboy.tilemap_background[1:16, 16] == [
        134, 160, 172, 164, 383, 129, 174, 184, 383, 130, 174, 171, 174, 177, 232
    ] # Assert that the screen says "Game Boy Color." at the bottom.

    pyboy.stop(save=False)


OVERWRITE_PNGS = False


@pytest.mark.parametrize("cgb", [False, True, None])
@pytest.mark.parametrize(
    "_bootrom, frames", [(pytest.lazy_fixture("boot_cgb_rom"), 120), (pytest.lazy_fixture("boot_rom"), 120), (None, 30)]
)
@pytest.mark.parametrize("rom", [pytest.lazy_fixture("tetris_rom"), pytest.lazy_fixture("any_rom_cgb")])
def test_all_modes(cgb, _bootrom, frames, rom, any_rom_cgb, boot_cgb_rom):
    if cgb == False and _bootrom == boot_cgb_rom:
        pytest.skip("Invalid combination")

    if cgb == None and _bootrom == boot_cgb_rom and rom != any_rom_cgb:
        pytest.skip("Invalid combination")

    pyboy = PyBoy(rom, window_type="headless", bootrom_file=_bootrom, cgb=cgb)
    pyboy.set_emulation_speed(0)
    pyboy.tick(frames, True)

    rom_name = "cgbrom" if rom == any_rom_cgb else "dmgrom"
    png_path = Path(f"tests/test_results/all_modes/{rom_name}_{cgb}_{os.path.basename(str(_bootrom))}.png")
    image = pyboy.screen.screen_image()
    if OVERWRITE_PNGS:
        png_path.parents[0].mkdir(parents=True, exist_ok=True)
        png_buf = BytesIO()
        image.save(png_buf, "png")
        with open(png_path, "wb") as f:
            f.write(b"".join([(x ^ 0b10011101).to_bytes(1, sys.byteorder) for x in png_buf.getvalue()]))
    else:
        png_buf = BytesIO()
        with open(png_path, "rb") as f:
            data = f.read()
            png_buf.write(b"".join([(x ^ 0b10011101).to_bytes(1, sys.byteorder) for x in data]))
        png_buf.seek(0)

        old_image = PIL.Image.open(png_buf)
        diff = PIL.ImageChops.difference(image, old_image)
        if diff.getbbox() and not os.environ.get("TEST_CI"):
            image.show()
            old_image.show()
            diff.show()
        assert not diff.getbbox(), f"Images are different! {(cgb, _bootrom, frames, rom)}"

    pyboy.stop(save=False)
