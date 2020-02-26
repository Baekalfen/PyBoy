#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#
import base64
import hashlib
import os

import pytest
from pyboy import PyBoy
from pyboy import __main__ as main
from pyboy import windowevent

from . import utils

tetris_rom = utils.tetris_rom
any_rom = tetris_rom
test_file = 'test.replay'


def test_record_replay():
    pyboy = PyBoy(tetris_rom, window_type="headless", bootrom_file=utils.boot_rom, record_input=test_file)
    pyboy.tick()
    pyboy.send_input(windowevent.PRESS_ARROW_DOWN)
    pyboy.tick()
    pyboy.send_input(windowevent.PRESS_ARROW_UP)
    pyboy.tick()
    pyboy.tick()
    pyboy.send_input(windowevent.PRESS_ARROW_DOWN)
    pyboy.tick()
    pyboy.send_input(windowevent.PRESS_ARROW_UP)
    pyboy.tick()

    events = pyboy.plugin_manager.record_replay.recorded_input
    assert len(events) == 4, "We assumed only 4 frames were recorded, as frames without events are skipped."
    frame_no, keys, frame_data = events[0]
    assert frame_no == 1, "We inserted the key on the second frame"
    assert keys[0] == windowevent.PRESS_ARROW_DOWN, "Check we have the right keypress"
    assert sum(base64.b64decode(frame_data)) / 0xFF == 144 * 160 * 3, "Frame does not contain 160x144 of RGB data"

    pyboy.stop(save=False)

    with open(test_file, 'rb') as f:
        m = hashlib.sha256()
        m.update(f.read())
        digest = m.digest()

    os.remove(test_file)

    assert digest == b'\xd1\xe2\x13B\xf0$\xaa\xaa\xe2\xf2\xf3Iz\x9aj\x98\xc8^\xc4J:\x08\x1d\xf4n}\x80\x08o\x03)\xda', \
        "The replay did not result in the expected output"


def test_profiling():
    pyboy = PyBoy(any_rom, window_type="dummy", bootrom_file=utils.boot_rom, profiling=True)
    pyboy.tick()

    hitrate = pyboy._get_cpu_hitrate()
    CHECK_SUM = 7546
    assert sum(hitrate) == CHECK_SUM, "The amount of instructions called in the first frame of the boot-ROM has changed"

    assert list(main.profiling_printer(hitrate)) == [
        ' 32       LD (HL-),A 2515',
        '17c          BIT 7,H 2514',
        ' 20         JR NZ,r8 2514',
        ' af            XOR A 1',
        ' 31        LD SP,d16 1',
        ' 21        LD HL,d16 1',
    ], "The output of the profiling formatter has changed. Either the output is wrong, or the formatter has changed."
    pyboy.stop(save=False)


def test_argv_parser(*args):
    parser = main.parser

    # Check error when ROM doesn't exist
    with pytest.raises(FileNotFoundError):
        parser.parse_args('not_a_rom_file_that_would_exist.rom'.split(' '))

    file_that_exists = "setup.py"
    # Check defaults
    empty = parser.parse_args(file_that_exists.split(' ')).__dict__
    for k, v in {
            "ROM": file_that_exists, "autopause": False, "bootrom": None, "debug": False, "loadstate": None,
            "no_input": False, "no_logger": False, "profiling": False, "record_input": None, "rewind": False,
            "scale": 3, "window_type": 'SDL2'
            }.items():
        assert empty[k] == v

    # Check the assumed behavior of loadstate with and without argument
    assert parser.parse_args(file_that_exists.split(' ')).loadstate is None
    assert parser.parse_args(f'{file_that_exists} --loadstate'.split(' ')).loadstate == main.INTERNAL_LOADSTATE
    assert parser.parse_args(
        f'{file_that_exists} --loadstate {file_that_exists}'.split(' ')
    ).loadstate == file_that_exists

    # Check flags become True
    flags = parser.parse_args(
        f'{file_that_exists} --debug --autopause --profiling --rewind --no-input --no-logger'.split(' ')
    ).__dict__
    for k, v in {"autopause": True, "debug": True, "no_input": True, "no_logger": True, "profiling": True,
            "rewind": True}.items():
        assert flags[k] == v


def test_all_buttons():
    pyboy = PyBoy(any_rom, window_type="dummy", bootrom_file=utils.boot_rom)
    pyboy.tick()
    pyboy.stop(save=False)
