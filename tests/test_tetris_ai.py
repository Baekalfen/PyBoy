#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import platform
from pathlib import Path

import pytest

record_gif_py = """
import time
import os
import io
import pickle
import numpy as np
import torch
from pyboy import utils
import sys

from datetime import datetime
from core.gen_algo import get_score, Population, Network
from core.utils import check_needed_turn, do_action, drop_down, \
    do_sideway, do_turn, check_needed_dirs, feature_names
from pyboy import PyBoy, WindowEvent
from multiprocessing import Pool, cpu_count

logger = utils.getLogger("tetris")
logger.setLevel(logging.INFO)

fh = logging.FileHandler('logs.out')
fh.setLevel(logging.INFO)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

epochs = 50
population = None
run_per_child = 3
max_fitness = 0
pop_size = 50
max_score = 999999
n_workers = cpu_count()


frames = []


def eval_network(epoch, child_index, child_model, record_to):
    pyboy = PyBoy('tetris_1.1.gb', game_wrapper=True, window_type="null")
    pyboy.set_emulation_speed(0)
    tetris = pyboy.game_wrapper()
    tetris.start_game()
    pyboy._rendering(False)
    pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)

    # Set block animation to fall instantly
    pyboy.memory[0xff9a] = 2

    run = 0
    scores = []
    levels = []
    lines = []

    while run < run_per_child:
        # Beginning of action
        best_action_score = np.NINF
        best_action = {'Turn': 0, 'Left': 0, 'Right': 0}
        begin_state = io.BytesIO()
        begin_state.seek(0)
        pyboy.save_state(begin_state)
        # Number of lines at the start
        s_lines = tetris.lines

        # Determine how many possible rotations we need to check for the block
        block_tile = pyboy.memory[0xc203]
        turns_needed = check_needed_turn(block_tile)
        lefts_needed, rights_needed = check_needed_dirs(block_tile)

        # Do middle
        for move_dir in do_action('Middle', pyboy, n_dir=1,
                                  n_turn=turns_needed):
            score = get_score(tetris, child_model, s_lines)
            if score is not None and score >= best_action_score:
                best_action_score = score
                best_action = {'Turn': move_dir['Turn'],
                               'Left': move_dir['Left'],
                               'Right': move_dir['Right']}
            begin_state.seek(0)
            pyboy.load_state(begin_state)

        # Do left
        for move_dir in do_action('Left', pyboy, n_dir=lefts_needed,
                                  n_turn=turns_needed):
            score = get_score(tetris, child_model, s_lines)
            if score is not None and score >= best_action_score:
                best_action_score = score
                best_action = {'Turn': move_dir['Turn'],
                               'Left': move_dir['Left'],
                               'Right': move_dir['Right']}
            begin_state.seek(0)
            pyboy.load_state(begin_state)

        # Do right
        for move_dir in do_action('Right', pyboy, n_dir=rights_needed,
                                  n_turn=turns_needed):
            score = get_score(tetris, child_model, s_lines)
            if score is not None and score >= best_action_score:
                best_action_score = score
                best_action = {'Turn': move_dir['Turn'],
                               'Left': move_dir['Left'],
                               'Right': move_dir['Right']}
            begin_state.seek(0)
            pyboy.load_state(begin_state)

        # Do best action
        for _ in range(best_action['Turn']):
            do_turn(pyboy)
        for _ in range(best_action['Left']):
            do_sideway(pyboy, 'Left')
        for _ in range(best_action['Right']):
            do_sideway(pyboy, 'Right')
        drop_down(pyboy)
        pyboy.tick(1, True)
        frames.append(pyboy.screen_image())
        pyboy._rendering(False)
        if len(frames) >= record_to:
            directory = os.path.join(os.path.curdir, "recordings")
            if not os.path.exists(directory):
                os.makedirs(directory, mode=0o755)
            path = os.path.join(directory, time.strftime(f"{pyboy.cartridge_title()}-%Y.%m.%d-%H.%M.%S.gif"))

            frames[0].save(
                path,
                save_all=True,
                interlace=False,
                loop=0,
                optimize=True,
                append_images=frames[1:],
                duration=int(round(1000 / 30, -1))
            )
            pyboy.stop()
            exit(0)

        # Game over:
        if tetris.game_over() or tetris.score == max_score:
            scores.append(tetris.score)
            levels.append(tetris.level)
            lines.append(tetris.lines)
            if run == run_per_child - 1:
                pyboy.stop()
            else:
                tetris.reset_game()
            run += 1

    child_fitness = np.average(scores)
    logger.info("-" * 20)
    logger.info("Iteration %s - child %s" % (epoch, child_index))
    logger.info("Score: %s, Level: %s, Lines %s" % (scores, levels, lines))
    logger.info("Fitness: %s" % child_fitness)
    logger.info("Output weight:")
    weights = {}
    for i, j in zip(feature_names, child_model.output.weight.data.tolist()[0]):
        weights[i] = np.round(j, 3)
    logger.info(weights)

    return child_fitness


if __name__ == '__main__':
    state_dict = torch.load('models/best.pkl')
    model = Network()
    model.load_state_dict(state_dict)
    eval_network(0, 0, model, 5)


"""


@pytest.mark.skipif(
    os.path.isfile("extras/README/7.gif") or platform.system() == "Windows",
    reason="This test takes too long for regular use"
)
def test_tetris_ai(git_tetris_ai, tetris_rom):
    script_py = "tetris_gif.py"
    with open(Path(git_tetris_ai) / script_py, "w") as f:
        f.write(record_gif_py)

    root_path = Path("../")
    assert os.system(f'rm -rf {Path(git_tetris_ai) / "recordings"}') == 0
    assert os.system(f"cp {tetris_rom} {Path(git_tetris_ai) / 'tetris_1.1.gb'}") == 0
    assert os.system(f'cd {git_tetris_ai} && . {Path(".venv") / "bin" / "activate"} && python {script_py}') == 0
    assert os.system(f'mv {Path(git_tetris_ai) / "recordings" / "TETRIS*"} {Path("extras/README/7.gif")}') == 0
