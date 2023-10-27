#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import platform
import sys

import numpy as np
import pytest

from pyboy import PyBoy, WindowEvent

py_version = platform.python_version()[:3]
is_pypy = platform.python_implementation() == "PyPy"


def test_mario_basics(supermarioland_rom):
    pyboy = PyBoy(supermarioland_rom, window_type="null", game_wrapper=True)
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


def test_mario_advanced(supermarioland_rom):
    pyboy = PyBoy(supermarioland_rom, window_type="null", game_wrapper=True)
    pyboy.set_emulation_speed(0)
    assert pyboy.cartridge_title() == "SUPER MARIOLAN"

    mario = pyboy.game_wrapper()
    mario.start_game(world_level=(3, 2))
    lives = 99
    mario.set_lives_left(lives)
    pyboy.tick(1, False)

    assert mario.score == 0
    assert mario.lives_left == lives
    assert mario.time_left == 400
    assert mario.world == (3, 2)
    assert mario.fitness == 10000*lives + 6510 # A built-in fitness score for AI development
    pyboy.stop()


def test_mario_game_over(supermarioland_rom):
    pyboy = PyBoy(supermarioland_rom, window_type="null", game_wrapper=True)
    pyboy.set_emulation_speed(0)

    mario = pyboy.game_wrapper()
    mario.start_game()
    mario.set_lives_left(0)
    pyboy.button_press("right")
    for _ in range(500): # Enough to game over correctly, and not long enough it'll work without setting the lives
        pyboy.tick(1, False)
        if mario.game_over():
            break
    pyboy.stop()


@pytest.mark.skipif(is_pypy, reason="This requires gym, which doesn't work on this platform")
class TestOpenAIGym:
    def test_observation_type_compressed(self, supermarioland_rom):
        pyboy = PyBoy(supermarioland_rom, window_type="null", game_wrapper=True)
        pyboy.set_emulation_speed(0)

        env = pyboy.openai_gym(observation_type="compressed")
        if env is None:
            raise Exception("'env' is None. Did you remember to install 'gym'?")
        observation = env.reset()

        expected_observation = np.zeros_like(observation)
        expected_observation[-4:-2, 4:6] = 1 # Mario
        expected_observation[-2:, :] = 10 # Ground
        expected_observation[-4:-2, 1:3] = 14 # Pipe
        expected_observation[9, 5] = 13 # ? Block

        print(observation)
        print(expected_observation)
        assert np.all(observation == expected_observation)

    def test_observation_type_minimal(self, supermarioland_rom):
        pyboy = PyBoy(supermarioland_rom, window_type="null", game_wrapper=True)
        pyboy.set_emulation_speed(0)

        env = pyboy.openai_gym(observation_type="minimal")
        if env is None:
            raise Exception("'env' is None. Did you remember to install 'gym'?")
        observation = env.reset()

        expected_observation = np.zeros_like(observation)
        expected_observation[-4:-2, 4:6] = 1 # Mario
        expected_observation[-2:, :] = 3 # Ground
        expected_observation[-4:-2, 1:3] = 3 # Pipe
        expected_observation[9, 5] = 3 # ? Block

        print(observation)
        print(expected_observation)
        assert np.all(observation == expected_observation)

    def test_start_level(self, supermarioland_rom):
        pyboy = PyBoy(supermarioland_rom, window_type="null", game_wrapper=True)
        pyboy.set_emulation_speed(0)

        starting_level = (2, 1)
        env = pyboy.openai_gym(observation_type="minimal", action_type="toggle", world_level=starting_level)
        if env is None:
            raise Exception("'env' is None. Did you remember to install 'gym'?")
        observation = env.reset()

        print(env.game_wrapper.world, starting_level)
        assert env.game_wrapper.world == starting_level

        env.game_wrapper.set_lives_left(0)
        env.step(4) # PRESS LEFT

        for _ in range(200):
            env.step(0)
        assert env.game_wrapper.time_left == 399
        assert env.game_wrapper.world == starting_level
