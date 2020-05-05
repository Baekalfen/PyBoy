#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import pytest
from pyboy import PyBoy, WindowEvent
from tests.utils import supermarioland_rom


@pytest.mark.skipif(not supermarioland_rom, reason="ROM not present")
def test_mario_basics():
    pyboy = PyBoy(supermarioland_rom, window_type="dummy", game_wrapper=True)
    pyboy.set_emulation_speed(0)
    assert pyboy.cartridge_title() == "SUPER MARIOLAN"

    mario = pyboy.game_wrapper()
    mario.start_game(world_level=(1, 1))

    assert mario.score == 0
    assert mario.lives_left == 2
    assert mario.time_left == 400
    assert mario.world == (1, 1)
    assert mario.fitness == 0 # A built-in fitness score for AI development
    pyboy.stop()


@pytest.mark.skipif(not supermarioland_rom, reason="ROM not present")
def test_mario_advanced():
    pyboy = PyBoy(supermarioland_rom, window_type="dummy", game_wrapper=True)
    pyboy.set_emulation_speed(0)
    assert pyboy.cartridge_title() == "SUPER MARIOLAN"

    mario = pyboy.game_wrapper()
    mario.start_game(world_level=(3, 2))
    lives = 99
    mario.set_lives_left(lives)
    pyboy.tick()

    assert mario.score == 0
    assert mario.lives_left == lives
    assert mario.time_left == 400
    assert mario.world == (3, 2)
    assert mario.fitness == 10000*lives + 6510 # A built-in fitness score for AI development
    pyboy.stop()


@pytest.mark.skipif(not supermarioland_rom, reason="ROM not present")
def test_mario_game_over():
    pyboy = PyBoy(supermarioland_rom, window_type="dummy", game_wrapper=True)
    pyboy.set_emulation_speed(0)

    mario = pyboy.game_wrapper()
    mario.start_game()
    mario.set_lives_left(0)
    pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
    for _ in range(500): # Enough to game over correctly, and not long enough it'll work without setting the lives
        pyboy.tick()
        if mario.game_over():
            break
    pyboy.stop()
