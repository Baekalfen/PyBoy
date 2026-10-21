from io import BytesIO

import pytest

from pyboy import PyBoy
from pyboy import __main__ as main
from pyboy.utils import PyBoyInvalidOperationException


def test_fast_mode_disables_sound_and_serial(default_rom):
    pyboy = PyBoy(default_rom, window="null", fast_mode=True)
    try:
        assert pyboy.fast_mode

        pyboy.memory[0xFF26] = 0x80
        assert pyboy.memory[0xFF26] == 0

        pyboy.memory[0xFF01] = 0x12
        pyboy.memory[0xFF02] = 0x81
        assert pyboy.memory[0xFF01] == 0xFF
        assert not pyboy.memory[0xFF02] & 0x80

        assert pyboy.tick(3, render=True, sound=True)
    finally:
        pyboy.stop(save=False)


def test_fast_mode_serial_stub_ignores_loaded_transfer_state(default_rom):
    accurate = PyBoy(default_rom, window="null")
    fast = PyBoy(default_rom, window="null", fast_mode=True)
    try:
        accurate.memory[0xFF01] = 0x12
        accurate.memory[0xFF02] = 0x81
        assert accurate.memory[0xFF02] & 0x80

        state = BytesIO()
        accurate.save_state(state)
        state.seek(0)
        fast.load_state(state)
        assert fast.memory[0xFF01] == 0xFF
        assert not fast.memory[0xFF02] & 0x80

        fast.memory[0xFF01] = 0x34
        fast.memory[0xFF02] = 0x81
        assert fast.memory[0xFF01] == 0xFF
        assert not fast.memory[0xFF02] & 0x80

        fast.tick(1, render=False, sound=False)
        assert not fast.memory[0xFF02] & 0x80
        assert not fast.memory[0xFF0F] & 0x08
    finally:
        accurate.stop(save=False)
        fast.stop(save=False)


def test_fast_mode_is_opt_in(default_rom):
    pyboy = PyBoy(default_rom, window="null")
    try:
        assert not pyboy.fast_mode
        assert pyboy.memory[0xFF26] == 0x70
    finally:
        pyboy.stop(save=False)


@pytest.mark.parametrize(
    ("rom_fixture", "cgb"),
    (("default_rom", False), ("default_rom_cgb", True)),
)
def test_fast_mode_window_uses_its_tilemap(request, rom_fixture, cgb, tmp_path):
    with open(request.getfixturevalue(rom_fixture), "rb") as rom_file:
        rom = bytearray(rom_file.read())
    rom[0x100:0x102] = b"\x18\xfe"
    rom_path = tmp_path / ("window_tilemap_test.gbc" if cgb else "window_tilemap_test.gb")
    rom_path.write_bytes(rom)

    pyboy = PyBoy(str(rom_path), window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(5, False, False)
        pyboy.memory[0xFF40] = 0
        pyboy.memory[0xFF4A] = 0
        pyboy.memory[0xFF4B] = 87

        if cgb:
            pyboy.memory[0xFF68] = 0x80
            for value in (0x1F, 0x00, 0xE0, 0x03):
                pyboy.memory[0xFF69] = value
        else:
            pyboy.memory[0xFF47] = 0xE4

        for map_index in range(32 * 32):
            pyboy.memory[0, 0x9800 + map_index] = 0
            pyboy.memory[0, 0x9C00 + map_index] = 1
            if cgb:
                pyboy.memory[1, 0x9800 + map_index] = 0
                pyboy.memory[1, 0x9C00 + map_index] = 0

        for row in range(8):
            pyboy.memory[0, 0x8010 + row * 2] = 0xFF
            pyboy.memory[0, 0x8011 + row * 2] = 0

        pyboy.memory[0xFF40] = 0xF1
        pyboy.tick(3, True, False)
        frame = pyboy.screen.ndarray.copy()

        assert tuple(frame[0, 79, :3]) != tuple(frame[0, 80, :3])

        for row in range(8):
            pyboy.memory[0, 0x8010 + row * 2] = 0
        pyboy.tick(3, True, False)
        updated_frame = pyboy.screen.ndarray

        assert tuple(updated_frame[0, 79, :3]) == tuple(updated_frame[0, 80, :3])
    finally:
        pyboy.stop(save=False)


def test_fast_mode_rejects_serial_shared_memory(default_rom):
    with pytest.raises(PyBoyInvalidOperationException, match="Serial shared memory"):
        PyBoy(default_rom, window="null", fast_mode=True, serial_shared_memory=object())


def test_fast_mode_pcm_reads_remain_silent_when_loading_sound_state(default_rom):
    accurate = PyBoy(default_rom, window="null", cgb=True)
    fast = PyBoy(default_rom, window="null", cgb=True, fast_mode=True)
    try:
        accurate.memory[0xFF26] = 0x80
        accurate.memory[0xFF30] = 0xAB
        accurate.memory[0xFF1A] = 0x80
        accurate.memory[0xFF1C] = 0x20
        accurate.memory[0xFF1D] = 0xE6
        accurate.memory[0xFF1E] = 0x83
        accurate.tick(1, True)
        assert accurate.memory[0xFF77] & 0x0F == 0x0B

        state = BytesIO()
        accurate.save_state(state)
        state.seek(0)
        fast.load_state(state)
        assert fast.memory[0xFF77] == 0
    finally:
        accurate.stop(save=False)
        fast.stop(save=False)
def test_fast_mode_state_round_trip(default_rom):
    pyboy = PyBoy(default_rom, window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(2, render=False, sound=False)
        saved_state = BytesIO()
        pyboy.save_state(saved_state)
        saved_state.seek(0)
        pyboy.load_state(saved_state)
        assert pyboy.tick(1, render=False, sound=False)
    finally:
        pyboy.stop(save=False)


def test_fast_mode_keeps_pokemon_functional(pokemon_blue_rom):
    pyboy = PyBoy(pokemon_blue_rom, window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.game_wrapper.start_game()

        pyboy.game_wrapper.set_event_flag("got_pokedex")
        pyboy.button("start", 10)
        pyboy.tick(30, False, False)
        assert pyboy.tilemap_window[12:19, 2] == pyboy.game_wrapper._encode_text("POKéDEX")

        pyboy.button("start", 10)
        pyboy.tick(30, False, False)
        pyboy.game_wrapper.warp("viridian_pokecenter")
        pyboy.tick(120, False, False)
        assert pyboy.memory[0xD35E] == 0x29
    finally:
        pyboy.stop(save=False)


def test_cli_fast_mode_flag(default_rom):
    args = main.parser.parse_args([str(default_rom), "--fast"])
    assert args.fast_mode
