from io import BytesIO
from pathlib import Path

import numpy as np
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
    ("rom_fixture", "cgb", "lcdc"),
    (
        ("default_rom", False, 0xF1),
        ("default_rom", False, 0xF0),
        ("default_rom_cgb", True, 0xF1),
    ),
)
def test_fast_mode_window_uses_its_tilemap(request, rom_fixture, cgb, lcdc, tmp_path):
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

        pyboy.memory[0xFF40] = lcdc
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


def test_fast_mode_oam_dma_copies_immediately(default_rom):
    pyboy = PyBoy(default_rom, window="null", fast_mode=True)
    try:
        pyboy.memory[0xFF50] = 1
        pyboy.memory[0xFF40] = 0

        rom_data = pyboy.memory[0x0200:0x02A0]
        pyboy.memory[0xFF46] = 0x02
        assert pyboy.memory[0xFE00:0xFEA0] == rom_data

        wram_data = list(range(0xA0))
        pyboy.memory[0xC000:0xC0A0] = wram_data
        pyboy.memory[0xFF46] = 0xC0
        assert pyboy.memory[0xFE00:0xFEA0] == wram_data
    finally:
        pyboy.stop(save=False)


@pytest.mark.parametrize("command", [0x01, 0x81])
def test_fast_mode_hdma_copies_rom_blocks_immediately(default_rom_cgb, command):
    pyboy = PyBoy(default_rom_cgb, window="null", fast_mode=True)
    try:
        pyboy.memory[0xFF50] = 1
        pyboy.memory[0xFF40] = 0
        rom_data = pyboy.memory[0x0200:0x0220]

        pyboy.memory[0xFF51] = 0x02
        pyboy.memory[0xFF52] = 0x00
        pyboy.memory[0xFF53] = 0x00
        pyboy.memory[0xFF54] = 0x00
        pyboy.memory[0xFF55] = command

        assert pyboy.memory[0x8000:0x8020] == rom_data
        assert pyboy.memory[0xFF55] == 0xFF
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


def test_fast_mode_renders_more_than_ten_sprites_on_a_scanline(default_rom, tmp_path):
    rom = bytearray(Path(default_rom).read_bytes())
    rom[0x100:0x102] = b"\x18\xfe"
    rom_path = tmp_path / "sprite_test.gb"
    rom_path.write_bytes(rom)

    pyboy = PyBoy(str(rom_path), window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(5, False, False)
        pyboy.memory[0xFF40] = 0
        pyboy.memory[0xFF47] = 0xE4
        pyboy.memory[0xFF48] = 0xE4
        pyboy.memory[0xFF49] = 0xE4
        for row in range(8):
            pyboy.memory[0x8000 + row * 2] = 0xFF
            pyboy.memory[0x8000 + row * 2 + 1] = 0xFF
        for index in range(40):
            address = 0xFE00 + index * 4
            pyboy.memory[address] = 0
            pyboy.memory[address + 1] = 0
            pyboy.memory[address + 2] = 0
            pyboy.memory[address + 3] = 0
        for index in range(11):
            address = 0xFE00 + index * 4
            pyboy.memory[address] = 16
            pyboy.memory[address + 1] = 8 + index * 12
            pyboy.memory[address + 3] = 0x10 if index % 2 else 0
        pyboy.memory[0xFF40] = 0x92
        pyboy.tick(3, True, False)

        row = pyboy.screen.ndarray[0, :, :3]
        visible = [np.any(row[x : x + 8] != 255) for x in range(0, 132, 12)]
        assert all(visible)
    finally:
        pyboy.stop(save=False)


def test_fast_mode_blanks_frame_when_all_dmg_layers_are_disabled(default_rom, tmp_path):
    rom = bytearray(Path(default_rom).read_bytes())
    rom[0x100:0x102] = b"\x18\xfe"
    rom_path = tmp_path / "disabled_layers_test.gb"
    rom_path.write_bytes(rom)

    pyboy = PyBoy(str(rom_path), window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(5, False, False)
        pyboy.memory[0xFF40] = 0x80
        pyboy.tick(2, True, False)

        assert np.all(pyboy.screen.ndarray == pyboy.screen.ndarray[0, 0])
    finally:
        pyboy.stop(save=False)


def test_fast_mode_sprite_transparency_and_clipping(default_rom, tmp_path):
    rom = bytearray(Path(default_rom).read_bytes())
    rom[0x100:0x102] = b"\x18\xfe"
    rom_path = tmp_path / "sprite_transparency_test.gb"
    rom_path.write_bytes(rom)

    pyboy = PyBoy(str(rom_path), window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(5, False, False)
        pyboy.memory[0xFF40] = 0
        pyboy.memory[0xFF47] = 0xE4
        pyboy.memory[0xFF48] = 0xE4
        for row in range(8):
            pyboy.memory[0x8010 + row * 2] = 0xAA
            pyboy.memory[0x8011 + row * 2] = 0
        for index in range(40):
            address = 0xFE00 + index * 4
            pyboy.memory[address] = 0
            pyboy.memory[address + 1] = 4
            pyboy.memory[address + 2] = 1
            pyboy.memory[address + 3] = 0

        pyboy.memory[0xFF40] = 0x92
        pyboy.tick(3, True, False)
        before = pyboy.screen.ndarray.copy()

        pyboy.memory[0xFE00] = 16
        pyboy.tick(3, True, False)
        after = pyboy.screen.ndarray

        changed = np.any(before[0, :4, :3] != after[0, :4, :3], axis=1)
        assert np.any(changed)
        assert np.any(~changed)
    finally:
        pyboy.stop(save=False)


def test_fast_mode_sprite_behind_background_respects_color_zero(default_rom, tmp_path):
    rom = bytearray(Path(default_rom).read_bytes())
    rom[0x100:0x102] = b"\x18\xfe"
    rom_path = tmp_path / "sprite_priority_test.gb"
    rom_path.write_bytes(rom)

    pyboy = PyBoy(str(rom_path), window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(5, False, False)
        pyboy.memory[0xFF40] = 0
        pyboy.memory[0xFF47] = 0xE4
        pyboy.memory[0xFF48] = 0xE4
        for row in range(8):
            pyboy.memory[0x8000 + row * 2] = 0xFF
            pyboy.memory[0x8000 + row * 2 + 1] = 0
            pyboy.memory[0x8010 + row * 2] = 0
            pyboy.memory[0x8010 + row * 2 + 1] = 0xFF
        for index in range(40):
            address = 0xFE00 + index * 4
            pyboy.memory[address] = 0
            pyboy.memory[address + 1] = 0
            pyboy.memory[address + 2] = 0
            pyboy.memory[address + 3] = 0
        pyboy.memory[0xFE00:0xFE04] = [16, 8, 1, 0x80]
        pyboy.memory[0xFF40] = 0x93
        pyboy.tick(3, True, False)
        background_frame = pyboy.screen.ndarray.copy()
        background_pixel = pyboy.screen.ndarray[0, 0].copy()

        pyboy.memory[0xFF40] = 0
        for row in range(8):
            pyboy.memory[0x8000 + row * 2] = 0
            pyboy.memory[0x8000 + row * 2 + 1] = 0
        pyboy.memory[0xFF40] = 0x93
        pyboy.tick(3, True, False)
        transparent_background_frame = pyboy.screen.ndarray.copy()

        assert np.array_equal(background_pixel, background_frame[0, 8])
        assert not np.array_equal(transparent_background_frame[0, 0], transparent_background_frame[0, 8])

        pyboy.memory[0xFE03] = 0
        pyboy.memory[0xFF40] = 0x91
        pyboy.tick(3, True, False)
        disabled_sprite_frame = pyboy.screen.ndarray

        assert np.array_equal(disabled_sprite_frame[0, 0], disabled_sprite_frame[0, 8])
    finally:
        pyboy.stop(save=False)


def test_fast_mode_cgb_sprite_respects_background_map_priority(default_rom_cgb, tmp_path):
    rom = bytearray(Path(default_rom_cgb).read_bytes())
    rom[0x100:0x102] = b"\x18\xfe"
    rom_path = tmp_path / "cgb_sprite_priority_test.gbc"
    rom_path.write_bytes(rom)

    pyboy = PyBoy(str(rom_path), window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(5, False, False)
        pyboy.memory[0xFF40] = 0
        pyboy.memory[0xFF68] = 0x82
        pyboy.memory[0xFF69] = 0xE0
        pyboy.memory[0xFF69] = 0x03
        pyboy.memory[0xFF6A] = 0x84
        pyboy.memory[0xFF6B] = 0
        pyboy.memory[0xFF6B] = 0x7C

        for row in range(8):
            pyboy.memory[0, 0x8000 + row * 2] = 0xFF
            pyboy.memory[0, 0x8000 + row * 2 + 1] = 0
            pyboy.memory[0, 0x8010 + row * 2] = 0
            pyboy.memory[0, 0x8010 + row * 2 + 1] = 0xFF
        for map_index in range(32 * 32):
            pyboy.memory[0, 0x9800 + map_index] = 0
            pyboy.memory[1, 0x9800 + map_index] = 0
        pyboy.memory[1, 0x9800] = 0x80
        for index in range(40):
            address = 0xFE00 + index * 4
            pyboy.memory[address] = 0
            pyboy.memory[address + 1] = 0
            pyboy.memory[address + 2] = 0
            pyboy.memory[address + 3] = 0
        pyboy.memory[0xFE00:0xFE04] = [16, 8, 1, 0]

        pyboy.memory[0xFF40] = 0x93
        pyboy.tick(3, True, False)
        priority_blocked_frame = pyboy.screen.ndarray.copy()

        pyboy.memory[0xFF40] = 0
        for row in range(8):
            pyboy.memory[0, 0x8000 + row * 2] = 0
            pyboy.memory[0, 0x8000 + row * 2 + 1] = 0
        pyboy.memory[0xFF40] = 0x93
        pyboy.tick(3, True, False)
        transparent_background_frame = pyboy.screen.ndarray.copy()

        assert np.array_equal(priority_blocked_frame[0, 0], priority_blocked_frame[0, 8])
        assert not np.array_equal(transparent_background_frame[0, 0], transparent_background_frame[0, 8])
    finally:
        pyboy.stop(save=False)


def test_fast_mode_renders_8x16_sprite_with_flips(default_rom, tmp_path):
    rom = bytearray(Path(default_rom).read_bytes())
    rom[0x100:0x102] = b"\x18\xfe"
    rom_path = tmp_path / "sprite_8x16_flip_test.gb"
    rom_path.write_bytes(rom)

    pyboy = PyBoy(str(rom_path), window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(5, False, False)
        pyboy.memory[0xFF40] = 0
        pyboy.memory[0xFF48] = 0xE4
        for address in range(0x8020, 0x8040):
            pyboy.memory[address] = 0
        pyboy.memory[0x802E] = 0x80
        pyboy.memory[0x803F] = 0x80
        for index in range(40):
            address = 0xFE00 + index * 4
            pyboy.memory[address] = 0
            pyboy.memory[address + 1] = 0
            pyboy.memory[address + 2] = 0
            pyboy.memory[address + 3] = 0
        pyboy.memory[0xFE00] = 16
        pyboy.memory[0xFE01] = 8
        pyboy.memory[0xFE02] = 2
        pyboy.memory[0xFE03] = 0x60
        pyboy.memory[0xFF40] = 0x96
        pyboy.tick(3, True, False)

        nonwhite = np.any(pyboy.screen.ndarray[:16, :, :3] != 255, axis=2)
        assert nonwhite[0, 7]
        assert nonwhite[8, 7]
        assert not np.any(nonwhite[0, :7])
        assert not np.any(nonwhite[8, :7])
        assert pyboy.screen.ndarray[0, 7, 0] != pyboy.screen.ndarray[8, 7, 0]
    finally:
        pyboy.stop(save=False)


def test_fast_mode_sparse_refreshes_modified_background_tile(default_rom, tmp_path):
    rom = bytearray(Path(default_rom).read_bytes())
    rom[0x100:0x102] = b"\x18\xfe"
    rom_path = tmp_path / "background_tile_test.gb"
    rom_path.write_bytes(rom)

    pyboy = PyBoy(str(rom_path), window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(5, False, False)
        pyboy.memory[0xFF40] = 0
        pyboy.memory[0xFF42] = 0
        pyboy.memory[0xFF43] = 0
        pyboy.memory[0xFF47] = 0xE4
        pyboy.memory[0x9800] = 1
        for row in range(8):
            pyboy.memory[0x8010 + row * 2] = 0
            pyboy.memory[0x8011 + row * 2] = 0

        pyboy.memory[0xFF40] = 0x91
        pyboy.tick(3, True, False)
        before = pyboy.screen.ndarray.copy()

        for row in range(8):
            pyboy.memory[0x8010 + row * 2] = 0xFF
            pyboy.memory[0x8011 + row * 2] = 0xFF
        pyboy.tick(3, True, False)
        after = pyboy.screen.ndarray

        assert np.any(before[0, 0] != after[0, 0])
        assert np.array_equal(before[0, 8], after[0, 8])
    finally:
        pyboy.stop(save=False)


def test_fast_mode_background_view_wraps_scroll_coordinates(default_rom, tmp_path):
    rom = bytearray(Path(default_rom).read_bytes())
    rom[0x100:0x102] = b"\x18\xfe"
    rom_path = tmp_path / "background_scroll_wrap_test.gb"
    rom_path.write_bytes(rom)

    pyboy = PyBoy(str(rom_path), window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(5, False, False)
        pyboy.memory[0xFF40] = 0
        pyboy.memory[0xFF42] = 248
        pyboy.memory[0xFF43] = 248
        pyboy.memory[0xFF47] = 0xE4

        for map_y in range(32):
            for map_x in range(32):
                pyboy.memory[0x9800 + map_y * 32 + map_x] = (map_x ^ map_y) & 1
        for row in range(8):
            pyboy.memory[0x8000 + row * 2] = 0
            pyboy.memory[0x8001 + row * 2] = 0
            pyboy.memory[0x8000 + 16 + row * 2] = 0xFF
            pyboy.memory[0x8001 + 16 + row * 2] = 0

        pyboy.memory[0xFF40] = 0x91
        pyboy.tick(3, True, False)
        screen = pyboy.screen.ndarray

        assert np.array_equal(screen[0, 0, :3], screen[8, 8, :3])
        assert np.array_equal(screen[0, 8, :3], screen[8, 0, :3])
        assert np.any(screen[0, 0, :3] != screen[0, 8, :3])
    finally:
        pyboy.stop(save=False)


def test_fast_mode_sparse_refreshes_cgb_vram_bank_tile(default_rom_cgb, tmp_path):
    rom = bytearray(Path(default_rom_cgb).read_bytes())
    rom[0x100:0x102] = b"\x18\xfe"
    rom_path = tmp_path / "cgb_background_tile_test.gbc"
    rom_path.write_bytes(rom)

    pyboy = PyBoy(str(rom_path), window="null", fast_mode=True)
    try:
        pyboy.set_emulation_speed(0)
        pyboy.tick(5, False, False)
        pyboy.memory[0xFF40] = 0

        pyboy.memory[0, 0x9800] = 1
        pyboy.memory[1, 0x9800] = 0x08
        for row in range(8):
            pyboy.memory[1, 0x8010 + row * 2] = 0
            pyboy.memory[1, 0x8011 + row * 2] = 0

        pyboy.memory[0xFF40] = 0x91
        pyboy.tick(3, True, False)
        before = pyboy.screen.ndarray[0, 0].copy()

        for row in range(8):
            pyboy.memory[1, 0x8010 + row * 2] = 0xFF
            pyboy.memory[1, 0x8011 + row * 2] = 0xFF
        pyboy.tick(3, True, False)
        after = pyboy.screen.ndarray[0, 0]

        assert np.any(before != after)
    finally:
        pyboy.stop(save=False)


def test_cli_fast_mode_flag(default_rom):
    args = main.parser.parse_args([str(default_rom), "--fast"])
    assert args.fast_mode
