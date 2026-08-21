#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy import PyBoy


def test_mario_deluxe_basics(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    assert pyboy.cartridge_title == "MARIO DELUXAHY"

    mario = pyboy.game_wrapper
    mario.start_game()

    assert mario.world == (1, 1)
    assert mario.level == 0
    assert mario.score == 0
    assert mario.coins == 0
    assert mario.lives_left == 5
    assert mario.time_left > 0


def test_mario_deluxe_level_selection(supermariobrosdeluxe_rom):
    pyboy = PyBoy(supermariobrosdeluxe_rom, window="null")
    pyboy.set_emulation_speed(0)

    mario = pyboy.game_wrapper
    mario.set_world_level(2, 2)
    mario.start_game()

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
    assert area.shape == (16, 20)
    assert area[14, 0] == 1  # The first level's floor is interaction type solid.
    assert area[14, 0] == area[15, 0]
    assert max(max(row) for row in area) >= 0x100  # Sprites must not share the background's empty value.

    pyboy.button_press("right")
    pyboy.tick(240, False)
    pyboy.button_release("right")
    assert mario.game_area()[6, 1] == 2  # The rendered coin/item box remains aligned after scrolling.
