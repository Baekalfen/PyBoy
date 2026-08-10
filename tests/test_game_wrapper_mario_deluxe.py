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
