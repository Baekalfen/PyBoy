#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import platform
from pathlib import Path

import pytest

record_gif_py = '''
# MIT License

# Copyright (c) 2023 Peter Whidden

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from os.path import exists
from pathlib import Path
import uuid
from red_gym_env import RedGymEnv
from stable_baselines3 import A2C, PPO
from stable_baselines3.common import env_checker
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.callbacks import CheckpointCallback
from argparse_pokemon import *

from pyboy import WindowEvent

RedGymEnv.add_video_frame = lambda x: None

def make_env(rank, env_conf, seed=0):
    """
    Utility function for multiprocessed env.
    :param env_id: (str) the environment ID
    :param num_env: (int) the number of environments you wish to have in subprocesses
    :param seed: (int) the initial seed for RNG
    :param rank: (int) index of the subprocess
    """
    def _init():
        env = RedGymEnv(env_conf)
        env.pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
        #env.seed(seed + rank)
        return env
    set_random_seed(seed)
    return _init

if __name__ == '__main__':

    sess_path = f'session_{str(uuid.uuid4())[:8]}'
    ep_length = 48 # 2**16
    args = get_args(usage_string=None, headless=False, ep_length=ep_length, sess_path=sess_path)

    env_config = {
                'headless': False, 'save_final_state': True, 'early_stop': False,
                'action_freq': 24, 'init_state': '../has_pokedex_nballs.state', 'max_steps': ep_length,
                'print_rewards': True, 'save_video': False, 'fast_video': True, 'session_path': sess_path,
                'gb_path': '../PokemonRed.gb', 'debug': False, 'sim_frame_dist': 2_000_000.0
            }
    env_config = change_env(env_config, args)

    num_cpu = 1 #64 #46  # Also sets the number of episodes per training iteration
    env = make_env(0, env_config)() #SubprocVecEnv([make_env(i, env_config) for i in range(num_cpu)])

    #env_checker.check_env(env)
    file_name = 'session_4da05e87_main_good/poke_439746560_steps'

    if exists(file_name + '.zip'):
        print('\\nloading checkpoint')
        model = PPO.load(file_name, env=env, custom_objects={'lr_schedule': 0, 'clip_range': 0})
        model.n_steps = ep_length
        model.n_envs = num_cpu
        model.rollout_buffer.buffer_size = ep_length
        model.rollout_buffer.n_envs = num_cpu
        model.rollout_buffer.reset()
    else:
        model = PPO('CnnPolicy', env, verbose=1, n_steps=ep_length, batch_size=512, n_epochs=1, gamma=0.999)

    #keyboard.on_press_key("M", toggle_agent)
    obs, info = env.reset()
    env.pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
    while True:
        action = 7 # pass action
        try:
            with open("agent_enabled.txt", "r") as f:
                agent_enabled = f.readlines()[0].startswith("yes")
        except:
            agent_enabled = False
        if agent_enabled:
            action, _states = model.predict(obs, deterministic=False)
        obs, rewards, terminated, truncated, info = env.step(action)
        env.render()
        if truncated:
            break
    env.pyboy.send_input(WindowEvent.SCREEN_RECORDING_TOGGLE)
    env.close()
'''


@pytest.mark.skipif(
    True or \
    os.path.isfile("extras/README/8.gif") or platform.system() == "Windows",
    reason="This test takes too long for regular use"
)
def test_pokemon_rl(git_pokemon_red_experiments, pokemon_red_rom):
    script_py = "record_gif.py"
    with open(Path(git_pokemon_red_experiments) / "baselines" / script_py, "w") as f:
        f.write(record_gif_py)

    root_path = Path("../")
    assert os.system(f'rm -rf {Path(git_pokemon_red_experiments) / "recordings"}') == 0
    assert os.system(
        f'cp "{pokemon_red_rom}" {git_pokemon_red_experiments}/PokemonRed.gb && cd {git_pokemon_red_experiments}/baselines && . {"../" / Path(".venv") / "bin" / "activate"} && python {script_py}'
    ) == 0
    assert os.system(f'mv {Path(git_pokemon_red_experiments) / "recordings" / "SUPER*"} {Path("README/8.gif")}') == 0
