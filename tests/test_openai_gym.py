#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import platform

import numpy as np
import pytest
from pyboy import PyBoy, WindowEvent
from pyboy.botsupport.constants import COLS, ROWS
from tests.utils import tetris_rom

is_pypy = platform.python_implementation() == "PyPy"


@pytest.fixture
def pyboy():
    pyboy = PyBoy(tetris_rom, window_type="headless", disable_input=True, game_wrapper=True)
    pyboy.set_emulation_speed(0)
    return pyboy


@pytest.fixture
def id0_block():
    return np.array((1, 1, 2, 2))


@pytest.fixture
def id1_block():
    return np.array((3, 4, 4, 5))


@pytest.fixture
def tiles_id():
    return {"BLANK": 47, "Z": 130, "DEADBLOCK": 135}


@pytest.mark.skipif(
    is_pypy or bool(os.getenv("MSYS")) or (not tetris_rom), reason="This requires gym, which doesn't install on PyPy"
)
class TestOpenAIGym:
    def test_raw(self, pyboy):
        env = pyboy.openai_gym(observation_type="raw", action_type="press")
        observation = env.reset()
        assert observation.shape == (ROWS, COLS, 3)
        assert observation.dtype == np.uint8

        observation, _, _, _ = env.step(0)
        assert observation.shape == (ROWS, COLS, 3)
        assert observation.dtype == np.uint8

    def test_tiles(self, pyboy, tiles_id, id0_block, id1_block):
        env = pyboy.openai_gym(observation_type="tiles")
        tetris = pyboy.game_wrapper()
        tetris.set_tetromino("Z")
        observation = env.reset()

        # Build the expected first observation
        game_area_shape = pyboy.game_wrapper().shape[::-1]
        expected_observation = tiles_id["BLANK"] * np.ones(game_area_shape, dtype=np.uint16)
        expected_observation[id0_block, id1_block] = tiles_id["Z"]
        print(observation, expected_observation)
        assert np.all(observation == expected_observation)

        expected_observation[id0_block, id1_block] = tiles_id["BLANK"]

        action = 2 # DOWN
        observation, _, _, _ = env.step(action) # Press DOWN
        observation, _, _, _ = env.step(action) # Press DOWN

        # Build the expected second observation
        expected_observation[id0_block + 1, id1_block] = tiles_id["Z"]
        print(observation, expected_observation)
        assert np.all(observation == expected_observation)

    def test_compressed(self, pyboy, tiles_id, id0_block, id1_block):
        env = pyboy.openai_gym(observation_type="compressed")
        tetris = pyboy.game_wrapper()
        tetris.set_tetromino("Z")
        observation = env.reset()

        # Build the expected first observation
        game_area_shape = pyboy.game_wrapper().shape[::-1]
        expected_observation = np.zeros(game_area_shape, dtype=np.uint16)
        expected_observation[id0_block, id1_block] = 2
        print(observation, expected_observation)
        assert np.all(observation == expected_observation)

        expected_observation[id0_block, id1_block] = 0

        action = 2 # DOWN
        observation, _, _, _ = env.step(action) # Press DOWN
        observation, _, _, _ = env.step(action) # Press DOWN

        # Build the expected second observation
        expected_observation[id0_block + 1, id1_block] = 2
        print(observation, expected_observation)
        assert np.all(observation == expected_observation)

    def test_minimal(self, pyboy, tiles_id, id0_block, id1_block):
        env = pyboy.openai_gym(observation_type="minimal")
        tetris = pyboy.game_wrapper()
        tetris.set_tetromino("Z")
        observation = env.reset()

        # Build the expected first observation
        game_area_shape = pyboy.game_wrapper().shape[::-1]
        expected_observation = np.zeros(game_area_shape, dtype=np.uint16)
        expected_observation[id0_block, id1_block] = 1
        print(observation, expected_observation)
        assert np.all(observation == expected_observation)

        expected_observation[id0_block, id1_block] = 0

        action = 2 # DOWN
        observation, _, _, _ = env.step(action) # Press DOWN
        observation, _, _, _ = env.step(action) # Press DOWN

        # Build the expected second observation
        expected_observation[id0_block + 1, id1_block] = 1
        print(observation, expected_observation)
        assert np.all(observation == expected_observation)

    def test_press(self, pyboy, tiles_id, id0_block, id1_block):
        env = pyboy.openai_gym(observation_type="tiles", action_type="press")
        tetris = pyboy.game_wrapper()
        tetris.set_tetromino("Z")
        assert env.action_space.n == 9

        env.reset()
        action = 3 # RIGHT
        observation, _, _, _ = env.step(action) # Press RIGHT
        observation, _, _, _ = env.step(0) # Press NOTHING

        game_area_shape = pyboy.game_wrapper().shape[::-1]
        expected_observation = tiles_id["BLANK"] * np.ones(game_area_shape, dtype=np.uint16)
        expected_observation[id0_block, id1_block + 1] = tiles_id["Z"]
        print(observation, expected_observation)
        assert np.all(observation == expected_observation)

        action = 0 # NOTHING
        for _ in range(25):
            observation, _, _, _ = env.step(action) # Press NOTHING
        print(observation, expected_observation)
        assert np.all(observation == expected_observation)

    def test_toggle(self, pyboy, tiles_id, id0_block, id1_block):
        env = pyboy.openai_gym(observation_type="tiles", action_type="toggle")
        tetris = pyboy.game_wrapper()
        tetris.set_tetromino("Z")
        assert env.action_space.n == 9

        env.reset()
        action = 3 # RIGHT
        observation, _, _, _ = env.step(action) # Press RIGHT
        observation, _, _, _ = env.step(0) # Press NOTHING

        game_area_shape = pyboy.game_wrapper().shape[::-1]
        expected_observation = tiles_id["BLANK"] * np.ones(game_area_shape, dtype=np.uint16)
        expected_observation[id0_block, id1_block + 1] = tiles_id["Z"]
        print(observation, expected_observation)
        assert np.all(observation == expected_observation)

        expected_observation[id0_block, id1_block + 1] = tiles_id["BLANK"]

        action = 0 # NOTHING
        for _ in range(25):
            observation, _, _, _ = env.step(action) # Press NOTHING
        print(observation, expected_observation)
        expected_observation[id0_block, id1_block + 2] = tiles_id["Z"]
        assert np.all(observation == expected_observation)

    def test_all(self, pyboy):
        env = pyboy.openai_gym(observation_type="tiles", action_type="all")
        assert env.action_space.n == 17

    def test_tetris(self, pyboy):
        tetris = pyboy.game_wrapper()
        tetris.set_tetromino("I")
        tetris.start_game()

        assert tetris.score == 0
        assert tetris.lines == 0

        for n in range(3):
            pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
            pyboy.tick()
            pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
            pyboy.tick()

        pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
        while tetris.score == 0:
            pyboy.tick()
        pyboy.tick()
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)

        for n in range(3):
            pyboy.send_input(WindowEvent.PRESS_ARROW_LEFT)
            pyboy.tick()
            pyboy.send_input(WindowEvent.RELEASE_ARROW_LEFT)
            pyboy.tick()

        tetris.set_tetromino("O")
        pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
        while tetris.score == 16:
            pyboy.tick()
        pyboy.tick()
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)

        pyboy.tick()
        pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
        while tetris.score == 32:
            pyboy.tick()
        pyboy.tick()
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)

        while tetris.score == 47:
            pyboy.tick()

        pyboy.tick()
        pyboy.tick()
        assert tetris.score == 87
        assert tetris.lines == 1

        while not tetris.game_over():
            pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
            pyboy.tick()
            pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)
            pyboy.tick()

        pyboy.stop(save=False)

    def test_reward(self, pyboy):
        tetris = pyboy.game_wrapper()
        tetris.set_tetromino("I")

        env = pyboy.openai_gym(action_type="all")
        env.reset()

        for n in range(3):
            _, reward, _, _ = env.step(WindowEvent.PRESS_ARROW_RIGHT)
            assert reward == 0
            _, reward, _, _ = env.step(WindowEvent.RELEASE_ARROW_RIGHT)
            assert reward == 0

        _, reward, _, _ = env.step(WindowEvent.PRESS_ARROW_DOWN)
        while tetris.score == 0:
            assert reward == 0
            _, reward, _, _ = env.step(0)
        assert reward == 16

        env.step(0)
        env.step(0)
        _, reward, _, _ = env.step(WindowEvent.RELEASE_ARROW_DOWN)
        assert reward == 0

        for n in range(3):
            _, reward, _, _ = env.step(WindowEvent.PRESS_ARROW_LEFT)
            assert reward == 0
            _, reward, _, _ = env.step(WindowEvent.RELEASE_ARROW_LEFT)
            assert reward == 0

        tetris.set_tetromino("O")
        env.step(WindowEvent.PRESS_ARROW_DOWN)
        while tetris.score == 16:
            assert reward == 0
            _, reward, _, _ = env.step(0)
        assert reward == 16

        _, reward, _, _ = env.step(0)
        assert reward == 0

        env.step(0)
        _, reward, _, _ = env.step(WindowEvent.RELEASE_ARROW_DOWN)
        assert reward == 0

        env.step(0)
        env.step(WindowEvent.PRESS_ARROW_DOWN)
        while tetris.score == 32:
            assert reward == 0
            _, reward, _, _ = env.step(0)
        assert reward == 15

        env.step(0)
        env.step(0)
        _, reward, _, _ = env.step(WindowEvent.RELEASE_ARROW_DOWN)

        while tetris.score == 47:
            assert reward == 0
            _, reward, _, _ = env.step(0)
        assert reward == 40

        env.step(0)
        env.step(0)
        assert tetris.score == 87
        assert tetris.lines == 1

        while not tetris.game_over():
            env.step(WindowEvent.PRESS_ARROW_DOWN)
            env.step(WindowEvent.RELEASE_ARROW_DOWN)

        env.close()
