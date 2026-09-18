#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# Puzznic, Flipull, Amazing Tater and Adventures of Lolo keep their boards in work RAM rather
# than in the tilemap, and their wrappers read them from there. These tests write a board by
# hand and check that it is decoded the way the cartridge writes it, which needs no game ROM:
# the title in a copy of PyBoy's own default ROM is patched so the right wrapper is picked.

import pytest

from pyboy import PyBoy
from pyboy.plugins.game_wrapper_adventures_of_lolo import GameWrapperAdventuresOfLolo
from pyboy.plugins.game_wrapper_amazing_tater import GameWrapperAmazingTater
from pyboy.plugins.game_wrapper_flipull import GameWrapperFlipull
from pyboy.plugins.game_wrapper_puzznic import GameWrapperPuzznic
from pyboy.plugins.game_wrapper_super_mario_land import GameWrapperSuperMarioLand
from pyboy.utils import PyBoyException


def _rom_with_title(source, destination, title):
    """A copy of `source` whose cartridge header claims `title`, checksum and all."""
    with open(source, "rb") as rom_file:
        data = bytearray(rom_file.read())
    data[0x134:0x144] = title.encode("ascii").ljust(16, b"\x00")[:16]
    checksum = 0
    for address in range(0x134, 0x14D):
        checksum = (checksum - data[address] - 1) & 0xFF
    data[0x14D] = checksum
    destination.write_bytes(bytes(data))
    return str(destination)


@pytest.fixture
def stub_rom(default_rom, tmp_path):
    def build(title):
        return _rom_with_title(default_rom, tmp_path / f"{title.lower()}.gb", title)

    return build


def test_puzznic_reads_its_playfield(stub_rom):
    pyboy = PyBoy(stub_rom("PUZZNIC"), window="null")
    try:
        puzznic = pyboy.game_wrapper
        assert isinstance(puzznic, GameWrapperPuzznic)

        # Two blocks of one type and a lone block of another, sitting on a wall.
        grid = [0x03] * 240
        for col in range(10):
            grid[20 * 11 + 2 * col] = 0x06
        grid[20 * 10 + 2 * 3] = 0x08
        grid[20 * 10 + 2 * 4] = 0x08
        grid[20 * 10 + 2 * 6] = 0x09
        pyboy.memory[0xDF00 : 0xDF00 + 240] = grid
        pyboy.memory[0xD018] = 3
        pyboy.memory[0xD019] = 3
        pyboy.memory[0xD013] = 10
        pyboy.memory[0xD012] = 3
        puzznic.post_tick()

        assert puzznic.blocks() == [(10, 3, 1), (10, 4, 1), (10, 6, 2)]
        assert puzznic.block_counts() == {1: 2, 2: 1}
        assert puzznic.cursor == (10, 3)
        assert puzznic.blocks_remaining == 3
        assert puzznic.blocks_cleared == 0
        assert not puzznic.stage_cleared()
        # A type down to a single block can never be matched away again.
        assert puzznic.game_over()

        game_area = puzznic.game_area()
        assert game_area.shape == (12, 10)
        assert game_area[10][3] == 0x08
        assert game_area[11][0] == 0x06

        puzznic.game_area_mapping(puzznic.mapping_minimal, 0)
        game_area = puzznic.game_area()
        assert game_area[10][3] == 2  # Any block
        assert game_area[11][0] == 1  # Anything solid
        assert game_area[0][0] == 0  # Outside the playfield

        assert "Blocks: 3/3" in str(puzznic)
    finally:
        pyboy.stop(save=False)


def test_flipull_reads_its_field(stub_rom):
    pyboy = PyBoy(stub_rom("FLIPULL"), window="null")
    try:
        flipull = pyboy.game_wrapper
        assert isinstance(flipull, GameWrapperFlipull)

        field = [0x00] * (14 * 0x20)
        for col in range(16):
            field[0 * 0x20 + col] = 0x80
            field[13 * 0x20 + col] = 0x80
        for row in range(14):
            field[row * 0x20] = 0x80
        field[6 * 0x20 + 3] = 0x83
        field[6 * 0x20 + 4] = 0x84
        field[7 * 0x20 + 3] = 0x83
        field[7 * 0x20 + 4] = 0x87  # The staircase is structural, never a block
        pyboy.memory[0xC840 : 0xC840 + 14 * 0x20] = field
        # The counters are decimal digits, ones first, and nearly all of them are in HRAM.
        pyboy.memory[0xFFC9] = 3
        pyboy.memory[0xFFCA] = 0
        pyboy.memory[0xFFC0] = 5
        pyboy.memory[0xFFC1] = 0
        pyboy.memory[0xFFCF] = 1
        pyboy.memory[0xFFC6] = 2
        pyboy.memory[0xFFC7] = 1
        pyboy.memory[0xFFCB] = 9
        pyboy.memory[0xFFCC] = 5
        pyboy.memory[0xFFCE] = 2
        pyboy.memory[0xFFD2] = 2
        pyboy.memory[0xFFD3] = 2
        flipull.post_tick()

        assert flipull.blocks() == [(6, 3, 1), (6, 4, 2), (7, 3, 1)]
        assert flipull.row_blocks(6) == [(3, 1), (4, 2)]
        assert flipull.stage == 12
        assert flipull.blocks_remaining == 3
        assert flipull.blocks_initial == 5
        assert flipull.blocks_cleared == 2
        assert flipull.clear_target == 1
        assert flipull.time_left == 179
        assert flipull.throws == 2
        assert not flipull.stage_cleared()
        assert not flipull.game_over()

        # The clock running out is how a life is lost.
        pyboy.memory[0xFFCB] = 0
        pyboy.memory[0xFFCC] = 0
        pyboy.memory[0xFFCE] = 0
        flipull.post_tick()
        assert flipull.game_over()

        game_area = flipull.game_area()
        assert game_area.shape == (14, 16)
        assert game_area[7][4] == 0x87
    finally:
        pyboy.stop(save=False)


def test_amazing_tater_reads_its_board(stub_rom):
    pyboy = PyBoy(stub_rom("AMAZING-TATER"), window="null")
    try:
        tater = pyboy.game_wrapper
        assert isinstance(tater, GameWrapperAmazingTater)

        board = [0xFF] * 360
        for row in range(2, 8):
            for col in range(2, 10):
                board[20 * row + col] = 0x00
        for col in range(1, 11):
            board[20 * 1 + col] = 0xF0
            board[20 * 8 + col] = 0xF0
        for row in range(1, 9):
            board[20 * row + 1] = 0xF0
            board[20 * row + 10] = 0xF0
        board[20 * 3 + 3] = 0xC0  # The first tater
        board[20 * 3 + 4] = 0x40  # A block square
        board[20 * 4 + 6] = 0xE0  # A pit
        board[20 * 5 + 7] = 0xA3  # A turnstile pivot
        board[20 * 5 + 6] = 0x80  # ... and one of its arms
        board[20 * 6 + 8] = 0xD0  # The exit flag
        pyboy.memory[0xC2F2 : 0xC2F2 + 360] = board
        pyboy.memory[0xC2BD] = 10
        pyboy.memory[0xC2BE] = 8
        pyboy.memory[0xC2AC] = 0
        pyboy.memory[0xC2AD] = 0b0001  # A mask of who is still out, not a count
        pyboy.memory[0xC2AE] = 0
        tater.post_tick()

        assert tater.taters() == {0: (3, 3)}
        assert tater.taters_left == 1
        assert tater.taters_total == 1
        assert tater.taters_home == 0
        assert tater.room_size == (8, 6)
        assert tater.blocks() == [(3, 4, False)]
        assert tater.pits() == [(4, 6)]
        assert tater.exit_cell() == (6, 8)
        assert len(tater.turnstiles()) == 1
        assert not tater.level_solved()
        assert not tater.game_over()  # A room in these modes cannot be lost

        # The mask empties as each character reaches the flag, which is the win condition.
        pyboy.memory[0xC2AD] = 0
        tater.post_tick()
        assert tater.level_solved()
        assert tater.taters_home == 1

        assert tater.level_label(0) == "A-01"
        assert tater.level_label(41) == "C-01"
        assert tater.game_area().shape == (18, 20)
    finally:
        pyboy.stop(save=False)


def test_adventures_of_lolo_reads_its_room(stub_rom):
    pyboy = PyBoy(stub_rom("LOLO2"), window="null")
    try:
        lolo = pyboy.game_wrapper
        assert isinstance(lolo, GameWrapperAdventuresOfLolo)

        board = [0x88] * 64
        for col in range(8):
            board[col] = 0x81
            board[7 * 8 + col] = 0x81
        board[3 * 8 + 2] = 0x90  # A heart framer
        board[4 * 8 + 5] = 0x8F  # An Emerald Framer
        board[1 * 8 + 7] = 0x96  # The door
        board[6 * 8 + 1] = 0x00  # Where Lolo starts
        board[2 * 8 + 4] = 0x18  # A Snakey
        pyboy.memory[0xC3BF : 0xC3BF + 64] = board
        pyboy.memory[0xC3A6] = 38
        pyboy.memory[0xC3A9] = 1
        pyboy.memory[0xC4AD] = 2
        pyboy.memory[0xC3BE] = 0x17  # The scene a graded room runs in

        # Lolo is the first pair of sprites, then one pair per enemy or egg.
        oam = [0] * 160
        oam[0], oam[1] = 24 + 6 * 16, 16 + 1 * 16
        oam[4], oam[5] = 24 + 6 * 16, 16 + 1 * 16 + 8
        oam[8], oam[9] = 24 + 2 * 16, 16 + 4 * 16
        oam[12], oam[13] = 24 + 2 * 16, 16 + 4 * 16 + 8
        pyboy.memory[0xC000 : 0xC000 + 160] = oam

        lolo.post_tick()
        lolo._learn_tiles()

        assert lolo.room == 38
        assert lolo.room_label() == "int 1-1"
        assert lolo.hearts_left == 1
        assert lolo.magic_shots == 2
        assert lolo.lolo == (6.0, 1.0)
        assert lolo.enemies() == [(2.0, 4.0)]
        assert lolo.door == (1, 7)
        assert lolo.hearts() == [(3, 2)]
        assert lolo.framers() == [(4, 5)]
        assert not lolo.room_solved()
        assert not lolo.game_over()

        game_area = lolo.game_area()
        assert game_area.shape == (8, 8)
        assert game_area[6][1] == 0x00  # Lolo, drawn in from his sprite
        assert game_area[2][4] == 0x01  # An enemy, likewise

        # A death is not a flag: the cartridge restarts the room, and the hearts come back.
        pyboy.memory[0xC3A9] = 2
        lolo.post_tick()
        assert lolo.game_over()

        # The room table is in bank 13, which a stub ROM this size does not have.
        with pytest.raises(PyBoyException):
            lolo.room_layout(38)
    finally:
        pyboy.stop(save=False)


def test_super_mario_land_object_slots(stub_rom):
    pyboy = PyBoy(stub_rom("SUPER MARIOLAND"), window="null")
    try:
        mario = pyboy.game_wrapper
        assert isinstance(mario, GameWrapperSuperMarioLand)

        objects = [0xFF] * (10 * 0x10)
        objects[0x00], objects[0x01], objects[0x02], objects[0x03], objects[0x04] = 0x01, 0x0A, 0x60, 0x40, 0x02
        objects[0x10], objects[0x11], objects[0x12], objects[0x13], objects[0x14] = 0x01, 0x0B, 0x50, 0x70, 0x01
        pyboy.memory[0xD100 : 0xD100 + 160] = objects
        pyboy.memory[0xC201] = 0x70  # Mario's Y
        pyboy.memory[0xC202] = 0x30  # ... and his X, both on the screen and not in the level
        pyboy.memory[0xC205] = 0x20  # Facing left
        pyboy.memory[0xC207] = 1  # Mid-jump
        pyboy.memory[0xC20A] = 0  # ... so not on the ground
        pyboy.memory[0xC20C] = 0x19
        pyboy.memory[0xC20D] = 0x20
        mario.post_tick()

        assert mario.mario_position == (0x30, 0x70)
        assert mario.mario_facing == "left"
        assert not mario.mario_on_ground
        assert mario.mario_speed == 0x19
        assert mario.mario_direction == "left"
        assert mario.mario_jump_phase == 1

        slots = mario.object_slots()
        assert len(slots) == 2  # The other eight slots are empty
        assert slots[0] == {"slot": 0, "type": 0x0A, "x": 0x40, "y": 0x60, "animation": 2}
        assert slots[1] == {"slot": 1, "type": 0x0B, "x": 0x70, "y": 0x50, "animation": 1}

        annotations = mario.game_area_annotations()
        assert annotations[0] == (0x40, 0x60, "s0 t0A")
        assert annotations[-1] == (0x30, 0x70, "MARIO")
    finally:
        pyboy.stop(save=False)
