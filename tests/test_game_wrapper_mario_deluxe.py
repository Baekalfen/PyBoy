#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from types import SimpleNamespace

from pyboy import PyBoy
from pyboy.plugins.game_wrapper_super_mario_bros_deluxe import (
    ADDR_SPRITE_ID,
    ADDR_SPRITE_STATUS,
    ADDR_SPRITE_X_HIGH,
    ADDR_SPRITE_X_LOW,
    ADDR_SPRITE_Y_HIGH,
    ADDR_SPRITE_Y_LOW,
    SPRITE_WRAM_BANK,
)


def test_mario_deluxe_basics(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    assert pyboy.cartridge_title == "MARIO DELUXAHY"

    mario = pyboy.game_wrapper
    mario.start_game()

    assert pyboy.memory[0xFFB5] == 0x0B
    assert mario.world == (1, 1)
    assert mario.level == 0
    assert mario.score == 0
    assert mario.coins == 0
    assert mario.lives_left == 5
    assert mario.time_left > 0


def test_mario_deluxe_left_only_progress_reaches_left_wall(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    try:
        mario = pyboy.game_wrapper
        mario.start_game()
        pyboy.tick(60, False)

        progress = []
        for _ in range(150):
            pyboy.button_press("left")
            pyboy.tick(2, False)
            pyboy.button_release("left")
            progress.append(int(mario.level_progress))

        print({"action": "left", "progress": progress})
        assert min(progress) < progress[0]
        assert max(progress) <= progress[0]
        assert progress[-1] == 0
    finally:
        pyboy.stop(save=False)


def test_mario_deluxe_right_only_progress_reaches_first_enemy(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    try:
        mario = pyboy.game_wrapper
        mario.start_game()
        pyboy.tick(60, False)

        progress = []
        for _ in range(150):
            pyboy.button_press("right")
            pyboy.tick(2, False)
            pyboy.button_release("right")
            progress.append(int(mario.level_progress))
            if mario.game_over():
                break

        print({"action": "right", "progress": progress})
        assert progress
        assert max(progress) > progress[0] + 100
        assert max(progress) >= 500
    finally:
        pyboy.stop(save=False)


def test_mario_deluxe_stuck_flag_after_ten_seconds_without_horizontal_progress(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    try:
        mario = pyboy.game_wrapper
        mario.start_game()
        pyboy.tick(60, False)
        assert not mario.stuck

        for _ in range(600):
            pyboy.tick(1, False)
            if mario.stuck:
                break

        assert mario.stuck
        assert mario.stuck_frames >= 600
    finally:
        pyboy.stop(save=False)


def test_mario_deluxe_reset_clears_stuck_flag(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    try:
        mario = pyboy.game_wrapper
        mario.start_game()
        pyboy.tick(60, False)
        for _ in range(600):
            pyboy.tick(1, False)
            if mario.stuck:
                break
        assert mario.stuck

        mario.reset_game()
        assert not mario.stuck
        assert mario.stuck_frames == 0
    finally:
        pyboy.stop(save=False)


def test_mario_deluxe_level_selection(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    mario = pyboy.game_wrapper
    mario.set_world_level(2, 2)
    mario.start_game()

    assert pyboy.memory[0xFFB5] == 0x0B
    assert mario.world == (2, 2)
    assert mario.level == 5


def test_mario_deluxe_super_player_level_selection(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    mario = pyboy.game_wrapper
    mario.set_world_level(9, 1, super_player_levels=True)
    mario.start_game()

    assert pyboy.memory[0xFFB5] == 0x0B
    assert mario.level == 32


def test_mario_deluxe_challenge_level_selection(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    mario = pyboy.game_wrapper
    mario.set_world_level(2, 2)
    mario.start_game(challenge=True)

    assert pyboy.memory[0xFFB5] == 0x0B
    assert mario.world == (2, 2)
    assert mario.level == 5


def test_mario_deluxe_challenge_selector(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    mario = pyboy.game_wrapper
    mario.start_game(unlock_level_select=True)

    assert pyboy.memory[0xFFB5] == 0x1E
    assert pyboy.memory[0xC18E] == 1


def test_mario_deluxe_game_area_uses_metatile_interactions(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    mario = pyboy.game_wrapper
    mario.start_game()
    pyboy.tick(1000, False)

    area = mario.game_area()
    assert area.shape == (26, 20)
    assert area[24, 0] == 3  # Solid floor is distinct from Mario.
    assert area[24, 0] == area[25, 0]
    assert area[22, 4] == 1  # Mario.

    pyboy.button_press("right")
    pyboy.tick(240, False)
    pyboy.button_release("right")
    assert mario.game_area()[16, 1] == 2  # The rendered coin/item box remains aligned after scrolling.


def test_mario_deluxe_bubbles_are_not_mario(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    mario = pyboy.game_wrapper
    mario.start_game(world_level=(2, 2))
    pyboy.tick(1000, False)

    area = mario.game_area()
    assert sum(int(tile) == 1 for row in area for tile in row) == 4


def test_mario_deluxe_custom_level_sequence(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    mario = pyboy.game_wrapper
    mario.start_game()

    for expected_level in (1, 2, 4):
        pyboy.memory[0xFFB5] = 0x04
        mario.post_tick()
        assert pyboy.memory[0xC163] == expected_level
        pyboy.memory[0xFFB5] = 0x0B
        mario.post_tick()


def test_mario_deluxe_object_slots_distinguish_fireballs(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    try:
        mario = pyboy.game_wrapper
        mario.start_game(world_level=(1, 4))
        pyboy.memory[SPRITE_WRAM_BANK, ADDR_SPRITE_STATUS] = 1
        pyboy.memory[SPRITE_WRAM_BANK, ADDR_SPRITE_ID] = 0x0D
        pyboy.memory[SPRITE_WRAM_BANK, ADDR_SPRITE_X_LOW] = 100
        pyboy.memory[SPRITE_WRAM_BANK, ADDR_SPRITE_X_HIGH] = 0
        pyboy.memory[SPRITE_WRAM_BANK, ADDR_SPRITE_Y_LOW] = 50
        pyboy.memory[SPRITE_WRAM_BANK, ADDR_SPRITE_Y_HIGH] = 0

        objects = mario.object_slots()
        assert objects[0]["id"] == 0x0D
        assert objects[0]["mapped_id"] == 12
        assert objects[0]["game_area_x"] == ((100 - mario._camera_x() + 4) // 8) - mario.game_area_section[0]
        assert objects[0]["game_area_y"] == ((50 - mario._camera_y() + 4) // 8) - mario.game_area_section[1]
        assert len(objects[0]) >= 50
        assert objects[0]["d0d2"] == pyboy.memory[SPRITE_WRAM_BANK, 0xD0D2]
        assert objects[0]["d2d0"] == pyboy.memory[SPRITE_WRAM_BANK, 0xD2D0]
        sprite = SimpleNamespace(
            tile_identifier=92,
            x=100 - mario._camera_x(),
            y=50 - mario._camera_y(),
        )
        assert mario._fireball_mapping(sprite, objects) == 12

        pyboy.memory[SPRITE_WRAM_BANK, ADDR_SPRITE_ID] = 0x0F
        objects = mario.object_slots()
        assert objects[0]["mapped_id"] == 18
        assert mario._fireball_mapping(sprite, objects) == 18
    finally:
        pyboy.stop(save=False)
