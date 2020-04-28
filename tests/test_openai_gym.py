#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import numpy as np
import pytest
from pyboy import PyBoy, WindowEvent
from pyboy.botsupport.constants import COLS, ROWS

try:
    from .utils import tetris_rom
except:
    tetris_rom = "ROMs/Tetris.GB"


@pytest.fixture
def pyboy():
    pyboy = PyBoy(tetris_rom, window_type="headless", bootrom_file="pyboy_fast", disable_input=True, game_wrapper=True)
    pyboy.set_emulation_speed(0)
    return pyboy


@pytest.fixture
def screen_shape(pyboy):
    return (ROWS, COLS, 3)


@pytest.fixture
def game_area_shape(pyboy):
    return pyboy.game_wrapper().shape[::-1]


@pytest.fixture
def id0_block():
    return np.array((1, 1, 1, 2))


@pytest.fixture
def id1_block():
    return np.array((3, 4, 5, 5))


@pytest.fixture
def tiles_id():
    return {"BLANK": 47, "J": 129, "DEADBLOCK": 135}


def test_raw(pyboy, screen_shape):
    env = pyboy.openai_gym(observation_type="raw", action_type="press")
    observation = env.reset()
    assert observation.shape == screen_shape
    assert observation.dtype == np.uint8

    observation, _, _, _ = env.step(0)
    assert observation.shape == screen_shape
    assert observation.dtype == np.uint8


def test_tiles(pyboy, game_area_shape, tiles_id, id0_block, id1_block):
    env = pyboy.openai_gym(observation_type="tiles", action_type="press")
    observation = env.reset()

    # Build the expected first observation
    expected_observation = tiles_id["BLANK"] * np.ones(game_area_shape, dtype=np.uint16)
    expected_observation[id0_block, id1_block] = tiles_id["J"]
    print(observation, expected_observation)
    assert np.all(observation == expected_observation)

    expected_observation[id0_block, id1_block] = tiles_id["BLANK"]

    action = 2 # DOWN
    observation, _, _, _ = env.step(action) # Press DOWN
    observation, _, _, _ = env.step(action) # Press DOWN

    # Build the expected second observation
    expected_observation[id0_block + 1, id1_block] = tiles_id["J"]
    print(observation, expected_observation)
    assert np.all(observation == expected_observation)


def test_press(pyboy, game_area_shape, tiles_id, id0_block, id1_block):
    env = pyboy.openai_gym(observation_type="tiles", action_type="press")
    assert env.action_space.n == 9

    env.reset()
    action = 3 # RIGHT
    observation, _, _, _ = env.step(action) # Press RIGHT
    observation, _, _, _ = env.step(0) # Press NOTHING

    expected_observation = tiles_id["BLANK"] * np.ones(game_area_shape, dtype=np.uint16)
    expected_observation[id0_block, id1_block + 1] = tiles_id["J"]
    print(observation, expected_observation)
    assert np.all(observation == expected_observation)

    action = 0 # NOTHING
    for _ in range(25):
        observation, _, _, _ = env.step(action) # Press NOTHING
    print(observation, expected_observation)
    assert np.all(observation == expected_observation)


def test_toggle(pyboy, game_area_shape, tiles_id, id0_block, id1_block):
    env = pyboy.openai_gym(observation_type="tiles", action_type="toggle")
    assert env.action_space.n == 9

    env.reset()
    action = 3 # RIGHT
    observation, _, _, _ = env.step(action) # Press RIGHT
    observation, _, _, _ = env.step(0) # Press NOTHING

    expected_observation = tiles_id["BLANK"] * np.ones(game_area_shape, dtype=np.uint16)
    expected_observation[id0_block, id1_block + 1] = tiles_id["J"]
    print(observation, expected_observation)
    assert np.all(observation == expected_observation)

    expected_observation[id0_block, id1_block + 1] = tiles_id["BLANK"]

    action = 0 # NOTHING
    for _ in range(25):
        observation, _, _, _ = env.step(action) # Press NOTHING
    print(observation, expected_observation)
    expected_observation[id0_block, id1_block + 2] = tiles_id["J"]
    assert np.all(observation == expected_observation)


def test_tetris(pyboy):
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


def test_all(pyboy):
    env = pyboy.openai_gym(observation_type="tiles", action_type="all")
    assert env.action_space.n == 17
