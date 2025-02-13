#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from pyboy import PyBoy


def test_mario_basics(supermarioland_rom):
    pyboy = PyBoy(supermarioland_rom, window="null")
    pyboy.set_emulation_speed(0)
    assert pyboy.cartridge_title == "SUPER MARIOLAND"

    mario = pyboy.game_wrapper
    mario.start_game(world_level=(1, 1))

    assert mario.score == 0
    assert mario.lives_left == 2
    assert mario.time_left == 400
    assert mario.world == (1, 1)


def test_mario_advanced(supermarioland_rom):
    pyboy = PyBoy(supermarioland_rom, window="null")
    pyboy.set_emulation_speed(0)
    assert pyboy.cartridge_title == "SUPER MARIOLAND"

    mario = pyboy.game_wrapper
    mario.start_game(world_level=(3, 2))
    lives = 99
    mario.set_lives_left(lives)
    pyboy.tick(1, False, False)

    assert mario.score == 0
    assert mario.lives_left == lives
    assert mario.time_left == 400
    assert mario.world == (3, 2)


def test_mario_game_over(supermarioland_rom):
    pyboy = PyBoy(supermarioland_rom, window="null")
    pyboy.set_emulation_speed(0)

    mario = pyboy.game_wrapper
    mario.start_game()
    mario.set_lives_left(0)
    pyboy.button_press("right")
    for _ in range(500):  # Enough to game over correctly, and not long enough it'll work without setting the lives
        pyboy.tick(1, False, False)
        if mario.game_over():
            break
